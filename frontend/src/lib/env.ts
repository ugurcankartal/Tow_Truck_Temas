/** Ortam bazlı site/API adresleri (Vite PUBLIC_* değişkenleri). */

const DEFAULT_PROD_SITE = 'https://temasotoyolyardim.com';

export function normalizeSiteUrl(url: string): string {
  return url.replace(/\/$/, '');
}

export function getPublicSiteUrl(): string {
  const fromEnv = import.meta.env.PUBLIC_SITE_URL ?? import.meta.env.SITE_URL;
  return normalizeSiteUrl(fromEnv || DEFAULT_PROD_SITE);
}

export function getPublicApiUrl(): string {
  return normalizeSiteUrl(import.meta.env.PUBLIC_API_URL ?? 'http://127.0.0.1:8000');
}
