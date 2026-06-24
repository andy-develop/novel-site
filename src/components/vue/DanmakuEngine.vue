<template>
  <canvas ref="canvasRef" class="danmaku-canvas"></canvas>
  <div v-if="expandedIdx >= 0" ref="cabinRef" class="quantum-cabin">
    <div class="cabin-header">
      <span class="cabin-title">✦ Paragraph {{ expandedIdx }}</span>
      <button class="cabin-close" @click="expandedIdx = -1">✕</button>
    </div>
    <div class="cabin-comments">
      <div v-for="c in getCommentsForIdx(expandedIdx)" :key="c.id" class="cabin-comment">
        <span class="cabin-avatar">👤</span>
        <span class="cabin-text">{{ c.content }}</span>
      </div>
      <div v-if="getCommentsForIdx(expandedIdx).length === 0" class="cabin-empty">
        No echoes yet… leave a mark?
      </div>
    </div>
    <div class="cabin-emojis">
      <button v-for="r in activeReactions" :key="r.emoji" class="emoji-btn"
        @click="submitEmoji(expandedIdx, r.emoji, $event)">{{ r.emoji }} {{ r.label }}</button>
    </div>
    <div class="cabin-input-row">
      <input
        v-model="inputText"
        class="cabin-input"
        placeholder="Drop a thought…"
        maxlength="140"
        @keydown.enter="submitText(expandedIdx)"
      />
      <button class="cabin-submit" @click="submitText(expandedIdx)">Send</button>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue';

const props = defineProps({
  bookId: { type: Number, required: true },
  chapterId: { type: Number, required: true },
});

const canvasRef = ref(null);
const entries = ref([]);
const expandedIdx = ref(-1);
const inputText = ref('');
const activeReactions = ref([]);
let particles = [];
let ctx = null;
let animFrame = null;

// ---- Reaction pool ----
const REACTION_POOL = [
  { emoji: '😂', label: 'Lol' },
  { emoji: '🚨', label: 'Spoiler' },
  { emoji: '🤯', label: 'Mind-blown' },
  { emoji: '💀', label: "I'm dead" },
  { emoji: '🔥', label: 'On fire' },
  { emoji: '😭', label: 'Crying' },
  { emoji: '👑', label: 'King move' },
  { emoji: '😱', label: 'Shook' },
  { emoji: '🤡', label: 'Clownery' },
  { emoji: '🙏', label: 'Blessed' },
  { emoji: '💅', label: 'Slay' },
  { emoji: '🫡', label: 'Respect' },
  { emoji: '👀', label: 'The tea' },
  { emoji: '🥶', label: 'Chills' },
  { emoji: '🌋', label: 'Volcanic' },
  { emoji: '🧠', label: 'Big brain' },
  { emoji: '🫶', label: 'Adore' },
  { emoji: '🎭', label: 'Drama' },
  { emoji: '🪦', label: 'RIP' },
  { emoji: '⚡', label: 'Electric' },
  { emoji: '🌙', label: 'Late vibes' },
  { emoji: '⚔️', label: 'Wars' },
  { emoji: '🫠', label: 'Melting' },
  { emoji: '🎯', label: 'Spot on' },
  { emoji: '🐉', label: 'Epic' },
  { emoji: '🥺', label: 'Pleading' },
  { emoji: '🎭', label: 'Plot twist' },
  { emoji: '💪', label: 'Power' },
  { emoji: '🫣', label: 'Can\'t look' },
  { emoji: '🤌', label: 'Chef kiss' },
];

const pickRandomReactions = (count = 3) => {
  const shuffled = [...REACTION_POOL].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, count);
};

// ---- Particle system ----
class Particle {
  constructor(x, y, char) {
    this.x = x;
    this.y = y;
    this.char = char;
    this.vx = (Math.random() - 0.5) * 8;
    this.vy = -(Math.random() * 10 + 4);
    this.alpha = 1;
    this.gravity = 0.25;
    this.size = Math.floor(Math.random() * 10) + 20;
  }
  update() {
    this.vy += this.gravity;
    this.x += this.vx;
    this.y += this.vy;
    this.alpha -= 0.018;
  }
  draw(c) {
    c.save();
    c.globalAlpha = Math.max(0, this.alpha);
    c.font = `${this.size}px serif`;
    c.fillStyle = '#b0a896';
    c.fillText(this.char, this.x, this.y);
    c.restore();
  }
}

const triggerParticleBurst = (x, y, emoji, count) => {
  for (let i = 0; i < count; i++) {
    particles.push(new Particle(x, y, emoji));
  }
};

const triggerCritRain = (emoji, count, durationMs) => {
  if (!canvasRef.value) return;
  const w = canvasRef.value.width;
  const endTime = Date.now() + durationMs;
  const spawn = () => {
    const batch = Math.min(Math.ceil(count / 8), 6);
    for (let i = 0; i < batch; i++) {
      particles.push(new Particle(Math.random() * w, -20, emoji));
    }
    if (Date.now() < endTime && particles.length < 300) {
      setTimeout(spawn, 60);
    }
  };
  spawn();
};

const tick = () => {
  if (!ctx || !canvasRef.value) return;
  ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height);
  particles = particles.filter(p => p.alpha > 0);
  particles.forEach(p => { p.update(); p.draw(ctx); });
  animFrame = requestAnimationFrame(tick);
};

// ---- Data fetching ----
const fetchDanmaku = async () => {
  try {
    const res = await fetch(`/api/danmaku?book_id=${props.bookId}&chapter_id=${props.chapterId}`);
    if (res.ok) {
      const data = await res.json();
      entries.value = data.entries || [];
    }
  } catch { /* silent */ }
};

// ---- Paragraph helpers ----
const getCommentsForIdx = (idx) => entries.value.filter(e => e.paragraph_idx === idx);
const getEmojiCounts = (idx) => {
  const comments = getCommentsForIdx(idx);
  return comments.filter(c => c.reaction_type === 'emoji').length;
};
const getTotalCount = (idx) => getCommentsForIdx(idx).length;

// ---- Submit logic ----
const submitText = async (idx) => {
  const text = inputText.value.trim();
  if (!text) return;
  // Optimistic: add locally now
  const tempEntry = {
    id: Date.now(),
    paragraph_idx: idx,
    content: text,
    reaction_type: 'text',
    session_hash: '',
    created_at: Math.floor(Date.now() / 1000),
  };
  entries.value.push(tempEntry);
  inputText.value = '';
  // Particle splash
  triggerParticleBurst(window.innerWidth / 2, window.innerHeight / 2, '💬', 6);
  // Fire-and-forget POST
  try {
    await fetch('/api/danmaku', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        book_id: props.bookId,
        chapter_id: props.chapterId,
        paragraph_idx: idx,
        content: text,
        reaction_type: 'text',
      }),
    });
  } catch { /* optimistic, ignore */ }
};

// ---- DOM: Mount bubble buttons on paragraph blocks ----
const MIN_PARAGRAPH_CHARS = 120; // ~3 lines of body text

const mountBubbles = () => {
  const blocks = document.querySelectorAll('.paragraph-block');
  blocks.forEach(block => {
    const idx = parseInt(block.getAttribute('data-p-idx'));
    if (isNaN(idx)) return;
    // Skip short paragraphs — no bubble
    const pEl = block.querySelector('p');
    const text = (pEl?.textContent || '').trim();
    if (text.length < MIN_PARAGRAPH_CHARS) return;
    const total = getTotalCount(idx);
    const bubble = document.createElement('button');
    bubble.className = 'danmaku-bubble';
    bubble.setAttribute('data-dm-idx', idx);
    bubble.textContent = total > 0 ? `💬 ${total}` : '💬';
    bubble.addEventListener('click', (e) => {
      e.stopPropagation();
      if (expandedIdx.value === idx) {
        expandedIdx.value = -1;
      } else {
        activeReactions.value = pickRandomReactions(3);
        expandedIdx.value = idx;
      }
    });
    // Insert inline at the end of the last <p> inside the block
    const lastP = block.querySelector('p:last-of-type') || block.querySelector('p');
    if (lastP) {
      lastP.appendChild(bubble);
    } else {
      block.appendChild(bubble);
    }
  });
};

// Sync bubble counts when entries change
const syncBubbleCounts = () => {
  const bubbles = document.querySelectorAll('.danmaku-bubble');
  bubbles.forEach(bubble => {
    const idx = parseInt(bubble.getAttribute('data-dm-idx'));
    if (isNaN(idx)) return;
    const total = getTotalCount(idx);
    bubble.textContent = total > 0 ? `💬 ${total}` : '💬';
  });
};

// Watch entries to update bubbles reactively
watch(entries, () => { syncBubbleCounts(); }, { deep: true });

// ---- Lifecycle ----
const handleResize = () => {
  if (!canvasRef.value) return;
  const dpr = window.devicePixelRatio || 1;
  canvasRef.value.width = window.innerWidth * dpr;
  canvasRef.value.height = window.innerHeight * dpr;
  canvasRef.value.style.width = window.innerWidth + 'px';
  canvasRef.value.style.height = window.innerHeight + 'px';
  if (ctx) ctx.scale(dpr, dpr);
};

onMounted(async () => {
  await fetchDanmaku();
  handleResize();
  window.addEventListener('resize', handleResize);
  if (canvasRef.value) {
    ctx = canvasRef.value.getContext('2d');
    tick();
  }
  mountBubbles();
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  if (animFrame) cancelAnimationFrame(animFrame);
});

// ---- Emoji reaction ----
const submitEmoji = async (idx, emoji, event) => {
  const tempEntry = {
    id: Date.now(),
    paragraph_idx: idx,
    content: emoji,
    reaction_type: 'emoji',
    session_hash: '',
    created_at: Math.floor(Date.now() / 1000),
  };
  entries.value.push(tempEntry);
  const totalN = getEmojiCounts(idx);
  if (totalN > 10) {
    triggerCritRain(emoji, totalN, 2000);
  } else if (totalN > 2) {
    triggerCritRain(emoji, totalN, 1000);
  } else {
    const rect = event?.target?.getBoundingClientRect?.();
    const x = rect ? rect.left + rect.width / 2 : window.innerWidth / 2;
    const y = rect ? rect.top : window.innerHeight / 2;
    triggerParticleBurst(x, y, emoji, 8);
  }
  try {
    await fetch('/api/danmaku', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        book_id: props.bookId,
        chapter_id: props.chapterId,
        paragraph_idx: idx,
        content: emoji,
        reaction_type: 'emoji',
      }),
    });
  } catch { /* optimistic, ignore */ }
};
</script>

<style scoped>
.danmaku-canvas {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 90;
}
.quantum-cabin {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: min(420px, 92vw);
  background: var(--bg-card, #1f1e1c);
  border: 1px solid var(--gold-dim, rgba(176,168,150,0.15));
  border-radius: 12px;
  padding: 16px;
  z-index: 100;
  animation: cabinIn 0.25s ease-out;
}
.cabin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.cabin-title {
  font-family: var(--font-ui, 'DM Sans', sans-serif);
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--gold, #b0a896);
}
.cabin-close {
  background: none;
  border: none;
  color: var(--text-dim, #8e887d);
  font-size: 1rem;
  cursor: pointer;
}
.cabin-comments {
  max-height: 140px;
  overflow-y: auto;
  margin-bottom: 10px;
}
.cabin-comment {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 0;
  border-bottom: 1px solid var(--border, rgba(176,168,150,0.08));
}
.cabin-avatar { font-size: 0.8rem; }
.cabin-text {
  font-size: 0.82rem;
  color: var(--text-dim, #8e887d);
  word-break: break-word;
}
.cabin-empty {
  font-style: italic;
  font-size: 0.82rem;
  color: var(--text-muted, #5d574d);
  text-align: center;
  padding: 12px 0;
}
.cabin-emojis {
  display: flex;
  gap: 6px;
  margin-bottom: 10px;
}
.emoji-btn {
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.15s;
  border: 1px solid var(--border, rgba(176,168,150,0.08));
  background: transparent;
  color: var(--text-dim, #8e887d);
}
.emoji-btn:hover {
  border-color: var(--gold, #b0a896);
  color: var(--gold, #b0a896);
}
.cabin-input-row {
  display: flex;
  gap: 6px;
}
.cabin-input {
  flex: 1;
  padding: 7px 12px;
  border: 1px solid var(--border, rgba(176,168,150,0.08));
  border-radius: 6px;
  background: var(--bg, #151413);
  color: var(--text, #e0dcd3);
  font-size: 0.82rem;
  outline: none;
}
.cabin-input:focus {
  border-color: var(--gold, #b0a896);
}
.cabin-input::placeholder {
  color: var(--text-muted, #5d574d);
}
.cabin-submit {
  padding: 7px 16px;
  background: var(--gold-dim, rgba(176,168,150,0.15));
  color: var(--gold, #b0a896);
  border: 1px solid var(--gold, #b0a896);
  border-radius: 6px;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}
.cabin-submit:hover {
  background: var(--gold, #b0a896);
  color: var(--bg, #151413);
}
@keyframes cabinIn {
  from { opacity: 0; transform: translateX(-50%) translateY(8px); }
  to { opacity: 1; transform: translateX(-50%) translateY(0); }
}
</style>
