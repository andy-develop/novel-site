<script setup>
import { ref, onMounted, watch } from 'vue'

const props = defineProps({
  bookId: Number,
  chapterId: Number,
  bookTitle: String,
})

const fontSize = ref(18)
const darkMode = ref(false)

onMounted(() => {
  const saved = localStorage.getItem('nv-reader')
  if (saved) {
    try {
      const s = JSON.parse(saved)
      if (s.fontSize) fontSize.value = s.fontSize
      if (s.darkMode !== undefined) darkMode.value = s.darkMode
    } catch {}
  }
  applyTheme()
})

watch([fontSize, darkMode], () => {
  localStorage.setItem('nv-reader', JSON.stringify({
    fontSize: fontSize.value,
    darkMode: darkMode.value,
  }))
  applyTheme()
})

function applyTheme() {
  const el = document.querySelector('.content')
  if (el) el.style.fontSize = fontSize.value + 'px'
  document.body.classList.toggle('dark-mode', darkMode.value)
}

function larger() { if (fontSize.value < 28) fontSize.value += 2 }
function smaller() { if (fontSize.value > 12) fontSize.value -= 2 }
function toggleDark() { darkMode.value = !darkMode.value }
</script>

<template>
  <div class="reader-toolbar">
    <div class="toolbar-left">
      <button @click="smaller" :disabled="fontSize<=12" title="Smaller">A-</button>
      <span class="size-label">{{fontSize}}px</span>
      <button @click="larger" :disabled="fontSize>=28" title="Larger">A+</button>
    </div>
    <div class="toolbar-right">
      <button @click="toggleDark" :class="['mode-btn',{active:darkMode}]" title="Toggle dark mode">
        {{ darkMode ? '☀' : '☾' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.reader-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  margin-bottom: 16px;
}
.toolbar-left, .toolbar-right { display: flex; align-items: center; gap: 8px; }
.reader-toolbar button {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text);
  padding: 4px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: .85rem;
  transition: all .15s;
}
.reader-toolbar button:hover { border-color: var(--gold); color: var(--gold); }
.reader-toolbar button:disabled { opacity: .3; cursor: default; }
.size-label { font-size: .75rem; color: var(--text-dim); min-width: 36px; text-align: center; }
.mode-btn.active { background: var(--gold-dim); color: var(--gold); border-color: var(--gold); }
</style>
