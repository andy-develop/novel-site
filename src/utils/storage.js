/**
 * LocalStorage utility for Novel Vault (Astro edition)
 * Three storage keys: readHistory, userBookshelf, bookshelfTipIgnore
 */
const KEYS = {
  history: 'novel-vault-history',
  bookshelf: 'novel-vault-bookshelf',
  tipIgnore: 'novel-vault-bookshelf-tip-ignore',
};

function load(key) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : [];
  } catch { return []; }
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
  return true;
}

export function isTipIgnored(bookId) { return load(KEYS.tipIgnore).includes(bookId); }

export function addTipIgnore(bookId) {
  const list = load(KEYS.tipIgnore);
  if (!list.includes(bookId)) { list.push(bookId); save(KEYS.tipIgnore, list); }
}
