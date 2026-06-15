<script setup>
import { ref, onMounted } from 'vue'
import { getBookshelf, addToBookshelf, removeFromBookshelf, isInBookshelf, getBookProgress } from '../utils/storage.js'

const props = defineProps({
  bookId: Number,
  title: String,
  author: String,
  totalChapters: Number,
})

const onShelf = ref(false)
const progress = ref(null)

onMounted(() => {
  onShelf.value = isInBookshelf(props.bookId)
  progress.value = getBookProgress(props.bookId)
})

function toggleShelf() {
  if (onShelf.value) {
    removeFromBookshelf(props.bookId)
    onShelf.value = false
  } else {
    addToBookshelf({ bookId: props.bookId, title: props.title, author: props.author, total_chapters: props.totalChapters })
    onShelf.value = true
  }
}
</script>

<template>
  <button :class="['shelf-btn', 'reader-shelf-btn', { active: onShelf }]" @click="toggleShelf">
    {{ onShelf ? '★ On Shelf' : '☆ Add to Shelf' }}
  </button>
</template>
