const novels = [
  {id:1, title:'The Name of the Wind', author:'Patrick Rothfuss', cover:'N', category:'Fantasy', chapters:35},
  {id:2, title:'Dune', author:'Frank Herbert', cover:'D', category:'Sci-Fi', chapters:48},
  {id:3, title:'The Hobbit', author:'J.R.R. Tolkien', cover:'H', category:'Fantasy', chapters:24},
  {id:4, title:'Neuromancer', author:'William Gibson', cover:'N', category:'Sci-Fi', chapters:20},
  {id:5, title:'The Way of Kings', author:'Brandon Sanderson', cover:'W', category:'Fantasy', chapters:58},
  {id:6, title:'The Shadow of the Wind', author:'Carlos Ruiz Zafón', cover:'S', category:'Mystery', chapters:30},
  {id:7, title:'The Left Hand of Darkness', author:'Ursula K. Le Guin', cover:'L', category:'Sci-Fi', chapters:22},
  {id:8, title:'Jonathan Strange & Mr Norrell', author:'Susanna Clarke', cover:'J', category:'Fantasy', chapters:42},
  {id:9, title:'The Road', author:'Cormac McCarthy', cover:'R', category:'Literary', chapters:18},
  {id:10, title:'Snow Crash', author:'Neal Stephenson', cover:'S', category:'Sci-Fi', chapters:28},
  {id:11, title:'The Secret History', author:'Donna Tartt', cover:'S', category:'Literary', chapters:26},
  {id:12, title:'House of Leaves', author:'Mark Z. Danielewski', cover:'H', category:'Horror', chapters:32}
]

const categories = ['All','Fantasy','Sci-Fi','Mystery','Literary','Horror']

const chapters = ['Prologue','Chapter I','Chapter II','Chapter III','Chapter IV','Chapter V']

const sampleContent = {
  'Prologue': 'The night air was cold, sharp as a blade drawn from its sheath.\n\nHe stood at the edge of the forest, watching the lights of the town flicker in the distance. Three years had passed since he last saw those streets, since he last heard the bells of the old cathedral.\n\nThree years since everything ended. And three years since everything began.\n\nHe adjusted the strap of his bag, feeling the weight of the book inside — leather-bound, worn at the edges, its pages filled with a script he had spent countless nights learning to read.\n\n"One more time," he whispered to himself. "One more time, and then it\'s over."\n\nThe wind carried his words away into the dark. Somewhere in the distance, an owl called out, its voice echoing through the trees like a question that demanded an answer.\n\nHe took a step forward. Then another. The town grew closer, its lights resolving into windows, into doorways, into the shapes of buildings he remembered from a life he had left behind.\n\nAbove him, the stars were bright — cold and distant and utterly indifferent. But they were the same stars that had guided him through the darkest nights of his journey. He trusted them.\n\nHe reached the edge of town. The first house stood silent, its chimney smokeless, its windows dark. He passed it without a glance. His destination lay deeper in, where the streets narrowed and the old stone walls leaned close together, whispering secrets to one another.\n\nAt the end of a crooked lane, he stopped. A door, painted blue and faded by weather, stood before him. He raised his hand, hesitated, then knocked. Three times.\n\nThe sound of footsteps, slow and deliberate. Then the door creaked open, and a face appeared in the crack — old, lined with years, with eyes that had seen too much.\n\n"You\'re late," the old man said.\n\n"I know."\n\n"Did you find it?"\n\nHe reached into his bag and pulled out the book. Its cover gleamed faintly in the lamplight.\n\nThe old man stared at it for a long moment. Then he smiled — a thin, knowing smile.\n\n"Then come in. We have work to do."',
  'Chapter I': 'The room was small and cluttered, filled with stacks of papers, dried herbs hanging from the ceiling, and candles that burned at all hours despite the daylight filtering through the dusty window.\n\nThe old man — his name was Aldric — placed the book on a heavy wooden table and opened it with the reverence of a priest handling a sacred text.\n\n"Do you know what this is?" he asked, though the question seemed rhetorical.\n\n"A journal," Kael replied. "My father\'s journal."\n\n"More than that. It is a record — a map, if you will — of what happened on the night the world changed."\n\nKael sat down across from him, his eyes fixed on the familiar handwriting. His father had died twelve years ago, but here, in these pages, his voice still lived.\n\n"I have spent my entire life trying to understand that night," Kael said quietly. "I remember the fire. I remember the screaming. But I don\'t remember why."\n\nAldric turned the pages slowly, stopping at a passage marked with a ribbon.\n\n"Your father was not a victim, Kael. He was a guardian. And what he guarded — what he died protecting — is still out there."\n\nThe candlelight flickered, casting long shadows across the walls.\n\n"Show me," Kael said.\n\nAldric began to read.'
}

const app = document.getElementById('app')
let currentNovel = null
let currentCategory = 'All'
let searchCache = ''

function renderHome() {
  const filtered = currentCategory === 'All'
    ? novels
    : novels.filter(n => n.category === currentCategory)
  app.innerHTML = `
    <header>
      <div class="header-inner">
        <div class="logo"><span>A</span>rcana</div>
        <div class="search-wrap">
          <span class="icon">⌕</span>
          <input type="search" id="search" placeholder="Search by title or author..." oninput="onSearch(this.value)">
        </div>
      </div>
    </header>
    <div class="categories">${categories.map(c =>
      `<button class="cat-btn ${c===currentCategory?'active':''}" onclick="setCategory('${c}')">${c}</button>`
    ).join('')}</div>
    <div class="grid" id="novelGrid">
      ${filtered.map((n,i) => `
        <div class="novel-card" onclick="openReader(${n.id})" style="animation-delay:${i*0.04}s">
          <div class="card-cover">${n.cover}</div>
          <div class="card-body">
            <div class="card-title">${n.title}</div>
            <div class="card-author">${n.author}</div>
            <div class="card-meta">
              <span>${n.category}</span>
              <span>${n.chapters} ch.</span>
            </div>
          </div>
        </div>
      `).join('')}
    </div>
  `
}

function renderReader() {
  const novel = novels.find(n => n.id === currentNovel)
  if (!novel) { renderHome(); return }
  const content = sampleContent['Prologue'] || 'Loading...'
  app.innerHTML = `
    <header>
      <div class="header-inner">
        <div class="logo"><span>A</span>rcana</div>
      </div>
    </header>
    <div class="reader">
      <button class="back-btn" onclick="renderHome()">← Back to Library</button>
      <h1>${novel.title}</h1>
      <div class="author">${novel.author}</div>
      <div class="chapter-nav">
        <select id="chapterSelect" onchange="changeChapter(this.value)">
          ${chapters.map((ch, i) =>
            `<option value="${ch}" ${i===0?'selected':''}>${ch}</option>`
          ).join('')}
        </select>
        <button onclick="prevChapter()" id="prevBtn">← Prev</button>
        <button onclick="nextChapter()" id="nextBtn">Next →</button>
      </div>
      <div class="content" id="chapterContent">
        ${content.split('\n\n').filter(Boolean).map(p => `<p>${p.replace(/\n/g,'<br>')}</p>`).join('')}
      </div>
    </div>
  `
}

function openReader(id) {
  currentNovel = id
  renderReader()
  window.scrollTo({top:0, behavior:'smooth'})
}

function setCategory(cat) {
  currentCategory = cat
  renderHome()
}

function onSearch(val) {
  const grid = document.getElementById('novelGrid')
  if (!grid) return
  const q = val.trim().toLowerCase()
  const filtered = novels.filter(n =>
    n.title.toLowerCase().includes(q) ||
    n.author.toLowerCase().includes(q)
  )
  grid.innerHTML = filtered.length
    ? filtered.map((n,i) => `<div class="novel-card" onclick="openReader(${n.id})" style="animation-delay:${i*0.04}s">
        <div class="card-cover">${n.cover}</div>
        <div class="card-body">
          <div class="card-title">${n.title}</div>
          <div class="card-author">${n.author}</div>
          <div class="card-meta">
            <span>${n.category}</span>
            <span>${n.chapters} ch.</span>
          </div>
        </div>
      </div>`).join('')
    : '<p style="grid-column:1/-1;text-align:center;color:var(--text-dim);padding:40px 0">No novels found</p>'
}

function changeChapter(ch) {
  const el = document.getElementById('chapterContent')
  if (!el) return
  const content = sampleContent[ch] || 'Chapter content loading...'
  el.innerHTML = content.split('\n\n').filter(Boolean).map(p => `<p>${p.replace(/\n/g,'<br>')}</p>`).join('')
  window.scrollTo({top:0, behavior:'smooth'})
}

function prevChapter() {
  const sel = document.getElementById('chapterSelect')
  if (!sel || sel.selectedIndex <= 0) return
  sel.selectedIndex--
  changeChapter(sel.value)
}

function nextChapter() {
  const sel = document.getElementById('chapterSelect')
  if (!sel || sel.selectedIndex >= sel.options.length-1) return
  sel.selectedIndex++
  changeChapter(sel.value)
}

renderHome()
