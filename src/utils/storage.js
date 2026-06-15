/**
 * LocalStorage utility for Novel Vault (Astro edition)
 * Storage keys: readHistory, userBookshelf, bookshelfTipIgnore, readingProgress
 */
const KEYS = {
  history: 'novel-vault-history',
  bookshelf: 'novel-vault-bookshelf',
  tipIgnore: 'novel-vault-bookshelf-tip-ignore',
  progress: 'novel-vault-progress',
};

function load(key) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : [];
  } catch { return []; }
}

function loadObj(key) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : {};
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
