import type { Book } from './data';

export const DEFAULT_OG_IMAGE = 'https://lyriq.space/og-default.png';

export function getBookLang(book: Book): string {
  const lang = (book.lang || 'en').toLowerCase();
  if (lang === 'chinese' || lang === 'zh' || lang === 'zh-cn' || lang === 'zh-hans') return 'zh-CN';
  if (lang === 'english' || lang === 'en') return 'en';
  return lang || 'en';
}

export function slugify(text: string): string {
  const trimmed = text.toString().trim();
  // If already clean kebab-case, preserve it (e.g. "the-architecture-of-forgetting")
  if (/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(trimmed)) {
    return trimmed;
  }
  // Otherwise normalize CamelCase / spaces / punctuation into kebab-case
  return trimmed
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    // Insert hyphen between lowercase/digit and uppercase: GoodForUs -> good-for-us
    .replace(/([a-z0-9])([A-Z])/g, '$1-$2')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .replace(/-+/g, '-')
    || 'untitled';
}

export function getBookSlug(book: Book): string {
  return slugify(book.slug || book.title);
}

export function getBookUrl(book: Book): string {
  return `/novel/${getBookSlug(book)}`;
}

export function getChapterUrl(book: Book, chapterId: number | string): string {
  return `/novel/${getBookSlug(book)}/${chapterId}`;
}

export function getCanonicalBookUrl(book: Book): string {
  return `https://lyriq.space${getBookUrl(book)}`;
}

export function getCanonicalChapterUrl(book: Book, chapterId: number | string): string {
  return `https://lyriq.space${getChapterUrl(book, chapterId)}`;
}

export function findBookBySlug(books: Book[], slug: string): Book | undefined {
  return books.find(b => getBookSlug(b) === slug);
}

export function findBookByIdOrSlug(books: Book[], idOrSlug: string): Book | undefined {
  const numericId = parseInt(idOrSlug, 10);
  if (!isNaN(numericId) && String(numericId) === idOrSlug) {
    return books.find(b => b.id === numericId);
  }
  return findBookBySlug(books, idOrSlug);
}

export function truncateDescription(text: string, maxLength = 160): string {
  if (!text) return '';
  if (text.length <= maxLength) return text.trim();

  // Try to end at a sentence boundary
  const truncated = text.slice(0, maxLength);
  const lastSentenceEnd = Math.max(
    truncated.lastIndexOf('.'),
    truncated.lastIndexOf('!'),
    truncated.lastIndexOf('?')
  );
  if (lastSentenceEnd > maxLength * 0.6) {
    return truncated.slice(0, lastSentenceEnd + 1).trim();
  }
  // Fallback to word boundary
  const lastSpace = truncated.lastIndexOf(' ');
  if (lastSpace > 0) {
    return truncated.slice(0, lastSpace).trim() + '…';
  }
  return truncated.trim() + '…';
}

export function getCoverImageUrl(book: Book): string {
  const slug = getBookSlug(book);
  return `https://data.lyriq.space/covers/${slug}.jpg`;
}

export function getAllTags(books: Book[]): string[] {
  const tagSet = new Set(books.flatMap(b => b.tags || []));
  return Array.from(tagSet).sort();
}

export interface BreadcrumbItem {
  name: string;
  item?: string;
}

export function buildBreadcrumbList(items: BreadcrumbItem[]) {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items.map((item, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: item.name,
      ...(item.item ? { item: item.item } : {}),
    })),
  };
}
