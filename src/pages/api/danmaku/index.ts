import type { APIRoute } from 'astro';
import { getDanmaku, appendDanmaku, recentCountByHash } from '../../../utils/danmaku';
import { validateDanmaku } from '../../../utils/badwords';

const RATE_LIMIT_PER_MINUTE = 5;
const RATE_WINDOW_SEC = 60;
const MAX_ENTRIES_PER_CHAPTER = 500;

function hashIp(ip: string): string {
  // Simple hash — not crypto-grade, just for basic throttle grouping
  let h = 0;
  for (let i = 0; i < ip.length; i++) {
    h = ((h << 5) - h + ip.charCodeAt(i)) | 0;
  }
  return 'h_' + Math.abs(h).toString(36);
}

function getClientIP(request: Request): string {
  return request.headers.get('cf-connecting-ip')
    || request.headers.get('x-forwarded-for')?.split(',')[0]?.trim()
    || 'unknown';
}

export const GET: APIRoute = async ({ url }) => {
  const bookId = parseInt(url.searchParams.get('book_id') || '');
  const chapterId = parseInt(url.searchParams.get('chapter_id') || '');
  if (!bookId || !chapterId) {
    return new Response(JSON.stringify({ error: 'Missing book_id or chapter_id' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const file = await getDanmaku(bookId, chapterId);
  return new Response(JSON.stringify(file), {
    headers: {
      'Content-Type': 'application/json',
      'Cache-Control': 'no-store',
    },
  });
};

export const POST: APIRoute = async ({ request }) => {
  let body: any;
  try {
    body = await request.json();
  } catch {
    return new Response(JSON.stringify({ error: 'Invalid JSON' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const { book_id, chapter_id, paragraph_idx, content, reaction_type } = body;
  if (!book_id || !chapter_id || paragraph_idx === undefined || !content) {
    return new Response(JSON.stringify({ error: 'Missing required fields' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  // Validate content
  const v = validateDanmaku(content);
  if (!v.ok) {
    return new Response(JSON.stringify({ error: v.error }), {
      status: 422,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  // Rate limit by IP
  const ip = getClientIP(request);
  const sessionHash = hashIp(ip);
  const currentFile = await getDanmaku(book_id, chapter_id);
  const recent = recentCountByHash(currentFile, sessionHash, RATE_WINDOW_SEC);
  if (recent >= RATE_LIMIT_PER_MINUTE) {
    return new Response(JSON.stringify({ error: 'Rate limit exceeded' }), {
      status: 429,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  // Chapter total cap — keep newest, trim oldest before append
  if (currentFile.entries.length >= MAX_ENTRIES_PER_CHAPTER) {
    currentFile.entries = currentFile.entries.slice(-(MAX_ENTRIES_PER_CHAPTER - 1));
  }

  const entry = {
    id: 0, // will be assigned by appendDanmaku
    paragraph_idx: parseInt(paragraph_idx),
    content: content.trim(),
    reaction_type: (['text', 'emoji'].includes(reaction_type)
      ? reaction_type : 'text') as 'text' | 'emoji',
    session_hash: sessionHash,
    created_at: Math.floor(Date.now() / 1000),
  };

  const updated = await appendDanmaku(book_id, chapter_id, entry);
  return new Response(JSON.stringify(updated), {
    status: 201,
    headers: { 'Content-Type': 'application/json' },
  });
};
