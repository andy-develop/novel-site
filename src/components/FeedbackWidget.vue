<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue';

const isOpen = ref(false);
const isHidden = ref(false);
const isSubmitting = ref(false);
const isSuccess = ref(false);
const content = ref('');
const errorMsg = ref('');
const textareaRef = ref(null);

let lastScrollY = 0;
let scrollTicking = false;
let touchStartY = 0;

const placeholders = [
  "Caught a typo? Wanna roast the plot? The admin is online and ready...",
  "Loading slow? Found a broken chapter? Tell us everything.",
  "Spotted a bug? Have a wild theory? Drop it here.",
];
const placeholder = placeholders[Math.floor(Math.random() * placeholders.length)];

function detectContext() {
  const path = window.location.pathname;
  const url = window.location.href;
  let chapter = '';
  let book = '';

  // Chapter page: /novel/{id}/{chapterId}
  const chapterMatch = path.match(/^\/novel\/\d+\/\d+/);
  if (chapterMatch) {
    const h1 = document.querySelector('.reader h1');
    chapter = h1 ? h1.innerText.trim() : '';
  }

  // Book page: /novel/{id}
  const bookMatch = path.match(/^\/novel\/\d+$/);
  if (bookMatch) {
    const h1 = document.querySelector('.reader h1');
    book = h1 ? h1.innerText.trim() : '';
    chapter = book ? `Book page: ${book}` : '';
  }

  // Home
  if (path === '/' || path === '') {
    chapter = 'Homepage';
  }

  return {
    user: getUserName(),
    content: content.value.trim(),
    currentUrl: url,
    chapter: chapter || path,
    ua: navigator.userAgent,
    timestamp: Date.now(),
  };
}

function getUserName() {
  try {
    return localStorage.getItem('feedback-username') || '';
  } catch {
    return '';
  }
}

function saveUserName(name) {
  try {
    if (name) localStorage.setItem('feedback-username', name);
  } catch {}
}

function toggle() {
  isOpen.value = !isOpen.value;
  if (isOpen.value) {
    isSuccess.value = false;
    errorMsg.value = '';
    nextTick(() => {
      textareaRef.value?.focus();
    });
  }
}

function close() {
  isOpen.value = false;
}

function handleScroll() {
  if (scrollTicking) return;
  scrollTicking = true;
  requestAnimationFrame(() => {
    const y = window.scrollY || window.pageYOffset;
    const delta = y - lastScrollY;
    if (delta > 6 && y > 80) {
      // Scrolling down & past header — tuck away
      isHidden.value = true;
    } else if (delta < -4) {
      // Scrolling up — reappear
      isHidden.value = false;
    }
    lastScrollY = y;
    scrollTicking = false;
  });
}

function handleTouchStart(e) {
  touchStartY = e.touches[0]?.clientY || 0;
}

function handleTouchMove(e) {
  const y = e.touches[0]?.clientY || 0;
  const delta = touchStartY - y;
  if (delta > 10) {
    isHidden.value = true;
  } else if (delta < -8) {
    isHidden.value = false;
  }
  touchStartY = y;
}

async function submit() {
  if (isSubmitting.value) return;
  const text = content.value.trim();
  if (!text) {
    errorMsg.value = 'Say something first~';
    return;
  }

  isSubmitting.value = true;
  errorMsg.value = '';

  const payload = detectContext();
  saveUserName(payload.user);

  try {
    const res = await fetch('/api/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (res.ok && data.success) {
      isSuccess.value = true;
      content.value = '';
      setTimeout(() => {
        isOpen.value = false;
        setTimeout(() => { isSuccess.value = false; }, 300);
      }, 1800);
    } else {
      errorMsg.value = data.error || 'Failed to send. Try again later.';
    }
  } catch (err) {
    errorMsg.value = 'Network error. Please try again.';
  } finally {
    isSubmitting.value = false;
  }
}

function onBackdropClick(e) {
  if (e.target === e.currentTarget) close();
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll, { passive: true });
  window.addEventListener('touchstart', handleTouchStart, { passive: true });
  window.addEventListener('touchmove', handleTouchMove, { passive: true });
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
  window.removeEventListener('touchstart', handleTouchStart);
  window.removeEventListener('touchmove', handleTouchMove);
});
</script>

<template>
  <div class="feedback-widget">
    <!-- Floating trigger -->
    <button
      class="feedback-trigger"
      :class="{ hidden: isHidden }"
      @click="toggle"
      aria-label="Send feedback"
      title="Feedback"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
      </svg>
      <span class="trigger-text">Feedback</span>
    </button>

    <!-- Modal -->
    <Teleport to="body">
      <div v-if="isOpen" class="feedback-backdrop" @click="onBackdropClick">
        <div class="feedback-modal" role="dialog" aria-modal="true" aria-labelledby="feedback-title">
          <div class="feedback-header">
            <h4 id="feedback-title">Feedback</h4>
            <button class="feedback-close" @click="close" aria-label="Close">×</button>
          </div>

          <div v-if="isSuccess" class="feedback-success">
            <svg class="success-plane" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M22 2L11 13"/>
              <path d="M22 2l-7 20-4-9-9-4 20-7z"/>
            </svg>
            <p>🚀 Your note is on its way to the admin!</p>
          </div>

          <template v-else>
            <textarea
              ref="textareaRef"
              v-model="content"
              :placeholder="placeholder"
              rows="4"
              maxlength="1000"
            />
            <div class="feedback-meta">
              <span>{{ content.length }}/1000</span>
            </div>
            <p v-if="errorMsg" class="feedback-error">{{ errorMsg }}</p>
            <button class="feedback-submit" @click="submit" :disabled="isSubmitting">
              {{ isSubmitting ? 'Sending...' : 'Send Feedback' }}
            </button>
          </template>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.feedback-widget {
  position: fixed;
  bottom: 24px;
  right: 18px;
  z-index: 180;
  font-family: var(--font-ui);
}

.feedback-trigger {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px 10px 12px;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: rgba(250, 248, 245, 0.72);
  backdrop-filter: blur(14px) saturate(1.2);
  -webkit-backdrop-filter: blur(14px) saturate(1.2);
  color: var(--text-dim);
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.06);
  transition: transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.3s, background 0.2s, color 0.2s;
  outline: none;
}

.feedback-trigger:hover,
.feedback-trigger:focus-visible {
  background: var(--color-paper-2);
  color: var(--color-accent);
  border-color: oklch(56% 0.150 350 / 0.25);
}

.feedback-trigger.hidden {
  opacity: 0;
  transform: translateX(110%);
  pointer-events: none;
}

.feedback-trigger svg {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.feedback-backdrop {
  position: fixed;
  inset: 0;
  z-index: 190;
  display: flex;
  align-items: flex-end;
  justify-content: flex-end;
  padding: 0 18px 88px 18px;
  background: rgba(0, 0, 0, 0.12);
  backdrop-filter: blur(2px);
  animation: fadeIn 0.2s ease;
}

.feedback-modal {
  width: min(320px, calc(100vw - 36px));
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
  animation: popIn 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
  color: var(--text);
}

.feedback-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.feedback-header h4 {
  font-family: var(--font-display);
  font-size: 1rem;
  font-weight: 400;
  color: var(--gold);
  margin: 0;
}

.feedback-close {
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 1.3rem;
  line-height: 1;
  cursor: pointer;
  padding: 0 0 2px 8px;
  transition: color 0.15s;
}

.feedback-close:hover {
  color: var(--text);
}

.feedback-modal textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--bg-card);
  color: var(--text);
  font-family: var(--font-body);
  font-size: 0.9rem;
  line-height: 1.55;
  resize: none;
  outline: none;
  transition: border-color 0.2s;
}

.feedback-modal textarea::placeholder {
  color: var(--text-muted);
}

.feedback-modal textarea:focus-visible {
  border-color: var(--color-accent);
  outline: 2px solid var(--color-focus);
  outline-offset: 2px;
}

.feedback-meta {
  display: flex;
  justify-content: flex-end;
  margin-top: 6px;
  font-size: 0.7rem;
  color: var(--text-muted);
}

.feedback-error {
  margin: 10px 0 0;
  font-size: 0.78rem;
  color: #c45a5a;
}

.feedback-submit {
  width: 100%;
  margin-top: 12px;
  padding: 10px 14px;
  border: none;
  border-radius: 10px;
  background: var(--gold);
  color: var(--bg);
  font-family: var(--font-ui);
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: filter 0.2s, transform 0.15s;
}

.feedback-submit:hover:not(:disabled) {
  filter: brightness(1.08);
}

.feedback-submit:active:not(:disabled) {
  transform: scale(0.98);
}

.feedback-submit:disabled {
  opacity: 0.6;
  cursor: default;
}

.feedback-success {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 18px 8px;
  text-align: center;
}

.feedback-success p {
  margin: 0;
  font-size: 0.9rem;
  color: var(--text-dim);
}

.success-plane {
  width: 44px;
  height: 44px;
  color: #5fa862;
  stroke-dasharray: 60;
  stroke-dashoffset: 60;
  animation: drawPlane 0.6s ease forwards, flyAway 0.8s ease 0.7s forwards;
}

@keyframes drawPlane {
  to { stroke-dashoffset: 0; }
}

@keyframes flyAway {
  0% { transform: translate(0, 0) rotate(0); opacity: 1; }
  100% { transform: translate(28px, -28px) rotate(-12deg); opacity: 0; }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes popIn {
  from { opacity: 0; transform: translateY(12px) scale(0.96); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

/* Dark mode */
:global(body.dark-mode) .feedback-trigger {
  background: rgba(31, 30, 28, 0.75);
  color: var(--text-dim);
  border-color: rgba(227, 221, 210, 0.1);
}
:global(body.dark-mode) .feedback-trigger:hover,
:global(body.dark-mode) .feedback-trigger:focus-visible {
  background: var(--color-paper-2);
  color: var(--color-accent);
  border-color: oklch(72% 0.135 350 / 0.3);
}
:global(body.dark-mode) .feedback-modal {
  background: var(--bg-card);
  border-color: rgba(227, 221, 210, 0.1);
}
:global(body.dark-mode) .feedback-modal textarea {
  background: rgba(21, 20, 19, 0.6);
  color: var(--text);
}

@media (max-width: 480px) {
  .feedback-widget {
    bottom: 18px;
    right: 14px;
  }
  .feedback-trigger {
    padding: 9px 12px 9px 10px;
  }
  .trigger-text {
    display: none;
  }
  .feedback-trigger svg {
    width: 18px;
    height: 18px;
  }
  .feedback-backdrop {
    padding-bottom: 78px;
  }
}
</style>
