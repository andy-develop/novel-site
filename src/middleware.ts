import { defineMiddleware } from 'astro:middleware';

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
const DEFAULT_SMAXAGE = 900; // 15 min fresh
const MAX_SMAXAGE = 900; // cap: content fixes should reach readers within minutes
const DEFAULT_SWR = 86400; // serve stale for a day while revalidating

function edgeCacheControl(existing: string | null): string {
  const maxAge = /max-age=(\d+)/.exec(existing ?? '')?.[1] ?? '0';
  const declared = Number(/s-maxage=(\d+)/.exec(existing ?? '')?.[1] ?? DEFAULT_SMAXAGE);
  const sMaxAge = Math.min(declared, MAX_SMAXAGE);
  return `public, max-age=${maxAge}, s-maxage=${sMaxAge}, stale-while-revalidate=${DEFAULT_SWR}`;
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

  const hit = await cache!.match(key);
  if (hit) {
    // Cache API responses have immutable headers; copy them so the runtime can
    // still set its own response headers.
    const headers = new Headers();
    hit.headers.forEach((value, name) => headers.set(name, value));
    return new Response(hit.body, { status: hit.status, headers });
  }

  const res = await next();

  const type = res.headers.get('content-type') ?? '';
  if (res.status !== 200 || !type.includes('text/html')) return res;

  const headers = new Headers();
  res.headers.forEach((value, name) => headers.set(name, value));
  // Chapter pages declare their own browser policy; the edge TTL is capped so
  // corrected text is visible within minutes rather than days.
  headers.set('Cache-Control', edgeCacheControl(res.headers.get('cache-control')));

  const body = await res.arrayBuffer();
  const out = new Response(body, { status: 200, statusText: res.statusText, headers });

  try {
    await cache!.put(key, out.clone());
  } catch {
    // A failed put must never break the response.
  }

  return out;
});