/* bio Service Worker — network-first für Seiten (immer aktuell), SWR für Bilder.
   Die CACHE-Version wird bei jedem Deploy in deploy.yml frisch gestempelt. Der neue SW
   wartet (KEIN skipWaiting bei install) → die Seite zeigt das „Neue Version"-Banner
   (wie Flora/Fauna); erst der Klick „Jetzt aktualisieren" aktiviert ihn. */
const CACHE = "bio-cache-v1";
self.addEventListener("install", (e) => {});   /* nicht skipWaiting: neuer SW wartet aufs Banner */
self.addEventListener("activate", (e) => { e.waitUntil((async () => {
  const keys = await caches.keys();
  await Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)));
  await self.clients.claim();
})()); });
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
