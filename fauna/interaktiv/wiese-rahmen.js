/* Gemeinsamer Rahmen für die sieben Stationen des Wiesenpasses (Expedition Wiese).
   Macht aus den einzelnen Stationsseiten dieselbe Bauform wie in den anderen Pässen:
     – feste Kopfzeile mit Rückweg in den Pass und Blätter-Zähler
     – Zeile „Expedition Wiese · Station x von 7 · ca. n Min“
     – Merke-Kasten (wieseMerke) im Stil der anderen Pässe
   Einbinden im Seitenkopf, VOR dem Skript der Station:
     <script src="wiese-rahmen.js?v=1" data-station="grundlagen"></script>
   Der Fortschritt steht wie bisher in localStorage["mibaso.fauna.expedition"]. */
(function () {
  "use strict";
  var STATIONEN = [
    ["grundlagen", "Wem gehört die Wiese?", 10],
    ["verwandlung", "Wie wird man Insekt?", 12],
    ["bestaeubung", "Wer bestäubt wen?", 12],
    ["lebensraum", "Wo wohnen Insekten?", 8],
    ["nahrungsnetz", "Wer frisst wen?", 10],
    ["wiese", "Wie hängt alles zusammen?", 10],
    ["boden", "Was wir nicht sehen", 10]
  ];
  var KEY = "mibaso.fauna.expedition", MAX = STATIONEN.length * 3;
  var ich = document.currentScript ? document.currentScript.getAttribute("data-station") : "";
  var nr = STATIONEN.map(function (s) { return s[0]; }).indexOf(ich);

  var css = document.createElement("style");
  css.textContent =
    ".w-subkopf{position:sticky;top:0;z-index:6;background:#F7F3E8;border-bottom:1px solid #d9d2c1;" +
      "padding:calc(env(safe-area-inset-top,0px) + 8px) max(16px,env(safe-area-inset-right,0px)) 8px max(16px,env(safe-area-inset-left,0px));}" +
    ".w-subkopf .row{max-width:720px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;gap:10px;}" +
    ".w-subkopf a{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;font-size:15px;font-weight:normal;text-decoration:none;color:#233D5C;padding:6px 4px;}" +
    ".w-chip{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;font-size:14px;background:#fff;border:1px solid #d9d2c1;border-radius:999px;padding:5px 12px;color:#233D5C;font-variant-numeric:tabular-nums;white-space:nowrap;}" +
    "body.w-rahmen{padding-top:0!important;}" +
    "body.w-rahmen .huelle>.kopf{justify-content:flex-start;flex-wrap:wrap;gap:2px 8px;margin-top:10px;}" +
    ".w-eb,body.w-rahmen .huelle>.kopf .zaehler{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:#5d6b78;}" +
    "body.w-rahmen .huelle>.kopf .zaehler:not(:empty)::before{content:'· ';}" +
    ".merke{border:1.5px dashed #33587c;border-radius:12px;padding:14px 16px;display:grid;gap:8px;background:#f8fbfd;text-align:left;margin:12px 0;font-size:17px;line-height:1.5;color:#1c2e42;}" +
    ".merke p{margin:0;}" +
    ".merke b{color:#233D5C;}" +
    ".merke .merke-eb{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#233D5C;}" +
    ".merke-weiter{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;font-size:14px;color:#5d6b78;text-align:center;margin:10px 0 0;}";
  document.head.appendChild(css);

  /* Merke-Kasten: s = { titel, punkte:[…], weiter } */
  window.wieseMerke = function (s) {
    return (s.titel ? "<h2>" + s.titel + "</h2>" : "") +
      '<div class="merke"><span class="merke-eb">Merke</span>' +
      s.punkte.map(function (p) { return "<p>" + p + "</p>"; }).join("") + "</div>" +
      (s.weiter ? '<p class="merke-weiter">' + s.weiter + "</p>" : "");
  };

  function summe() {
    var d = {}, n = 0;
    try { d = JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) {}
    STATIONEN.forEach(function (s) { var e = d[s[0]]; if (e && e.done) n += Math.max(0, Math.min(3, e.blaetter || 0)); });
    return n;
  }

  function aufbauen() {
    var huelle = document.querySelector(".huelle"), kopf = huelle && huelle.querySelector(".kopf");
    if (!huelle || !kopf || nr < 0) return;
    document.body.classList.add("w-rahmen");
    var bar = document.createElement("div");
    bar.className = "w-subkopf";
    bar.innerHTML = '<div class="row"><a href="wiesenpass.html">‹ Wiesenpass</a><span class="w-chip" id="wChip"></span></div>';
    huelle.parentNode.insertBefore(bar, huelle);
    var alt = kopf.querySelector("a.zurueck"); if (alt) alt.remove();
    var eb = document.createElement("span");
    eb.className = "w-eb";
    eb.textContent = "Station " + (nr + 1) + " von " + STATIONEN.length + " · ca. " + STATIONEN[nr][2] + " Min";
    kopf.insertBefore(eb, kopf.firstChild);
    var chip = document.getElementById("wChip"), letzte = -1;
    function zeige() { var n = summe(); if (n !== letzte) { letzte = n; chip.textContent = "🍃 " + n + " / " + MAX; } }
    zeige(); setInterval(zeige, 1500);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", aufbauen); else aufbauen();
})();
