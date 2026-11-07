import type { APIRoute } from 'astro';
import { getBooks, getEnglishBooks, getAllTags } from '../utils/data';
import { getBookUrl, getChapterUrl, slugify } from '../utils/seo';

interface UrlEntry {
  loc: string;
  lastmod: string;
}

/**
 * Building this document walks every book and every chapter (~50k URLs, ~6 MB
 * of XML). Doing that on each request was the single most expensive route on
 * the free Workers plan, so the rendered XML is cached at the edge.
 */
const CACHE_TTL_SECONDS = 21_600; // 6 h
const STALE_WHILE_REVALIDATE = 86_400;

export const GET: APIRoute = async ({ request }) => {
  const origin = new URL(request.url).origin;
  const cache = (globalThis as any).caches?.default as Cache | undefined;
  const cacheKey = new Request(`${origin}/__cache__/sitemap.xml`, { method: 'GET' });

  if (cache) {
    const hit = await cache.match(cacheKey);
    if (hit) return hit;
  }

  const now = new Date().toISOString();
  const allBooks = await getBooks();
  const books = getEnglishBooks(allBooks);
  const entries: UrlEntry[] = [{ loc: origin, lastmod: now }];

  // Novel pages and chapter pages
  for (const book of books) {
    const bookUrl = `${origin}${getBookUrl(book)}`;
    entries.push({ loc: bookUrl, lastmod: now });

    const totalChapters = book.total_chapters || 0;
    for (let i = 1; i <= totalChapters; i++) {
      entries.push({ loc: `${origin}${getChapterUrl(book, i)}`, lastmod: now });
    }
  }

  // Tag pages (slug URLs)
  const tags = getAllTags(books);
  for (const tag of tags) {
    entries.push({ loc: `${origin}/tag/${slugify(tag)}`, lastmod: now });
  }

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${entries.map(e => `  <url>\n    <loc>${e.loc}</loc>\n    <lastmod>${e.lastmod}</lastmod>\n  </url>`).join('\n')}
</urlset>`;

  const response = new Response(xml, {
    headers: {
      'Content-Type': 'application/xml; charset=utf-8',
      'Cache-Control': `public, max-age=0, s-maxage=${CACHE_TTL_SECONDS}, stale-while-revalidate=${STALE_WHILE_REVALIDATE}`,
    },
  });

  if (cache) {
    try {
      await cache.put(cacheKey, response.clone());
    } catch {
      // Ignore cache write failures; the response is still valid.
    }
  }

  return response;
};
