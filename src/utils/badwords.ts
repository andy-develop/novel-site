/**
 * Simple sensitive-word filter for danmaku
 * Returns censored text (replaces bad chars with *) or throws if too toxic
 */

const BLOCKED: string[] = [
  // Add more as needed — keep sorted for readability
  'fuck', 'shit', 'bitch', 'asshole', 'nigger', 'nigga',
  'cunt', 'dick', 'pussy', 'whore', 'slut',
  '强奸', '轮奸', '恋童', '幼女', '杀人', '自杀',
  '炸弹', '恐怖袭击', 'isis',
];

/** Returns true if text contains any blocked word (case-insensitive) */
export function hasBlockedWord(text: string): boolean {
  const lower = text.toLowerCase();
  return BLOCKED.some(w => lower.includes(w));
}

/** Censor blocked words by replacing with asterisks */
export function censorText(text: string): string {
  let result = text;
  for (const w of BLOCKED) {
    const re = new RegExp(w, 'gi');
    result = result.replace(re, '*'.repeat(w.length));
  }
  return result;
}

/** Validate danmaku content: length + blocked words */
export function validateDanmaku(content: string): { ok: boolean; error?: string } {
  const trimmed = content.trim();
  if (!trimmed) return { ok: false, error: 'Empty content' };
  if (trimmed.length > 140) return { ok: false, error: 'Max 140 characters' };
  if (hasBlockedWord(trimmed)) return { ok: false, error: 'Contains blocked content' };
  return { ok: true };
}
