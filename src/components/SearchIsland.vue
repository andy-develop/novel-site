<script setup>
import { ref, computed, onMounted } from 'vue'
import MiniSearch from 'minisearch'
import { getBookshelf, addToBookshelf, removeFromBookshelf, getReadingProgress } from '../utils/storage.js'

const props = defineProps({
  books: Array,
})

const query = ref('')
const ms = ref(null)
const shelf = ref([])
const progress = ref({})

onMounted(() => {
  const idx = new MiniSearch({
    fields: ['title', 'author', 'tags', 'intro'],
    storeFields: ['id', 'title', 'author', 'tags', 'intro', 'total_chapters', 'slug'],
    searchOptions: { boost: { title: 3, author: 2 }, prefix: true, fuzzy: 0.2 }
  })
  idx.addAll(props.books)
  ms.value = idx
  shelf.value = getBookshelf()
  progress.value = getReadingProgress()
})

const hasSearch = computed(() => query.value.trim().length > 0)

const results = computed(() => {
  if (!hasSearch.value || !ms.value) return []
  const res = ms.value.search(query.value.trim())
  const ids = new Set(res.map(r => r.id))
  return props.books
    .filter(b => ids.has(b.id))
    .sort((a, b) => res.findIndex(r => r.id === a.id) - res.findIndex(r => r.id === b.id))
})

function cover(title) {
  const c = title.charAt(0)
  return /[a-zA-Z]/.test(c) ? c.toUpperCase() : c
}

function esc(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') }
function hl(text, q) {
  if (!q || !text) return text || ''
  const terms = q.trim().split(/\s+/).filter(Boolean)
  if (!terms.length) return text
  return text.replace(new RegExp(`(${terms.map(esc).join('|')})`, 'gi'), '<mark class="hl">$1</mark>')
}

function onShelf(bookId) { return shelf.value.some(b => b.bookId === bookId) }

function toggleShelf(book, e) {
  e.stopPropagation()
  if (onShelf(book.id)) {
    removeFromBookshelf(book.id)
  } else {
    addToBookshelf({ bookId: book.id, title: book.title, author: book.author, total_chapters: book.total_chapters })
  }
  shelf.value = getBookshelf()
}

function getProgressChapter(bookId) {
  const p = progress.value[bookId]
  return p ? p.chapterTitle : null
}

function getProgressHref(book) {
  const p = progress.value[book.id]
  return p ? `/novel/${book.slug || book.id}/${p.chapterId}` : `/novel/${book.slug || book.id}`
}

function bookUrl(book) {
  return `/novel/${book.slug || book.id}`
}

function shelfUrl(bookId) {
  const b = props.books.find(book => book.id === bookId)
  return b ? bookUrl(b) : `/novel/${bookId}`
}
</script>

<template>
  <header>
    <div class="header-inner">
      <a href="/" class="logo"><span>N</span>OVEL VAULT</a>
      <div class="search-wrap">
        <span class="icon">⌕</span>
        <input type="search" v-model="query" placeholder="Search by title, author, or synopsis..." />
        <button v-if="hasSearch" class="search-clear" @click="query = ''" aria-label="Clear search">×</button>
      </div>
    </div>
  </header>

  <div class="shelf-section" v-if="shelf.length && !hasSearch">
    <div class="shelf-title">My Shelf</div>
    <div class="shelf-scroll">
      <a v-for="item in shelf" :key="item.bookId" :href="shelfUrl(item.bookId)" class="shelf-item">
        <span class="shelf-book-title">{{ item.title }}</span>
        <span class="shelf-progress" v-if="getProgressChapter(item.bookId)">{{ getProgressChapter(item.bookId) }}</span>
        <span class="shelf-progress" v-else>Ch. 1</span>
      </a>
    </div>
  </div>

  <!-- Instant search results overlay replaces the SSR grid when searching -->
  <div v-if="hasSearch" class="search-results" aria-live="polite">
    <div class="search-results-header">
      <h2>Search results for "{{ query.trim() }}"</h2>
      <span class="result-count">{{ results.length }} found</span>
    </div>
    <div v-if="results.length" class="grid">
      <div v-for="book in results" :key="book.id" class="novel-card">
        <a :href="bookUrl(book)" class="card-main">
          <div class="card-cover"><span class="cover-char">{{ cover(book.title) }}</span></div>
          <div class="card-body">
            <div class="title-row">
              <div class="card-title" v-html="hl(book.title, query)"></div>
              <button :class="['shelf-btn', 'card-shelf-btn', { active: onShelf(book.id) }]" @click.prevent="toggleShelf(book, $event)" :title="onShelf(book.id) ? 'Remove from shelf' : 'Add to shelf'">{{ onShelf(book.id) ? '★ On Shelf' : '☆ Add to Shelf' }}</button>
            </div>
            <div class="card-author" v-html="hl(book.author || 'Unknown', query)"></div>
            <div class="card-meta">
              <span v-for="t in (book.tags || []).slice(0, 3)" :key="t" class="tag-pill">{{ t }}</span>
              <span>{{ book.total_chapters }} ch.</span>
            </div>
            <div class="card-continue" v-if="getProgressChapter(book.id)">Continue: {{ getProgressChapter(book.id) }}</div>
          </div>
        </a>
      </div>
    </div>
    <div v-else class="empty-state">
      <p>No novels found for "{{ query.trim }}"</p>
    </div>
  </div>
</template>

<style scoped>
.search-clear {
  background: none;
  border: none;
  color: var(--text-dim);
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0 8px;
  line-height: 1;
}
.search-clear:hover { color: var(--text); }
.search-results { padding: 0 20px 40px; max-width: 900px; margin: 0 auto; }
.search-results-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}
.search-results-header h2 {
  font-family: var(--font-display);
  font-size: 1.4rem;
  color: var(--gold);
  font-weight: 400;
}
.result-count {
  font-family: var(--font-ui);
  font-size: 0.85rem;
  color: var(--text-dim);
}
</style>
