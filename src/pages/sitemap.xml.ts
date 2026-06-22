import type { APIRoute } from 'astro';
import { env as cfEnv } from 'cloudflare:workers';
import { getBooks, getEnglishBooks } from '../utils/data';

interface UrlEntry {
  loc: string;
  lastmod: string;
}

function iso(dt: Date): string {
  return dt.toISOString();
}

export const GET: APIRoute = async () => {
  const bucket = (cfEnv as Record<string, any>).R2_BUCKET as R2Bucket | null;
  const allBooks = await getBooks();
  const books = getEnglishBooks(allBooks);
  const tags = Array.from(new Set(books.flatMap(b => b.tags || []))).sort();

  const now = iso(new Date());
  const urls: UrlEntry[] = [
    { loc: 'https://lyriq.space', lastmod: now },
  ];

  // --- Collect R2 object timestamps via list() ---
  // Key pattern: "{bookId}/{chId}.json" for chapters, "catalog_{bookId}.json", "books.json"
  // R2Object.uploaded gives us the precise last-modified time
  const chapterLastmod = new Map<string, string>(); // "bookId/chId" -> ISO
  const bookLatestLastmod = new Map<number, string>(); // bookId -> latest ISO

  if (bucket) {
    // Batch-list all objects (chapters are under "{bookId}/" prefixes)
    for (const book of books) {
      const prefix = `${book.id}/`;
      let cursor: string | undefined;
      try {
        do {
          const listed = await bucket.list({ prefix, limit: 500, cursor });
          for (const obj of listed.objects) {
            // obj.key = "1/45.json"
            const match = obj.key.match(/^(\d+)\/(\d+)\.json$/);
            if (match) {
              const [, , chId] = match;
              const ts = iso(obj.uploaded);
              chapterLastmod.set(`${book.id}/${chId}`, ts);
              // Track latest for book-level lastmod
              const existing = bookLatestLastmod.get(book.id);
              if (!existing || ts > existing) {
                bookLatestLastmod.set(book.id, ts);
              }
            }
          }
          cursor = listed.truncated ? listed.cursor : undefined;
        } while (cursor);
      } catch {
        // If list fails for a book, we'll fall back to 'now'
      }
    }
  }

  // --- Book pages ---
  for (const book of books) {
    const bookLastmod = bookLatestLastmod.get(book.id) || now;
    urls.push({ loc: `https://lyriq.space/novel/${book.id}`, lastmod: bookLastmod });

    // Chapter pages
    const total = book.total_chapters || 0;
    for (let i = 1; i <= total; i++) {
      const chLastmod = chapterLastmod.get(`${book.id}/${i}`) || bookLastmod;
      urls.push({ loc: `https://lyriq.space/novel/${book.id}/${i}`, lastmod: chLastmod });
    }
  }

  // --- Tag pages ---
  for (const tag of tags) {
    urls.push({ loc: `https://lyriq.space/tag/${encodeURIComponent(tag)}`, lastmod: now });
  }

  // --- Build XML ---
  const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls.map(u => `  <url>
    <loc>${esc(u.loc)}</loc>
    <lastmod>${u.lastmod}</lastmod>
  </url>`).join('\n')}
</urlset>`;

  return new Response(xml, {
    headers: { 'Content-Type': 'application/xml; charset=utf-8' },
  });
};
