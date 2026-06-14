<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import MiniSearch from 'minisearch'

const props = defineProps({
  books: { type: Array, default: () => [] },
  tags: { type: Array, default: () => ['All'] },
  r2Base: { type: String, default: '' },
})

const emit = defineEmits(['open-reader'])

const searchQuery = ref('')
const selectedTag = ref('All')
const miniSearch = ref(null)
const readingHistory = ref([])
const expandedId = ref(null)

onMounted(() => {
  if (props.books.length) initSearch()
  loadHistory()
})

function loadHistory() {
  try {
    const saved = localStorage.getItem('novel-vault-history')
    readingHistory.value = saved ? JSON.parse(saved) : []
  } catch { readingHistory.value = [] }
}

watch(() => props.books, (books) => {
  if (books.length && !miniSearch.value) initSearch()
})

function initSearch() {
  const ms = new MiniSearch({
    fields: ['title', 'author', 'tags'],
    storeFields: ['id', 'title', 'author', 'tags', 'intro', 'total_chapters'],
    searchOptions: { boost: { title: 2 }, prefix: true, fuzzy: 0.2 }
  })
  ms.addAll(props.books)
  miniSearch.value = ms
}

const filteredBooks = computed(() => {
  let list = props.books
  if (searchQuery.value.trim()) {
    const results = miniSearch.value?.search(searchQuery.value.trim()) || []
    list = results.map(r => r)
  }
  if (selectedTag.value !== 'All') {
    list = list.filter(b => (b.tags || []).includes(selectedTag.value))
  }
  return list
})

function getCoverChar(title) {
  const first = title.charAt(0)
  return /[a-zA-Z]/.test(first) ? first.toUpperCase() : first
}

function formatTime(ts) {
  const d = new Date(ts)
  const now = new Date()
  const diffMs = now - d
  const diffMin = Math.floor(diffMs / 60000)
  if (diffMin < 1) return 'Just now'
  if (diffMin < 60) return `${diffMin}m ago`
  const diffHr = Math.floor(diffMin / 60)
  if (diffHr < 24) return `${diffHr}h ago`
  const diffDay = Math.floor(diffHr / 24)
  if (diffDay < 7) return `${diffDay}d ago`
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

function openHistory(entry) {
  emit('open-reader', entry.bookId, entry.chapterId)
}

function toggleExpand(bookId) {
  expandedId.value = expandedId.value === bookId ? null : bookId
}

function startReading(bookId) {
  emit('open-reader', bookId)
}
</script>

<template>
  <header>
    <div class="header-inner">
      <div class="logo"><span>N</span>OVEL VAULT</div>
      <div class="search-wrap">
        <span class="icon">⌕</span>
        <input type="search" v-model="searchQuery" placeholder="Search by title or author..." />
      </div>
    </div>
  </header>

  <div v-if="readingHistory.length" class="history-bar">
    <div class="history-title">📖 Continue Reading</div>
    <div class="history-items">
      <div v-for="h in readingHistory.slice(0, 3)" :key="h.bookId" class="history-item" @click="openHistory(h)">
        <span class="history-book">{{ h.bookTitle }}</span>
        <span class="history-chapter">— {{ h.chapterTitle }}</span>
        <span class="history-time">{{ formatTime(h.timestamp) }}</span>
      </div>
    </div>
  </div>

  <div class="categories">
    <button v-for="tag in tags" :key="tag"
      :class="['cat-btn', { active: selectedTag === tag }]"
      @click="selectedTag = tag">{{ tag }}</button>
  </div>

  <div class="grid" v-if="filteredBooks.length">
    <div v-for="(book, i) in filteredBooks" :key="book.id"
      :class="['novel-card', { expanded: expandedId === book.id }]"
      :style="{ animationDelay: i * 0.04 + 's' }">
      <div class="card-main" @click="toggleExpand(book.id)">
        <div class="card-cover">
          <span class="cover-char">{{ getCoverChar(book.title) }}</span>
        </div>
        <div class="card-body">
          <div class="card-title">{{ book.title }}</div>
          <div class="card-author">{{ book.author || 'Unknown' }}</div>
          <div class="card-meta">
            <span v-for="t in (book.tags || []).slice(0, 3)" :key="t" class="tag-pill">{{ t }}</span>
            <span>{{ book.total_chapters }} chapters</span>
          </div>
        </div>
        <span class="expand-icon">{{ expandedId === book.id ? '▾' : '▸' }}</span>
      </div>
      <transition name="slide">
        <div v-if="expandedId === book.id" class="card-intro">
          <p v-if="book.intro" class="intro-text">{{ book.intro }}</p>
          <p v-else class="intro-text intro-placeholder">No synopsis available.</p>
          <button class="start-btn" @click.stop="startReading(book.id)">Start Reading →</button>
        </div>
      </transition>
    </div>
  </div>

  <div v-else class="empty-state">
    <p>No novels found</p>
  </div>
</template>