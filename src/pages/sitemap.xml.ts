import type { APIRoute } from 'astro';
import { getBooks, getEnglishBooks, getAllTags } from '../utils/data';
import { getBookUrl, getChapterUrl, slugify } from '../utils/seo';

interface UrlEntry {
  loc: string;
  lastmod: string;
}

export const GET: APIRoute = async () => {
  const now = new Date().toISOString();
  const allBooks = await getBooks();
  const books = getEnglishBooks(allBooks);
  const entries: UrlEntry[] = [{ loc: 'https://lyriq.space', lastmod: now }];

  // Novel pages and chapter pages
  for (const book of books) {
    const bookUrl = `https://lyriq.space${getBookUrl(book)}`;
    entries.push({ loc: bookUrl, lastmod: now });

    const totalChapters = book.total_chapters || 0;
    for (let i = 1; i <= totalChapters; i++) {
      entries.push({ loc: `https://lyriq.space${getChapterUrl(book, i)}`, lastmod: now });
    }
  }

  // Tag pages (slug URLs)
  const tags = getAllTags(books);
  for (const tag of tags) {
    entries.push({ loc: `https://lyriq.space/tag/${slugify(tag)}`, lastmod: now });
  }

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${entries.map(e => `  <url>\n    <loc>${e.loc}</loc>\n    <lastmod>${e.lastmod}</lastmod>\n  </url>`).join('\n')}
</urlset>`;

  return new Response(xml, {
    headers: { 'Content-Type': 'application/xml; charset=utf-8' },
  });
};
