<script setup>
import { ref, computed, onMounted } from 'vue'
import MiniSearch from 'minisearch'
import { getBookshelf, isInBookshelf, addToBookshelf, removeFromBookshelf, getBookProgress, getReadingProgress } from '../utils/storage.js'

const props = defineProps({
  books: Array,
  tags: Array,
  tagCounts: Object,
})

const query = ref('')
const activeTag = ref('All')
const ms = ref(null)
const shelf = ref([])
const progress = ref({})

onMounted(() => {
  const idx = new MiniSearch({
    fields: ['title','author','tags','intro'],
    storeFields: ['id','title','author','tags','intro','total_chapters'],
    searchOptions: { boost: { title:3, author:2 }, prefix:true, fuzzy:0.2 }
  })
  idx.addAll(props.books)
  ms.value = idx
  shelf.value = getBookshelf()
  progress.value = getReadingProgress()
})

const filtered = computed(() => {
  let list = props.books
  if (query.value.trim() && ms.value) {
    const res = ms.value.search(query.value.trim())
    const ids = new Set(res.map(r=>r.id))
    list = list.filter(b=>ids.has(b.id))
    list.sort((a,b)=> res.findIndex(r=>r.id===a.id) - res.findIndex(r=>r.id===b.id))
  }
  if (activeTag.value !== 'All') list = list.filter(b=>(b.tags||[]).includes(activeTag.value))
  return list
})

function cover(title) { const c=title.charAt(0); return /[a-zA-Z]/.test(c)?c.toUpperCase():c }
function esc(s) { return s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&') }
function hl(text,q) {
  if(!q||!text) return text||''
  const terms=q.trim().split(/\s+/).filter(Boolean)
  if(!terms.length) return text
  return text.replace(new RegExp(`(${terms.map(esc).join('|')})`,'gi'),'<mark class="hl">$1</mark>')
}

function onShelf(bookId) { return shelf.value.some(b => b.bookId === bookId) }

function toggleShelf(book, e) {
  e.stopPropagation()
  if (onShelf(book.id)) {
    removeFromBookshelf(book.id)
  } else {
    addToBookshelf({ bookId: book.id, title: book.title, author: book.author, total_chapters: book.total_chapters })
  }
  shelf.value = getBookshelf()
}

function getProgressChapter(bookId) {
  const p = progress.value[bookId]
  return p ? p.chapterTitle : null
}

function getProgressHref(bookId) {
  const p = progress.value[bookId]
  return p ? `/novel/${bookId}/${p.chapterId}` : `/novel/${bookId}`
}
</script>

<template>
  <header>
    <div class="header-inner">
      <a href="/" class="logo"><span>N</span>OVEL VAULT</a>
      <div class="search-wrap">
        <span class="icon">⌕</span>
        <input type="search" v-model="query" placeholder="Search by title, author, or synopsis..." />
      </div>
    </div>
  </header>

  <div class="shelf-section" v-if="shelf.length">
    <div class="shelf-title">My Shelf</div>
    <div class="shelf-scroll">
      <a v-for="item in shelf" :key="item.bookId" :href="getProgressHref(item.bookId)" class="shelf-item">
        <span class="shelf-book-title">{{item.title}}</span>
        <span class="shelf-progress" v-if="getProgressChapter(item.bookId)">{{getProgressChapter(item.bookId)}}</span>
        <span class="shelf-progress" v-else>Ch. 1</span>
      </a>
    </div>
  </div>

  <div class="categories">
    <button :class="['cat-btn',{active:activeTag==='All'}]" @click="activeTag='All'">All</button>
    <button v-for="t in tags" :key="t" :class="['cat-btn',{active:activeTag===t}]" @click="activeTag=t">{{t}}</button>
  </div>

  <div class="grid" v-if="filtered.length">
    <div v-for="(book,i) in filtered" :key="book.id" class="novel-card" :style="{animationDelay:i*0.04+'s'}">
      <a :href="'/novel/'+book.id" class="card-main">
        <div class="card-cover"><span class="cover-char">{{cover(book.title)}}</span></div>
        <div class="card-body">
          <div class="title-row">
            <div class="card-title" v-html="hl(book.title,query)"></div>
            <button :class="['shelf-btn','card-shelf-btn',{active:onShelf(book.id)}]" @click.prevent="toggleShelf(book,$event)" :title="onShelf(book.id)?'Remove from shelf':'Add to shelf'">{{onShelf(book.id)?'★ On Shelf':'☆ Add to Shelf'}}</button>
          </div>
          <div class="card-author" v-html="hl(book.author||'Unknown',query)"></div>
          <div class="card-meta">
            <span v-for="t in (book.tags||[]).slice(0,3)" :key="t" class="tag-pill">{{t}}</span>
            <span>{{book.total_chapters}} ch.</span>
          </div>
          <div class="card-continue" v-if="getProgressChapter(book.id)">Continue: {{getProgressChapter(book.id)}}</div>
        </div>
      </a>
    </div>
  </div>
  <div v-else class="empty-state"><p>No novels found</p></div>
</template>
