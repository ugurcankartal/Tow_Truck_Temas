import { bundleToUi, type LanguageInfo, type Locale, type UiMessages } from '@/i18n';
import { tr as fallbackTr } from '@/i18n';
import { getBuildApiUrl, getPublicApiUrl } from '@/lib/env';

const CLIENT_API_URL = getPublicApiUrl();
const BUILD_API_URL = getBuildApiUrl();

export function apiUrl(path: string): string {
  const base = CLIENT_API_URL.replace(/\/$/, '');
  const normalized = path.startsWith('/') ? path.slice(1) : path;
  return `${base}/api/v1/${normalized}`;
}

function buildApiUrl(path: string): string {
  const base = BUILD_API_URL.replace(/\/$/, '');
  const normalized = path.startsWith('/') ? path.slice(1) : path;
  return `${base}/api/v1/${normalized}`;
}

export interface I18nBundleResponse {
  language: string | null;
  strings: Record<string, string>;
}

const FALLBACK_LANGUAGES: LanguageInfo[] = [
  { id: 1, code: 'tr', name_native: 'Türkçe', flag_url: null, is_active: true, is_default: true, sort_order: 1 },
  { id: 2, code: 'en', name_native: 'English', flag_url: null, is_active: true, is_default: false, sort_order: 2 },
];

export async function getLanguages(): Promise<LanguageInfo[]> {
  try {
    const res = await fetch(buildApiUrl('languages/'), {
      headers: { Accept: 'application/json' },
      cache: import.meta.env.DEV ? 'no-store' : 'default',
    });
    if (!res.ok) throw new Error(`API ${res.status}`);
    return (await res.json()) as LanguageInfo[];
  } catch {
    return FALLBACK_LANGUAGES;
  }
}

export async function getUiBundle(locale: string): Promise<{ locale: Locale; ui: UiMessages }> {
  try {
    const res = await fetch(buildApiUrl(`bundle/?lang=${locale}`), {
      headers: { Accept: 'application/json' },
      cache: import.meta.env.DEV ? 'no-store' : 'default',
    });
    if (!res.ok) throw new Error(`API ${res.status}`);
    const data = (await res.json()) as I18nBundleResponse;
    const resolved = (data.language ?? locale) as Locale;
    if (Object.keys(data.strings).length > 0) {
      return { locale: resolved, ui: bundleToUi(data.strings, fallbackTr) };
    }
  } catch {
    const { getUi } = await import('@/i18n');
    return { locale: locale as Locale, ui: getUi(locale) };
  }
  const { getUi } = await import('@/i18n');
  return { locale: locale as Locale, ui: getUi(locale) };
}

export function getDefaultLanguageCode(languages: LanguageInfo[]): Locale {
  return (languages.find((l) => l.is_default)?.code ?? languages[0]?.code ?? 'tr') as Locale;
}
