<script setup>
import { ref, onMounted, watch } from 'vue'

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
  document.documentElement.style.setProperty('--reader-font-size', fontSize.value + 'px')
  document.body.classList.toggle('dark-mode', darkMode.value)
}

function larger() { if (fontSize.value < 28) fontSize.value += 2 }
function smaller() { if (fontSize.value > 12) fontSize.value -= 2 }
function toggleDark() { darkMode.value = !darkMode.value }
</script>

<template>
  <div class="global-controls">
    <button @click="smaller" :disabled="fontSize<=12" class="ctrl-btn font-btn" title="Smaller font">A-</button>
    <button @click="larger" :disabled="fontSize>=28" class="ctrl-btn font-btn" title="Larger font">A+</button>
    <button @click="toggleDark" :class="['ctrl-btn','mode-btn',{active:darkMode}]" :title="darkMode?'Light mode':'Dark mode'">
      {{ darkMode ? '☀' : '☾' }}
    </button>
  </div>
</template>

<style scoped>
.global-controls {
  position: fixed;
  top: 16px;
  right: 16px;
  z-index: 200;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: rgba(250, 248, 245, 0.85);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border);
  border-radius: 20px;
}
.ctrl-btn {
  background: transparent;
  border: none;
  color: var(--text-dim);
  padding: 4px 8px;
  border-radius: 12px;
  cursor: pointer;
  font-size: 0.78rem;
  transition: color var(--dur-short) var(--ease-out), background-color var(--dur-short) var(--ease-out);
  line-height: 1;
}
.ctrl-btn:hover { color: var(--gold); background: var(--gold-dim); }
.ctrl-btn:disabled { opacity: 0.3; cursor: default; }
.ctrl-btn:disabled:hover { color: var(--text-dim); background: transparent; }
.font-btn { font-weight: 600; font-family: var(--font-ui); }
.mode-btn { font-size: 0.95rem; }
.mode-btn.active { background: var(--gold-dim); color: var(--gold); }
</style>
