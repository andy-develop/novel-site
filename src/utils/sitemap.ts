import type { Book } from './data';
import { getTagStats } from './data';
import { getBookUrl, getChapterUrl, slugify } from './seo';

/**
 * Google/Bing ignore a single sitemap with more than 50,000 URLs. The catalog
 * is ~2,000 books and ~75,000 chapters, so the URL set is split into shards of
 * at most MAX_URLS_PER_SHARD, listed by /sitemap.xml (a sitemap index).
 */
export const MAX_URLS_PER_SHARD = 40_000;

export interface SitemapShard {
  /** File name, e.g. `sitemap-1.xml`. */
  name: string;
  /** Books whose chapter URLs belong to this shard. */
  books: Book[];
  /** Home + tag URLs are only emitted once, in the first shard. */
  includeMeta: boolean;
  urlCount: number;
}

/**
 * Tag pages listed in the sitemap: only the indexable ones (see
 * `MIN_BOOKS_PER_INDEXABLE_TAG`). The ~2,800 long-tail tags are 1-2 book pages
 * that would otherwise eat most of the crawl budget.
 */
export function uniqueTagSlugs(books: Book[]): string[] {
  const seen = new Set<string>();
  for (const { tag } of getTagStats(books)) {
    const slug = slugify(tag);
    if (slug) seen.add(slug);
  }
  return Array.from(seen).sort();
}

export function planSitemap(books: Book[]): SitemapShard[] {
  const metaCount = 1 + uniqueTagSlugs(books).length; // home page + tag pages
  const shards: SitemapShard[] = [];

  let current: SitemapShard = {
    name: 'sitemap-1.xml',
    books: [],
    includeMeta: true,
    urlCount: metaCount,
  };

  for (const book of books) {
    const chapters = Math.max(0, book.total_chapters || 0);
    const cost = 1 + chapters; // book page + its chapter pages
    if (current.urlCount + cost > MAX_URLS_PER_SHARD && current.books.length > 0) {
      shards.push(current);
      current = {
        name: `sitemap-${shards.length + 1}.xml`,
        books: [],
        includeMeta: false,
        urlCount: 0,
      };
    }
    current.books.push(book);
    current.urlCount += cost;
  }

  shards.push(current);
  return shards;
}

export interface SitemapEntry {
  loc: string;
  lastmod: string;
}

export function shardEntries(shard: SitemapShard, origin: string, lastmod: string, allBooks: Book[]): SitemapEntry[] {
  const entries: SitemapEntry[] = [];

  if (shard.includeMeta) {
    entries.push({ loc: `${origin}/`, lastmod });
    for (const slug of uniqueTagSlugs(allBooks)) {
      entries.push({ loc: `${origin}/tag/${slug}`, lastmod });
    }
  }

  for (const book of shard.books) {
    entries.push({ loc: `${origin}${getBookUrl(book)}`, lastmod });
    const chapters = Math.max(0, book.total_chapters || 0);
    for (let i = 1; i <= chapters; i++) {
      entries.push({ loc: `${origin}${getChapterUrl(book, i)}`, lastmod });
    }
  }

  return entries;
}

export function renderUrlset(entries: SitemapEntry[]): string {
  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${entries.map(e => `  <url>\n    <loc>${e.loc}</loc>\n    <lastmod>${e.lastmod}</lastmod>\n  </url>`).join('\n')}
</urlset>`;
}

export function renderIndex(shards: SitemapShard[], origin: string, lastmod: string): string {
  return `<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${shards.map(s => `  <sitemap>\n    <loc>${origin}/${s.name}</loc>\n    <lastmod>${lastmod}</lastmod>\n  </sitemap>`).join('\n')}
</sitemapindex>`;
}