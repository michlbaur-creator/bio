#!/usr/bin/env python3
"""
build_bio.py — baut/aktualisiert die Unterrichts-Site bio.mibaso.de aus den
Lernpfaden von flora/ und fauna/.

Aufruf (im Ordner Documents/GitHub):  python3 bio/build_bio.py

Was es tut:
  * kopiert alle interaktiv/*.html aus flora und fauna nach bio/<repo>/interaktiv/
  * kopiert die von den Pfaden referenzierten Bilder (gezielt, nicht die ganzen
    tafeln/fotos-Ordner), dazu assets/ und ueber/ komplett
  * biegt Rücklinks (../index.html usw.) auf die bio-Startseite um
  * erzeugt die bio-Startseite (nach Flora/Fauna gruppiert)
Kopien sind Momentaufnahmen — nach Änderungen an den Originalen einfach neu laufen lassen.
"""
import os, re, shutil, html

def _find_root(start):
    # GitHub-Wurzel = enthält flora, fauna UND media (media wird nie nach bio kopiert,
    # verhindert Selbst-Treffer, sobald bio schon flora/fauna-Kopien enthält).
    p = start
    while p != os.path.dirname(p):
        if all(os.path.isdir(os.path.join(p, d)) for d in ("flora", "fauna", "media")):
            return p
        p = os.path.dirname(p)
    return os.path.dirname(os.path.dirname(start))

# Quellen- und Zielordner: in der CI per Umgebungsvariablen gesetzt, lokal automatisch.
ROOT = os.environ.get("BIO_SRC_ROOT") or _find_root(os.path.dirname(os.path.abspath(__file__)))
BIO = os.environ.get("BIO_OUT")
if not BIO:
    _cands = [os.path.join(ROOT, "bio", "bio"), os.path.join(ROOT, "bio")]
    BIO = next((c for c in _cands if os.path.isdir(os.path.join(c, ".git"))), os.path.join(ROOT, "bio"))

REPOS = [
    {"key": "flora", "label": "Flora Mibaso", "emoji": "🌼", "akzent": "#2F4F3E",
     "pass": {"href": "pflanzenpass.html", "img": "images/bluetenoekologie.jpg",
              "eyebrow": "Dein Forscherpass", "titel": "Expedition Wiese",
              "sub": "Spiel die Pfade, lass deine Wiese erblühen und kröne dich zum Flora-Meister."}},
    {"key": "fauna", "label": "Fauna Mibaso", "emoji": "🦋", "akzent": "#233D5C",
     "pass": {"href": "interaktiv/wiesenpass.html", "img": "images/wiese/wiese-sommer.png",
              "eyebrow": "Dein Forscherpass", "titel": "Expedition Wiese",
              "sub": "Spiel die Pfade, lass deine Wiese wachsen und kröne dich zum Wiesen-Meister."}},
]

# Thematische Gruppen je Repo: (Überschrift, Farbe, [Dateien]). Seit dem Fauna-Stil-
# Umbau (Juli 2026) werden die Farben NICHT mehr benutzt: Gruppen-Titel sind einheitlich
# Honiggold-Kapitälchen mit feiner Linie, Icons tragen die Seiten-Akzentfarbe.
# Nicht zugeordnete Pfade landen unter „Mehr entdecken".
GROUPS = {
    "flora": [
        ("Wie ist eine Pflanze aufgebaut?", "#5A6B7A",
         ["pflanze-verstehen.html"]),
        ("Wie entstehen neue Pflanzen?", "#2C7A6A",
         ["bestaeubung-erklaerung.html", "samenreise.html"]),
        ("Wie meistern Pflanzen das Leben?", "#C4603A",
         ["jahreszeiten-baum.html", "pflanzenstrategien.html", "pflanzen-energie.html"]),
    ],
    "fauna": [
        ("Bestimmen & Verwandtschaft", "#5A6B7A",
         ["grundlagen.html", "schluessel.html", "systematik.html", "stammbaum.html"]),
        ("Verwandlung & Bestäubung", "#2C7A6A",
         ["verwandlung.html", "bestaeubung.html"]),
        ("Wiese & Lebensraum", "#C4603A",
         ["lebensraum.html", "nahrungsnetz.html", "wiese-lebt.html", "bodenleben.html", "insektenschwund.html"]),
    ],
}

# Zusätzliche „Entdecken"-Kacheln, die auf die Original-Apps verlinken (absolute URLs).
# Nur für die Repo-Unterseite (write_sub). Reihenfolge = Kachel-Reihenfolge.
# Tupel: (Ziel-Datei, Icon-Key, Titel, Untertitel).
EXTRA = {
    "flora": {
        "titel": "Entdecken",
        "hinweis": "Diese Kacheln öffnen die Flora-App in einem neuen Tab.",
        "basis": "https://flora.mibaso.de/",
        "kacheln": [
            ("bestimmen-gefuehrt.html", "frage", "Frag dich durch",
             "Ein paar Fragen — und du landest bei der passenden Pflanze."),
            ("bestimmen.html", "lupe", "Was blüht denn hier?",
             "Alle 150 Pflanzen zum Stöbern, Filtern und Vergleichen."),
            ("sammelpass.html", "abzeichen", "Mein Sammelpass",
             "Deine im Bestimmungstool gefundenen Arten — mit Fortschritt und Abzeichen."),
        ],
    },
}

# Kleine Linien-Icons je Pfad (Inline-SVG-Innenteil, 24er Raster). Fallback: Blatt.
_G = {
    "leaf":   'M5 21c0-9 7-16 16-16 0 9-7 16-16 16z M6 20c4-4 8-6 12-8',
    "layers": 'M12 3l8 4-8 4-8-4 8-4z M4 12l8 4 8-4 M4 16l8 4 8-4',
    "sprout": 'M12 21v-9 M12 12c-3 0-5-2-5-5 3 0 5 2 5 5z M12 12c0-2.5 2-4.5 5-4.5 0 2.5-2 4.5-5 4.5z',
    "sun":    'M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8z M12 2v2 M12 20v2 M4 12H2 M22 12h-2 M5 5l1.5 1.5 M17.5 17.5 19 19 M19 5l-1.5 1.5 M6.5 17.5 5 19',
    "zoom":   'M11 5a6 6 0 1 0 0 12 6 6 0 0 0 0-12z M20 20l-4.3-4.3',
    "flower": 'M12 9.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5z M12 9.5V5 M12 14.5V19 M9.5 12H5 M14.5 12H19',
    "cycle":  'M4.5 12a7.5 7.5 0 0 1 12.8-5.3 M19.5 12a7.5 7.5 0 0 1-12.8 5.3 M17 3v4h-4 M7 21v-4h4',
    "network":'M12 9.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5z M5 4a2 2 0 1 0 0 4 2 2 0 0 0 0-4z M19 4a2 2 0 1 0 0 4 2 2 0 0 0 0-4z M5 16a2 2 0 1 0 0 4 2 2 0 0 0 0-4z M19 16a2 2 0 1 0 0 4 2 2 0 0 0 0-4z M6.6 7.4l3.6 3.4 M17.4 7.4l-3.6 3.4 M6.6 16.6l3.6-3.4 M17.4 16.6l-3.6-3.4',
    "wind":   'M4 8h9a3 3 0 1 0-3-3 M4 12h13a3 3 0 1 1-3 3 M4 16h7',
    "tree":   'M12 8a6 6 0 1 0 0 .001 M12 8v13 M8.5 18h7',
    "shield": 'M12 3l7 3v5c0 4.5-3 7.6-7 9-4-1.4-7-4.5-7-9V6l7-3z',
    "fork":   'M7 3v5 M7 8a5 5 0 0 0 5 5 M17 3v5 M17 8a5 5 0 0 1-5 5 M12 13v6',
    "sitemap":'M9.5 3h5v4h-5z M3.5 17h5v4h-5z M15.5 17h5v4h-5z M12 7v4 M6 17v-2h12v2 M12 11v2',
    "hier":   'M12 3a2.3 2.3 0 1 0 0 4.6A2.3 2.3 0 0 0 12 3z M6 17a2.3 2.3 0 1 0 0 4.6A2.3 2.3 0 0 0 6 17z M18 17a2.3 2.3 0 1 0 0 4.6A2.3 2.3 0 0 0 18 17z M12 7.6 6.7 15 M12 7.6 17.3 15',
    "biotop": 'M12 21v-6 M12 15c-3 0-5-2-5-5 3 0 5 2 5 5z M12 13c0-2.5 2-4.5 5-4.5 0 2.5-2 4.5-5 4.5z M4 21h16',
    "grass":  'M12 21c0-6 0-9 0-12 M12 21c-2-4-4-6-7-7 M12 21c2-4 4-6 7-7 M8 21c0-3-1-5-3-6 M16 21c0-3 1-5 3-6',
    "alert":  'M12 4l9 16H3l9-16z M12 10v5 M12 17.5h.01',
    "lupe":   'M11 4a6 6 0 1 0 0 12 6 6 0 0 0 0-12z M15.5 15.5 20 20 M8.5 9.5h5 M11 7v5',
    "frage":  'M9.3 9.2a2.8 2.8 0 1 1 3.9 2.6c-1 .5-1.7 1.1-1.7 2.4 M12 17.4h.01',
    "abzeichen":'M12 3l2.4 1.8 3-.2 1 2.8 2.4 1.8-.9 2.9.9 2.9-2.4 1.8-1 2.8-3-.2L12 21l-2.4-1.8-3 .2-1-2.8-2.4-1.8.9-2.9-.9-2.9 2.4-1.8 1-2.8 3 .2L12 3z M8.8 12.3l2.3 2.2 4.2-4.4',
}
ICON = {
    "pflanze-erklaerung.html": "layers", "pflanze-verstehen.html": "sprout",
    "pflanzen-energie.html": "sun", "bluete-zoom.html": "zoom",
    "bestaeubung-erklaerung.html": "flower", "bestaeubung-animiert.html": "cycle",
    "bluetenoekologie.html": "network", "samenverbreitung.html": "wind",
    "samenreise.html": "wind",
    "jahreszeiten-baum.html": "tree", "kreislauf.html": "cycle",
    "pflanzenstrategien.html": "shield",
    "grundlagen.html": "lupe",
    "schluessel.html": "fork", "systematik.html": "sitemap", "stammbaum.html": "hier",
    "verwandlung.html": "cycle", "bestaeubung.html": "flower", "lebensraum.html": "biotop",
    "nahrungsnetz.html": "network", "wiese-lebt.html": "grass", "insektenschwund.html": "alert",
    "bodenleben.html": "sprout",
}
def _icon(fn):
    d = _G.get(ICON.get(fn, "leaf"), _G["leaf"])
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="{d}"/></svg>')
# Kopiert, aber nicht auf der Startseite gelistet (z.B. der Pass als Footer-Ziel)
# kopiert, aber nicht als eigene Kachel gelistet (bestaeubung-animiert wird als iframe
# in „Bestäubung" eingebunden – Datei muss vorhanden sein, Kachel entfällt).
SKIP_LISTING = {"tafel.html", "wiesenpass.html", "sammelpass.html", "bestaeubung-animiert.html"}
# Ganz aus bio ausschließen (nicht kopieren, nicht listen): Staunen-Häppchen,
# Quizze/Tests und Ordnen-/Zuordnungs-Spiele — bio zeigt nur die echten Lernpfade.
# Einträge ohne Repo-Präfix gelten für beide; mit Präfix nur für ein Repo.
EXCLUDE = {"tierquiz.html", "gesamttest.html", "pflanze-zuordnung.html", "verwandte-finden.html",
           "flora/systematik.html",
           # Flora-Umbau (Juli 2026): Samenverbreitung-Kachel raus; die Anatomie-Grafik
           # „Aufbau einer Pflanze" wohnt jetzt als erste Station im Lernpfad
           # „Wurzel, Blatt, Blüte" (pflanze-verstehen), die Einzel-Kachel entfällt.
           "flora/samenverbreitung.html", "flora/pflanze-erklaerung.html",
           # „Blüten und ihre Gäste" (bluetenoekologie) aus bio entfernt (Juli 2026).
           "flora/bluetenoekologie.html",
           # „Hinein in die Blüte" wohnt jetzt eingebettet als erste Station im Pfad
           # „Aufbau der Pflanze" (pflanze-verstehen) → eigene Kachel + Pass-Station entfallen.
           # Die Datei bluete-zoom.html bleibt liegen (wird als iframe eingebunden).
           "flora/bluete-zoom.html",
           # alle „Warum"-Pfade
           "blumen-nachts.html", "kletten.html", "schaumzikaden.html", "sonnenblumen.html",
           # Energie: die vollständige „Pflanzen & Energie" (pflanzen-energie) bleibt;
           # die Übersichts-Hülle energie-pfad und „Der Gas-Kreislauf" raus.
           "energie-pfad.html", "energie-kreislauf-anim.html",
           # „Der ewige Kreislauf" raus — seine Stationen (Blüte-Zoom, Jahr im Baum)
           # stecken jetzt einzeln im Forscherpass.
           "kreislauf.html"}
def _excluded(key, fn):
    return (fn.endswith("-flyer.html") or fn.startswith("staunen-")
            or fn in EXCLUDE or f"{key}/{fn}" in EXCLUDE)

# --- Forscherpass-Pfade („Expedition") wohnen seit Juli 2026 NUR in bio -----------
# flora/fauna enthalten dafür nur noch schlanke Weiterleitungen. Diese Dateien werden
# deshalb NICHT mehr aus der Quelle kopiert (sonst überschrieben die Weiterleitungs-
# Stubs die bio-Master), aber weiterhin auf der bio-Startseite gelistet. Titel/Inhalt
# kommen dann direkt aus den bio-Dateien. Der Forscherpass selbst (pflanzenpass.html /
# wiesenpass.html) ebenso — er wird unten NICHT mehr kopiert.
# WICHTIG: bei einem kompletten Neubau bio/flora & bio/fauna NICHT komplett leeren,
# sonst gehen diese Master verloren.
NATIVE_LIST = {
    "flora": ["pflanze-verstehen.html", "bluete-zoom.html", "bestaeubung-erklaerung.html",
              "samenreise.html", "jahreszeiten-baum.html", "pflanzenstrategien.html", "pflanzen-energie.html"],
    "fauna": ["grundlagen.html", "verwandlung.html", "bestaeubung.html", "lebensraum.html",
              "nahrungsnetz.html", "wiese-lebt.html", "bodenleben.html"],
}
# beim Kopieren zu überspringen: die Expeditions-Pfade + der Forscherpass selbst
NATIVE_SKIP = {
    "flora": set(NATIVE_LIST["flora"]),
    "fauna": set(NATIVE_LIST["fauna"]) | {"wiesenpass.html"},
}

# Stimmige Reihenfolge je Repo (nicht gelistete kommen alphabetisch danach).
ORDER = {
    "flora": ["pflanze-erklaerung.html", "pflanze-verstehen.html", "pflanzen-energie.html",
              "bluete-zoom.html", "bestaeubung-erklaerung.html", "bestaeubung-animiert.html",
              "bluetenoekologie.html", "samenverbreitung.html", "samenreise.html", "jahreszeiten-baum.html",
              "pflanzenstrategien.html"],
    "fauna": ["grundlagen.html", "schluessel.html", "systematik.html", "stammbaum.html", "verwandlung.html",
              "bestaeubung.html", "lebensraum.html", "nahrungsnetz.html", "wiese-lebt.html",
              "bodenleben.html", "insektenschwund.html"],
}
# Typ-Kennzeichnung der Kacheln: „Übersicht" (Einzelseite) vs. „Lernpfad" (mehrstufig).
UEBERSICHT = {"pflanze-erklaerung.html", "bestaeubung-erklaerung.html", "bluetenoekologie.html",
              "samenverbreitung.html", "insektenschwund.html"}
def _typ(fn):
    return "Übersicht" if fn in UEBERSICHT else "Lernpfad"
# Kacheln ohne Typ-Badge (weder „Lernpfad" noch „Übersicht"): Bestimmen-/Verwandtschaft-
# Werkzeuge, die keine schrittweisen Lernpfade sind.
NO_BADGE = {"schluessel.html", "systematik.html", "stammbaum.html"}
def _ordidx(key, fn):
    o = ORDER.get(key, [])
    return o.index(fn) if fn in o else len(o) + 1

IMG_RE   = re.compile(r'([A-Za-z0-9_][A-Za-z0-9_.\-]*\.(?:jpg|jpeg|png|gif|svg|webp))', re.I)
SUBDIR_RE= re.compile(r'\.\./images/([A-Za-z0-9_\-/]+)/')  # auch verschachtelt, z.B. wiese/tiere
TITLE_RE = re.compile(r'<title>(.*?)</title>', re.S | re.I)

def clean_title(raw):
    t = html.unescape(raw.strip())
    for sep in (" — ", " – ", " · ", " — Lernpfad"):
        if sep in t:
            t = t.split(sep)[0]
    return t.strip()

# Abweichende Kachel-Beschriftungen NUR in bio (die Quell-Titel bleiben unberührt).
TITLE_OVERRIDE = {
    "bluetenoekologie.html": "Blüten und ihre Gäste",
    "pflanzenstrategien.html": "Überlebenskünstler",
    "pflanzen-energie.html": "Wie Pflanzen Sonnenlicht essen",
}
def label_for(fn, raw):
    return TITLE_OVERRIDE.get(fn) or (clean_title(raw) if raw else fn)

def rewrite_links(txt):
    # ../index.html zeigt jetzt korrekt auf die Repo-Unterseite (bio/flora/ bzw bio/fauna/).
    # Andere App-Rücklinks auf dieselbe Unterseite biegen.
    for a in ("../bestimmen.html", "../quiz/", "../interaktiv/"):
        txt = txt.replace('href="' + a + '"', 'href="../index.html"')
    # In bio existieren weder der arten/-Ordner noch die „Warum/Staunen"-Tafeln
    # (siehe EXCLUDE). „Absprung"-Buttons in den Lernpfad-Daten, die dorthin
    # zeigen, würden ins Leere führen — hier für bio herausnehmen (Fauna behält sie).
    # Trifft absprung:{...} und absprung2:{...} mit url auf ../arten/… oder staunen-…
    txt = re.sub(r'\s*absprung2?:\{[^}]*url:"[^"]*(?:\.\./arten/|staunen-)[^"]*"\},',
                 '', txt)
    return txt

def copytree(src, dst):
    if os.path.isdir(src):
        shutil.copytree(src, dst, dirs_exist_ok=True)

def build():
    # Kein Vorab-Löschen (im verbundenen Ordner nicht erlaubt) — Dateien werden
    # überschrieben. ACHTUNG: bio/flora & bio/fauna NICHT komplett leeren! Dort liegen
    # die einzigen Master der Forscherpass-Pfade (siehe NATIVE_LIST) — sie würden sonst
    # unwiederbringlich verschwinden.
    os.makedirs(BIO, exist_ok=True)

    listing = {r["key"]: [] for r in REPOS}
    total_imgs = 0

    for r in REPOS:
        key = r["key"]
        src = os.path.join(ROOT, key)
        dst = os.path.join(BIO, key)
        src_inter = os.path.join(src, "interaktiv")
        if not os.path.isdir(src_inter):
            print("!! kein", src_inter); continue
        os.makedirs(os.path.join(dst, "interaktiv"), exist_ok=True)

        # assets + ueber komplett
        copytree(os.path.join(src, "assets"), os.path.join(dst, "assets"))
        copytree(os.path.join(src, "ueber"),  os.path.join(dst, "ueber"))

        for fn in sorted(os.listdir(src_inter)):
            if not fn.endswith(".html"): continue
            if _excluded(key, fn): continue     # aus bio ganz raus
            if fn in NATIVE_SKIP.get(key, ()): continue  # lebt nativ in bio, nicht überkopieren
            raw = open(os.path.join(src_inter, fn), encoding="utf-8").read()

            # Bilder gezielt kopieren
            subdirs = set(SUBDIR_RE.findall(raw))
            names   = set(IMG_RE.findall(raw))
            for sub in subdirs:
                for nm in names:
                    s = os.path.join(src, "images", sub, nm)
                    if os.path.isfile(s):
                        d = os.path.join(dst, "images", sub, nm)
                        os.makedirs(os.path.dirname(d), exist_ok=True)
                        shutil.copy2(s, d); total_imgs += 1
            # evtl. top-level Bilder (../images/foo.jpg)
            for nm in names:
                s = os.path.join(src, "images", nm)
                if os.path.isfile(s):
                    d = os.path.join(dst, "images", nm)
                    os.makedirs(os.path.dirname(d), exist_ok=True)
                    shutil.copy2(s, d); total_imgs += 1

            # Pfad-HTML mit umgebogenen Rücklinks schreiben
            open(os.path.join(dst, "interaktiv", fn), "w", encoding="utf-8").write(rewrite_links(raw))

            if fn not in SKIP_LISTING:
                m = TITLE_RE.search(raw)
                listing[key].append((label_for(fn, m.group(1) if m else None), fn))

    # Startseiten-Bausteine aus Flora übernehmen: Über mich, Impressum, Anleitung, Assets
    copytree(os.path.join(ROOT, "flora", "assets"),    os.path.join(BIO, "assets"))
    copytree(os.path.join(ROOT, "flora", "ueber"),     os.path.join(BIO, "ueber"))
    copytree(os.path.join(ROOT, "flora", "impressum"), os.path.join(BIO, "impressum"))
    copytree(os.path.join(ROOT, "flora", "anleitung"), os.path.join(BIO, "anleitung"))
    # bio-eigener Über-mich-Schlusssatz (statt Flora-Version) + Namens-Korrekturen
    _uidx = os.path.join(BIO, "ueber", "index.html")
    if os.path.isfile(_uidx):
        _u = open(_uidx, encoding="utf-8").read()
        _u = _u.replace(
            "Möge sie als digitaler Kompass durch die wunderbare Welt der Botanik dienen. Viel Spaß beim virtuellen Botanisieren! 😉",
            "Ich hoffe, diese App bietet dir eine spannende Entdeckungsreise durch die Welt der Pflanzen und Tiere. Klick dich durch die Pfade und werde selbst zum Natur-Experten! 😉")
        _u = _u.replace("Flora Mibaso", "Bio Mibaso")
        open(_uidx, "w", encoding="utf-8").write(_u)
    # Der Flora-Forscherpass (pflanzenpass.html) wird NICHT mehr aus der Quelle kopiert –
    # er lebt jetzt nativ in bio (flora/ enthält nur eine Weiterleitung). Nur das
    # Banner-Bild der Flora-Unterseite weiterhin gezielt mitkopieren.
    _fimg = os.path.join(ROOT, "flora", "images", "bluetenoekologie.jpg")
    if os.path.isfile(_fimg):
        os.makedirs(os.path.join(BIO, "flora", "images"), exist_ok=True)
        shutil.copy2(_fimg, os.path.join(BIO, "flora", "images", "bluetenoekologie.jpg"))
    # eigenes bio-Icon (grün+blau Blatt) über die von Flora kopierten Icons legen
    BRAND = os.path.join(os.path.dirname(os.path.abspath(__file__)), "brand")
    copytree(BRAND, os.path.join(BIO, "assets"))
    open(os.path.join(BIO, "manifest.webmanifest"), "w", encoding="utf-8").write(MANIFEST)
    # Bilder, die Über-mich/Impressum per ../images/… referenzieren, aus Flora mitkopieren
    for page in ("ueber", "impressum"):
        pg = os.path.join(BIO, page, "index.html")
        if not os.path.isfile(pg):
            continue
        txt = open(pg, encoding="utf-8").read()
        for rel in set(re.findall(r'\.\./images/([A-Za-z0-9_\-/.]+\.(?:jpg|jpeg|png|webp|svg|gif))', txt, re.I)):
            s = os.path.join(ROOT, "flora", "images", rel)
            if os.path.isfile(s):
                d = os.path.join(BIO, "images", rel)
                os.makedirs(os.path.dirname(d), exist_ok=True)
                shutil.copy2(s, d)
    # Bio-eigene Forscherpass-Pfade (leben nur in bio) mit auflisten – Titel aus bio.
    for r in REPOS:
        key = r["key"]; di = os.path.join(BIO, key, "interaktiv")
        have = {fn for _, fn in listing[key]}
        for fn in NATIVE_LIST.get(key, ()):
            p = os.path.join(di, fn)
            if os.path.isfile(p) and fn not in have and fn not in SKIP_LISTING and not _excluded(key, fn):
                m = TITLE_RE.search(open(p, encoding="utf-8").read())
                listing[key].append((label_for(fn, m.group(1) if m else None), fn))

    for k in listing:                       # stimmige Reihenfolge herstellen
        listing[k].sort(key=lambda ti: _ordidx(k, ti[1]))
    write_hub(listing)
    for r in REPOS:
        write_sub(r, listing[r["key"]])
    write_anleitung()
    open(os.path.join(BIO, "CNAME"), "w").write("bio.mibaso.de\n")
    # eigene deploy.yml (ohne sw.js-Zwang, da bio keine Offline-Hülle hat)
    wf_dst = os.path.join(BIO, ".github", "workflows", "deploy.yml")
    os.makedirs(os.path.dirname(wf_dst), exist_ok=True)
    open(wf_dst, "w", encoding="utf-8").write(DEPLOY_YML)
    # Auto-Sync-Workflow BEWUSST NICHT mehr schreiben: sein „rm -rf flora fauna"
    # würde die Forscherpass-Master löschen, die seit Juli 2026 nur in bio leben.
    # bio wird daher von Hand gebaut (python3 bio/bio/build_bio.py). Eine evtl. alte
    # sync.yml wird entfernt.
    _sy_old = os.path.join(BIO, ".github", "workflows", "sync.yml")
    if os.path.isfile(_sy_old):
        try: os.remove(_sy_old)
        except OSError: pass
    # .gitignore (schließt Build-Junk und die CI-Quell-Checkouts aus)
    open(os.path.join(BIO, ".gitignore"), "w", encoding="utf-8").write(GITIGNORE)
    # Service Worker: network-first für Seiten (immer aktuell, kein „App schließen")
    open(os.path.join(BIO, "sw.js"), "w", encoding="utf-8").write(SW_JS)

    n = sum(len(v) for v in listing.values())
    print(f"OK: {n} Pfade gelistet, {total_imgs} Bilder kopiert.")

SW_JS = '''/* bio Service Worker — network-first für Seiten (immer aktuell), SWR für Bilder.
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
'''

DEPLOY_YML = '''name: bio zu GitHub Pages veroeffentlichen
on:
  push:
    branches: [main]
  workflow_dispatch:
permissions:
  contents: read
  pages: write
  id-token: write
concurrency:
  group: pages
  cancel-in-progress: true
jobs:
  build-deploy:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Dateien holen
        uses: actions/checkout@v4
      - name: Pages vorbereiten
        uses: actions/configure-pages@v5
      - name: Seite verpacken
        uses: actions/upload-pages-artifact@v3
        with:
          path: .
      - name: Veroeffentlichen
        id: deployment
        uses: actions/deploy-pages@v4
        continue-on-error: true
      - name: Zweiter Versuch bei Timeout
        if: steps.deployment.outcome == 'failure'
        uses: actions/deploy-pages@v4
'''

GITIGNORE = "/bio/\n_src/\n.DS_Store\n**/.DS_Store\n"

MANIFEST = '''{
  "name": "Bio Mibaso",
  "short_name": "Bio Mibaso",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#F7F3E8",
  "theme_color": "#2F4F3E",
  "icons": [
    {"src": "/assets/icon-192.png", "sizes": "192x192", "type": "image/png"},
    {"src": "/assets/icon-512.png", "sizes": "512x512", "type": "image/png"},
    {"src": "/assets/icon-192-maskable.png", "sizes": "192x192", "type": "image/png", "purpose": "maskable"},
    {"src": "/assets/icon-512-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}
  ]
}
'''

SYNC_YML = '''name: bio Auto-Sync (flora + fauna)
on:
  schedule:
    - cron: '17 4 * * *'
  workflow_dispatch:
permissions:
  contents: write
  pages: write
  id-token: write
concurrency:
  group: pages
  cancel-in-progress: false
jobs:
  sync:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: bio holen
        uses: actions/checkout@v4
      - name: flora holen
        uses: actions/checkout@v4
        with:
          repository: michlbaur-creator/flora
          path: _src/flora
      - name: fauna holen
        uses: actions/checkout@v4
        with:
          repository: michlbaur-creator/fauna
          path: _src/fauna
      - name: Alten Build entfernen
        run: rm -rf flora fauna index.html
      - name: Neu zusammenbauen
        env:
          BIO_SRC_ROOT: ${{ github.workspace }}/_src
          BIO_OUT: ${{ github.workspace }}
        run: python3 build_bio.py
      - name: Aenderungen sichern
        run: |
          rm -rf _src
          git config user.name "bio-sync"
          git config user.email "actions@users.noreply.github.com"
          git add -A
          if git diff --cached --quiet; then
            echo "Keine Aenderungen."
          else
            git commit -m "Auto-Sync: Lernpfade aus flora/fauna aktualisiert"
            git push
          fi
      - name: Pages vorbereiten
        uses: actions/configure-pages@v5
      - name: Seite verpacken
        uses: actions/upload-pages-artifact@v3
        with:
          path: .
      - name: Veroeffentlichen
        id: deployment
        uses: actions/deploy-pages@v4
        continue-on-error: true
'''

CSS = """
  :root{--gruen:#2F4F3E;--blau:#233D5C;--creme:#F7F3E8;--creme-tief:#EEE7D5;--pergament:#EDE3CC;
    --honig:#C28A3A;--honig-tief:#a9762c;--orange:#C4603A;--linie:#d7cfba;--tinte:#26312b;--akzent:#2F4F3E;
    --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;}
  *{box-sizing:border-box;-webkit-tap-highlight-color:transparent;}
  html{-webkit-text-size-adjust:100%;}
  body{margin:0;background:var(--creme);color:var(--tinte);font-family:Georgia,"Times New Roman",serif;
    line-height:1.5;padding-top:calc(env(safe-area-inset-top) + 12px);}
  .huelle{max-width:720px;margin:0 auto;padding:0 clamp(14px,4vw,28px) 14px;}
  .chips{display:flex;justify-content:center;gap:9px;flex-wrap:wrap;margin:2px 0 16px;}
  .chip{display:inline-flex;align-items:center;gap:6px;background:#fff;border:1px solid var(--linie);
    border-radius:999px;padding:5px 12px;font-family:var(--sans);font-size:13px;color:var(--tinte);text-decoration:none;}
  .chip:hover{border-color:var(--akzent);}
  .hero{position:relative;border-radius:18px;overflow:hidden;border:1px solid #cdbf9e;background:var(--pergament);}
  .hero img{display:block;width:100%;height:clamp(160px,32vw,250px);object-fit:cover;}
  .hero .cap{position:absolute;left:0;right:0;bottom:0;padding:18px;
    background:linear-gradient(transparent,rgba(18,28,20,.74));color:#fff;}
  .hero .marke{display:inline-block;font-family:var(--sans);font-size:clamp(18px,4.6vw,24px);font-weight:700;
    letter-spacing:.02em;color:#2F4F3E;background:rgba(255,255,255,.94);padding:3px 12px;border-radius:9px;margin-bottom:7px;}
  .hero h1{font-family:Georgia,serif;font-weight:normal;font-size:clamp(24px,6vw,34px);margin:2px 0 0;color:#fff;}
  .lead{font-family:var(--sans);font-size:14.5px;color:#5c6b60;text-align:left;margin:16px 2px 22px;}
  .lead p{margin:0 0 9px;} .lead p:last-child{margin:0;}
  .kacheln{display:grid;grid-template-columns:1fr 1fr;gap:14px;}
  .kachel{display:flex;flex-direction:column;gap:5px;text-decoration:none;color:#fff;border-radius:16px;
    padding:20px 18px;min-height:126px;justify-content:flex-end;box-shadow:0 4px 16px rgba(0,0,0,.12);transition:transform .15s;}
  .kachel:hover{transform:translateY(-2px);}
  .kachel .ke{font-size:30px;line-height:1;} .kachel .kt{font-family:Georgia,serif;font-size:22px;}
  .kachel .kb{font-family:var(--sans);font-size:12.5px;opacity:.92;}
  .k-flora{background:linear-gradient(150deg,#3A5F4A,#2F4F3E);}
  .k-fauna{background:linear-gradient(150deg,#33587c,#233D5C);}
  @media (max-width:520px){.kacheln{grid-template-columns:1fr;}}
  .subkopf{font-family:var(--sans);margin:2px 0 4px;}
  .zurueck{font-size:13px;font-weight:600;color:var(--akzent);text-decoration:none;}
  .subtitel{display:flex;align-items:center;gap:8px;font-family:var(--sans);font-weight:700;
    font-size:15px;color:#fff;background:var(--akzent);border-radius:8px;padding:9px 16px;margin:8px 0 18px;}
  .liste{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:10px;}
  .pfad{display:flex;align-items:center;gap:11px;text-decoration:none;color:var(--tinte);background:#fff;
    border:1px solid var(--linie);border-radius:13px;padding:13px 15px;transition:transform .14s,box-shadow .14s,border-color .14s;}
  .pfad:hover{transform:translateY(-1px);box-shadow:0 4px 14px rgba(0,0,0,.08);border-color:var(--akzent);}
  .pfad .dot{flex:0 0 auto;width:10px;height:10px;border-radius:50%;background:var(--akzent);}
  .pfad .pt{flex:1 1 auto;font-size:16px;} .pfad .pf{flex:0 0 auto;color:#b7b0a0;font-size:18px;}
  .pfad .ptxt{flex:1 1 auto;min-width:0;}
  .pfad .pt2{display:block;font-size:16px;}
  .pfad .psub{display:block;font-family:var(--sans);font-size:12px;color:#6f7b70;margin-top:2px;line-height:1.3;}
  .badge{flex:0 0 auto;font-family:var(--sans);font-size:10.5px;font-weight:700;letter-spacing:.03em;
    padding:2px 8px;border-radius:999px;text-transform:uppercase;}
  .badge-l{background:#e7efe4;color:#3a5f4a;} .badge-u{background:#efe6d2;color:#8a6a2e;}
  .badge-ext{background:#f1e7d6;color:#9a6a3a;white-space:nowrap;}
  .pfad-ext .pt2{display:inline;} .pfad-ext{align-items:center;}
  .gt-hint{font-family:var(--sans);font-size:12.5px;color:#8a8578;margin:-6px 0 12px;font-style:italic;}
  .pfad .pic{flex:0 0 auto;width:34px;height:34px;border-radius:10px;display:flex;align-items:center;justify-content:center;}
  .pfad .pic svg{width:19px;height:19px;}
  .gt{font-family:var(--sans);font-size:12px;letter-spacing:.16em;text-transform:uppercase;
    color:var(--honig);font-weight:700;margin:26px 0 12px;padding-bottom:8px;border-bottom:1px solid var(--linie);}
  .aktion-banner{display:flex;align-items:center;gap:14px;margin:6px 0 8px;text-decoration:none;
    background:#fff;border:1px solid var(--linie);border-left:4px solid var(--honig);border-radius:14px;
    padding:12px 14px;color:var(--akzent);box-shadow:0 2px 10px rgba(0,0,0,.06);transition:transform .12s,border-color .15s;}
  .aktion-banner:hover{transform:translateY(-2px);border-color:#cdbf9e;}
  .aktion-banner img{flex:0 0 auto;width:56px;height:76px;object-fit:cover;border-radius:8px;border:1px solid var(--linie);background:var(--creme-tief);}
  .aktion-banner .ab-tx{flex:1;min-width:0;}
  .ab-eyebrow{display:block;font-family:var(--sans);font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--honig);font-weight:700;}
  .aktion-banner strong{display:block;font-size:1.1rem;font-weight:normal;margin:2px 0;line-height:1.15;}
  .ab-sub{display:block;font-family:var(--sans);font-size:12.5px;color:#6f7b86;line-height:1.35;}
  .ab-pf{margin-left:auto;color:var(--honig);font-size:20px;flex:0 0 auto;}
  footer.fuss{background:#fff;border:1px solid var(--linie);margin-top:34px;
    padding:18px;padding-bottom:max(22px,calc(env(safe-area-inset-bottom) + 14px));border-radius:14px;}
  footer.fuss .fin{max-width:640px;margin:0 auto;}
  footer.fuss .echips{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px;}
  footer.fuss .echip{font-family:var(--sans);font-size:12.5px;color:var(--honig-tief);text-decoration:none;
    border:1px solid var(--honig);border-radius:999px;padding:4px 11px;}
  footer.fuss .echip:hover{background:var(--honig);color:#fff;}
  footer.fuss .klein{font-family:var(--sans);font-size:12px;color:#8a8578;line-height:1.8;}
  footer.fuss a{color:var(--honig-tief);}
  footer.fuss .essenz{font-family:Georgia,serif;font-style:italic;font-size:14px;color:#5c6b60;margin:0 0 12px;}
  footer.fuss .app-btns{display:flex;gap:10px;flex-wrap:wrap;margin:0 0 12px;}
  footer.fuss .appbtn{display:inline-flex;align-items:center;gap:7px;font-family:var(--sans);font-size:14px;font-weight:600;
    background:#fff;border:1px solid #d8ccb2;border-radius:999px;padding:7px 15px;text-decoration:none;box-shadow:0 1px 3px rgba(0,0,0,.06);}
  footer.fuss .app-flora{color:#2F4F3E;border-color:#bcd0a0;} footer.fuss .app-fauna{color:#233D5C;border-color:#a9c0dc;}
  footer.fuss .appbtn:hover{border-color:#8a96a1;}
  .topbar{display:flex;justify-content:flex-end;margin:0 0 12px;}
  .topbtn{display:inline-flex;align-items:center;gap:5px;font-family:var(--sans);font-size:12px;font-weight:600;
    color:var(--honig-tief);background:#fff;border:1px solid var(--honig);border-radius:999px;padding:4px 11px;text-decoration:none;}
  .topbtn:hover{background:var(--honig);color:#fff;}
  .lead a{color:var(--gruen);font-weight:600;text-decoration:none;border-bottom:1.5px solid var(--honig);}
  .hero-apps{position:absolute;top:10px;right:10px;display:flex;gap:7px;z-index:2;}
  .hero-apps .happ{display:inline-flex;align-items:center;gap:5px;font-family:var(--sans);font-size:12.5px;font-weight:600;
    color:#26312b;background:rgba(255,255,255,.93);border-radius:999px;padding:5px 11px;text-decoration:none;box-shadow:0 1px 5px rgba(20,30,20,.28);}
  .hero-apps .happ:hover{background:#fff;}
  .anl h2{font-family:Georgia,serif;font-weight:normal;color:var(--gruen);font-size:21px;margin:22px 0 6px;}
  .anl ol{font-family:var(--sans);font-size:15px;padding-left:22px;margin:6px 0;} .anl li{margin:6px 0;}
  .anl .tipp{font-family:var(--sans);font-size:13px;color:#6b5340;background:var(--creme-tief);border-radius:10px;padding:10px 13px;margin:10px 0 0;}
"""

def _shell(title, theme, body, akzent=None):
    style = f' style="--akzent:{akzent}"' if akzent else ""
    return ('<!DOCTYPE html><html lang="de"><head><meta charset="UTF-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
            f'<title>{title}</title><meta name="theme-color" content="{theme}">'
            '<link rel="icon" href="/assets/icon.svg" type="image/svg+xml">'
            '<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">'
            '<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">'
            '<link rel="manifest" href="/manifest.webmanifest">'
            '<meta name="apple-mobile-web-app-capable" content="yes">'
            '<meta name="mobile-web-app-capable" content="yes">'
            '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">'
            '<meta name="apple-mobile-web-app-title" content="Bio Mibaso">'
            f'<style>{CSS}</style></head><body{style}><div class="huelle">{body}</div>'
            '<script>if("serviceWorker" in navigator){navigator.serviceWorker.register("/sw.js")'
            '.then(function(reg){if(reg){reg.update();'
            'document.addEventListener("visibilitychange",function(){'
            'if(document.visibilityState==="visible")reg.update();});'
            'setInterval(function(){reg.update();},60*60*1000);}});'
            'navigator.serviceWorker.addEventListener("controllerchange",function(){'
            'if(window.__reloaded)return;window.__reloaded=true;location.reload();});}</script>'
            '</body></html>')

def _chips():
    return ('<nav class="chips"><a class="chip" href="https://flora.mibaso.de/">🌼 Flora</a>'
            '<a class="chip" href="https://fauna.mibaso.de/">🦋 Fauna</a></nav>')

def _footer(base=""):
    return (f'<footer class="fuss"><div class="fin">'
            f'<div class="echips"><a class="echip" href="{base}ueber/">Über mich</a>'
            f'<a class="echip" href="{base}impressum/">Impressum &amp; Datenschutz</a></div>'
            f'<div class="klein">© 2026 Michael Baur · Kontakt: <a href="mailto:mibaur@me.com">mibaur@me.com</a></div>'
            f'</div></footer>')

def write_hub(listing):
    nf, na = len(listing["flora"]), len(listing["fauna"])
    body = ('<div class="topbar"><a class="topbtn" id="installBtn" href="anleitung.html">📱 Als App aufs Handy</a></div>'
        '<div class="hero"><img src="fauna/images/wiese/wiese-sommer.png" alt="Blühende Wiese" '
        'onerror="this.style.display=\'none\'">'
        '<div class="hero-apps"><a class="happ" href="https://flora.mibaso.de/">🌼 Flora</a>'
        '<a class="happ" href="https://fauna.mibaso.de/">🦋 Fauna</a></div>'
        '<div class="cap"><div class="marke">Bio Mibaso</div>'
        '<h1>Lernpfade für Naturentdecker</h1></div></div>'
        '<div class="lead"><p>Dein Lernort zu <a href="https://flora.mibaso.de/">Flora</a> und '
        '<a href="https://fauna.mibaso.de/">Fauna</a>:</p>'
        '<p>Interaktive Stationen zum Erkunden, Verstehen und Ausprobieren. '
        'Fülle deinen Forschungspass mit Leben!</p></div>'
        '<div class="kacheln">'
        f'<a class="kachel k-flora" href="flora/"><span class="ke">🌼</span>'
        f'<span class="kt">Flora verstehen</span><span class="kb">{nf} Lernpfade zur Welt der Pflanzen</span></a>'
        f'<a class="kachel k-fauna" href="fauna/"><span class="ke">🦋</span>'
        f'<span class="kt">Fauna verstehen</span><span class="kb">{na} Lernpfade zur Welt der Tiere</span></a>'
        '</div>' + _footer("") +
        '<script>if(window.matchMedia("(display-mode: standalone)").matches||window.navigator.standalone)'
        '{var b=document.getElementById("installBtn");if(b)b.style.display="none";}</script>')
    open(os.path.join(BIO, "index.html"), "w", encoding="utf-8").write(
        _shell("Bio Mibaso — Lernpfade für Naturentdecker", "#2F4F3E", body))

def _pfad(t, fn, col):
    b = "u" if _typ(fn) == "Übersicht" else "l"
    badge = "" if fn in NO_BADGE else f'<span class="badge badge-{b}">{_typ(fn)}</span>'
    return (f'<a class="pfad" href="interaktiv/{html.escape(fn)}">'
            f'<span class="pic" style="background:{col}1f;color:{col}">{_icon(fn)}</span>'
            f'<span class="pt">{html.escape(t)}</span>'
            f'{badge}'
            f'<span class="pf">›</span></a>')

def _extra_pfad(basis, fn, icon, titel, sub, col):
    d = _G.get(icon, _G["leaf"])
    svg = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
           f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="{d}"/></svg>')
    return (f'<a class="pfad pfad-ext" href="{basis}{html.escape(fn)}" target="_blank" rel="noopener">'
            f'<span class="pic" style="background:{col}1f;color:{col}">{svg}</span>'
            f'<span class="ptxt"><span class="pt2">{html.escape(titel)}</span>'
            f'<span class="psub">{html.escape(sub)}</span></span>'
            f'<span class="badge badge-ext">Flora-App&nbsp;↗</span></a>')

def _pass_banner(p):
    return (f'<a class="aktion-banner" href="{p["href"]}">'
            f'<img src="{p["img"]}" alt="" aria-hidden="true" onerror="this.style.display=\'none\'">'
            f'<span class="ab-tx"><span class="ab-eyebrow">{html.escape(p["eyebrow"])}</span>'
            f'<strong>{html.escape(p["titel"])}</strong>'
            f'<span class="ab-sub">{html.escape(p["sub"])}</span></span>'
            f'<span class="ab-pf" aria-hidden="true">›</span></a>')

def write_sub(r, items):
    key = r["key"]
    by_fn = {fn: t for t, fn in items}
    used, sections = set(), []
    for gt, col, fns in GROUPS.get(key, []):
        rows = [_pfad(by_fn[fn], fn, r["akzent"]) for fn in fns if fn in by_fn]
        used.update(fn for fn in fns if fn in by_fn)
        if rows:
            sections.append(f'<h2 class="gt">{html.escape(gt)}</h2>'
                            f'<div class="liste">{"".join(rows)}</div>')
    rest = [(t, fn) for t, fn in items if fn not in used]
    if rest:
        rows = "".join(_pfad(t, fn, r["akzent"]) for t, fn in rest)
        sections.append('<h2 class="gt">Mehr entdecken</h2>'
                        f'<div class="liste">{rows}</div>')
    ex = EXTRA.get(key)
    if ex:
        rows = "".join(_extra_pfad(ex["basis"], fn, ic, t, s, r["akzent"])
                       for (fn, ic, t, s) in ex["kacheln"])
        hint = (f'<p class="gt-hint">{html.escape(ex["hinweis"])}</p>'
                if ex.get("hinweis") else "")
        sections.append(f'<h2 class="gt">{html.escape(ex["titel"])}</h2>{hint}'
                        f'<div class="liste">{rows}</div>')
    banner = _pass_banner(r["pass"]) if r.get("pass") else ""
    body = ('<div class="subkopf"><a class="zurueck" href="../index.html">‹ Bio Mibaso</a></div>'
            + f'<div class="subtitel"><span>{r["emoji"]}</span> {html.escape(r["label"])}</div>'
            + banner + "".join(sections) + _footer("../"))
    open(os.path.join(BIO, r["key"], "index.html"), "w", encoding="utf-8").write(
        _shell(r["label"] + " — Bio Mibaso",r["akzent"], body, akzent=r["akzent"]))

def write_anleitung():
    steps = (
        '<div class="anl">'
        '<h1 style="font-family:Georgia,serif;font-weight:normal;color:var(--gruen);'
        'font-size:clamp(24px,6vw,32px);margin:6px 0 4px;">Als App aufs Handy legen</h1>'
        '<p class="lead" style="text-align:left;margin:8px 0 4px;max-width:none;">So liegt Bio Mibaso wie '
        'eine echte App auf dem Startbildschirm — praktisch für den Unterricht.</p>'
        '<h2>📱 iPhone / iPad</h2>'
        '<ol><li>Im Browser oben rechts auf das <em>Teilen-Symbol</em></li>'
        '<li><em>„In Chrome (alternativ Safari) öffnen"</em></li>'
        '<li>Dort noch einmal auf das <em>Teilen-Symbol</em> (evtl. vorher <em>„Mehr anzeigen"</em>) → '
        '<em>„Zum Home-Bildschirm"</em> → <em>„Hinzufügen"</em></li></ol>'
        '<h2>🤖 Android</h2>'
        '<p style="font-family:var(--sans);font-size:14px;margin:0 0 4px;"><strong>In Chrome:</strong></p>'
        '<ol><li>Oben rechts auf das <em>Drei-Punkte-Menü</em> (⋮)</li>'
        '<li><em>„App installieren"</em> oder <em>„Zum Startbildschirm hinzufügen"</em></li>'
        '<li>Auf <em>„Installieren"</em> bzw. <em>„Hinzufügen"</em> tippen</li></ol>'
        '<p class="tipp">Tipp: Du findest bio auch, wenn du <strong>bio.mibaso.de</strong> in die Suchmaske '
        'eingibst — der Weg über Chrome/Safari funktioniert genauso.</p></div>')
    body = ('<div class="subkopf"><a class="zurueck" href="index.html">‹ Bio Mibaso</a></div>'
            + steps + _footer(""))
    open(os.path.join(BIO, "anleitung.html"), "w", encoding="utf-8").write(
        _shell("Anleitung — Bio Mibaso","#2F4F3E", body))

if __name__ == "__main__":
    build()
