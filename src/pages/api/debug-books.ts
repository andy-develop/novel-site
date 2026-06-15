import type { APIRoute } from 'astro';
import { getBooks } from '../../utils/data';

export const GET: APIRoute = async ({ locals }) => {
  const allBooks = await getBooks(locals);
  const ids = allBooks.map(b => b.id);
  const has29 = allBooks.some(b => b.id === 29);
  const b29 = allBooks.find(b => b.id === 29);

  return new Response(JSON.stringify({
    total: allBooks.length,
    ids,
    has29,
    book29: b29 || null,
    source: locals?.runtime?.env?.R2_BUCKET ? 'R2_BINDING' : 'HTTP_FALLBACK',
  }, null, 2), {
    headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' }
  });
};
