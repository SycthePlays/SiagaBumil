// Service worker: keeps a copy of the site's own files so the page opens
// with no internet after the first visit. It only handles this site's files.

const CACHE = "sigapbumil-v1";
const FILES = [
  "./", "index.html", "style.css", "app.js", "inference.js", "model.json", "results.json",
  "img/favicon.svg", "img/confusion_m1_triage.png", "img/threshold_curve.png",
];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(FILES)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (event) => event.waitUntil(self.clients.claim()));

// Cache first (fast, works offline). When online, the copy is refreshed in
// the background, so the next visit gets the newest version.
self.addEventListener("fetch", (event) => {
  const sameSite = new URL(event.request.url).origin === location.origin;
  if (event.request.method !== "GET" || !sameSite) return;
  event.respondWith(
    caches.open(CACHE).then(async (cache) => {
      const cached = await cache.match(event.request);
      const fresh = fetch(event.request)
        .then((response) => {
          if (response.ok) cache.put(event.request, response.clone());
          return response;
        })
        .catch(() => cached);
      return cached || fresh;
    })
  );
});
