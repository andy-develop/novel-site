<script setup>
import { ref, computed, onMounted } from 'vue'
import MiniSearch from 'minisearch'

const props = defineProps({
  books: Array,
  tags: Array,
  tagCounts: Object,
})

const query = ref('')
const activeTag = ref('All')
const expandedId = ref(null)
const ms = ref(null)

onMounted(() => {
  const idx = new MiniSearch({
    fields: ['title','author','tags','intro'],
    storeFields: ['id','title','author','tags','intro','total_chapters'],
    searchOptions: { boost: { title:3, author:2 }, prefix:true, fuzzy:0.2 }
  })
  idx.addAll(props.books)
  ms.value = idx
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

  <div class="categories">
    <button :class="['cat-btn',{active:activeTag==='All'}]" @click="activeTag='All'">All ({{books.length}})</button>
    <button v-for="t in tags" :key="t" :class="['cat-btn',{active:activeTag===t}]" @click="activeTag=t">{{t}} ({{tagCounts[t]||0}})</button>
  </div>

  <div class="grid" v-if="filtered.length">
    <div v-for="(book,i) in filtered" :key="book.id" :class="['novel-card',{expanded:expandedId===book.id}]" :style="{animationDelay:i*0.04+'s'}">
      <div class="card-main" @click="expandedId=expandedId===book.id?null:book.id">
        <div class="card-cover"><span class="cover-char">{{cover(book.title)}}</span></div>
        <div class="card-body">
          <div class="title-row">
            <div class="card-title" v-html="hl(book.title,query)"></div>
          </div>
          <div class="card-author" v-html="hl(book.author||'Unknown',query)"></div>
          <div class="card-meta">
            <span v-for="t in (book.tags||[]).slice(0,3)" :key="t" class="tag-pill">{{t}}</span>
            <span>{{book.total_chapters}} ch.</span>
          </div>
        </div>
        <span class="expand-icon">{{expandedId===book.id?'▾':'▸'}}</span>
      </div>
      <div v-if="expandedId===book.id" class="card-intro">
        <p v-if="book.intro" class="intro-text" v-html="hl(book.intro,query)"></p>
        <a :href="'/novel/'+book.id" class="start-btn">Start Reading →</a>
      </div>
    </div>
  </div>
  <div v-else class="empty-state"><p>No novels found</p></div>
</template>
