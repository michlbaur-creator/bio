/* bio Service Worker — network-first für Seiten (immer aktuell), SWR für Bilder.
   Kein „Neue Version"-Banner nötig: online lädt jede Seite frisch, offline aus dem Cache. */
const CACHE = "bio-cache-v1";
self.addEventListener("install", (e) => { self.skipWaiting(); });
self.addEventListener("activate", (e) => { e.waitUntil(self.clients.claim()); });
self.addEventListener("message", (e) => { if (e.data && e.data.type === "SKIP_WAITING") self.skipWaiting(); });
self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const accept = req.headers.get("accept") || "";
  const isPage = req.mode === "navigate" || accept.includes("text/html");
  if (isPage) {
    e.respondWith(
      fetch(req).then((res) => {
        const copy = res.clone(); caches.open(CACHE).then((c) => c.put(req, copy)); return res;
      }).catch(() => caches.match(req).then((r) => r || caches.match("/index.html")))
    );
  } else {
    e.respondWith(
      caches.match(req).then((cached) => {
        const net = fetch(req).then((res) => {
          const copy = res.clone(); caches.open(CACHE).then((c) => c.put(req, copy)); return res;
        }).catch(() => cached);
        return cached || net;
      })
    );
  }
});
