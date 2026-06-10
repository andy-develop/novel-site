<script setup>
import { ref, computed } from 'vue'
import HomePage from './components/HomePage.vue'
import ReaderPage from './components/ReaderPage.vue'

const R2_BASE = 'https://data.lyriq.space'
const route = ref('home')
const params = ref({})

const booksData = ref([])
const categories = ref([])

// 路由解析: #/reader/1/5 或 #/
function parseHash() {
  const hash = window.location.hash.slice(1) || '/'
  const parts = hash.split('/').filter(Boolean)
  if (parts[0] === 'reader' && parts.length >= 2) {
    route.value = 'reader'
    params.value = { bookId: parseInt(parts[1]), chapterId: parts[2] ? parseInt(parts[2]) : 1 }
  } else {
    route.value = 'home'
    params.value = {}
  }
}

window.addEventListener('hashchange', parseHash)
parseHash()

function navigateToReader(bookId, chapterId = 1) {
  window.location.hash = `#/reader/${bookId}/${chapterId}`
}

function navigateToHome() {
  window.location.hash = '#/'
}

const BOOKS_URL = './data/books.json'

async function loadBooks() {
  try {
    const res = await fetch(BOOKS_URL)
    const data = await res.json()
    booksData.value = data
    const cats = new Set(data.map(b => b.category).filter(Boolean))
    categories.value = ['全部', ...Array.from(cats)]
  } catch (e) {
    console.error('Failed to load books:', e)
  }
}
loadBooks()
</script>

<template>
  <HomePage
    v-if="route === 'home'"
    :books="booksData"
    :categories="categories"
    :r2Base="R2_BASE"
    @open-reader="navigateToReader"
  />
  <ReaderPage
    v-else-if="route === 'reader'"
    :bookId="params.bookId"
    :chapterId="params.chapterId"
    :books="booksData"
    :r2Base="R2_BASE"
    @navigate-home="navigateToHome"
    @navigate-chapter="(chId) => navigateToReader(params.bookId, chId)"
  />
</template>