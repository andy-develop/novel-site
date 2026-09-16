<script setup>
/**
 * SaveBookIsland — offline save of a whole novel via the Service Worker.
 * Click = SW fetches the catalog page + every chapter page (+ their hashed assets)
 * into a per-book Cache Storage. Offline, the SW serves saved pages instantly.
 * Communication uses a MessageChannel port (robust on first visit, no controller race).
 */
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  bookId: { type: Number, required: true },
  slug: { type: String, required: true },
  title: { type: String, required: true },
  chapters: { type: Array, default: () => [] },
})

const supported = ref(null) // null = unknown, true/false after check
const status = ref('checking') // checking | unsaved | saving | saved | partial
const progress = ref({ done: 0, total: 0 })
const confirmRemove = ref(false)
let confirmTimer = null
let saveToken = 0

/** Post to the active SW; replies (progress + final) arrive on the MessageChannel port. */
function postToSW(msg, timeoutMs = 30000) {
  return new Promise((resolve) => {
    if (!('serviceWorker' in navigator)) return resolve(null)
    navigator.serviceWorker.ready.then((reg) => {
      const active = reg.active || navigator.serviceWorker.controller
      if (!active) return resolve(null)
      const mc = new MessageChannel()
      const timer = setTimeout(() => resolve(null), timeoutMs)
      mc.port1.onmessage = (ev) => {
        const d = ev.data || {}
        if (d.type === 'SAVE_PROGRESS') {
          progress.value = { done: d.done || 0, total: d.total || 0 }
          return // keep waiting for the final result
        }
        clearTimeout(timer)
        mc.port1.onmessage = null
        resolve(d)
      }
      try { active.postMessage(msg, [mc.port2]) } catch { resolve(null) }
    }).catch(() => resolve(null))
  })
}

async function refreshStatus() {
  const res = await postToSW({ type: 'QUERY_BOOKS' }, 8000)
  if (!res || res.type !== 'BOOKS') { status.value = 'unsaved'; return }
  const mine = res.books.find(b => b.bookId === props.bookId)
  if (mine) {
    progress.value = { done: mine.saved, total: mine.total }
    status.value = mine.saved >= mine.total ? 'saved' : 'partial'
  } else {
    status.value = 'unsaved'
  }
}

async function save(onlyMissing = false) {
  if (status.value === 'saving') return
  const token = ++saveToken
  status.value = 'saving'
  progress.value = { done: 0, total: props.chapters.length }
  const res = await postToSW({
    type: 'SAVE_BOOK',
    bookId: props.bookId,
    slug: props.slug,
    title: props.title,
    chapters: props.chapters.map(c => ({ chapter_id: c.chapter_id })),
    onlyMissing,
  }, 120000)
  if (token !== saveToken) return
  if (!res) { status.value = 'unsaved'; return }
  progress.value = { done: res.saved || 0, total: res.total || 0 }
  status.value = res.saved >= res.total ? 'saved' : 'partial'
}

async function remove() {
  const token = ++saveToken
  await postToSW({ type: 'DELETE_BOOK', bookId: props.bookId }, 10000)
  if (token !== saveToken) return
  status.value = 'unsaved'
}

function toggle() {
  if (status.value === 'saving' || status.value === 'checking') return
  if (status.value === 'saved') {
    if (!confirmRemove.value) {
      confirmRemove.value = true
      confirmTimer = setTimeout(() => { confirmRemove.value = false }, 3000)
      return
    }
    clearTimeout(confirmTimer)
    confirmRemove.value = false
    remove()
  } else if (status.value === 'partial') {
    save(true) // retry only the missing chapters
  } else {
    save()
  }
}

const icon = computed(() => {
  if (status.value === 'saved') return confirmRemove.value ? '?' : '✓'
  if (status.value === 'partial') return '↻'
  return '⬇'
})

const label = computed(() => {
  switch (status.value) {
    case 'checking': return '…'
    case 'saving': return `Saving ${progress.value.done}/${progress.value.total}`
    case 'saved': return confirmRemove.value ? 'Remove?' : 'Saved'
    case 'partial': return 'Retry'
    default: return 'Save'
  }
})

const tooltip = computed(() => {
  if (status.value === 'saved') return 'Offline copy saved — click to remove'
  if (status.value === 'saving') return 'Downloading chapters…'
  if (status.value === 'partial') return 'Some chapters failed — click to retry'
  return `Download ${props.title} (${props.chapters.length} chapters) for offline reading`
})

const btnTitle = computed(() =>
  supported.value === false ? 'Offline saving needs a modern browser' : tooltip.value
)

onMounted(async () => {
  if (!('serviceWorker' in navigator)) { supported.value = false; return }
  supported.value = true
  try {
    await navigator.serviceWorker.register('/sw.js')
    await navigator.serviceWorker.ready
    refreshStatus()
  } catch {
    supported.value = false
  }
})

onBeforeUnmount(() => {
  clearTimeout(confirmTimer)
  saveToken += 1
})
</script>

<template>
  <button
    v-if="supported !== false"
    :class="['save-book-btn', status, { confirm: confirmRemove }]"
    :disabled="status === 'saving' || status === 'checking'"
    :title="btnTitle"
    aria-label="Save book for offline reading"
    @click="toggle"
  >
    <span class="sb-icon" :class="{ spin: status === 'saving' }">{{ icon }}</span>
    <span class="sb-label">{{ label }}</span>
  </button>
</template>

<style scoped>
.save-book-btn {
  position: fixed;
  top: 16px;
  right: 168px;
  z-index: 190;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  background: rgba(250, 248, 245, 0.85);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border, rgba(43, 36, 24, 0.12));
  border-radius: 20px;
  font-family: var(--font-ui, inherit);
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-dim, #6f6452);
  cursor: pointer;
  line-height: 1;
  box-shadow: 0 2px 10px rgba(43, 36, 24, 0.06);
  transition: color 0.15s ease, background-color 0.15s ease, border-color 0.15s ease;
}
.save-book-btn:hover {
  color: var(--gold, #8a6d2f);
  background: var(--gold-dim, rgba(138, 109, 47, 0.12));
  border-color: var(--gold, #8a6d2f);
}
.save-book-btn:disabled {
  opacity: 0.6;
  cursor: default;
}
.save-book-btn:disabled:hover {
  color: var(--text-dim, #6f6452);
  background: rgba(250, 248, 245, 0.85);
  border-color: var(--border, rgba(43, 36, 24, 0.12));
}
.save-book-btn.saved {
  color: #2e7d32;
  border-color: rgba(46, 125, 50, 0.45);
  background: rgba(46, 125, 50, 0.08);
}
.save-book-btn.saved:hover {
  background: rgba(46, 125, 50, 0.16);
}
.save-book-btn.partial {
  color: #b26a00;
  border-color: rgba(178, 106, 0, 0.45);
}
.save-book-btn.confirm {
  color: #c62828;
  border-color: rgba(198, 40, 40, 0.5);
  background: rgba(198, 40, 40, 0.08);
}
.sb-icon {
  display: inline-block;
  font-size: 0.9rem;
}
.sb-icon.spin {
  width: 11px;
  height: 11px;
  border: 2px solid var(--text-dim, #6f6452);
  border-top-color: transparent;
  border-radius: 50%;
  font-size: 0;
  animation: sb-rotate 0.8s linear infinite;
}
@keyframes sb-rotate {
  to { transform: rotate(360deg); }
}

@media (max-width: 640px) {
  .save-book-btn {
    top: 10px;
    right: 148px;
    padding: 6px 10px;
  }
  .sb-label {
    max-width: 74px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}
</style>
