<script setup>
import { ref, computed } from 'vue'
import HomePage from './components/HomePage.vue'
import ReaderPage from './components/ReaderPage.vue'

const R2_BASE = 'https://data.lyriq.space'
const route = ref('home')
const params = ref({})

const allBooks = ref([])

// Parse hash routing
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

// Only show English novels
const books = computed(() =>
  allBooks.value.filter(b => b.lang === 'english' || b.lang === 'en')
)

const tags = computed(() => {
  const tagSet = new Set(books.value.flatMap(b => b.tags || []))
  return ['All', ...Array.from(tagSet).sort()]
})

async function loadBooks() {
  try {
    const res = await fetch('./data/books.json')
    allBooks.value = await res.json()
  } catch (e) {
    console.error('Failed to load books:', e)
  }
}
loadBooks()
</script>

<template>
  <HomePage
    v-if="route === 'home'"
    :books="books"
    :tags="tags"
    :r2Base="R2_BASE"
    @open-reader="navigateToReader"
  />
  <ReaderPage
    v-else-if="route === 'reader'"
    :bookId="params.bookId"
    :chapterId="params.chapterId"
    :books="books"
    :r2Base="R2_BASE"
    @navigate-home="navigateToHome"
    @navigate-chapter="(chId) => navigateToReader(params.bookId, chId)"
  />
</template>