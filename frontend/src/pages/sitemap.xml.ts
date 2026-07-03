import type { APIRoute } from 'astro';

import { getPublicApiUrl } from '@/lib/env';

const API_URL = getPublicApiUrl();

/** Static build: rebuild sırasında API'den alınır. Dev: text/plain ile XML kaynağı görünür. */
export const prerender = process.env.ASTRO_OUTPUT !== 'server';

function emptySitemapXml(): string {
  return [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
    '        xmlns:xhtml="http://www.w3.org/1999/xhtml">',
    '</urlset>',
    '',
  ].join('\n');
}

function sitemapContentType(): string {
  // Dev: tarayıcıda etiketlerle birlikte ham XML görünsün (request.headers kullanılmaz).
  // Build: dist/sitemap.xml dosyası yalnızca gövdeyi yazar; prod MIME .xml uzantısından gelir.
  return import.meta.env.DEV
    ? 'text/plain; charset=utf-8'
    : 'application/xml; charset=utf-8';
}

export const GET: APIRoute = async () => {
  try {
    const upstream = await fetch(`${API_URL}/api/v1/sitemap.xml`, {
      headers: { Accept: 'application/xml,text/xml;q=0.9,*/*;q=0.8' },
    });
    if (!upstream.ok) {
      throw new Error(`upstream ${upstream.status}`);
    }
    const text = await upstream.text();
    return new Response(text, {
      status: 200,
      headers: {
        'Content-Type': sitemapContentType(),
        'Cache-Control': 'public, max-age=300, must-revalidate',
        'X-Content-Type-Options': 'nosniff',
      },
    });
  } catch {
    return new Response(emptySitemapXml(), {
      status: 503,
      headers: {
        'Content-Type': sitemapContentType(),
        'X-Content-Type-Options': 'nosniff',
      },
    });
  }
};
