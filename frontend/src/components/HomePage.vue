<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import MiniSearch from 'minisearch'

const props = defineProps({
  books: { type: Array, default: () => [] },
  categories: { type: Array, default: () => ['全部'] },
  r2Base: { type: String, default: '' },
})

const emit = defineEmits(['open-reader'])

const searchQuery = ref('')
const selectedCat = ref('全部')
const miniSearch = ref(null)

onMounted(() => {
  if (props.books.length) initSearch()
})

watch(() => props.books, (books) => {
  if (books.length && !miniSearch.value) initSearch()
})

function initSearch() {
  const ms = new MiniSearch({
    fields: ['title', 'author'],
    storeFields: ['id', 'title', 'author', 'category', 'intro', 'total_chapters', 'lang'],
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
  if (selectedCat.value !== '全部') {
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
      <div class="logo"><span>书</span>阁</div>
      <div class="search-wrap">
        <span class="icon">⌕</span>
        <input type="search" v-model="searchQuery" placeholder="搜索书名或作者..." />
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
        <span v-if="book.lang === 'english'" class="lang-badge">EN</span>
      </div>
      <div class="card-body">
        <div class="card-title">{{ book.title }}</div>
        <div class="card-author">{{ book.author || '匿名' }}</div>
        <div class="card-meta">
          <span>{{ book.category || '未分类' }}</span>
          <span>{{ book.total_chapters }} 章</span>
        </div>
      </div>
    </div>
  </div>

  <div v-else class="empty-state">
    <p>未找到匹配的小说</p>
  </div>
</template>