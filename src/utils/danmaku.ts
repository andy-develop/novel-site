/**
 * Danmaku data layer — R2 JSON storage
 * Key pattern: danmaku/{bookId}/{chapterId}.json
 */
import { env as cfEnv } from 'cloudflare:workers';

export interface DanmakuEntry {
  id: number;
  paragraph_idx: number;
  content: string;
  reaction_type: 'text' | 'emoji';
  session_hash: string;
  created_at: number;
}

export interface DanmakuFile {
  book_id: number;
  chapter_id: number;
  entries: DanmakuEntry[];
}

function getBucket(): R2Bucket | null {
  return (cfEnv as Record<string, any>).R2_BUCKET ?? null;
}

function r2Key(bookId: number, chapterId: number): string {
  return `danmaku/${bookId}/${chapterId}.json`;
}

export async function getDanmaku(bookId: number, chapterId: number): Promise<DanmakuFile> {
  const bucket = getBucket();
  const key = r2Key(bookId, chapterId);
  if (bucket) {
    try {
      const obj = await bucket.get(key);
      if (obj) return await obj.json();
    } catch { /* fall through */ }
  }
  return { book_id: bookId, chapter_id: chapterId, entries: [] };
}

export async function appendDanmaku(
  bookId: number,
  chapterId: number,
  entry: DanmakuEntry
): Promise<DanmakuFile> {
  const file = await getDanmaku(bookId, chapterId);
  entry.id = file.entries.length > 0
    ? Math.max(...file.entries.map(e => e.id)) + 1
    : 1;
  file.entries.push(entry);

  const bucket = getBucket();
  if (bucket) {
    await bucket.put(r2Key(bookId, chapterId), JSON.stringify(file));
  }
  return file;
}

/** Count entries from a specific hash in the last N seconds */
export function recentCountByHash(
  file: DanmakuFile,
  sessionHash: string,
  withinSec: number
): number {
  const cutoff = Math.floor(Date.now() / 1000) - withinSec;
  return file.entries.filter(
    e => e.session_hash === sessionHash && e.created_at >= cutoff
  ).length;
}