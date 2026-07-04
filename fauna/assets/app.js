/* Gemeinsamer App-Baustein für Fauna Mibaso:
   Service-Worker-Registrierung + „Neue Version"-Banner (mit iPhone/iPad-Failsafe).
   Einbinden mit:  <script src="…/assets/app.js" defer></script>  */
(function () {
  var css =
    '.fl-update-banner{position:fixed;top:0;left:0;right:0;background:#233D5C;color:#fff;' +
    'padding:max(50px,calc(env(safe-area-inset-top) + 6px)) 14px 8px;display:none;align-items:center;' +
    'justify-content:center;gap:12px;font-size:.92rem;font-family:Georgia,serif;z-index:9999;' +
    'box-shadow:0 2px 8px rgba(0,0,0,.18)}' +
    '.fl-update-banner.aktiv{display:flex;flex-wrap:wrap}' +
    '.fl-update-banner .fl-update-text{flex:1 1 auto;text-align:center;min-width:0}' +
    '.fl-update-banner button{background:#fff;color:#233D5C;border:none;padding:6px 14px;' +
    'border-radius:7px;font-family:inherit;font-size:inherit;font-weight:600;cursor:pointer;' +
    'white-space:nowrap;box-shadow:0 2px 4px rgba(0,0,0,.15)}';
  var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);

  if (!('serviceWorker' in navigator)) return;
  var refreshing = false;
  navigator.serviceWorker.addEventListener('controllerchange', function () {
    if (refreshing) return; refreshing = true; window.location.reload();
  });
  function zeigeBanner(reg) {
    var b = document.getElementById('fl-update-banner');
    if (!b) {
      b = document.createElement('div');
      b.id = 'fl-update-banner'; b.className = 'fl-update-banner';
      b.innerHTML = '<span class="fl-update-text">🦋 Neue Version verfügbar.</span>' +
                    '<button type="button">Jetzt aktualisieren</button>';
      document.body.appendChild(b);
      b.querySelector('button').addEventListener('click', function () {
        this.disabled = true; this.textContent = 'Aktualisiere …';
        if (reg.waiting) reg.waiting.postMessage({ type: 'SKIP_WAITING' });
        setTimeout(function () { if (!refreshing) { refreshing = true; window.location.reload(); } }, 1200);
      });
    }
    b.classList.add('aktiv');
  }
  window.addEventListener('load', function () {
    navigator.serviceWorker.register('/sw.js').then(function (reg) {
      if (reg.waiting && navigator.serviceWorker.controller) zeigeBanner(reg);
      reg.addEventListener('updatefound', function () {
        var neu = reg.installing; if (!neu) return;
        neu.addEventListener('statechange', function () {
          if (neu.state === 'installed' && navigator.serviceWorker.controller) zeigeBanner(reg);
        });
      });
      reg.update();
      document.addEventListener('visibilitychange', function () {
        if (document.visibilityState === 'visible') reg.update();
      });
      setInterval(function () { reg.update(); }, 60 * 60 * 1000);
    }).catch(function () {});
  });
})();
