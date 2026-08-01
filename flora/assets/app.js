/* Gemeinsamer App-Baustein für alle Seiten von Flora Mibaso.
   Bündelt, was früher in jede Seite einzeln kopiert war:
     1. GoatCounter (anonyme, cookiefreie Reichweiten-Statistik)
     2. Service-Worker-Registrierung + vollautomatische Aktualisierung
   Die App prüft beim Öffnen, bei Rückkehr zur App und alle 3 Minuten,
   ob eine neue Version vorliegt, übernimmt sie sofort und lädt die Seite
   einmal sanft neu — ohne Knopf, ohne Banner.
   Einbinden mit:  <script src="…/assets/app.js" defer></script>
*/
(function () {
  // 1) GoatCounter dynamisch laden
  var gc = document.createElement('script');
  gc.async = true;
  gc.src = '//gc.zgo.at/count.js';
  gc.setAttribute('data-goatcounter', 'https://mibaso.goatcounter.com/count');
  document.head.appendChild(gc);

  // 2) Service-Worker registrieren + automatisch aktualisieren
  if (!('serviceWorker' in navigator)) return;
  var refreshing = false;
  navigator.serviceWorker.addEventListener('controllerchange', function () {
    if (refreshing) return;
    refreshing = true;
    window.location.reload();
  });

  // Wartet eine neue Version? Dann sofort aktivieren (löst controllerchange aus).
  function uebernehmen(reg) {
    if (reg && reg.waiting && navigator.serviceWorker.controller) {
      reg.waiting.postMessage({ type: 'SKIP_WAITING' });
      // Failsafe für iPhone/iPad: dort feuert „controllerchange" im
      // installierten App-Modus oft nicht — darum nach kurzer Wartezeit
      // selbst neu laden.
      setTimeout(function () {
        if (!refreshing) { refreshing = true; window.location.reload(); }
      }, 1500);
    }
  }

  window.addEventListener('load', function () {
    navigator.serviceWorker.register('/sw.js').then(function (reg) {
      uebernehmen(reg);
      reg.addEventListener('updatefound', function () {
        var neu = reg.installing;
        if (!neu) return;
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

/* ── Sammelpass: lokal gespeicherte „gefundene" Arten (localStorage) ──
   Eigene Funktion, damit der return oben (kein Service-Worker) sie nicht überspringt. */
(function () {
  var KEY = 'flora-gefunden';
  function liste() { try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch (e) { return []; } }
  function speichere(a) { try { localStorage.setItem(KEY, JSON.stringify(a)); } catch (e) {} }
  function hat(slug) { return liste().indexOf(slug) >= 0; }
  function toggle(slug) {
    var a = liste(), i = a.indexOf(slug);
    if (i >= 0) a.splice(i, 1); else a.push(slug);
    speichere(a);
    return i < 0; // true = jetzt gefunden
  }
  function anzahl() { return liste().length; }

  // ── Belohnungs-Meilensteine ──
  var MEILENSTEINE = [5, 10, 20, 30, 50, 75, 100, 146];
  function istMeilenstein(n) { return MEILENSTEINE.indexOf(n) >= 0; }
  var SPRUCH = {
    5:   '🌱 5 Arten! Der Anfang ist gemacht.',
    10:  '🌿 10 Arten gesammelt — du hast den Bogen raus!',
    20:  '🍀 20 Arten! Eine echte Botanik-Spürnase.',
    30:  '🌼 30 Arten — die Wiese kennt dich schon.',
    50:  '🌳 50 Arten! Halbzeit-Held:in der heimischen Flora.',
    75:  '🏵️ 75 Arten — das ist schon richtig beeindruckend!',
    100: '🏅 100 Arten! Ein wandelndes Pflanzenlexikon.',
    146: '🏆 ALLE 146 Arten gefunden — Flora-Meister:in! Chapeau!'
  };
  function spruch(n) { return SPRUCH[n] || ('🎉 ' + n + ' Arten gefunden!'); }

  // Kurze Fanfare per WebAudio (ohne Audiodatei)
  function fanfare() {
    try {
      var Ctx = window.AudioContext || window.webkitAudioContext;
      if (!Ctx) return;
      var ctx = new Ctx();
      if (ctx.state === 'suspended') ctx.resume();
      var t0 = ctx.currentTime + 0.05;
      var noten = [[523.25, 0, .16, .2], [659.25, .15, .16, .2], [783.99, .3, .16, .2],
                   [1046.5, .46, .65, .22], [783.99, .46, .65, .12]];
      noten.forEach(function (x) {
        var o = ctx.createOscillator(), g = ctx.createGain();
        o.type = 'triangle'; o.frequency.value = x[0];
        g.gain.setValueAtTime(0, t0 + x[1]);
        g.gain.linearRampToValueAtTime(x[3], t0 + x[1] + 0.02);
        g.gain.exponentialRampToValueAtTime(0.001, t0 + x[1] + x[2]);
        o.connect(g).connect(ctx.destination);
        o.start(t0 + x[1]); o.stop(t0 + x[1] + x[2] + 0.05);
      });
      setTimeout(function () { ctx.close().catch(function () {}); }, 1800);
    } catch (e) {}
  }

  // Feuerwerk + Spruch als kurze Vollbild-Feier
  function feiere(n) {
    if (!document.getElementById('fl-feier-style')) {
      var st = document.createElement('style');
      st.id = 'fl-feier-style';
      st.textContent =
        '.fl-feier{position:fixed;inset:0;z-index:10000;display:flex;align-items:center;justify-content:center;overflow:hidden;cursor:pointer}' +
        '.fl-konf{position:absolute;top:-14px;border-radius:2px;animation:fl-fall linear forwards}' +
        '@keyframes fl-fall{0%{transform:translateY(-14px) rotate(0);opacity:1}85%{opacity:1}100%{transform:translateY(105vh) rotate(620deg);opacity:0}}' +
        '.fl-feier-msg{position:relative;z-index:2;max-width:88%;background:#fff;border:2px solid #3A5F4A;border-radius:16px;' +
        'padding:18px 22px;text-align:center;font-family:Georgia,serif;font-size:1.12rem;font-weight:700;color:#2F4F3E;' +
        'box-shadow:0 8px 30px rgba(0,0,0,.25);animation:fl-bounce .7s cubic-bezier(.36,.07,.19,.97) forwards}' +
        '.fl-feier-msg small{display:block;margin-top:6px;font-weight:400;font-size:.82rem;color:#6b5340;font-style:italic}' +
        '@keyframes fl-bounce{0%{transform:scale(.3)}55%{transform:scale(1.12)}75%{transform:scale(.94)}100%{transform:scale(1)}}';
      document.head.appendChild(st);
    }
    var farben = ['#3A5F4A','#5A8068','#f4c430','#e8a020','#c0392b','#e74c3c','#3498db','#9b59b6','#2ecc71'];
    var ov = document.createElement('div');
    ov.className = 'fl-feier';
    var html = '';
    for (var i = 0; i < 70; i++) {
      var c = farben[(Math.random() * farben.length) | 0];
      var left = (Math.random() * 98).toFixed(1);
      var delay = (Math.random() * 1.2).toFixed(2);
      var dur = (1.6 + Math.random() * 1.6).toFixed(2);
      var w = 6 + ((Math.random() * 7) | 0);
      var h = 6 + ((Math.random() * 7) | 0);
      html += '<span class="fl-konf" style="left:' + left + '%;width:' + w + 'px;height:' + h +
              'px;background:' + c + ';animation-delay:' + delay + 's;animation-duration:' + dur + 's"></span>';
    }
    html += '<div class="fl-feier-msg">' + spruch(n) + '<small>Tippen zum Schließen</small></div>';
    ov.innerHTML = html;
    document.body.appendChild(ov);
    fanfare();
    var weg = function () { if (ov.parentNode) ov.parentNode.removeChild(ov); };
    ov.addEventListener('click', weg);
    setTimeout(weg, 5000);
  }

  window.FloraSammel = {
    liste: liste, hat: hat, toggle: toggle, anzahl: anzahl,
    istMeilenstein: istMeilenstein, feiere: feiere
  };

  // Artenseiten: Verwechslungshinweise aus pflanzen.json (Markieren passiert nur im Bestimmungstool)
  document.addEventListener('DOMContentLoaded', function () {
    var slug = (location.pathname.split('/').pop() || '').replace(/\.html$/, '');
    var vw = document.getElementById('verwechslung');
    if (!slug || !vw) return;
    fetch('/pflanzen.json').then(function (r) { return r.json(); }).then(function (daten) {
      var name = {};
      daten.forEach(function (p) { name[p.slug] = p.deutsch; });
      var me = daten.filter(function (p) { return p.slug === slug; })[0];
      if (!me || !me.verwechslung || !me.verwechslung.length) return;
      var links = me.verwechslung
        .filter(function (s) { return name[s]; })
        .map(function (s) { return '<a href="' + s + '.html">' + name[s] + '</a>'; })
        .join(', ');
      if (!links) return;
      vw.innerHTML = '<h2>Leicht zu verwechseln mit</h2><p>' + links + '</p>';
      vw.hidden = false;
    }).catch(function () {});
  });
})();
