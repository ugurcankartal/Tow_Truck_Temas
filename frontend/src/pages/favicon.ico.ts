import type { APIRoute } from 'astro';
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

export const prerender = true;

const faviconSvg = readFileSync(
  resolve(dirname(fileURLToPath(import.meta.url)), '../../public/favicon.svg'),
);

export const GET: APIRoute = async () => {
  return new Response(faviconSvg, {
    status: 200,
    headers: {
      'Content-Type': 'image/svg+xml',
      'Cache-Control': 'public, max-age=86400',
    },
  });
};
