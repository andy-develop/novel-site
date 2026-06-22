/**
 * Data layer - R2 binding first, HTTP fallback for dev/preview
 * Astro v6: top-level import from cloudflare:workers (locals.runtime.env removed)
 */
import { env as cfEnv } from 'cloudflare:workers';

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
  highlight?: string;
}

const R2_PUBLIC = 'https://data.lyriq.space';

function getBucket(): R2Bucket | null {
  return (cfEnv as Record<string, any>).R2_BUCKET ?? null;
}

/* ---------- Books list ---------- */

export async function getBooks(): Promise<Book[]> {
  const bucket = getBucket();
  if (bucket) {
    try {
      const obj = await bucket.get('books.json');
      if (obj) return await obj.json();
    } catch { /* fall through */ }
  }
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

export async function getCatalog(bookId: number): Promise<Catalog | null> {
  const bucket = getBucket();
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

export async function getChapter(bookId: number, chapterId: number): Promise<ChapterData | null> {
  const bucket = getBucket();
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

/* ---------- Character config ---------- */

export interface EpicNode {
  title: string;
  url: string;
}

export interface CharacterDossier {
  title: string;
  dopamine_sync?: string;
  heartbreak_logs?: string;
  epic_nodes: EpicNode[];
}

export interface CharacterEntry {
  primary_name: string;
  aliases: string[];
  dossier: CharacterDossier;
}

export type CharactersFile = Record<string, CharacterEntry>;

/** Fetch per-book character configuration from R2 (characters_{bookId}.json) */
export async function getCharacters(bookId: number): Promise<CharactersFile | null> {
  const bucket = getBucket();
  const key = `characters_${bookId}.json`;
  if (bucket) {
    try {
      const obj = await bucket.get(key);
      if (obj) return await obj.json();
    } catch { /* fall through */ }
  }
  const res = await fetch(`${R2_PUBLIC}/${key}`);
  return res.ok ? res.json() : null;
}

/* ---------- Tag display names ---------- */

export const TAG_DISPLAY: Record<string, string> = {
  'Romance':        '💋 Crush',
  'Fantasy':        '🏰 Realm',
  'Sci-Fi':         '🌌 Neon',
  'Thriller':       '🔪 Shadow',
  'Dark Academia':  '🦇 Midnight',
  'Dystopia':       '🔥 Rebel',
  'Contemporary':   '🏙️ Real',
  'Female Lead':    '👑 Her',
  'Queer':          '🌈 Spectrum',
};

export function getTagDisplay(tag: string): string {
  return TAG_DISPLAY[tag] ?? tag;
}

/* ---------- Books by tag ---------- */

export function getBooksByTag(books: Book[], tag: string): Book[] {
  return books.filter(b => (b.tags || []).includes(tag));
}
