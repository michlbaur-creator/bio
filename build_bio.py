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
    {"key": "flora", "label": "Flora Mibaso", "emoji": "🌼", "akzent": "#2F4F3E"},
    {"key": "fauna", "label": "Fauna Mibaso", "emoji": "🦋", "akzent": "#233D5C"},
]
# Kopiert, aber nicht auf der Startseite gelistet (z.B. der Pass als Footer-Ziel)
SKIP_LISTING = {"tafel.html", "wiesenpass.html", "sammelpass.html"}
# Ganz aus bio ausschließen (nicht kopieren, nicht listen): Staunen-Häppchen,
# Quizze/Tests und Ordnen-/Zuordnungs-Spiele — bio zeigt nur die echten Lernpfade.
# Einträge ohne Repo-Präfix gelten für beide; mit Präfix nur für ein Repo.
EXCLUDE = {"tierquiz.html", "gesamttest.html", "pflanze-zuordnung.html", "verwandte-finden.html",
           "flora/systematik.html",
           # alle „Warum"-Pfade
           "blumen-nachts.html", "kletten.html", "schaumzikaden.html", "sonnenblumen.html",
           # Energie: die vollständige „Pflanzen & Energie" (pflanzen-energie) bleibt;
           # die Übersichts-Hülle energie-pfad und „Der Gas-Kreislauf" raus.
           "energie-pfad.html", "energie-kreislauf-anim.html"}
def _excluded(key, fn):
    return (fn.endswith("-flyer.html") or fn.startswith("staunen-")
            or fn in EXCLUDE or f"{key}/{fn}" in EXCLUDE)

# Stimmige Reihenfolge je Repo (nicht gelistete kommen alphabetisch danach).
ORDER = {
    "flora": ["pflanze-erklaerung.html", "pflanze-verstehen.html", "pflanzen-energie.html",
              "bluete-zoom.html", "bestaeubung-erklaerung.html", "bestaeubung-animiert.html",
              "bluetenoekologie.html", "samenverbreitung.html", "jahreszeiten-baum.html",
              "kreislauf.html", "pflanzenstrategien.html"],
    "fauna": ["schluessel.html", "systematik.html", "stammbaum.html", "verwandlung.html",
              "bestaeubung.html", "lebensraum.html", "nahrungsnetz.html", "wiese-lebt.html",
              "insektenschwund.html"],
}
# Typ-Kennzeichnung der Kacheln: „Übersicht" (Einzelseite) vs. „Lernpfad" (mehrstufig).
UEBERSICHT = {"pflanze-erklaerung.html", "bestaeubung-erklaerung.html", "bluetenoekologie.html",
              "samenverbreitung.html", "pflanzenstrategien.html", "insektenschwund.html"}
def _typ(fn):
    return "Übersicht" if fn in UEBERSICHT else "Lernpfad"
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

def rewrite_links(txt):
    # ../index.html zeigt jetzt korrekt auf die Repo-Unterseite (bio/flora/ bzw bio/fauna/).
    # Andere App-Rücklinks auf dieselbe Unterseite biegen.
    for a in ("../bestimmen.html", "../quiz/", "../interaktiv/"):
        txt = txt.replace('href="' + a + '"', 'href="../index.html"')
    return txt

def copytree(src, dst):
    if os.path.isdir(src):
        shutil.copytree(src, dst, dirs_exist_ok=True)

def build():
    # Kein Vorab-Löschen (im verbundenen Ordner nicht erlaubt) — Dateien werden
    # überschrieben. Für einen komplett sauberen Neubau bio/flora & bio/fauna
    # vorher von Hand leeren.
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
                listing[key].append((clean_title(m.group(1)) if m else fn, fn))

    # Startseiten-Bausteine aus Flora übernehmen: Über mich, Impressum, Anleitung, Assets
    copytree(os.path.join(ROOT, "flora", "assets"),    os.path.join(BIO, "assets"))
    copytree(os.path.join(ROOT, "flora", "ueber"),     os.path.join(BIO, "ueber"))
    copytree(os.path.join(ROOT, "flora", "impressum"), os.path.join(BIO, "impressum"))
    copytree(os.path.join(ROOT, "flora", "anleitung"), os.path.join(BIO, "anleitung"))
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
    # Auto-Sync-Workflow (holt flora/fauna, baut neu, committet & deployt)
    sy_dst = os.path.join(BIO, ".github", "workflows", "sync.yml")
    open(sy_dst, "w", encoding="utf-8").write(SYNC_YML)
    # .gitignore (schließt Build-Junk und die CI-Quell-Checkouts aus)
    open(os.path.join(BIO, ".gitignore"), "w", encoding="utf-8").write(GITIGNORE)

    n = sum(len(v) for v in listing.values())
    print(f"OK: {n} Pfade gelistet, {total_imgs} Bilder kopiert.")

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
    --honig:#C28A3A;--honig-tief:#a9762c;--linie:#d8ccb2;--tinte:#26312b;--akzent:#2F4F3E;
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
  .hero .marke{font-family:var(--sans);font-size:11.5px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;opacity:.92;}
  .hero h1{font-family:Georgia,serif;font-weight:normal;font-size:clamp(24px,6vw,34px);margin:2px 0 0;color:#fff;}
  .lead{font-family:var(--sans);font-size:14.5px;color:#5c6b60;text-align:center;max-width:48ch;margin:14px auto 22px;}
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
  .subtitel{display:inline-flex;align-items:center;gap:8px;font-family:var(--sans);font-weight:700;
    font-size:15px;color:#fff;background:var(--akzent);border-radius:8px;padding:7px 14px;margin:8px 0 16px;}
  .liste{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:10px;}
  .pfad{display:flex;align-items:center;gap:11px;text-decoration:none;color:var(--tinte);background:#fff;
    border:1px solid var(--linie);border-radius:13px;padding:13px 15px;transition:transform .14s,box-shadow .14s,border-color .14s;}
  .pfad:hover{transform:translateY(-1px);box-shadow:0 4px 14px rgba(0,0,0,.08);border-color:var(--akzent);}
  .pfad .dot{flex:0 0 auto;width:10px;height:10px;border-radius:50%;background:var(--akzent);}
  .pfad .pt{flex:1 1 auto;font-size:16px;} .pfad .pf{flex:0 0 auto;color:#b7b0a0;font-size:18px;}
  .badge{flex:0 0 auto;font-family:var(--sans);font-size:10.5px;font-weight:700;letter-spacing:.03em;
    padding:2px 8px;border-radius:999px;text-transform:uppercase;}
  .badge-l{background:#e7efe4;color:#3a5f4a;} .badge-u{background:#efe6d2;color:#8a6a2e;}
  footer.fuss{background:var(--creme-tief);border-top:3px solid var(--honig);margin-top:34px;
    padding:18px;padding-bottom:max(22px,calc(env(safe-area-inset-bottom) + 14px));border-radius:0 0 14px 14px;}
  footer.fuss .fin{max-width:640px;margin:0 auto;}
  footer.fuss .echips{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px;}
  footer.fuss .echip{font-family:var(--sans);font-size:12.5px;color:var(--honig-tief);text-decoration:none;
    border:1px solid var(--honig);border-radius:999px;padding:4px 11px;}
  footer.fuss .echip:hover{background:var(--honig);color:#fff;}
  footer.fuss .klein{font-family:var(--sans);font-size:12.5px;color:#8a8578;line-height:1.9;}
  footer.fuss a{color:var(--honig-tief);}
  .topbar{display:flex;justify-content:flex-end;margin:0 0 12px;}
  .topbtn{display:inline-flex;align-items:center;gap:6px;font-family:var(--sans);font-size:13px;font-weight:600;
    color:var(--honig-tief);background:#fff;border:1px solid var(--honig);border-radius:999px;padding:6px 14px;text-decoration:none;}
  .topbtn:hover{background:var(--honig);color:#fff;}
  .lead a{color:var(--gruen);font-weight:600;text-decoration:none;border-bottom:1.5px solid var(--honig);}
  .anl h2{font-family:Georgia,serif;font-weight:normal;color:var(--gruen);font-size:21px;margin:22px 0 6px;}
  .anl ol{font-family:var(--sans);font-size:15px;padding-left:22px;margin:6px 0;} .anl li{margin:6px 0;}
  .anl .tipp{font-family:var(--sans);font-size:13px;color:#6b5340;background:var(--creme-tief);border-radius:10px;padding:10px 13px;margin:10px 0 0;}
"""

def _shell(title, theme, body, akzent=None):
    style = f' style="--akzent:{akzent}"' if akzent else ""
    return ('<!DOCTYPE html><html lang="de"><head><meta charset="UTF-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
            f'<title>{title}</title><meta name="theme-color" content="{theme}">'
            '<link rel="icon" href="assets/icon.svg" type="image/svg+xml">'
            f'<style>{CSS}</style></head><body{style}><div class="huelle">{body}</div></body></html>')

def _chips():
    return ('<nav class="chips"><a class="chip" href="https://flora.mibaso.de/">🌼 Flora</a>'
            '<a class="chip" href="https://fauna.mibaso.de/">🦋 Fauna</a></nav>')

def _footer(base=""):
    return (f'<footer class="fuss"><div class="fin"><div class="echips">'
            f'<a class="echip" href="{base}ueber/">Über mich</a>'
            f'<a class="echip" href="{base}impressum/">Impressum &amp; Datenschutz</a></div>'
            f'<div class="klein">© 2026 Michael Baur · Kontakt: <a href="mailto:mibaur@me.com">mibaur@me.com</a><br>'
            f'Lernpfade aus Flora &amp; Fauna Mibaso — zusammengestellt für den Biologie-Unterricht.</div>'
            f'</div></footer>')

def write_hub(listing):
    nf, na = len(listing["flora"]), len(listing["fauna"])
    body = ('<div class="topbar"><a class="topbtn" href="anleitung.html">📲 App aufs Handy</a></div>'
        '<div class="hero"><img src="fauna/images/wiese/wiese-sommer.png" alt="Blühende Wiese" '
        'onerror="this.style.display=\'none\'"><div class="cap"><div class="marke">bio.mibaso</div>'
        '<h1>Lernpfade für den Unterricht</h1></div></div>'
        '<p class="lead">Interaktive Stationen aus '
        '<a href="https://flora.mibaso.de/">Flora</a> und '
        '<a href="https://fauna.mibaso.de/">Fauna</a> Mibaso — zum Erkunden, Verstehen und Selbst-Ausprobieren.</p>'
        '<div class="kacheln">'
        f'<a class="kachel k-flora" href="flora/"><span class="ke">🌼</span>'
        f'<span class="kt">Flora Mibaso</span><span class="kb">{nf} Lernpfade rund um Pflanzen</span></a>'
        f'<a class="kachel k-fauna" href="fauna/"><span class="ke">🦋</span>'
        f'<span class="kt">Fauna Mibaso</span><span class="kb">{na} Lernpfade rund um Tiere &amp; Insekten</span></a>'
        '</div>' + _footer(""))
    open(os.path.join(BIO, "index.html"), "w", encoding="utf-8").write(
        _shell("bio.mibaso — Lernpfade für den Unterricht", "#2F4F3E", body))

def write_sub(r, items):
    lis = "".join(
        f'<a class="pfad" href="interaktiv/{html.escape(fn)}"><span class="dot"></span>'
        f'<span class="pt">{html.escape(t)}</span>'
        f'<span class="badge badge-{"u" if _typ(fn)=="Übersicht" else "l"}">{_typ(fn)}</span>'
        f'<span class="pf">›</span></a>'
        for t, fn in items)
    body = ('<div class="subkopf"><a class="zurueck" href="../index.html">‹ bio.mibaso</a></div>'
            + f'<div class="subtitel"><span>{r["emoji"]}</span> {html.escape(r["label"])}</div>'
            + f'<div class="liste">{lis}</div>' + _footer("../"))
    open(os.path.join(BIO, r["key"], "index.html"), "w", encoding="utf-8").write(
        _shell(r["label"] + " — bio.mibaso", r["akzent"], body, akzent=r["akzent"]))

def write_anleitung():
    steps = (
        '<div class="anl">'
        '<h1 style="font-family:Georgia,serif;font-weight:normal;color:var(--gruen);'
        'font-size:clamp(24px,6vw,32px);margin:6px 0 4px;">Als App aufs Handy legen</h1>'
        '<p class="lead" style="text-align:left;margin:8px 0 4px;max-width:none;">So liegt bio.mibaso wie '
        'eine echte App auf dem Startbildschirm — praktisch für den Unterricht.</p>'
        '<h2>📱 iPhone</h2>'
        '<p style="font-family:var(--sans);font-size:14px;margin:0 0 4px;"><strong>In Safari (am einfachsten):</strong></p>'
        '<ol><li>Oben auf das <em>Teilen-Symbol</em> (Kästchen mit Pfeil nach oben)</li>'
        '<li><em>„Zum Home-Bildschirm"</em> antippen (evtl. vorher <em>„Mehr anzeigen"</em>)</li>'
        '<li>Oben rechts auf <em>„Hinzufügen"</em></li></ol>'
        '<p style="font-family:var(--sans);font-size:14px;margin:8px 0 4px;"><strong>In einem anderen Browser '
        '(Chrome, Google-App &amp; Co.):</strong></p>'
        '<ol><li>Oben auf das <em>Teilen-Symbol</em> → <em>„In Safari öffnen"</em></li>'
        '<li>Dort oben nochmal das <em>Teilen-Symbol</em></li>'
        '<li><em>„Zum Home-Bildschirm"</em> → <em>„Hinzufügen"</em></li></ol>'
        '<h2>🤖 Android</h2>'
        '<p style="font-family:var(--sans);font-size:14px;margin:0 0 4px;"><strong>In Chrome:</strong></p>'
        '<ol><li>Oben rechts auf das <em>Drei-Punkte-Menü</em> (⋮)</li>'
        '<li><em>„App installieren"</em> oder <em>„Zum Startbildschirm hinzufügen"</em></li>'
        '<li>Auf <em>„Installieren"</em> bzw. <em>„Hinzufügen"</em> tippen</li></ol>'
        '<p class="tipp">Tipp: Du findest bio auch, wenn du <strong>bio.mibaso.de</strong> in die Suchmaske '
        'eingibst — der Weg über Chrome/Safari funktioniert genauso.</p></div>')
    body = ('<div class="subkopf"><a class="zurueck" href="index.html">‹ bio.mibaso</a></div>'
            + steps + _footer(""))
    open(os.path.join(BIO, "anleitung.html"), "w", encoding="utf-8").write(
        _shell("Anleitung — bio.mibaso", "#2F4F3E", body))

if __name__ == "__main__":
    build()
