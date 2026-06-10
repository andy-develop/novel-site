<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import MiniSearch from 'minisearch'

const props = defineProps({
  books: { type: Array, default: () => [] },
  categories: { type: Array, default: () => ['All'] },
  r2Base: { type: String, default: '' },
})

const emit = defineEmits(['open-reader'])

const searchQuery = ref('')
const selectedCat = ref('All')
const miniSearch = ref(null)

onMounted(() => {
  if (props.books.length) initSearch()
})

watch(() => props.books, (books) => {
  if (books.length && !miniSearch.value) initSearch()
})

function initSearch() {
  const ms = new MiniSearch({
    fields: ['title', 'author', 'category'],
    storeFields: ['id', 'title', 'author', 'category', 'intro', 'total_chapters'],
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
  if (selectedCat.value !== 'All') {
    list = list.filter(b => b.category === selectedCat.value)
  }
  return list
})

function getCoverChar(title) {
  const first = title.charAt(0)
  return /[a-zA-Z]/.test(first) ? first.toUpperCase() : first
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

  <div class="categories">
    <button v-for="cat in categories" :key="cat"
      :class="['cat-btn', { active: selectedCat === cat }]"
      @click="selectedCat = cat">{{ cat }}</button>
  </div>

  <div class="grid" v-if="filteredBooks.length">
    <div v-for="(book, i) in filteredBooks" :key="book.id"
      class="novel-card" :style="{ animationDelay: i * 0.04 + 's' }"
      @click="emit('open-reader', book.id)">
      <div class="card-cover">
        <span class="cover-char">{{ getCoverChar(book.title) }}</span>
      </div>
      <div class="card-body">
        <div class="card-title">{{ book.title }}</div>
        <div class="card-author">{{ book.author || 'Unknown' }}</div>
        <div class="card-meta">
          <span>{{ book.category || 'Uncategorized' }}</span>
          <span>{{ book.total_chapters }} chapters</span>
        </div>
      </div>
    </div>
  </div>

  <div v-else class="empty-state">
    <p>No novels found</p>
  </div>
</template>