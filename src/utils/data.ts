/**
 * Data layer — R2 binding first, HTTP fallback for dev/preview
 */

export interface Book {
  id: number;
  slug: string;
  title: string;
  author: string;
  category: string;
  intro: string;
  total_chapters: number;
  lang: string;
  tags: string[];
}

export interface ChapterMeta {
  chapter_id: number;
  title: string;
}

export interface Catalog {
  book_id: number;
  chapters: ChapterMeta[];
}

export interface ChapterData {
  book_id: number;
  chapter_id: number;
  title: string;
  content: string[];
}

const R2_PUBLIC = 'https://data.lyriq.space';

/**
 * Get R2 bucket from Astro locals, or null if unavailable (static build/dev)
 */
function getBucket(locals: any): R2Bucket | null {
  try {
    return locals?.runtime?.env?.R2_BUCKET ?? null;
  } catch {
    return null;
  }
}

/* ---------- Books list ---------- */

export async function getBooks(locals?: any): Promise<Book[]> {
  const bucket = getBucket(locals);
  if (bucket) {
    try {
      const obj = await bucket.get('books.json');
      if (obj) return await obj.json();
    } catch { /* fall through */ }
  }
  // Fallback: fetch from public R2
  const res = await fetch(`${R2_PUBLIC}/books.json`);
  if (res.ok) return res.json();
  return [];
}

export function getEnglishBooks(books: Book[]): Book[] {
  return books.filter(b => b.lang === 'english' || b.lang === 'en');
}

export function getAllTags(books: Book[]): string[] {
  const tagSet = new Set(books.flatMap(b => b.tags || []));
  return Array.from(tagSet).sort();
}

/* ---------- Single book ---------- */

export function findBook(books: Book[], id: number): Book | undefined {
  return books.find(b => b.id === id);
}

/* ---------- Catalog ---------- */

export async function getCatalog(bookId: number, locals?: any): Promise<Catalog | null> {
  const bucket = getBucket(locals);
  const key = `catalog_${bookId}.json`;
  if (bucket) {
    try {
      const obj = await bucket.get(key);
      if (obj) return await obj.json();
    } catch { /* fall through */ }
  }
  const res = await fetch(`${R2_PUBLIC}/${key}`);
  return res.ok ? res.json() : null;
}

/* ---------- Chapter content ---------- */

export async function getChapter(bookId: number, chapterId: number, locals?: any): Promise<ChapterData | null> {
  const bucket = getBucket(locals);
  const key = `${bookId}/${chapterId}.json`;
  if (bucket) {
    try {
      const obj = await bucket.get(key);
      if (obj) return await obj.json();
    } catch { /* fall through */ }
  }
  const res = await fetch(`${R2_PUBLIC}/${key}`);
  return res.ok ? res.json() : null;
}

/* ---------- Books by tag ---------- */

export function getBooksByTag(books: Book[], tag: string): Book[] {
  return books.filter(b => (b.tags || []).includes(tag));
}
