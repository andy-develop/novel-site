/**
 * Data layer - R2 binding first, HTTP fallback for dev/preview
 * Astro v6: top-level import from cloudflare:workers (locals.runtime.env removed)
 */

import { execFile } from 'node:child_process';
import { promisify } from 'node:util';

const execFileAsync = promisify(execFile);

let cfEnv: Record<string, any> = {};
try {
  // @ts-ignore — Cloudflare Workers runtime module, not available in Node dev.
  const mod = await import('cloudflare:workers');
  cfEnv = mod.env ?? {};
} catch {
  // Not running in Cloudflare Workers environment; fall back to HTTP.
}

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
const BROWSER_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36';

function getBucket(): R2Bucket | null {
  return (cfEnv as Record<string, any>).R2_BUCKET ?? null;
}

async function httpGetJson(url: string): Promise<any> {
  const res = await fetch(url, {
    headers: { 'User-Agent': BROWSER_UA, 'Accept': '*/*' },
  });
  if (res.ok) return res.json();
  // Some environments (Node dev behind Cloudflare) block undici fetch but allow curl.
  try {
    const { stdout } = await execFileAsync('curl', ['-sL', '-A', BROWSER_UA, url], { maxBuffer: 20 * 1024 * 1024 });
    return JSON.parse(stdout);
  } catch {
    return null;
  }
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
  return (await httpGetJson(`${R2_PUBLIC}/books.json`)) ?? [];
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
  return await httpGetJson(`${R2_PUBLIC}/${key}`);
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
  return await httpGetJson(`${R2_PUBLIC}/${key}`);
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
  return await httpGetJson(`${R2_PUBLIC}/${key}`);
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
