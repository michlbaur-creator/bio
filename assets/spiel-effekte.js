/* Bio Mibaso – gemeinsame Effekte für die Sammel-Spiele
   (Sammelflug, Pollenpost, Hähersaat, Wettlauf ums Licht, Kalte Kost, Nestwerk).

   Die Datei ändert nichts an den Spielregeln. Sie schaut nur zu, was das Spiel
   zeichnet, und legt Effekte darüber:
     1. Wind: Pflanzen und Bäume wiegen sich sanft.
     2. Licht: Morgenrot und Abendlicht liegen über dem ganzen Spielfeld.
     3. Abheben: Die Spielfigur hebt beim Flug kurz ab.
     4. Funken: Wenn etwas gesammelt wird, sprühen kleine Funken.
     5. Stern-Moment: Sobald ein Stern erreicht ist, leuchtet er auf, mit kurzer Meldung.
     6. Schlussbild: Die verdienten Sterne erscheinen nacheinander.

   Einbinden vor </body>:
     <script src="../../assets/spiel-effekte.js?v=1" defer></script>
   Optional: data-wind="aus" schaltet den Wind ab (z. B. Wettlauf ums Licht).
   Wer im Gerät „Bewegung reduzieren“ eingestellt hat, bekommt keine Effekte.
   Bei Änderungen die Nummer hinter ?v= in allen sechs Spielen erhöhen. */
(function () {
  "use strict";
  if (window.__mibasoSpielEffekte) return;
  window.__mibasoSpielEffekte = true;
  var ruhig = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (ruhig) return;

  var skript = document.currentScript;
  var windAn = !(skript && skript.getAttribute("data-wind") === "aus");
  var SVGNS = "http://www.w3.org/2000/svg";

  /* Felder, die sich nicht im Wind bewegen sollen (Anfang der Feldbeschreibung) */
  var STILL = ["Nest", "Dein Nest", "Gemäht", "Futterhaus", "Nistkasten", "Brotreste",
    "Pfütze", "Lehm", "Weg", "Hühnerhof", "Zaun", "Laubboden", "Waldboden", "Dein Feld", "Wiese,"];

  /* ---------- Aussehen ---------- */
  var css = document.createElement("style");
  css.textContent = [
    ".fx-wiegt{transform-box:fill-box;transform-origin:50% 100%;animation:fxWind 3.6s ease-in-out infinite alternate}",
    "@keyframes fxWind{from{rotate:-2.2deg}to{rotate:2.2deg}}",
    "#fxLicht{transition:opacity 1.2s ease,fill 1.2s ease;mix-blend-mode:multiply;pointer-events:none}",
    ".planrahmen{position:relative}",
    ".fx-meldung{position:absolute;left:50%;top:18%;transform:translate(-50%,0);z-index:5;background:#fffaf0;border:2px solid #e2b23a;",
    "border-radius:999px;padding:10px 22px;font:700 20px/1.2 -apple-system,Segoe UI,Helvetica,Arial,sans-serif;color:#7a5200;",
    "box-shadow:0 8px 26px rgba(0,0,0,.25);white-space:nowrap;pointer-events:none;animation:fxMeld 2.2s ease forwards}",
    "@keyframes fxMeld{0%{opacity:0;transform:translate(-50%,14px) scale(.7)}14%{opacity:1;transform:translate(-50%,0) scale(1.06)}",
    "22%{transform:translate(-50%,0) scale(1)}80%{opacity:1}100%{opacity:0;transform:translate(-50%,-16px)}}",
    ".nestbalken span.fx-erreicht{animation:fxStern .9s cubic-bezier(.3,1.7,.5,1);filter:drop-shadow(0 0 6px #ffcf3f)}",
    "@keyframes fxStern{0%{transform:translateX(-50%) scale(1)}35%{transform:translateX(-50%) scale(2.1) rotate(-12deg)}100%{transform:translateX(-50%) scale(1)}}",
    ".ende .gross>span>span{display:inline-block}",
    ".ende .gross>span>span:not(.stern-leer){animation:fxPlopp .6s cubic-bezier(.3,1.7,.5,1) backwards}",
    ".ende .gross>span>span:nth-child(1){animation-delay:.35s}",
    ".ende .gross>span>span:nth-child(2){animation-delay:.75s}",
    ".ende .gross>span>span:nth-child(3){animation-delay:1.15s}",
    "@keyframes fxPlopp{from{opacity:0;transform:scale(.2) rotate(-40deg)}to{opacity:1;transform:none}}"
  ].join("\n");
  document.head.appendChild(css);

  /* Prüfen, ob der Stern-Marker im Balken mit translateX(-50%) zentriert ist;
     wenn nicht, ohne Verschiebung animieren. */
  function sternAnimation(span) {
    var t = getComputedStyle(span).transform;
    if (!t || t === "none") {
      span.animate([{ transform: "scale(1)" }, { transform: "scale(2.1) rotate(-12deg)", offset: .35 }, { transform: "scale(1)" }],
        { duration: 900, easing: "cubic-bezier(.3,1.7,.5,1)" });
      span.style.filter = "drop-shadow(0 0 6px #ffcf3f)";
    } else {
      span.classList.remove("fx-erreicht"); void span.offsetWidth; span.classList.add("fx-erreicht");
    }
  }

  /* ---------- 1. Wind ---------- */
  function wind(felder) {
    if (!windAn) return;
    var jetzt = Date.now() / 1000;
    felder.querySelectorAll(".feld").forEach(function (feld) {
      var name = feld.getAttribute("aria-label") || "";
      for (var k = 0; k < STILL.length; k++) if (name.indexOf(STILL[k]) === 0) return;
      var i = +feld.getAttribute("data-i") || 0;
      /* Die Phase hängt an der Uhrzeit: Beim Neuzeichnen nach jedem Zug läuft
         die Bewegung ohne Ruck weiter. Benachbarte Felder sind leicht versetzt,
         so dass der Wind über die Wiese zu wandern scheint. */
      var phase = ((jetzt + (i % 7) * .45 + Math.floor(i / 7) * .2) % 7.2).toFixed(2);
      Array.prototype.forEach.call(feld.children, function (el) {
        var tag = el.tagName.toLowerCase();
        if (tag !== "g" && tag !== "path") return;
        el.classList.add("fx-wiegt");
        el.style.animationDelay = "-" + phase + "s";
      });
    });
  }

  /* ---------- 2. Licht ---------- */
  function sonneIn(himmel) {
    var kreise = himmel.querySelectorAll("circle");
    for (var k = 0; k < kreise.length; k++) {
      var r = +kreise[k].getAttribute("r"), f = (kreise[k].getAttribute("fill") || "").toLowerCase();
      if (r >= 13 && r <= 16 && f.indexOf("#ffd") === 0) return kreise[k];
    }
    return null;
  }
  function licht(plan) {
    var himmel = plan.querySelector("#himmel"), rect = plan.querySelector("#fxLicht");
    if (!himmel || !rect) return;
    var sonne = sonneIn(himmel);
    if (!sonne) { rect.style.opacity = 0; return; }
    var deck = sonne.getAttribute("opacity");
    if (deck !== null && +deck < .95) { rect.style.opacity = 0; return; }   /* Nacht: das Spiel dunkelt selbst ab */
    var p = Math.max(0, Math.min(1, (+sonne.getAttribute("cx") - 40) / 620)), farbe = "#ffd9a8", stark = 0;
    if (p < .16) { farbe = "#ffd6b0"; stark = (.16 - p) / .16 * .22; }          /* Morgenrot */
    else if (p > .55) { var a = (p - .55) / .45; farbe = a > .8 ? "#f2955a" : "#ffb466"; stark = a * .34; }  /* Abendlicht */
    rect.style.fill = farbe; rect.style.opacity = stark.toFixed(3);
  }

  /* ---------- 3. Abheben ---------- */
  function abheben(figur) {
    if (figur.animate) figur.animate([{ scale: "1" }, { scale: "1.28", offset: .45 }, { scale: "1" }], { duration: 440, easing: "ease-in-out" });
  }

  /* ---------- 4. Funken ---------- */
  var FUNKENFARBE = { blau: ["#4a90d9", "#9cc8f2"], gelb: ["#f6b90d", "#ffe27a"], gruen: ["#3f9a4a", "#b6e3a1"] };
  function funken(fx, text) {
    var art = ["blau", "gelb", "gruen"].filter(function (c) { return text.classList.contains(c); })[0];
    if (!art) return;
    var x = +text.getAttribute("x"), y = +text.getAttribute("y") + 14, fa = FUNKENFARBE[art];
    for (var k = 0; k < 14; k++) {
      var c = document.createElementNS(SVGNS, "circle"), w = k / 14 * Math.PI * 2 + Math.random() * .4, d = 30 + Math.random() * 34;
      c.setAttribute("cx", x); c.setAttribute("cy", y); c.setAttribute("r", (3.5 + Math.random() * 3).toFixed(1)); c.setAttribute("stroke", "#fff"); c.setAttribute("stroke-width", "1.2");
      c.setAttribute("fill", fa[k % 2]); c.setAttribute("pointer-events", "none");
      fx.appendChild(c);
      var dx = Math.cos(w) * d, dy = Math.sin(w) * d - 10;
      var an = c.animate([{ transform: "translate(0,0)", opacity: 1 },
        { transform: "translate(" + (dx * .8).toFixed(1) + "px," + (dy * .8).toFixed(1) + "px)", opacity: 1, offset: .6 },
        { transform: "translate(" + dx.toFixed(1) + "px," + (dy + 8).toFixed(1) + "px)", opacity: 0 }],
        { duration: 750 + Math.random() * 300, easing: "ease-out" });
      an.onfinish = (function (el) { return function () { el.remove(); }; })(c);
    }
  }

  /* ---------- 5. Stern-Moment ---------- */
  var SPRUCH = ["⭐ Erster Stern!", "⭐⭐ Zweiter Stern!", "⭐⭐⭐ Alle drei Sterne!"];
  function sternMoment(balken) {
    var huelle = balken.parentNode, rahmen = document.getElementById("rahmen");
    if (!huelle) return;
    var breite = parseFloat(balken.style.width) || 0;
    var marken = huelle.querySelectorAll(":scope > span");
    if (balken.__fxStart === undefined) {          /* erster Blick: bereits erreichte Sterne nicht feiern */
      balken.__fxStart = true; balken.__fxGezeigt = 0;
      for (var a = 0; a < marken.length; a++) if (breite >= parseFloat(marken[a].style.left) - .01) balken.__fxGezeigt = a + 1;
      return;
    }
    for (var k = balken.__fxGezeigt; k < marken.length; k++) {
      if (breite >= parseFloat(marken[k].style.left) - .01) {
        balken.__fxGezeigt = k + 1;
        sternAnimation(marken[k]);
        if (rahmen) {
          var alt = rahmen.querySelector(".fx-meldung"); if (alt) alt.remove();
          var m = document.createElement("div"); m.className = "fx-meldung"; m.setAttribute("aria-hidden", "true");
          m.textContent = SPRUCH[Math.min(k, 2)];
          rahmen.appendChild(m); setTimeout(function () { m.remove(); }, 2300);
        }
      }
    }
  }

  /* ---------- Zuschauen ---------- */
  var beobachtet = new WeakSet();
  function einrichten() {
    var plan = document.getElementById("plan");
    if (plan && !beobachtet.has(plan)) {
      beobachtet.add(plan);
      var felder = plan.querySelector("#felder"), himmel = plan.querySelector("#himmel"), fx = plan.querySelector("#fx"), figur = plan.querySelector("#biene");
      if (felder) {
        var r = document.createElementNS(SVGNS, "rect");
        r.setAttribute("id", "fxLicht"); r.setAttribute("x", "0"); r.setAttribute("y", "0");
        r.setAttribute("width", "700"); r.setAttribute("height", "570"); r.style.opacity = 0;
        /* über die Felder, aber unter die Spielfigur – die bleibt hell und gut sichtbar */
        felder.parentNode.insertBefore(r, felder.nextSibling);
        wind(felder);
        new MutationObserver(function () { wind(felder); }).observe(felder, { childList: true });
      }
      if (himmel) { licht(plan); new MutationObserver(function () { licht(plan); }).observe(himmel, { childList: true, subtree: true }); }
      if (fx) new MutationObserver(function (ms) {
        ms.forEach(function (m) { m.addedNodes.forEach(function (n) { if (n.classList && n.classList.contains("schweb")) funken(fx, n); }); });
      }).observe(fx, { childList: true });
      if (figur) {
        var letzte = figur.getAttribute("style");
        new MutationObserver(function () { var s = figur.getAttribute("style"); if (s !== letzte) { letzte = s; abheben(figur); } })
          .observe(figur, { attributes: true, attributeFilter: ["style"] });
      }
    }
    var balken = document.getElementById("nBalk");
    if (balken && !beobachtet.has(balken)) {
      beobachtet.add(balken);
      sternMoment(balken);
      new MutationObserver(function () { sternMoment(balken); }).observe(balken, { attributes: true, attributeFilter: ["style"] });
    }
  }
  function start() {
    einrichten();
    new MutationObserver(einrichten).observe(document.body, { childList: true, subtree: true });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start); else start();
})();
