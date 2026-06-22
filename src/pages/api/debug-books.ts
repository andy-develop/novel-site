import type { APIRoute } from 'astro';
import { getBooks } from '../../utils/data';

export const GET: APIRoute = async () => {
  try {
    const allBooks = await getBooks();
    const ids = allBooks.map(b => b.id);
    const has29 = allBooks.some(b => b.id === 29);
    const b29 = allBooks.find(b => b.id === 29);

    // cloudflare:workers only available in CF runtime
    let bucketExists = false;
    try {
      const { env: cfEnv } = await import('cloudflare:workers');
      bucketExists = !!(cfEnv as Record<string, any>).R2_BUCKET;
    } catch { /* not in CF runtime */ }

    return new Response(JSON.stringify({
      total: allBooks.length,
      ids,
      has29,
      book29: b29 || null,
      source: bucketExists ? 'R2_BINDING' : 'HTTP_FALLBACK',
    }, null, 2), {
      headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' }
    });
  } catch (e: any) {
    return new Response(JSON.stringify({ error: e.message, stack: e.stack }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};
