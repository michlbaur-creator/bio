/* Gemeinsamer Rahmen für die Stationen von Pflanzenpass (Expedition Wiese · Pflanzen)
   und Waldpass (Expedition Wald). Gegenstück zu fauna/interaktiv/wiese-rahmen.js:
     – feste Kopfzeile mit Rückweg in den Pass und Blätter-Zähler
     – Zeile „Station x von n · ca. m Min“
     – Merke-Kasten (wieseMerke) im Stil der anderen Pässe
     – bei den älteren Stationen ohne eigene Fußzeile: Merke-Kasten und Fußzeile am Seitenende
   Einbinden im Seitenkopf, VOR dem Skript der Station:
     <script src="flora-rahmen.js?v=1" data-pass="wald" data-station="stockwerke"></script>
   Ältere Stationen geben ihren Merke-Text so mit:
     <script>window.FLORA_MERKE = ["…", "…"];</script>
   Läuft die Seite eingebettet in einer anderen (iframe), bleibt sie unverändert. */
(function () {
  "use strict";
  var PAESSE = {
    pflanze: { key: "mibaso.flora.expedition", href: "../pflanzenpass.html", name: "Pflanzenpass", st: [
      ["aufbau", 10], ["bestaeubung", 10], ["reise", 12], ["jahr", 8], ["strategien", 8], ["energie", 12]] },
    wald: { key: "mibaso.flora.wald", href: "../waldpass.html", name: "Waldpass", st: [
      ["stockwerke", 10], ["jahreslauf", 8], ["erkennen", 10], ["baeume", 10], ["fruehblueher", 10], ["waldboden", 10], ["eindringlinge", 10], ["nutzen", 10]] }
  };
  var tag = document.currentScript, P = PAESSE[tag ? tag.getAttribute("data-pass") : ""], ich = tag ? tag.getAttribute("data-station") : "";
  var SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif";

  var css = document.createElement("style");
  css.textContent =
    ".w-subkopf{position:sticky;top:0;z-index:6;background:#F7F3E8;border-bottom:1px solid #d9d2c1;" +
      "padding:calc(env(safe-area-inset-top,0px) + 8px) max(16px,env(safe-area-inset-right,0px)) 8px max(16px,env(safe-area-inset-left,0px));}" +
    ".w-subkopf .row{max-width:720px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;gap:10px;}" +
    ".w-subkopf a{font-family:" + SANS + ";font-size:15px;font-weight:normal;text-decoration:none;color:#2F4F3E;padding:6px 4px;}" +
    ".w-chip{font-family:" + SANS + ";font-size:14px;background:#fff;border:1px solid #d9d2c1;border-radius:999px;padding:5px 12px;color:#2F4F3E;font-variant-numeric:tabular-nums;white-space:nowrap;}" +
    "body.w-rahmen{padding-top:0!important;}" +
    "body.w-rahmen .huelle>.kopf{justify-content:flex-start;flex-wrap:wrap;gap:2px 8px;margin-top:10px;}" +
    ".w-eb,body.w-rahmen .huelle>.kopf .zaehler{font-family:" + SANS + ";font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:#5d6b78;}" +
    "body.w-rahmen .huelle>.kopf .zaehler:not(:empty)::before{content:'· ';}" +
    ".w-eb-zeile{max-width:760px;margin:10px auto 0;padding:0 16px;}" +
    ".merke{border:1.5px dashed #3f6b54;border-radius:12px;padding:14px 16px;display:grid;gap:8px;background:#f6faf6;text-align:left;margin:12px 0;font-family:Georgia,'Times New Roman',serif;font-size:17px;line-height:1.5;color:#1f3328;}" +
    ".merke p{margin:0;}" +
    ".merke b{color:#2F4F3E;}" +
    ".merke .merke-eb{font-family:" + SANS + ";font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#2F4F3E;}" +
    ".merke-weiter{font-family:" + SANS + ";font-size:14px;color:#5d6b78;text-align:center;margin:10px 0 0;}" +
    ".w-ende{max-width:760px;margin:18px auto 0;padding:0 16px 28px;}" +
    ".w-ende h2{font-family:Georgia,'Times New Roman',serif;font-weight:normal;font-size:22px;color:#2F4F3E;margin:0 0 6px;}" +
    ".w-fuss{border-top:1px solid #d9d2c1;margin-top:22px;padding-top:14px;text-align:center;font-family:" + SANS + ";font-size:13px;color:#5d6b78;line-height:1.7;}" +
    ".w-fuss a{color:#2F4F3E;}";
  document.head.appendChild(css);

  /* Merke-Kasten: s = { titel, punkte:[…], weiter } */
  window.wieseMerke = function (s) {
    return (s.titel ? "<h2>" + s.titel + "</h2>" : "") +
      '<div class="merke"><span class="merke-eb">Merke</span>' +
      s.punkte.map(function (p) { return "<p>" + p + "</p>"; }).join("") + "</div>" +
      (s.weiter ? '<p class="merke-weiter">' + s.weiter + "</p>" : "");
  };

  if (!P) return;
  var ids = P.st.map(function (s) { return s[0]; }), nr = ids.indexOf(ich), MAX = P.st.length * 3;
  var eingebettet = false; try { eingebettet = window.self !== window.top; } catch (e) { eingebettet = true; }

  function summe() {
    var d = {}, n = 0;
    try { d = JSON.parse(localStorage.getItem(P.key) || "{}") || {}; } catch (e) {}
    ids.forEach(function (id) { var e = d[id]; if (e && e.done) n += Math.max(0, Math.min(3, e.blaetter || 0)); });
    return n;
  }
  var FUSS = '<a href="' + P.href + '" style="font-weight:600">🍃 ' + P.name + '</a> · © 2026 <a href="../../ueber/">Michael Baur</a> · Bio Mibaso · <a href="../../impressum/">Impressum &amp; Datenschutz</a>';

  function aufbauen() {
    if (nr < 0 || eingebettet || document.body.classList.contains("eingebettet")) return;
    document.body.classList.add("w-rahmen");
    var bar = document.createElement("div");
    bar.className = "w-subkopf";
    bar.innerHTML = '<div class="row"><a href="' + P.href + '">‹ ' + P.name + '</a><span class="w-chip" id="wChip"></span></div>';
    var ebText = "Station " + (nr + 1) + " von " + P.st.length + " · ca. " + P.st[nr][1] + " Min";
    var eb = document.createElement("span"); eb.className = "w-eb"; eb.textContent = ebText;
    var huelle = document.querySelector(".huelle"), kopf = huelle && huelle.querySelector(".kopf");
    if (kopf) {                      // neuere Stationen mit eigener Kopfzeile und Fußzeile
      huelle.parentNode.insertBefore(bar, huelle);
      var alt = kopf.querySelector("a.zurueck"); if (alt) alt.remove();
      kopf.insertBefore(eb, kopf.firstChild);
      var f = huelle.querySelector("footer"); if (f) { f.className = "w-fuss"; f.innerHTML = FUSS; }
    } else {                         // ältere Stationen: Rücklink ersetzen, Merke und Fußzeile ans Ende
      var back = document.querySelector("a.back");
      var anker = back || document.body.firstChild;
      anker.parentNode.insertBefore(bar, anker);
      var z = document.createElement("div"); z.className = "w-eb-zeile"; z.appendChild(eb);
      anker.parentNode.insertBefore(z, anker);
      if (back) back.remove();
      var ende = document.createElement("div"); ende.className = "w-ende";
      ende.innerHTML = (window.FLORA_MERKE ? window.wieseMerke({ titel: "Das Wichtigste auf einen Blick", punkte: window.FLORA_MERKE }) : "") + '<div class="w-fuss">' + FUSS + "</div>";
      var erstes = document.body.querySelector("script[src*='app.js']");
      document.body.insertBefore(ende, erstes || null);
    }
    var chip = document.getElementById("wChip"), letzte = -1;
    function zeige() { var n = summe(); if (n !== letzte) { letzte = n; chip.textContent = "🍃 " + n + " / " + MAX; } }
    zeige(); setInterval(zeige, 1500);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", aufbauen); else aufbauen();
})();
