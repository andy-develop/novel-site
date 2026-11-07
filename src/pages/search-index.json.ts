import type { APIRoute } from 'astro';
import { getBooks, getEnglishBooks } from '../utils/data';

/**
 * Client-side search corpus.
 *
 * The home page used to inline all ~2,000 books into the SearchIsland props,
 * which added ~1.6 MB of JSON to every rendered page (and the matching
 * serialization cost to every request). The island now fetches this once, on
 * first focus, so the corpus stays out of the HTML.
 */
export const GET: APIRoute = async () => {
  const books = getEnglishBooks(await getBooks());

  const index = books.map(b => ({
    id: b.id,
    slug: b.slug,
    title: b.title,
    author: b.author,
    tags: b.tags,
    intro: (b.intro || '').slice(0, 120),
    total_chapters: b.total_chapters,
  }));

  return new Response(JSON.stringify(index), {
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Cache-Control': 'public, max-age=300, s-maxage=86400, stale-while-revalidate=604800',
    },
  });
};