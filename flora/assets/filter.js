/* Filter-Logik für das Pflanzenportal "Was blüht denn hier?".
   Filter: Farbe, Blühzeit (Monat), Lebensraum,
           Familie (deutsch + lateinisch durchsuchbar),
           Blütenaufbau, Volltext-Schnellsuche.
   Läuft vollständig im Browser.
*/
(function () {
  const state = {
    farben: new Set(),
    bereiche: new Set(),
    monate: new Set(),
    familien: new Set(),
    aufbau: new Set(),
    suche: '',
  };

  // Lesbare Monatskürzel für die aktiven Filter-Chips
  const MONAT_LABEL = {
    1: 'Jan', 2: 'Feb', 3: 'Mär', 4: 'Apr', 5: 'Mai', 6: 'Jun',
    7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Okt', 11: 'Nov', 12: 'Dez',
  };

  function toggleSet(set, value) {
    if (set.has(value)) set.delete(value); else set.add(value);
  }

  function matches(art, kartenText) {
    if (state.farben.size > 0) {
      const hit = (art.farben || []).some(f => state.farben.has(f));
      if (!hit) return false;
    }
    if (state.bereiche.size > 0 && !state.bereiche.has(art.habitat)) return false;
    if (state.monate.size > 0) {
      const hit = (art.monate || []).some(m => state.monate.has(m));
      if (!hit) return false;
    }
    if (state.familien.size > 0 && !state.familien.has(art.familie_de)) return false;
    if (state.aufbau.size > 0) {
      const hit = (art.bluetenaufbau || []).some(a => state.aufbau.has(a));
      if (!hit) return false;
    }
    if (state.suche) {
      const hay = kartenText.toLowerCase();
      if (!hay.includes(state.suche)) return false;
    }
    return true;
  }

  function refresh() {
    const cards = document.querySelectorAll('.card');
    let shown = 0;
    cards.forEach(card => {
      const a = JSON.parse(card.dataset.art);
      const text = (card.querySelector('.deutsch')?.textContent || '') + ' ' +
                   (card.querySelector('.wiss')?.textContent || '') + ' ' +
                   (card.querySelector('.familie')?.textContent || '');
      if (matches(a, text)) {
        card.style.display = '';
        shown++;
      } else {
        card.style.display = 'none';
      }
    });
    const z = document.getElementById('zaehler');
    if (z) {
      z.textContent = shown === cards.length
        ? `Alle ${cards.length} Arten angezeigt`
        : `${shown} von ${cards.length} Arten passen zu deiner Auswahl`;
    }
    const leer = document.getElementById('leer');
    if (leer) leer.style.display = shown === 0 ? '' : 'none';

    rendereAktiveFilter();
    aktualisiereResetButton();
  }

  // Prüft, ob irgendein Filter gesetzt ist (auch Schnellsuche)
  function irgendeinFilterAktiv() {
    return (
      state.farben.size +
      state.bereiche.size +
      state.monate.size +
      state.familien.size +
      state.aufbau.size > 0
    ) || state.suche.length > 0;
  }

  // Setzt den Reset-Button auf "aktiv" wenn mindestens ein Filter gesetzt ist
  function aktualisiereResetButton() {
    const btn = document.getElementById('reset');
    if (!btn) return;
    if (irgendeinFilterAktiv()) {
      btn.classList.add('aktiv');
      btn.removeAttribute('disabled');
    } else {
      btn.classList.remove('aktiv');
      btn.setAttribute('disabled', 'disabled');
    }
  }

  // Hilfsfunktion: einen einzelnen Filter abschalten
  function entferneFilter(typ, wert) {
    if (typ === 'farben')        state.farben.delete(wert);
    else if (typ === 'bereiche') state.bereiche.delete(wert);
    else if (typ === 'monate')   state.monate.delete(wert);
    else if (typ === 'familien') state.familien.delete(wert);
    else if (typ === 'aufbau')   state.aufbau.delete(wert);
    else if (typ === 'suche')    state.suche = '';

    // Visuell: zugehöriges Chip im Filter-Bereich entaktivieren
    if (typ === 'farben') {
      document.querySelectorAll(`.chip.farbe[data-farbe="${wert}"]`).forEach(c => c.classList.remove('aktiv'));
    } else if (typ === 'bereiche') {
      document.querySelectorAll(`.chip.bereich[data-bereich="${wert}"]`).forEach(c => c.classList.remove('aktiv'));
    } else if (typ === 'monate') {
      document.querySelectorAll(`.chip.monat[data-monat="${wert}"]`).forEach(c => c.classList.remove('aktiv'));
    } else if (typ === 'familien') {
      document.querySelectorAll(`.chip.familie[data-familie="${wert}"]`).forEach(c => c.classList.remove('aktiv'));
    } else if (typ === 'aufbau') {
      document.querySelectorAll(`.chip.aufbau[data-aufbau="${wert}"]`).forEach(c => c.classList.remove('aktiv'));
    } else if (typ === 'suche') {
      const sIn = document.getElementById('schnellsuche-input');
      if (sIn) sIn.value = '';
    }
    refresh();
  }

  // Zeichnet die Tag-/Chip-Anzeige der aktiven Filter über der Filterleiste
  function rendereAktiveFilter() {
    const ziel = document.getElementById('aktive-filter');
    if (!ziel) return;
    ziel.innerHTML = '';

    function chip(typ, wert, anzeige, label) {
      const span = document.createElement('span');
      span.className = 'aktiv-chip';
      if (label) {
        const lab = document.createElement('span');
        lab.className = 'label';
        lab.textContent = label + ':';
        span.appendChild(lab);
      }
      const txt = document.createElement('span');
      txt.textContent = anzeige;
      span.appendChild(txt);
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'schliessen';
      btn.setAttribute('aria-label', 'Filter "' + anzeige + '" entfernen');
      btn.textContent = '✕';
      btn.addEventListener('click', () => entferneFilter(typ, wert));
      span.appendChild(btn);
      ziel.appendChild(span);
    }

    // Farben (sind Strings)
    state.farben.forEach(v => chip('farben', v, v, 'Farbe'));
    // Lebensraum
    state.bereiche.forEach(v => chip('bereiche', v, v, 'Lebensraum'));
    // Monate (sind Zahlen)
    state.monate.forEach(v => chip('monate', v, MONAT_LABEL[v] || v, 'Monat'));
    // Familien
    state.familien.forEach(v => chip('familien', v, v, 'Familie'));
    // Blütenaufbau
    state.aufbau.forEach(v => chip('aufbau', v, v, 'Blüte'));
    // Schnellsuche
    if (state.suche) chip('suche', null, '"' + state.suche + '"', 'Suche');
  }

  function bindChips(selector, set, valueAttr, typeAttr) {
    document.querySelectorAll(selector).forEach(el => {
      el.addEventListener('click', () => {
        let v = el.dataset[valueAttr];
        if (typeAttr === 'number') v = parseInt(v, 10);
        toggleSet(set, v);
        el.classList.toggle('aktiv');
        refresh();
      });
    });
  }

  function reset() {
    state.farben.clear();
    state.bereiche.clear();
    state.monate.clear();
    state.familien.clear();
    state.aufbau.clear();
    state.suche = '';
    document.querySelectorAll('.chip.aktiv').forEach(c => c.classList.remove('aktiv'));
    const sIn = document.getElementById('schnellsuche-input');
    if (sIn) sIn.value = '';
    const fIn = document.getElementById('familie-suche');
    if (fIn) { fIn.value = ''; filterFamilieListe(''); }
    refresh();
  }

  function filterFamilieListe(query) {
    const q = (query || '').toLowerCase().trim();
    document.querySelectorAll('.familie-liste .chip').forEach(el => {
      const de = (el.dataset.familie || '').toLowerCase();
      const lat = (el.dataset.familieLat || '').toLowerCase();
      el.style.display = (!q || de.includes(q) || lat.includes(q)) ? '' : 'none';
    });
  }

  // Baut die Pflanzenkarten dynamisch aus pflanzen.json (eine Datenquelle).
  // Struktur identisch zur früheren statischen Karte, inkl. data-art für den Filter.
  function bauKarten(daten) {
    const grid = document.getElementById('grid');
    if (!grid) return;
    const frag = document.createDocumentFragment();
    const sammel = window.FloraSammel;
    daten.forEach(p => {
      const a = document.createElement('a');
      const an = sammel ? sammel.hat(p.slug) : false;
      a.className = 'card' + (an ? ' gefunden' : '');
      a.href = 'arten/' + p.slug + '.html';
      a.dataset.art = JSON.stringify({
        slug: p.slug, farben: p.farben || [], habitat: p.habitat,
        monate: p.monate || [], familie_de: p.familie_de,
        familie_lat: p.familie_lat, bluetenaufbau: p.bluetenaufbau || []
      });
      const farbe1 = (p.farben && p.farben[0]) || '';
      const punkte = (p.farben || [])
        .map(f => `<span class="farb-punkt" data-farbe="${f}" title="${f}"></span>`).join('');
      a.innerHTML =
        '<div class="tafel-wrap">' +
          `<span class="ecke-farbpunkt" data-farbe="${farbe1}"></span>` +
          `<img src="images/tafeln/${p.slug}.jpg" alt="Tafel ${p.deutsch}" loading="lazy" onerror="this.style.visibility='hidden'">` +
          `<span class="merk-btn" role="button" tabindex="0" data-slug="${p.slug}" aria-pressed="${an ? 'true' : 'false'}" title="In die Sammelmappe eintragen">✓</span>` +
        '</div>' +
        '<div class="card-body">' +
          `<div class="deutsch">${p.deutsch}</div>` +
          `<div class="wiss">${p.wiss}</div>` +
          `<div class="familie">${p.familie_de} · <span style="font-style:italic">${p.familie_lat}</span></div>` +
          '<div class="meta">' +
            `<span class="bluehzeit">${p.bluehzeit || ''}</span>` +
            `<span class="farbenpunkte">${punkte}</span>` +
            `<span style="margin-left:6px; color:var(--text-leise);">${p.habitat || ''}</span>` +
          '</div>' +
        '</div>';
      frag.appendChild(a);
    });
    grid.innerHTML = '';
    grid.appendChild(frag);

    // „In die Sammelmappe eintragen": nur hier (im Bestimmungstool) möglich
    if (!grid._merkGebunden) {
      grid._merkGebunden = true;
      const markiere = function (mb) {
        if (!window.FloraSammel) return;
        const slug = mb.dataset.slug;
        const jetzt = window.FloraSammel.toggle(slug);
        const karte = mb.closest('.card');
        if (karte) karte.classList.toggle('gefunden', jetzt);
        mb.setAttribute('aria-pressed', jetzt ? 'true' : 'false');
        if (jetzt && window.FloraSammel.istMeilenstein(window.FloraSammel.anzahl())) {
          window.FloraSammel.feiere(window.FloraSammel.anzahl());
        }
      };
      grid.addEventListener('click', function (e) {
        const mb = e.target.closest('.merk-btn');
        if (!mb) return;
        e.preventDefault();    // Karten-Navigation unterbinden
        e.stopPropagation();
        markiere(mb);
      });
      grid.addEventListener('keydown', function (e) {
        const mb = e.target.closest('.merk-btn');
        if (!mb || (e.key !== 'Enter' && e.key !== ' ')) return;
        e.preventDefault();
        markiere(mb);
      });
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    bindChips('.chip.farbe',    state.farben,   'farbe',    'string');
    bindChips('.chip.bereich',  state.bereiche, 'bereich',  'string');
    bindChips('.chip.monat',    state.monate,   'monat',    'number');
    bindChips('.chip.familie',  state.familien, 'familie',  'string');
    bindChips('.chip.aufbau',   state.aufbau,   'aufbau',   'string');

    const reset_btn = document.getElementById('reset');
    if (reset_btn) reset_btn.addEventListener('click', () => {
      // nur reagieren, wenn Filter aktiv sind
      if (irgendeinFilterAktiv()) reset();
    });

    const schnellsuche = document.getElementById('schnellsuche-input');
    if (schnellsuche) {
      schnellsuche.addEventListener('input', e => {
        state.suche = e.target.value.toLowerCase().trim();
        refresh();
      });
    }

    const famSuche = document.getElementById('familie-suche');
    if (famSuche) {
      famSuche.addEventListener('input', e => filterFamilieListe(e.target.value));
    }

    // Nach dem Aufbau der Karten: Direktsprung per URL + erstes Filtern
    function nachStart() {
      // Erlaubt direkte Sprünge per URL, z. B. aus der Systematik:
      // bestimmen.html?familie=Korbblütler  → setzt den passenden Familien-Filter
      try {
        const params = new URLSearchParams(window.location.search);
        const famParam = params.get('familie');
        if (famParam) {
          const ziel = document.querySelector(
            `.chip.familie[data-familie="${famParam.replace(/"/g, '\\"')}"]`
          );
          if (ziel && !ziel.classList.contains('aktiv')) {
            ziel.click();
            const det = ziel.closest('details');
            if (det) det.open = true;
          }
          // Direkt zu den gefilterten Arten scrollen (Filtermaske überspringen)
          const ergebnis = document.querySelector('.zaehler') || document.getElementById('grid');
          if (ergebnis) {
            setTimeout(function () {
              ergebnis.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 120);
          }
        }
      } catch (e) { /* ignorieren */ }
      refresh();
    }

    // Pflanzendaten laden und Karten erzeugen, danach filtern
    fetch('pflanzen.json')
      .then(r => r.json())
      .then(daten => { bauKarten(daten); nachStart(); })
      .catch(() => { nachStart(); });
  });
})();
