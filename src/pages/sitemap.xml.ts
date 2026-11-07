import type { APIRoute } from 'astro';
import { getBooks, getEnglishBooks } from '../utils/data';
import { planSitemap, renderIndex } from '../utils/sitemap';

/**
 * Sitemap index. The catalog is ~2,000 books and ~75,000 chapters, which is
 * more than a single sitemap may contain (50,000 URLs), so the URL set lives in
 * /sitemap-<n>.xml shards and this document lists them.
 *
 * Both the index and the shards are cached at the edge: rebuilding the URL set
 * walks the whole catalog and was the most expensive route on the free plan.
 */
const CACHE_TTL_SECONDS = 21_600; // 6 h
const STALE_WHILE_REVALIDATE = 86_400;

export const GET: APIRoute = async ({ request }) => {
  const origin = new URL(request.url).origin;
  const cache = (globalThis as any).caches?.default as Cache | undefined;
  const cacheKey = new Request(`${origin}/__cache__/sitemap-index.xml`, { method: 'GET' });

  if (cache) {
    const hit = await cache.match(cacheKey);
    if (hit) {
      const headers = new Headers();
      hit.headers.forEach((value, name) => headers.set(name, value));
      return new Response(hit.body, { status: hit.status, headers });
    }
  }

  const books = getEnglishBooks(await getBooks());
  const xml = renderIndex(planSitemap(books), origin, new Date().toISOString());

  const response = new Response(xml, {
    headers: {
      'Content-Type': 'application/xml; charset=utf-8',
      'Cache-Control': `public, max-age=0, s-maxage=${CACHE_TTL_SECONDS}, stale-while-revalidate=${STALE_WHILE_REVALIDATE}`,
    },
  });

  if (cache && books.length > 0) {
    try {
      await cache.put(cacheKey, response.clone());
    } catch {
      // Ignore cache write failures; the response is still valid.
    }
  }

  return response;
};