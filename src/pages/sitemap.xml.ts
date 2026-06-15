import type { APIRoute } from 'astro';
import { getBooks, getEnglishBooks } from '../utils/data';

export const GET: APIRoute = async ({ locals }) => {
  const allBooks = await getBooks(locals);
  const books = getEnglishBooks(allBooks);
  const tags = Array.from(new Set(books.flatMap(b => b.tags || []))).sort();

  const urls: { loc: string; changefreq: string; priority: string }[] = [
    { loc: 'https://lyriq.space', changefreq: 'daily', priority: '1.0' },
  ];

  for (const book of books) {
    urls.push({ loc: `https://lyriq.space/novel/${book.id}`, changefreq: 'weekly', priority: '0.8' });
    const total = book.total_chapters || 0;
    for (let i = 1; i <= total; i++) {
      urls.push({ loc: `https://lyriq.space/novel/${book.id}/${i}`, changefreq: 'monthly', priority: '0.6' });
    }
  }

  for (const tag of tags) {
    urls.push({ loc: `https://lyriq.space/tag/${encodeURIComponent(tag)}`, changefreq: 'weekly', priority: '0.7' });
  }

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls.map(u => `  <url><loc>${u.loc}</loc><changefreq>${u.changefreq}</changefreq><priority>${u.priority}</priority></url>`).join('\n')}
</urlset>`;

  return new Response(xml, { headers: { 'Content-Type': 'application/xml' } });
};
