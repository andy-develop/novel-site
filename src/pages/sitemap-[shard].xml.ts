import type { APIRoute } from 'astro';
import { getBooks, getEnglishBooks } from '../utils/data';
import { renderUrlset, planSitemap, shardEntries } from '../utils/sitemap';

/**
 * One shard of the URL set (`/sitemap-1.xml`, `/sitemap-2.xml`, ...).
 * See `utils/sitemap.ts` for the split rule and `/sitemap.xml` for the index.
 */
const CACHE_TTL_SECONDS = 21_600; // 6 h
const STALE_WHILE_REVALIDATE = 86_400;

export const GET: APIRoute = async ({ params, request }) => {
  const origin = new URL(request.url).origin;
  const shardParam = params.shard ?? '';
  const shardIndex = Number(shardParam);

  const cache = (globalThis as any).caches?.default as Cache | undefined;
  const cacheKey = new Request(`${origin}/__cache__/sitemap-${shardParam}.xml`, { method: 'GET' });

  if (cache) {
    const hit = await cache.match(cacheKey);
    if (hit) {
      const headers = new Headers();
      hit.headers.forEach((value, name) => headers.set(name, value));
      return new Response(hit.body, { status: hit.status, headers });
    }
  }

  if (!Number.isInteger(shardIndex) || shardIndex < 1) {
    return new Response('Not found', { status: 404 });
  }

  const books = getEnglishBooks(await getBooks());
  const shards = planSitemap(books);
  const shard = shards[shardIndex - 1];
  if (!shard) return new Response('Not found', { status: 404 });

  const lastmod = new Date().toISOString();
  const xml = renderUrlset(shardEntries(shard, origin, lastmod, books));

  const response = new Response(xml, {
    headers: {
      'Content-Type': 'application/xml; charset=utf-8',
      'Cache-Control': `public, max-age=0, s-maxage=${CACHE_TTL_SECONDS}, stale-while-revalidate=${STALE_WHILE_REVALIDATE}`,
    },
  });

  if (cache && shard.books.length > 0) {
    try {
      await cache.put(cacheKey, response.clone());
    } catch {
      // Ignore cache write failures; the response is still valid.
    }
  }

  return response;
};