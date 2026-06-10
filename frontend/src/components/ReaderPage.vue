<script setup>
import { ref, watch, onMounted, computed } from 'vue'

const props = defineProps({
  bookId: { type: Number, required: true },
  chapterId: { type: Number, required: true },
  books: { type: Array, default: () => [] },
  r2Base: { type: String, default: '' },
})

const emit = defineEmits(['navigate-home', 'navigate-chapter'])

const book = ref(null)
const chapters = ref([])
const chapterContent = ref('')
const chapterTitle = ref('')
const loading = ref(true)
const error = ref('')
const currentCh = ref(props.chapterId)

onMounted(() => loadBook())
watch(() => [props.bookId, props.chapterId], loadBook)

function findBook() {
  book.value = props.books.find(b => b.id === props.bookId) || null
}

function saveHistory() {
  if (!book.value) return
  const history = JSON.parse(localStorage.getItem('novel-vault-history') || '[]')
  const idx = history.findIndex(h => h.bookId === props.bookId)
  const entry = {
    bookId: props.bookId,
    bookTitle: book.value.title,
    chapterId: props.chapterId,
    chapterTitle: chapterTitle.value,
    timestamp: Date.now()
  }
  if (idx !== -1) {
    history.splice(idx, 1)
  }
  history.unshift(entry)
  // Keep max 30 entries
  localStorage.setItem('novel-vault-history', JSON.stringify(history.slice(0, 30)))
}

async function loadBook() {
  loading.value = true
  error.value = ''
  findBook()
  if (!book.value) {
    error.value = 'Novel not found'
    loading.value = false
    return
  }
  try {
    // 加载目录
    const catRes = await fetch(`${props.r2Base}/catalog_${props.bookId}.json`)
    if (!catRes.ok) throw new Error('目录加载失败')
    const catData = await catRes.json()
    chapters.value = catData.chapters || []

    // 加载章节
    const chRes = await fetch(`${props.r2Base}/${props.bookId}/${props.chapterId}.json`)
    if (!chRes.ok) throw new Error('章节加载失败')
    const chData = await chRes.json()
    chapterTitle.value = chData.title || ''
    chapterContent.value = (chData.content || []).join('\n\n')
    saveHistory()
  } catch (e) {
    error.value = e.message
    // fallback: 从本地 data 加载
    try {
      const fallback = await import(`../../data/${props.bookId}/${props.chapterId}.json`)
      const d = fallback.default || fallback
      chapterTitle.value = d.title || ''
      chapterContent.value = (d.content || []).join('\n\n')
      error.value = ''
      // 尝试加载本地目录
      const catFallback = await import(`../../data/catalog_${props.bookId}.json`)
      const cd = catFallback.default || catFallback
      chapters.value = cd.chapters || []
      saveHistory()
    } catch (f) {
      // keep original error
    }
  } finally {
    loading.value = false
  }
}

function renderMd(text) {
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>')
}

const paragraphs = computed(() => {
  return chapterContent.value.split('\n\n').filter(Boolean)
})

const renderedParagraphs = computed(() => {
  return paragraphs.value.map(p => renderMd(p))
})

const currentIndex = computed(() => {
  return chapters.value.findIndex(c => c.chapter_id === props.chapterId)
})

const isFirst = computed(() => currentIndex.value <= 0)
const isLast = computed(() => currentIndex.value >= chapters.value.length - 1)

function goChapter() {
  if (currentCh.value && currentCh.value !== props.chapterId) {
    emit('navigate-chapter', Number(currentCh.value))
  }
}

function prevChapter() {
  if (!isFirst.value) {
    const prev = chapters.value[currentIndex.value - 1]
    emit('navigate-chapter', prev.chapter_id)
  }
}

function nextChapter() {
  if (!isLast.value) {
    const next = chapters.value[currentIndex.value + 1]
    emit('navigate-chapter', next.chapter_id)
  }
}
</script>

<template>
  <header>
    <div class="header-inner">
      <div class="logo" @click="emit('navigate-home')" style="cursor:pointer">
        <span>N</span>OVEL VAULT
      </div>
      <span class="header-book-title" v-if="book">{{ book.title }}</span>
    </div>
  </header>

  <div v-if="loading" class="loading">Loading...</div>

  <div v-else-if="error" class="reader">
    <button class="back-btn" @click="emit('navigate-home')">← Back to Library</button>
    <p style="color:var(--text-dim);margin-top:40px">{{ error }}</p>
  </div>

  <div v-else class="reader">
    <button class="back-btn" @click="emit('navigate-home')">← Back to Library</button>

    <div class="chapter-nav">
      <select v-model="currentCh" @change="goChapter" v-if="chapters.length">
        <option v-for="ch in chapters" :key="ch.chapter_id" :value="ch.chapter_id">
          {{ ch.title }}
        </option>
      </select>
      <button @click="prevChapter" :disabled="isFirst">← Previous</button>
      <button @click="nextChapter" :disabled="isLast">Next →</button>
    </div>

    <h1>{{ chapterTitle }}</h1>

    <div class="content">
      <p v-for="(p, i) in renderedParagraphs" :key="i" v-html="p"></p>
    </div>

    <div class="chapter-nav bottom-nav">
      <button @click="prevChapter" :disabled="isFirst">← Previous</button>
      <button @click="nextChapter" :disabled="isLast">Next →</button>
    </div>
  </div>
</template>