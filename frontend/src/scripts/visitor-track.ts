const analyticsPixelEndpoint = '/api/v1/analytics/visit/pixel.gif';

function recordVisit() {
  if (typeof window === 'undefined' || window.__visitTracked) return;
  window.__visitTracked = true;

  const params = new URLSearchParams({
    path: window.location.pathname + window.location.search,
    full_url: window.location.href,
    referrer: document.referrer || '',
    screen_width: String(window.screen?.width ?? ''),
    screen_height: String(window.screen?.height ?? ''),
    viewport_width: String(window.innerWidth ?? ''),
    viewport_height: String(window.innerHeight ?? ''),
  });

  const img = new Image();
  img.decoding = 'async';
  img.src = `${analyticsPixelEndpoint}?${params.toString()}`;
}

recordVisit();
document.addEventListener('astro:page-load', recordVisit);

declare global {
  interface Window {
    __visitTracked?: boolean;
  }
}

export {};
