/**
 * LocalStorage utility for Lyriq (Astro edition)
 * Storage keys: readHistory, userBookshelf, bookshelfTipIgnore, readingProgress
 *
 * The site was called "Novel Vault" before the rename; keys written by that build
 * (LEGACY) are read once and copied forward to the `lyriq-*` names so existing
 * shelves / reading progress survive the rebrand.
 */
const KEYS = {
  history: 'lyriq-history',
  bookshelf: 'lyriq-bookshelf',
  tipIgnore: 'lyriq-bookshelf-tip-ignore',
  progress: 'lyriq-progress',
};

const LEGACY = {
  'lyriq-history': 'novel-vault-history',
  'lyriq-bookshelf': 'novel-vault-bookshelf',
  'lyriq-bookshelf-tip-ignore': 'novel-vault-bookshelf-tip-ignore',
  'lyriq-progress': 'novel-vault-progress',
};

function raw(key) {
  try {
    const cur = localStorage.getItem(key);
    if (cur !== null) return cur;
    const legacy = LEGACY[key];
    if (!legacy) return null;
    const old = localStorage.getItem(legacy);
    if (old === null) return null;
    try { localStorage.setItem(key, old); } catch { /* quota / private mode */ }
    return old;
  } catch { return null; }
}

function load(key) {
  try {
    const value = raw(key);
    return value ? JSON.parse(value) : [];
  } catch { return []; }
}

function loadObj(key) {
  try {
    const value = raw(key);
    return value ? JSON.parse(value) : {};
  } catch { return {}; }
}

function save(key, data) {
  localStorage.setItem(key, JSON.stringify(data));
}

export function getReadHistory() { return load(KEYS.history); }

export function saveReadHistory(entry) {
  const history = load(KEYS.history);
  const idx = history.findIndex(h => h.bookId === entry.bookId);
  if (idx !== -1) history.splice(idx, 1);
  history.unshift(entry);
  save(KEYS.history, history.slice(0, 30));
}

/* ---------- Bookshelf ---------- */

export function getBookshelf() { return load(KEYS.bookshelf); }

export function isInBookshelf(bookId) {
  return load(KEYS.bookshelf).some(b => b.bookId === bookId);
}

export function addToBookshelf(book) {
  const shelf = load(KEYS.bookshelf);
  if (shelf.some(b => b.bookId === book.bookId)) return false;
  shelf.unshift(book);
  save(KEYS.bookshelf, shelf);
  return true;
}

export function removeFromBookshelf(bookId) {
  const shelf = load(KEYS.bookshelf);
  const idx = shelf.findIndex(b => b.bookId === bookId);
  if (idx === -1) return false;
  shelf.splice(idx, 1);
  save(KEYS.bookshelf, shelf);
  // Also remove reading progress
  const progress = loadObj(KEYS.progress);
  delete progress[bookId];
  save(KEYS.progress, progress);
  return true;
}

export function isTipIgnored(bookId) { return load(KEYS.tipIgnore).includes(bookId); }

export function addTipIgnore(bookId) {
  const list = load(KEYS.tipIgnore);
  if (!list.includes(bookId)) { list.push(bookId); save(KEYS.tipIgnore, list); }
}

/* ---------- Reading Progress ---------- */

export function getReadingProgress() { return loadObj(KEYS.progress); }

export function getBookProgress(bookId) {
  const progress = loadObj(KEYS.progress);
  return progress[bookId] || null;
}

export function saveBookProgress(bookId, chapterId, chapterTitle) {
  const progress = loadObj(KEYS.progress);
  progress[bookId] = { chapterId, chapterTitle, updatedAt: Date.now() };
  save(KEYS.progress, progress);
}
