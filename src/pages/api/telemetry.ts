import type { APIRoute } from 'astro';
import { env as cfEnv } from 'cloudflare:workers';

function getBucket(): R2Bucket | null {
  return (cfEnv as Record<string, any>).R2_BUCKET ?? null;
}

const R2_PUBLIC = 'https://data.lyriq.space';

interface DanmakuEntry {
  id: number;
  paragraph_idx: number;
  content: string;
  reaction_type: string;
  session_hash: string;
  created_at: number;
}

interface DanmakuFile {
  book_id: number;
  chapter_id: number;
  entries: DanmakuEntry[];
}

async function getDanmakuFile(bookId: number, chapterId: number): Promise<DanmakuFile | null> {
  const bucket = getBucket();
  const key = `danmaku/${bookId}/${chapterId}.json`;
  if (bucket) {
    try {
      const obj = await bucket.get(key);
      if (obj) return await obj.json();
    } catch { /* fall through */ }
  }
  const res = await fetch(`${R2_PUBLIC}/${key}`);
  return res.ok ? res.json() : null;
}

export const GET: APIRoute = async ({ url }) => {
  const limit = Math.min(parseInt(url.searchParams.get('limit') || '30'), 50);
  
  // Get books list
  let books: any[] = [];
  const bucket = getBucket();
  try {
    if (bucket) {
      const obj = await bucket.get('books.json');
      if (obj) books = await obj.json();
    }
    if (!books.length) {
      const r = await fetch(`${R2_PUBLIC}/books.json`);
      if (r.ok) books = await r.json();
    }
  } catch { /* empty */ }
  
  const enBooks = books.filter(b => b.lang === 'english' || b.lang === 'en');
  
  // Sample: pick up to 8 books, first chapter each
  const allEntries: (DanmakuEntry & { book_id: number; chapter_id: number })[] = [];
  const booksToScan = enBooks.slice(0, 8);
  
  await Promise.all(booksToScan.map(async (book) => {
    const file = await getDanmakuFile(book.id, 1);
    if (file?.entries?.length) {
      file.entries.forEach(e => allEntries.push({ ...e, book_id: book.id, chapter_id: file.chapter_id }));
    }
  }));
  
  // Sort by created_at desc, take latest
  allEntries.sort((a, b) => b.created_at - a.created_at);
  const recent = allEntries.slice(0, limit);
  
  // Split into track_1 (alerts from emoji) and track_2 (text comments)
  const track1 = recent
    .filter(e => e.reaction_type === 'emoji')
    .slice(0, 15)
    .map((e, i) => ({
      id: i + 1,
      type: 'DOPAMINE_SPIKE',
      text: e.content,
      book_id: e.book_id,
      chapter_id: e.chapter_id,
    }));
  
  const track2 = recent
    .filter(e => e.reaction_type === 'text')
    .slice(0, 15)
    .map((e, i) => ({
      id: i + 1,
      content: e.content,
      book_id: e.book_id,
      chapter_id: e.chapter_id,
    }));
  
  // Enrich with book/chapter titles
  const bookMap = new Map(enBooks.map(b => [b.id, b]));
  const track1Final = track1.map(t => ({
    ...t,
    book: bookMap.get(t.book_id)?.title || `Book ${t.book_id}`,
  }));
  const track2Final = track2.map(t => ({
    ...t,
    book: bookMap.get(t.book_id)?.title || `Book ${t.book_id}`,
  }));
  
  return new Response(JSON.stringify({ track_1_alerts: track1Final, track_2_danmakus: track2Final }), {
    headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' },
  });
};