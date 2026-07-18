# Design — Novel Vault (lyriq.space)

A locked design system for this app. Every page redesign reads this file before
emitting code. Do not regenerate per page — extend or amend this file when the
system needs to grow.

## Genre

**Playful** (post-Linear soft school). Target audience: Western Gen-Z women,
BookTok / Coquette / Dark Academia TikTok aesthetic. Warm, human, tactile —
not the cold SaaS-developer minimalism, not the formal-library solemnity.

## Macrostructure family

- Catalog pages (`/`, `/tag/[tag]`): **Bento Grid** — Pinterest-style
  multi-column card grid, not a single-column vertical list. Hero is a
  typographic marquee strip (book titles scrolling) above the grid.
- Book detail (`/novel/[slug]`): **Long Document** — editorial serif headline,
  elegant chapter list, generous measure.
- Reader (`/novel/[slug]/[chapterId]`): existing structure preserved — only
  tokens + typography swap. Reading experience is already sound.

## Theme

Custom OKLCH palette anchored on BookTok berry/wine tones.

| Token | Value | Use |
|---|---|---|
| `--color-paper` | `oklch(97% 0.012 60)` | main bg — warm cream |
| `--color-paper-2` | `oklch(94% 0.018 55)` | card surface |
| `--color-paper-3` | `oklch(91% 0.020 50)` | hover surface |
| `--color-ink` | `oklch(28% 0.020 50)` | body text — warm brown-black |
| `--color-ink-2` | `oklch(45% 0.025 50)` | secondary text |
| `--color-ink-3` | `oklch(62% 0.020 50)` | muted text |
| `--color-rule` | `oklch(88% 0.015 55)` | dividers, borders |
| `--color-accent` | `oklch(56% 0.150 350)` | berry/wine — BookTok signature |
| `--color-accent-2` | `oklch(68% 0.110 25)` | warm coral — hover/secondary CTA |
| `--color-accent-soft` | `oklch(56% 0.150 350 / 12%)` | accent tint bg |
| `--color-focus` | `oklch(56% 0.150 350)` | focus ring |

Dark mode overrides:

| Token | Value |
|---|---|
| `--color-paper` | `oklch(18% 0.015 55)` |
| `--color-paper-2` | `oklch(22% 0.018 55)` |
| `--color-paper-3` | `oklch(26% 0.020 55)` |
| `--color-ink` | `oklch(90% 0.012 60)` |
| `--color-ink-2` | `oklch(72% 0.015 55)` |
| `--color-ink-3` | `oklch(55% 0.012 50)` |
| `--color-rule` | `oklch(30% 0.015 55)` |
| `--color-accent` | `oklch(72% 0.135 350)` |
| `--color-accent-2` | `oklch(78% 0.100 25)` |

## Typography

- **Display:** Fraunces (variable serif, free Google Fonts). Weight 400-600.
  Has SOFT axis for warmth — tuned to 50. Used for: site logo, book titles,
  reader h1, section heads in Long Document pages.
- **Body:** Plus Jakarta Sans (warm humanist sans). Weight 400/500/600.
  Used for: card body, nav, UI labels, reader prose.
- **Label:** Plus Jakarta Sans uppercase + `letter-spacing: 0.06em`. No
  separate mono family — keep the system to two faces.
- Display tracking: `-0.01em` for large sizes, `0` for small.
- Type scale anchor: `--text-display: clamp(2rem, 5vw, 3.5rem)`.

## Spacing

4-point named scale. Pages must use named tokens (`var(--space-md)`), never
raw values.

```
--space-3xs: 0.25rem;  --space-2xs: 0.5rem;  --space-xs: 0.75rem;
--space-sm:  1rem;     --space-md:  1.5rem;  --space-lg: 2rem;
--space-xl:  3rem;     --space-2xl: 4.5rem;  --space-3xl: 7rem;
```

## Motion

- Easings: `--ease-out: cubic-bezier(0.16, 1, 0.3, 1)` (exponential ease-out).
  Never browser default `ease`. Never bounce/overshoot on UI state.
- Durations: `--dur-short: 180ms`, `--dur-med: 320ms`, `--dur-long: 500ms`.
- Reveal pattern: card stagger fade-up on first load only (home page).
  No scroll-triggered fades on other pages. Content just *is there*.
- Reduced-motion fallback: `@media (prefers-reduced-motion: reduce)` — all
  animations become opacity-only ≤150ms, all transitions become 0.01ms.
- Animate `transform` and `opacity` only. Never layout properties.

## Microinteractions stance

- **Silent success.** Shelf add/remove, bookmark toggle → no celebratory toast.
  The button's own state change IS the feedback.
- **Hover:** card lifts `translateY(-2px)` + shadow deepens. Never `scale`.
- **Focus:** instant `outline: 2px solid var(--color-focus)` + `outline-offset: 2px`.
  Never animate the focus ring. Never use `transform: scale` on focus.
- **Transitions:** explicit properties, never `transition: all`. Pattern:
  `transition: background-color var(--dur-short) var(--ease-out), border-color var(--dur-short) var(--ease-out)`.
- **Tooltip** (if added): hover delay 800ms, focus delay 0ms.

## CTA voice

- **Primary CTA:** berry fill (`var(--color-accent)`), cream text
  (`var(--color-paper)`), `border-radius: 999px` (pill), `padding: var(--space-xs) var(--space-md)`.
  Copy: verb-led, ≤ 3 words. ("Start reading", "Add to shelf".)
- **Secondary CTA:** transparent bg, `1px solid var(--color-accent)`, berry text,
  `border-radius: 8px`. Same padding.
- **Tertiary / tags:** transparent, `1px solid var(--color-rule)`, ink-2 text,
  `border-radius: 999px`. Hover: berry border + berry text.

## Category buttons

**No emoji.** Pure text labels. Active state: berry tint bg + berry text + berry
border. A `::before` color dot (8px circle in `var(--color-accent)`) precedes
the active category label as the only chromatic signal.

## Book covers

CSS-only, no images. Dual-tone linear gradient: `135deg, var(--color-accent-soft),
var(--color-paper-3)`. First letter of title in Fraunces italic, `var(--color-accent)`,
centered. Dark mode: gradient darkens, letter stays berry.

## Per-page allowances

- Catalog pages MAY use a typographic marquee hero (book titles scrolling).
  No photographic enrichment, no illustrations.
- Detail page: typography only. No hero image.
- Reader page: typography only. No enrichment of any kind.

## What pages MUST share

- The wordmark / logotype: "NOVEL VAULT" in Fraunces, berry, with the leading
  "N" in ink (bold weight) — the split-letter logo pattern.
- The accent colour (berry) and its placement (≤ 5% per viewport).
- Fraunces (display) + Plus Jakarta Sans (body) across every page.
- The CTA voice (pill shape, berry fill, verb-led copy).
- Section heading rhythm: small uppercase label + serif display heading,
  stacked vertically (never tag-left/heading-right two-column).

## What pages MAY differ on

- Catalog vs detail: Bento Grid vs Long Document macrostructure.
- Card density: home grid can be 2-col on desktop; tag page can stay 1-col
  for narrower result sets.
- Chapter list presentation on detail page (inline list vs numbered).

## Anti-patterns to NOT carry over (from audit)

- `transition: all` — banned. Always explicit properties.
- `transform: scale()` on `:focus-visible` — banned. Instant outline only.
- Emoji as category icons — banned. Pure text + color dot.
- Missing `prefers-reduced-motion` — banned. Every animation needs a fallback.
- `border-left: 3px` side-stripe on `.chapter-teaser` — replace with full
  hairline border + berry left accent via `::before` bar (1px, not 3px).
- `:focus` (old) selectors — replace with `:focus-visible` only.

## Exports

### tokens.css

Lives at `src/styles/global.css` (the project's entry stylesheet). All tokens
declared in `:root`. Dark mode overrides in `body.dark-mode`. Pages reference
tokens by name, never inline raw values.

## Provenance

Created 2026-07-18 via `hallmark redesign` multi-page flow. Source: user's own
site (lyriq.space). Mood: Western Gen-Z women / BookTok aesthetic. System
locked — subsequent runs defer to this file; diversification inverted to
consistency.
