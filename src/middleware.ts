import { defineMiddleware } from 'astro:middleware';
import { dataStats } from './utils/data';

/**
 * Edge HTML cache.
 *
 * The site is a fully server-rendered Astro app on a Workers free-tier account:
 * every HTML response is rebuilt per request, which is the main source of CPU
 * time limit (error 1102) notifications. Caching the rendered HTML in the
 * Workers Cache API means repeat crawler/reader hits cost ~0 CPU.
 *
 * Only complete 2xx HTML documents are stored. Redirects, 404s, API routes and
 * static assets are passed through untouched.
 */
const DEFAULT_SMAXAGE = 3_600; // 1 h — home/tag/book pages change as books publish
const CHAPTER_SMAXAGE = 86_400; // 24 h — a chapter's HTML never changes once written
const DEFAULT_SWR = 86_400;

/**
 * Chapter URLs (`/novel/<slug>/<chapterId>`) are immutable: corrections are rare
 * and chapters arrive as new URLs, so one render per day per URL is enough.
 * Listing pages (home, tags, book) reflect new chapters and get an hour.
 */
function ttlForPath(pathname: string): number {
  return /^\/novel\/[^/]+\/\d+\/?$/.test(pathname) ? CHAPTER_SMAXAGE : DEFAULT_SMAXAGE;
}

function edgeCacheControl(existing: string | null, pathname: string): string {
  const maxAge = /max-age=(\d+)/.exec(existing ?? '')?.[1] ?? '0';
  return `public, max-age=${maxAge}, s-maxage=${ttlForPath(pathname)}, stale-while-revalidate=${DEFAULT_SWR}`;
}

export const onRequest = defineMiddleware(async (context, next) => {
  const { request, url } = context;
  const cache = (globalThis as any).caches?.default as Cache | undefined;

  const cacheable =
    !!cache &&
    request.method === 'GET' &&
    !url.pathname.startsWith('/api/') &&
    !url.pathname.startsWith('/cdn-cgi/');

  if (!cacheable) return next();

  const key = new Request(url.toString(), { method: 'GET' });
  // ?debug=1 forces a fresh render and reports timing; it never touches the cache.
  const debug = url.searchParams.has('debug');
  const startedAt = Date.now();

  const hit = debug ? null : await cache!.match(key);
  if (hit) {
    // Cache API responses have immutable headers; copy them so the runtime can
    // still set its own response headers.
    const headers = new Headers();
    hit.headers.forEach((value, name) => headers.set(name, value));
    headers.set('X-Lyriq-Cache', 'hit');
    return new Response(hit.body, { status: hit.status, headers });
  }

  const res = await next();
  const renderMs = Date.now() - startedAt;

  const type = res.headers.get('content-type') ?? '';
  if (res.status !== 200 || !type.includes('text/html')) return res;

  const headers = new Headers();
  res.headers.forEach((value, name) => headers.set(name, value));
  // Chapter pages keep their browser policy; the edge TTL follows the path.
  headers.set('Cache-Control', edgeCacheControl(res.headers.get('cache-control'), url.pathname));
  const body = await res.arrayBuffer();

  // A truncated render (Astro streams, so a runtime error yields 200 + partial
  // HTML) must never be cached; those responses have no closing body tag.
  // Only the tail is decoded: page scripts may be emitted after </html>.
  const tailBytes = Math.min(body.byteLength, 262_144);
  const tail = new TextDecoder('latin1').decode(
    new Uint8Array(body, body.byteLength - tailBytes, tailBytes)
  );
  const complete = body.byteLength > 2000 && tail.includes('</body>');

  headers.set('X-Lyriq-Cache', complete ? 'miss' : 'bypass');
  if (debug) {
    headers.set('X-Debug-Render-Ms', String(renderMs));
    headers.set('X-Debug-Body-Kb', String(Math.round(body.byteLength / 1024)));
    headers.set('X-Debug-Books', `${dataStats.cache}:${dataStats.source}:${dataStats.fetchMs}ms:${Math.round(dataStats.bytes / 1024)}kb:map${dataStats.mapMs}ms`);
  }
  const out = new Response(body, { status: 200, statusText: res.statusText, headers });

  if (complete && !debug) {
    try {
      await cache!.put(key, out.clone());
    } catch {
      // A failed put must never break the response.
    }
  }

  return out;
});