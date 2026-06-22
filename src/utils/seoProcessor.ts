/**
 * Character Link Injection — operates on HTML (after renderMd) to avoid
 * conflicts with existing markdown bold/italic markers.
 *
 * For each chapter, each character only gets an internal link on their
 * FIRST occurrence. Subsequent mentions are left plain.
 */

interface CharacterAlias {
  aliases: string[];
  primary_name: string;
}

export interface CharacterConfig {
  [charId: string]: CharacterAlias;
}

function escapeRegExp(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * Inject character links into already-rendered HTML paragraphs.
 * Each character is linked only on their first appearance per chapter.
 *
 * @param htmlParagraphs - Array of HTML strings (output of renderMd)
 * @param charConfig - Character configuration from R2
 * @returns New array with `<span class="character-link">` injected
 */
export function injectCharacterLinks(
  htmlParagraphs: string[],
  charConfig: CharacterConfig,
): string[] {
  if (!charConfig || Object.keys(charConfig).length === 0) return htmlParagraphs;

  const activated = new Set<string>();

  return htmlParagraphs.map((html) => {
    let updated = html;

    for (const [charId, config] of Object.entries(charConfig)) {
      if (activated.has(charId)) continue;

      // Sort aliases longest-first so "Arch-Hacker Yuki" matches before "Yuki"
      const sorted = [...config.aliases].sort((a, b) => b.length - a.length);

      for (const alias of sorted) {
        // Match the alias only when it's NOT inside an HTML tag.
        // We use a negative lookbehind for `<` and lookahead for `>`,
        // plus require word boundaries (English text).
        const pattern = `(?<![<\\w/])\\b(${escapeRegExp(alias)})\\b(?![^<]*>)`;
        const regex = new RegExp(pattern, 'i');

        if (regex.test(updated)) {
          const matched = updated.match(regex)![1];
          const replacement =
            `<span class="character-link" data-char-id="${charId}">👤 ${matched}</span>`;
          updated = updated.replace(regex, replacement);
          activated.add(charId);
          break; // Move to next character
        }
      }
    }
    return updated;
  });
}
