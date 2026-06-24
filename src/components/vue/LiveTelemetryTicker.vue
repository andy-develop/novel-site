<template>
  <div v-if="hasData" class="ticker-wrap">
    <div class="ticker-inner">
    <div class="ticker-track track-1">
      <div class="track-label">
        <span class="pulse-dot">💖</span>
        <span class="label-text">TELEMETRY</span>
      </div>
      <div class="scroll-inner scroll-left">
        <span v-for="(item, i) in doubled(t1)" :key="'a'+i" class="track-item" @click="jump(item.book_id, item.chapter_id)">
          <span class="item-type">{{ item.text }}</span>
          <span class="item-book">《{{ item.book }}》</span>
        </span>
      </div>
    </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';

const t1 = ref([]);

const hasData = computed(() => t1.value.length > 0);

const doubled = (arr) => [...arr, ...arr]; // duplicate for seamless loop

const jump = (bookId, chapterId) => {
  window.location.href = `/novel/${bookId}/${chapterId}`;
};

onMounted(async () => {
  try {
    const res = await fetch('/api/telemetry');
    if (res.ok) {
      const data = await res.json();
      t1.value = data.track_1_alerts || [];
    }
  } catch { /* silent */ }
});
</script>

<style scoped>
.ticker-wrap {
  width: 100%;
  background: var(--bg, #151413);
  border-bottom: 1px solid rgba(176,168,150,0.15);
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 11px;
  letter-spacing: 0.5px;
  overflow: hidden;
  user-select: none;
}
.ticker-inner {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 20px;
  overflow: hidden;
}
.ticker-track {
  display: flex;
  align-items: center;
  height: 36px;
  overflow: hidden;
  position: relative;
}
.track-label {
  position: absolute;
  left: 0;
  z-index: 10;
  background: var(--bg, #151413);
  padding: 0 10px;
  display: flex;
  align-items: center;
  gap: 6px;
  border-right: 1px solid rgba(176,168,150,0.15);
  height: 100%;
}
.pulse-dot {
  animation: pulse-glow 1.5s infinite;
}
@keyframes pulse-glow {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; text-shadow: 0 0 6px rgba(176,168,150,0.5); }
}
.label-text {
  color: var(--gold, #b0a896);
  font-weight: 700;
  font-size: 9px;
  text-transform: uppercase;
}
.scroll-inner {
  display: inline-flex;
  gap: 32px;
  white-space: nowrap;
  padding-left: 120px;
}
.scroll-left {
  animation: marquee-left 90s linear infinite;
}
.ticker-track:hover .scroll-inner {
  animation-play-state: paused;
}
@keyframes marquee-left {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}
.track-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  color: var(--text-dim, #8e887d);
  transition: color 0.15s;
}
.track-item:hover {
  color: var(--text, #e0dcd3);
}
.item-type {
  color: #7a9690;
}
.item-book {
  color: var(--gold, #b0a896);
  font-weight: 600;
}
</style>