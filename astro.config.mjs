import { defineConfig } from 'astro/config';
import cloudflare from '@astrojs/cloudflare';
import node from '@astrojs/node';
import vue from '@astrojs/vue';
import sitemap from '@astrojs/sitemap';

// Use Node adapter for local dev/build (Node 24 incompatible with miniflare)
// Cloudflare adapter is used in CI (Node 22) via CF_PAGES=true
const isCF = process.env.CF_PAGES === '1' || process.env.CF_PAGES === 'true';

export default defineConfig({
  output: 'server',
  adapter: isCF
    ? cloudflare({
        platformProxy: { enabled: false },
      })
    : node({ mode: 'standalone' }),
  site: 'https://lyriq.space',
  integrations: [
    vue(),
    sitemap({
      filter: (page) => !page.includes('/api/'),
    }),
  ],
  trailingSlash: 'never',
});
