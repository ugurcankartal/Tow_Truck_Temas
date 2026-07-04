import type { APIRoute } from 'astro';

import { getBuildApiUrl } from '@/lib/env';

const API_URL = getBuildApiUrl();

/** SSR: her istekte API; static build: rebuild sırasında API'den alınır. */
export const prerender = process.env.ASTRO_OUTPUT !== 'server';

async function fetchFromApi(path: string): Promise<Response> {
  const upstream = await fetch(`${API_URL}${path}`, {
    headers: { Accept: 'text/plain' },
  });
  if (!upstream.ok) {
    throw new Error(`upstream ${upstream.status}`);
  }
  const text = await upstream.text();
  return new Response(text, {
    status: 200,
    headers: {
      'Content-Type': 'text/plain; charset=utf-8',
      'Cache-Control': 'public, max-age=300, must-revalidate',
    },
  });
}

export const GET: APIRoute = async () => {
  try {
    return await fetchFromApi('/api/v1/robots.txt');
  } catch {
    return new Response('User-agent: *\nDisallow: /\n', {
      status: 503,
      headers: { 'Content-Type': 'text/plain; charset=utf-8' },
    });
  }
};
