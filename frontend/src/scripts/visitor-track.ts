const analyticsEndpoint = '/api/v1/analytics/visit/';

function recordVisit() {
  if (typeof window === 'undefined' || window.__visitTracked) return;
  window.__visitTracked = true;

  const payload = {
    path: window.location.pathname + window.location.search,
    full_url: window.location.href,
    referrer: document.referrer || '',
    screen_width: window.screen?.width ?? null,
    screen_height: window.screen?.height ?? null,
    viewport_width: window.innerWidth ?? null,
    viewport_height: window.innerHeight ?? null,
  };

  const body = JSON.stringify(payload);

  if (navigator.sendBeacon) {
    const blob = new Blob([body], { type: 'application/json' });
    if (navigator.sendBeacon(analyticsEndpoint, blob)) return;
  }

  fetch(analyticsEndpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body,
    keepalive: true,
    credentials: 'same-origin',
  }).catch(() => {});
}

recordVisit();
document.addEventListener('astro:page-load', recordVisit);

declare global {
  interface Window {
    __visitTracked?: boolean;
  }
}

export {};
