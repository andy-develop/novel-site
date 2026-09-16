/* Novel Vault Service Worker v2 — explicit offline book saves
 *
 * Caches:
 *   novel-vault-core-v2.0.0   precache (/ , /offline.html, manifest, icons) + shared hashed /_astro assets
 *   novel-vault-warm-v2.0.0   pages visited while online (automatic warm cache — browsing also enables offline)
 *   novel-vault-book-<id>     explicit per-book saves: chapter HTML + book meta
 *
 * Page ⇄ SW protocol (postMessage):
 *   page → SW: {type:'QUERY_BOOKS'}
 *              {type:'SAVE_BOOK', bookId, slug, title, chapters:[{chapter_id}], onlyMissing}
 *              {type:'DELETE_BOOK', bookId}
 *   SW → page: {type:'BOOKS', books:[{bookId, slug, title, total, saved, savedAt}]}
 *              {type:'SAVE_PROGRESS', bookId, done, total}
 *              {type:'SAVE_DONE', bookId, slug, title, total, saved}
 *              {type:'BOOK_DELETED', bookId}
 */
const VERSION = '2.0.1';
const CORE_CACHE = 'novel-vault-core-v' + VERSION;
const WARM_CACHE = 'novel-vault-warm-v' + VERSION;
const BOOK_CACHE_PREFIX = 'novel-vault-book-';
const META_KEY_PREFIX = '/__nv__/meta/';
const ASSET_RE = /\/_astro\/[A-Za-z0-9._-]+\.(?:js|css)/g;
const STATIC_PATHS = ['/_astro/', '/favicon.svg', '/manifest.json', '/icon-192.png', '/icon-512.png', '/og-default.png'];

/* ---------- lifecycle ---------- */

self.addEventListener('install', (e) => {
  e.waitUntil((async () => {
    const cache = await caches.open(CORE_CACHE);
    const origin = self.location.origin;
    // NOTE: /offline.html is served by Cloudflare Assets as a 307 → /offline (extensionless
    // pretty URL), so the canonical offline page is '/offline'.
    const pages = ['/', '/offline'];
    const statics = ['/manifest.json', '/favicon.svg', '/icon-192.png', '/icon-512.png'];
    const assetSet = new Set();
    await Promise.all([
      ...pages.map(async (u) => {
        try {
          const res = await fetch(u);
          if (!res.ok) return;
          const text = await res.text();
          for (const m of text.matchAll(ASSET_RE)) assetSet.add(m[0]);
          await cache.put(u, new Response(text, { headers: { 'Content-Type': 'text/html; charset=utf-8' } }));
        } catch { /* home page may not be reachable at install time */ }
      }),
      ...statics.map(async (u) => {
        try {
          const res = await fetch(u);
          if (res.ok) await cache.put(u, res);
        } catch { /* tolerate */ }
      }),
    ]);
    // The home page's hashed CSS/JS bundle, so even a cold offline open of / is styled.
    await Promise.all([...assetSet].map(async (u) => {
      try {
        const res = await fetch(u.startsWith('/') ? origin + u : u);
        if (res.ok) await cache.put(u.startsWith('/') ? origin + u : u, res);
      } catch { /* tolerate */ }
    }));
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', (e) => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys
      .filter(k => k.startsWith('novel-vault-')
        && k !== CORE_CACHE && k !== WARM_CACHE
        && !k.startsWith(BOOK_CACHE_PREFIX))
      .map(k => caches.delete(k)));
    await self.clients.claim();
  })());
});

/* ---------- helpers ---------- */

function sendToClients(msg) {
  self.clients.matchAll({ includeUncontrolled: true }).then(cls => {
    cls.forEach(c => c.postMessage(msg));
  }).catch(() => {});
}

async function fetchText(url) {
  const res = await fetch(url, { credentials: 'same-origin' });
  if (!res.ok) throw new Error('HTTP ' + res.status + ' ' + url);
  return res.text();
}

async function cacheHtml(cache, url, text) {
  await cache.put(url, new Response(text, { headers: { 'Content-Type': 'text/html; charset=utf-8' } }));
}

async function runPool(items, worker, concurrency = 4) {
  let i = 0;
  const results = new Array(items.length);
  async function runner() {
    while (i < items.length) {
      const idx = i++;
      try { results[idx] = await worker(items[idx]); }
      catch (err) { results[idx] = { error: err }; }
    }
  }
  await Promise.all(Array.from({ length: Math.min(concurrency, Math.max(items.length, 1)) }, runner));
  return results;
}

/* ---------- save / delete / query ---------- */

async function saveBook(msg, reply) {
  const { bookId, slug, title, chapters, onlyMissing } = msg;
  const cacheName = BOOK_CACHE_PREFIX + bookId;
  const cache = await caches.open(cacheName);
  const origin = self.location.origin;
  const metaKey = META_KEY_PREFIX + bookId;
  let meta = null;
  try {
    const hit = await cache.match(metaKey);
    if (hit) meta = await hit.json();
  } catch { /* no meta yet */ }
  meta = meta || { bookId, slug, title, total: chapters.length, saved: [], savedAt: 0 };

  const savedSet = new Set(meta.saved);
  const total = chapters.length;
  const assetUrls = new Set();
  let done = savedSet.size;

  // 1) catalog page + every chapter HTML (skip already-saved when retrying)
  const todo = [
    { url: `${origin}/novel/${slug}`, id: 'catalog' },
    ...chapters.filter(ch => !onlyMissing || !savedSet.has(String(ch.chapter_id)))
      .map(ch => ({ url: `${origin}/novel/${slug}/${ch.chapter_id}`, id: String(ch.chapter_id) })),
  ];

  await runPool(todo, async (item) => {
    const html = await fetchText(item.url);
    for (const m of html.matchAll(ASSET_RE)) assetUrls.add(m[0]);
    await cacheHtml(cache, item.url, html);
    if (item.id !== 'catalog') {
      savedSet.add(item.id);
      done = savedSet.size;
      if (done % 2 === 0 || done === total) {
        const m = { type: 'SAVE_PROGRESS', bookId, done, total };
        reply(m); sendToClients(m);
      }
    }
  }, 4);

  // 2) shared hashed assets into core (one copy serves every saved book)
  if (assetUrls.size) {
    const core = await caches.open(CORE_CACHE);
    await Promise.all([...assetUrls].map(async (u) => {
      const abs = u.startsWith('/') ? origin + u : u;
      try {
        const hit = await core.match(abs);
        if (hit) return;
        const res = await fetch(abs);
        if (res.ok) await core.put(abs, res);
      } catch { /* tolerate */ }
    }));
  }

  meta = { bookId, slug, title, total, saved: [...savedSet], savedAt: Date.now() };
  await cache.put(metaKey, new Response(JSON.stringify(meta), { headers: { 'Content-Type': 'application/json' } }));
  const doneMsg = { type: 'SAVE_DONE', bookId, slug, title, total, saved: meta.saved.length };
  reply(doneMsg); sendToClients(doneMsg);
}

async function deleteBook(bookId, reply) {
  await caches.delete(BOOK_CACHE_PREFIX + bookId);
  const m = { type: 'BOOK_DELETED', bookId };
  reply(m); sendToClients(m);
}

async function queryBooks(reply) {
  const keys = await caches.keys();
  const books = [];
  for (const k of keys.filter(k => k.startsWith(BOOK_CACHE_PREFIX))) {
    try {
      const cache = await caches.open(k);
      const hit = await cache.match(META_KEY_PREFIX + k.slice(BOOK_CACHE_PREFIX.length));
      if (hit) {
        const m = await hit.json();
        books.push({ bookId: m.bookId, slug: m.slug, title: m.title, total: m.total, saved: m.saved.length, savedAt: m.savedAt });
      }
    } catch { /* skip broken cache */ }
  }
  books.sort((a, b) => b.savedAt - a.savedAt);
  const m = { type: 'BOOKS', books };
  reply(m); sendToClients(m);
}

self.addEventListener('message', (e) => {
  const msg = e.data || {};
  const port = e.ports && e.ports[0];
  const reply = (m) => { try { if (port) port.postMessage(m); } catch { /* port closed */ } };
  if (msg.type === 'SAVE_BOOK') e.waitUntil(saveBook(msg, reply));
  else if (msg.type === 'DELETE_BOOK') e.waitUntil(deleteBook(msg.bookId, reply));
  else if (msg.type === 'QUERY_BOOKS') e.waitUntil(queryBooks(reply));
});

/* ---------- fetch strategy ---------- */

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return; // cross-origin (fonts, data CDN) untouched

  // HTML navigations: network-first (always fresh online), cache fallback offline ("秒开"),
  // successful pages are warm-cached so browsing also enables offline reading.
  if (req.mode === 'navigate') {
    e.respondWith((async () => {
      try {
        const res = await fetch(req);
        if (res && res.ok) {
          const clone = res.clone();
          caches.open(WARM_CACHE).then(c => c.put(req, clone)).catch(() => {});
        }
        return res;
      } catch (err) {
        const cached = await caches.match(req); // searches core + warm + book caches
        if (cached) return cached;
        const offline = await caches.match('/offline');
        if (offline) return offline;
        return new Response('You are offline and this page was not saved.', { status: 503 });
      }
    })());
    return;
  }

  // hashed/immutable assets: cache-first
  if (STATIC_PATHS.some(p => url.pathname.startsWith(p))) {
    e.respondWith((async () => {
      const hit = await caches.match(req);
      if (hit) return hit;
      try {
        const res = await fetch(req);
        if (res.ok) {
          const clone = res.clone();
          caches.open(CORE_CACHE).then(c => c.put(req, clone)).catch(() => {});
        }
        return res;
      } catch { throw new Error('offline'); }
    })());
    return;
  }

  // other same-origin GET (API, prefetched HTML): network-first with cache fallback + warm
  e.respondWith((async () => {
    try {
      const res = await fetch(req);
      if (res && res.ok) {
        const clone = res.clone();
        caches.open(WARM_CACHE).then(c => c.put(req, clone)).catch(() => {});
      }
      return res;
    } catch (err) {
      const cached = await caches.match(req);
      if (cached) return cached;
      throw err;
    }
  })());
});
