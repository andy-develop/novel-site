<template>
  <Transition name="slide-up">
    <div v-if="isOpen" class="dossier-overlay">
      <div class="dossier-header">
        <span class="dossier-label">🗂️ CHARACTER DOSSIER</span>
        <button @click="isOpen = false" class="dossier-close">✕</button>
      </div>
      <div class="dossier-core">
        <div class="dossier-name">{{ currentDossier.title }}</div>
        <div v-if="currentDossier.dopamine_sync" class="dossier-stat">
          ⚡ Sync: <span class="dossier-val">{{ currentDossier.dopamine_sync }}</span>
        </div>
        <div v-if="currentDossier.heartbreak_logs" class="dossier-stat">
          💔 Trauma: <span class="dossier-val-purple">{{ currentDossier.heartbreak_logs }}</span>
        </div>
      </div>
      <div class="dossier-nodes">
        <div class="nodes-label">📍 EPIC MOMENTS</div>
        <a v-for="(node, i) in filteredNodes" :key="i"
          :href="node.url" class="node-link">
          <span class="node-title">{{ node.title }}</span>
          <span class="node-arrow">▶</span>
        </a>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';

const props = defineProps({ charData: { type: Object, default: () => ({}) } });
const isOpen = ref(false);
const currentDossier = ref({ title: '', epic_nodes: [] });
const currentPath = ref('');

const filteredNodes = computed(() => {
  const nodes = currentDossier.value.epic_nodes || [];
  const path = currentPath.value;
  if (!path) return nodes;
  return nodes.filter(n => n.url !== path);
});

const handleContentClick = (e) => {
  const target = e.target.closest('.character-link');
  if (!target) return;
  const charId = target.getAttribute('data-char-id');
  if (props.charData[charId]) {
    const dossier = props.charData[charId].dossier;
    const path = window.location.pathname;
    currentPath.value = path;
    currentDossier.value = dossier;
    isOpen.value = true;
  }
};

onMounted(() => {
  const el = document.getElementById('novel-content');
  if (el) el.addEventListener('click', handleContentClick);
});

onUnmounted(() => {
  const el = document.getElementById('novel-content');
  if (el) el.removeEventListener('click', handleContentClick);
});
</script>

<style scoped>
.dossier-overlay {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: min(420px, 92vw);
  background: var(--bg-card);
  border: 1px solid var(--gold-dim);
  border-radius: 12px;
  padding: 16px;
  z-index: 110;
  backdrop-filter: blur(14px);
  box-shadow: 0 0 30px rgba(201,168,76,0.08);
  animation: dossierIn 0.25s ease-out;
}
.dossier-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 8px;
  margin-bottom: 10px;
  border-bottom: 1px solid var(--border);
}
.dossier-label {
  font-family: var(--font-ui);
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--gold);
}
.dossier-close {
  background: none;
  border: none;
  color: var(--text-dim);
  font-size: 1rem;
  cursor: pointer;
}
.dossier-close:hover { color: var(--gold); }
.dossier-core { margin-bottom: 12px; }
.dossier-name {
  font-family: var(--font-display);
  font-size: 1.1rem;
  color: var(--text);
  margin-bottom: 6px;
}
.dossier-stat {
  font-family: var(--font-ui);
  font-size: 0.78rem;
  color: var(--text-dim);
  margin-bottom: 2px;
}
.dossier-val { color: var(--gold); font-weight: 600; }
.dossier-val-purple { color: #b794f6; font-weight: 600; }
.nodes-label {
  font-family: var(--font-ui);
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-bottom: 8px;
}
.node-link {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 7px 10px;
  margin-bottom: 4px;
  background: rgba(0,0,0,0.25);
  border: 1px solid var(--border);
  border-radius: 6px;
  text-decoration: none;
  transition: all 0.15s;
}
.node-link:hover {
  border-color: var(--gold-dim);
  background: var(--bg-card-hover);
}
.node-title {
  font-family: var(--font-ui);
  font-size: 0.78rem;
  color: var(--text-dim);
}
.node-link:hover .node-title { color: var(--text); }
.node-arrow {
  font-size: 0.65rem;
  color: var(--gold);
  transition: transform 0.15s;
}
.node-link:hover .node-arrow { transform: translateX(3px); }
.slide-up-enter-active, .slide-up-leave-active {
  transition: all 0.25s cubic-bezier(0.16,1,0.3,1);
}
.slide-up-enter-from, .slide-up-leave-to {
  transform: translate(-50%, 100%);
  opacity: 0;
}
@keyframes dossierIn {
  from { opacity: 0; transform: translateX(-50%) translateY(8px); }
  to { opacity: 1; transform: translateX(-50%) translateY(0); }
}
</style>
