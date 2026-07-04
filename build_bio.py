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

ROOT = _find_root(os.path.dirname(os.path.abspath(__file__)))  # Documents/GitHub
# Ziel = das echte git-Repo (kann verschachtelt sein: bio/ oder bio/bio/)
_cands = [os.path.join(ROOT, "bio", "bio"), os.path.join(ROOT, "bio")]
BIO = next((c for c in _cands if os.path.isdir(os.path.join(c, ".git"))), os.path.join(ROOT, "bio"))

REPOS = [
    {"key": "flora", "label": "Flora — Pflanzen", "emoji": "🌼", "akzent": "#2F4F3E"},
    {"key": "fauna", "label": "Fauna — Tiere & Insekten", "emoji": "🦋", "akzent": "#233D5C"},
]
# Diese Dateien sind keine echten Lernpfade -> nicht auf der Startseite listen
SKIP_LISTING = {"tafel.html", "wiesenpass.html", "sammelpass.html"}

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
    # Rücklinks „zur App-Startseite" -> bio-Startseite (zwei Ebenen hoch)
    txt = txt.replace('href="../index.html"', 'href="../../index.html"')
    txt = txt.replace('href="../bestimmen.html"', 'href="../../index.html"')
    txt = txt.replace('href="../quiz/"', 'href="../../index.html"')
    txt = txt.replace('href="../interaktiv/"', 'href="../../index.html"')
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

            if fn not in SKIP_LISTING and not fn.endswith("-flyer.html"):
                m = TITLE_RE.search(raw)
                listing[key].append((clean_title(m.group(1)) if m else fn, key + "/interaktiv/" + fn))

    write_index(listing)
    open(os.path.join(BIO, "CNAME"), "w").write("bio.mibaso.de\n")
    # eigene deploy.yml (ohne sw.js-Zwang, da bio keine Offline-Hülle hat)
    wf_dst = os.path.join(BIO, ".github", "workflows", "deploy.yml")
    os.makedirs(os.path.dirname(wf_dst), exist_ok=True)
    open(wf_dst, "w", encoding="utf-8").write(DEPLOY_YML)
    # .gitignore (schließt evtl. verschachtelten Build-Junk aus)
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

GITIGNORE = "/bio/\n.DS_Store\n**/.DS_Store\n"

def write_index(listing):
    parts = []
    for r in REPOS:
        items = "".join(
            f'<a class="pfad" href="{html.escape(href)}"><span class="dot"></span>'
            f'<span class="pt">{html.escape(titel)}</span><span class="pf">›</span></a>\n'
            for titel, href in listing[r["key"]]
        )
        parts.append(f'''  <section class="gruppe" style="--akzent:{r['akzent']}">
    <h2><span class="ge">{r['emoji']}</span> {html.escape(r['label'])}</h2>
    <div class="liste">
{items}    </div>
  </section>''')
    body = "\n".join(parts)
    doc = INDEX_TMPL.replace("<!--GRUPPEN-->", body)
    open(os.path.join(BIO, "index.html"), "w", encoding="utf-8").write(doc)

INDEX_TMPL = '''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>bio.mibaso — Lernpfade für den Unterricht</title>
<meta name="description" content="Interaktive Lernpfade aus Flora und Fauna Mibaso, gebündelt für den Biologie-Unterricht.">
<meta name="theme-color" content="#2F4F3E">
<style>
  :root{--gruen:#2F4F3E;--blau:#233D5C;--creme:#F7F3E8;--creme-tief:#EEE7D5;
    --honig:#C28A3A;--linie:#d8ccb2;--tinte:#26312b;
    --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;}
  *{box-sizing:border-box;-webkit-tap-highlight-color:transparent;}
  body{margin:0;background:var(--creme);color:var(--tinte);font-family:Georgia,"Times New Roman",serif;
    line-height:1.5;padding:calc(env(safe-area-inset-top) + 4vh) 0 60px;}
  .huelle{max-width:720px;margin:0 auto;padding:0 clamp(14px,4vw,28px);}
  header{text-align:center;margin-bottom:6px;}
  .marke{font-family:var(--sans);font-size:12px;font-weight:700;letter-spacing:.14em;
    text-transform:uppercase;color:var(--honig);}
  h1{font-size:clamp(26px,7vw,38px);font-weight:normal;margin:8px 0 6px;color:var(--gruen);}
  .unter{font-family:var(--sans);font-size:14.5px;color:#5c6b60;max-width:46ch;margin:0 auto 8px;}
  .gruppe{margin-top:30px;}
  .gruppe h2{font-family:Georgia,serif;font-weight:normal;font-size:clamp(19px,5vw,24px);
    color:var(--akzent);border-bottom:2px solid var(--akzent);padding-bottom:8px;margin:0 0 12px;}
  .gruppe h2 .ge{font-size:1.1em;}
  .liste{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:10px;}
  .pfad{display:flex;align-items:center;gap:11px;text-decoration:none;color:var(--tinte);
    background:#fff;border:1px solid var(--linie);border-radius:13px;padding:13px 15px;
    transition:transform .14s,box-shadow .14s,border-color .14s;}
  .pfad:hover{transform:translateY(-1px);box-shadow:0 4px 14px rgba(0,0,0,.08);border-color:var(--akzent);}
  .pfad .dot{flex:0 0 auto;width:10px;height:10px;border-radius:50%;background:var(--akzent);}
  .pfad .pt{flex:1 1 auto;font-size:16px;}
  .pfad .pf{flex:0 0 auto;color:#b7b0a0;font-size:18px;}
  footer{margin-top:38px;text-align:center;font-family:var(--sans);font-size:12.5px;color:#8a8578;}
  footer a{color:inherit;}
</style>
</head>
<body>
<div class="huelle">
  <header>
    <div class="marke">bio.mibaso</div>
    <h1>Lernpfade für den Unterricht</h1>
    <p class="unter">Interaktive Stationen aus Flora und Fauna Mibaso — zum Erkunden, Verstehen und Selbst-Ausprobieren. Ganz ohne Konto, direkt im Browser.</p>
  </header>
<!--GRUPPEN-->
  <footer>© 2026 Michael Baur · Zusammengestellt für den Biologie-Unterricht<br>
    Teil des Mibaso-Universums · <a href="https://fauna.mibaso.de">fauna</a> · <a href="https://flora.mibaso.de">flora</a></footer>
</div>
</body>
</html>
'''

if __name__ == "__main__":
    build()
