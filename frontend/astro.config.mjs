import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import node from '@astrojs/node';

/**
 * ASTRO_OUTPUT=server  → SSR (prod'da her istekte API'den SEO)
 * ASTRO_OUTPUT=static  → SSG (varsayılan, webhook rebuild ile güncellenir)
 *
 * robots.txt ve sitemap.xml Django API'den gelir (src/pages/*.ts proxy).
 *
 * Üretim domain: frontend/.env.production (temasotoyolyardim.com)
 */
const isSSR = process.env.ASTRO_OUTPUT === 'server';
const siteUrl =
  process.env.SITE_URL ||
  process.env.PUBLIC_SITE_URL ||
  'http://localhost:4321';

export default defineConfig({
  site: siteUrl,
  output: isSSR ? 'server' : 'static',
  adapter: isSSR ? node({ mode: 'standalone' }) : undefined,
  vite: {
    plugins: [tailwindcss()],
  },
});
