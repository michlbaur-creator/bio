/* Tafelmodus für Beamer/Smartboard bzw. Activeboard
   Aktiv über ?tafel in der Adresse oder den Knopf „Für die Tafel“.
   Ausschalten: Knopf „Tafel aus“ oder ?tafel=aus.
   Der Zustand gilt für die laufende Browser-Sitzung (alle Seiten). */
(function () {
  "use strict";
  var KEY = "bio-tafel";
  var html = document.documentElement;

  function merken(an) {
    try { an ? sessionStorage.setItem(KEY, "1") : sessionStorage.removeItem(KEY); } catch (e) {}
  }
  function gemerkt() {
    try { return sessionStorage.getItem(KEY) === "1"; } catch (e) { return false; }
  }

  var q = location.search.match(/[?&]tafel(=([^&]*))?/);
  if (q) merken(q[2] !== "aus" && q[2] !== "0");
  if (window.self !== window.top) return; // nicht in eingebetteten Rahmen

  var css = document.createElement("style");
  css.textContent =
    "html.tafel body{min-height:0!important}" +
    "html.tafel{scrollbar-gutter:auto}" +
    ".tafel-leiste{position:fixed;right:1vw;bottom:1.5vh;z-index:2147483000;display:flex;gap:.6em;" +
    "font:600 clamp(15px,1.05vw,30px)/1 Inter,system-ui,sans-serif}" +
    ".tafel-leiste button{font:inherit;border:0;border-radius:999px;padding:.75em 1.15em;cursor:pointer;" +
    "background:#1f3a5f;color:#fff;box-shadow:0 2px 10px rgba(0,0,0,.25);touch-action:manipulation}" +
    ".tafel-leiste button.zart{background:rgba(255,255,255,.92);color:#1f3a5f;border:2px solid #1f3a5f}" +
    ".tafel-an{position:fixed;right:14px;bottom:14px;z-index:2147483000;font:600 14px/1 Inter,system-ui,sans-serif;" +
    "border:2px solid #1f3a5f;background:rgba(255,255,255,.9);color:#1f3a5f;border-radius:999px;padding:9px 14px;cursor:pointer;" +
    "opacity:.75}.tafel-an:hover{opacity:1}" +
    "@media (max-width:1199px),(orientation:portrait){.tafel-an{display:none}}" +
    "@media print{.tafel-leiste,.tafel-an{display:none}}";
  html.appendChild(css);

  var leiste = null, anKnopf = null, zoom = 1, plan = 0;

  function vollbildMoeglich() {
    return !!(html.requestFullscreen || html.webkitRequestFullscreen);
  }
  function imVollbild() {
    return !!(document.fullscreenElement || document.webkitFullscreenElement);
  }
  function vollbild() {
    if (imVollbild()) {
      (document.exitFullscreen || document.webkitExitFullscreen).call(document);
    } else {
      var p = (html.requestFullscreen || html.webkitRequestFullscreen).call(html);
      if (p && p.catch) p.catch(function () {});
    }
  }

  function introSichtbar() {
    var e = document.querySelector(".pfad-intro");
    return !!(e && !e.classList.contains("weg") && getComputedStyle(e).display !== "none");
  }
  // Breite und Höhe des Inhalts bei Zoom 1 messen
  function messen() {
    var b = document.body;
    var alt = b.style.zoom;
    b.style.zoom = "1";
    var spielfeld = document.getElementById("plan");
    var r = null, typ = "seite";
    if (spielfeld) {
      var sp = spielfeld.closest(".spiel") || spielfeld.parentElement;
      if (sp && sp.offsetWidth) {
        var top = 0, el = document.querySelector(".spielkopf");
        if (el && el.offsetParent !== null) top = el.getBoundingClientRect().top + window.scrollY;
        var rr = sp.getBoundingClientRect();
        r = { w: rr.width, h: rr.bottom + window.scrollY - top + 16 };
        typ = "spiel";
      }
    }
    if (!r) {
      var w = 0;
      var sel = ".pfad-intro .pi-inner, .huelle, main, .wrap, .container, .innen, .app-head .row";
      document.querySelectorAll(sel).forEach(function (e) {
        if (e.offsetParent === null && getComputedStyle(e).position !== "fixed") return;
        var x = e.getBoundingClientRect().width;
        if (x > w && x < window.innerWidth - 8) w = x;
      });
      r = { w: w || 900, h: 0 };
      var bu = document.getElementById("buehne");
      if (bu && bu.offsetParent !== null && !introSichtbar()) {
        r.h = bu.getBoundingClientRect().bottom + window.scrollY + 12;
      }
    }
    b.style.zoom = alt;
    r.typ = typ;
    return r;
  }

  function berechnen() {
    plan = 0;
    if (!html.classList.contains("tafel")) return;
    var m = messen(), W = window.innerWidth, H = window.innerHeight, z;
    if (m.typ === "spiel") {
      z = Math.min((W - 40) / m.w, (H - 10) / m.h);
    } else {
      z = (W * 0.72) / m.w;
      if (m.h) z = Math.min(z, Math.max(1.5, H / m.h));
    }
    z = Math.max(1, Math.min(4, z));
    z = Math.round(z * 100) / 100;
    if (Math.abs(z - zoom) > 0.015) {
      zoom = z;
      document.body.style.zoom = String(z);
    }
  }
  function spaeter() {
    if (plan) return;
    plan = setTimeout(berechnen, 120);
  }

  function leisteBauen() {
    leiste = document.createElement("div");
    leiste.className = "tafel-leiste";
    leiste.setAttribute("role", "toolbar");
    leiste.setAttribute("aria-label", "Tafelmodus");
    if (vollbildMoeglich()) {
      var vb = document.createElement("button");
      vb.type = "button";
      vb.textContent = "⛶ Vollbild";
      vb.addEventListener("click", vollbild);
      document.addEventListener("fullscreenchange", function () {
        vb.textContent = imVollbild() ? "⛶ Vollbild aus" : "⛶ Vollbild";
        spaeter();
      });
      leiste.appendChild(vb);
    }
    var aus = document.createElement("button");
    aus.type = "button";
    aus.className = "zart";
    aus.textContent = "✕ Tafel aus";
    aus.addEventListener("click", function () { setzen(false); });
    leiste.appendChild(aus);
  }

  function setzen(an) {
    merken(an);
    html.classList.toggle("tafel", an);
    if (an) {
      if (!leiste) leisteBauen();
      html.appendChild(leiste);
      if (anKnopf) anKnopf.remove();
      zoom = 1;
      berechnen();
    } else {
      if (leiste) leiste.remove();
      if (imVollbild()) vollbild();
      document.body.style.zoom = "";
      zoom = 1;
      if (!anKnopf) {
        anKnopf = document.createElement("button");
        anKnopf.type = "button";
        anKnopf.className = "tafel-an";
        anKnopf.textContent = "▣ Für die Tafel";
        anKnopf.title = "Große Ansicht für Beamer/Smartboard";
        anKnopf.addEventListener("click", function () { setzen(true); });
      }
      html.appendChild(anKnopf);
    }
  }

  function start() {
    setzen(gemerkt());
    window.addEventListener("resize", spaeter);
    window.addEventListener("orientationchange", spaeter);
    new MutationObserver(spaeter).observe(document.body, {
      childList: true, subtree: true, attributes: true, attributeFilter: ["hidden", "class", "style"]
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
})();
