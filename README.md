# Arcana — Dark Academia Novel Reader

A moody, mobile-first novel browsing and reading interface. Dark academia aesthetic with a focus on typography and reading comfort.

## Features

- **Dark Academia UI** — Deep navy backgrounds, gold accents, elegant serif typography
- **Mobile-First** — 2-column card grid on phones, smooth transitions, thumb-friendly tap targets
- **Instant Search** — Filter by title or author as you type
- **Category Browsing** — Fantasy, Sci-Fi, Mystery, Literary, Horror
- **Built-in Reader** — Chapter navigation, prev/next, comfortable body typography
- **Zero Dependencies** — Pure HTML + CSS + JS, no framework or build step

## Deploy to Cloudflare Pages

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com/) → **Pages**
2. Click **Connect to Git** → select `andy-develop/arcana-novel-reader`
3. **Build settings:**
   - Build command: *(leave empty — static site)*
   - Build output directory: `/` *(or leave default `/`)*
4. Click **Save and Deploy**

## Local Development

```bash
cd arcana-novel-reader
python3 -m http.server 8080
# Open http://localhost:8080
```

## Adding Novels

Edit `app.js` — add entries to the `novels` array:

```js
{id:13, title:'Your Novel', author:'Author Name', cover:'Y', category:'Fantasy', chapters:20}
```

Add chapter content to `sampleContent`:

```js
'Chapter VI': 'The story continues...'
```

## License
MIT