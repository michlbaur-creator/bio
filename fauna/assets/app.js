/* Gemeinsamer App-Baustein für Fauna Mibaso:
   1. GoatCounter (anonyme, cookiefreie Besucherzählung)
   2. Service-Worker-Registrierung + vollautomatische Aktualisierung.
   Die App prüft beim Öffnen, bei Rückkehr zur App und alle 3 Minuten,
   ob eine neue Version vorliegt (der Browser lädt sw.js dabei am
   Zwischenspeicher vorbei). Eine neue Version wird sofort übernommen
   und die Seite einmal sanft neu geladen — ohne Knopf, ohne Banner.
   Einbinden mit:  <script src="…/assets/app.js" defer></script>  */
(function () {
  // 1) GoatCounter: anonyme, cookiefreie Besucherzählung.
  //    Gezählt wird der Pfad mit Adresse, z. B. „fauna.mibaso.de/arten/amsel.html“.
  if (!window.__mibasoZaehler) {
    window.__mibasoZaehler = true;
    window.goatcounter = { path: function (p) { return location.host + p } };
    var gc = document.createElement('script');
    gc.async = true;
    gc.src = '//gc.zgo.at/count.js';
    gc.setAttribute('data-goatcounter', 'https://mibaso.goatcounter.com/count');
    document.head.appendChild(gc);
  }

  // 2) Service-Worker registrieren + automatisch aktualisieren
  if (!('serviceWorker' in navigator)) return;

  // Wenn der neue Service Worker übernimmt: Seite einmal neu laden.
  var refreshing = false;
  navigator.serviceWorker.addEventListener('controllerchange', function () {
    if (refreshing) return; refreshing = true; window.location.reload();
  });

  // Wartet eine neue Version? Dann sofort aktivieren (löst controllerchange aus).
  function uebernehmen(reg) {
    if (reg && reg.waiting && navigator.serviceWorker.controller) {
      reg.waiting.postMessage({ type: 'SKIP_WAITING' });
      // Failsafe (iPhone/iPad): falls controllerchange ausbleibt, trotzdem neu laden.
      setTimeout(function () { if (!refreshing) { refreshing = true; window.location.reload(); } }, 1500);
    }
  }

  window.addEventListener('load', function () {
    navigator.serviceWorker.register('/sw.js').then(function (reg) {
      uebernehmen(reg);
      reg.addEventListener('updatefound', function () {
        var neu = reg.installing; if (!neu) return;
        neu.addEventListener('statechange', function () {
          if (neu.state === 'installed') uebernehmen(reg);
        });
      });
      // Nach Neuigkeiten schauen: jetzt, bei Rückkehr zur App und alle 3 Minuten.
      reg.update();
      document.addEventListener('visibilitychange', function () {
        if (document.visibilityState === 'visible') reg.update();
      });
      setInterval(function () { reg.update(); }, 3 * 60 * 1000);
    }).catch(function () {});
  });
})();
