# Bilder für „Expedition Wald" — Merkzettel für ChatGPT

**Wohin damit?** Alle Bilder als **JPG** nach `bio/bio/flora/images/wald/`.
**Vorher verkleinern** (spart Platz, Originale aus ChatGPT sind groß):
`convert bild.png -auto-orient -resize 1600x1600\> -strip -quality 82 ziel.jpg`

Fehlt ein Bild, zeigt der Pfad automatisch einen Platzhalter mit dem erwarteten
Dateinamen an — die App funktioniert also auch, bevor alle Bilder da sind.

---

## 1. Der Forscherpass — der wachsende Wald (Bühne oben im Pass)

Fünf Bilder **derselben Stelle aus demselben Blickwinkel**, die den Wald vom Zapfen bis
zum dichten Wald wachsen lassen. Der Pass blendet sie je nach Fortschritt ineinander —
deshalb ist es wichtig, dass Perspektive, Licht und Jahreszeit gleich bleiben und sich
**nur die Größe/Dichte der Bäume** ändert.

**Format:** breiter Panorama-Streifen, Seitenverhältnis **ca. 2,86 : 1** (z. B. 1600 × 560 px),
fotorealistisch, **ohne Text/Schrift**. Am besten als Serie erzeugen („dieselbe Szene, später").

| Datei | Ausführlicher Prompt |
| --- | --- |
| `wald/wald-1.jpg` | **Stufe 1 – Der Zapfen.** Weite Panorama-Aufnahme (2,86:1) einer sonnigen Waldlichtung. Im Vordergrund liegt auf moosigem Boden ein geöffneter brauner Zapfen mit einigen geflügelten Samen. Ringsum offener, fast kahler Boden, nur vereinzelt Grashalme. Im Hintergrund viel heller Himmel, ganz hinten nur die Andeutung eines Waldrandes. Weiches, warmes Morgenlicht. Fotorealistisch, ohne Text. |
| `wald/wald-2.jpg` | **Stufe 2 – Keimlinge.** Genau dieselbe Lichtung, gleicher Blickwinkel und gleiches Licht. Jetzt sprießen überall kleine grüne Keimlinge und junge Sämlinge (knöchel- bis kniehoch), teils Nadel-, teils Laubbäumchen. Noch sehr viel offener Himmel. |
| `wald/wald-3.jpg` | **Stufe 3 – Junge Bäumchen.** Dieselbe Stelle, gleicher Blickwinkel. Aus den Sämlingen sind junge Bäumchen von etwa 2–3 m Höhe geworden, locker verteilt, mit ersten kleinen Kronen. Der Boden ist grüner, etwas Unterwuchs. Der Himmel ist noch zu gut einem Drittel sichtbar. |
| `wald/wald-4.jpg` | **Stufe 4 – Heranwachsender Wald.** Dieselbe Stelle, gleicher Blickwinkel. Schlanke Bäume stehen dicht an dicht, die Kronen beginnen sich zu berühren, das Blätter-/Nadeldach schließt sich langsam, nur noch wenig Himmel dazwischen. Sattes Grün. |
| `wald/wald-5.jpg` | **Stufe 5 – Dichter, ausgewachsener Wald.** Dieselbe Stelle, gleicher Blickwinkel. Ein dichter, hoher Mischwald mit geschlossenem grünem Kronendach; schräge Sonnenstrahlen fallen durch das Laub, tiefes, lebendiges Grün. |

**Wichtig für den Überblend-Effekt:** immer denselben Bildausschnitt/Horizont wählen. Ein
markanter Punkt (z. B. ein großer Baum oder Felsen am Rand) hilft, damit die Stufen beim
Ineinanderblenden zusammenpassen.

Wenn die fünf Bilder da sind, lege ich sie als `wald-1.jpg` … `wald-5.jpg` ein (ersetzt die
bisherige Jahreszeiten-Serie) und setze das Vorschaubild des Wald-Banners auf die reife
Stufe 5.

---

## 2. Station „Stockwerke des Waldes"

| Datei | Motiv-Prompt |
| --- | --- |
| `wald/stockwerke-intro.jpg` | Stimmungsvoller Blick in einen Mischwald von unten nach oben, Lichtstrahlen durchs Kronendach. Querformat 16:10. |
| `wald/waldprofil.jpg` | **Wichtigstes Bild.** Seitliche Illustration/Querschnitt eines Waldes mit **vier klar gestapelten Stockwerken übereinander**: ganz oben große Baumkronen, darunter Sträucher, darunter Blumen/Farne, ganz unten Moos/Boden. Kindgerecht, klar, **ohne Beschriftung** (die Zahlen setzt die App). Hochformat/quadratisch, damit die vier Ebenen von oben nach unten passen. |
| `wald/schicht-baum.jpg` | Blick hoch in ein grünes Buchen-/Eichen-Kronendach gegen den Himmel. |
| `wald/schicht-strauch.jpg` | Sträucher und junge Bäume im Wald (Haselnuss, Holunder), etwa hüft- bis kopfhoch. |
| `wald/schicht-kraut.jpg` | Waldboden-Teppich aus Blumen, Farnen und Gräsern (z. B. Buschwindröschen). |
| `wald/schicht-moos.jpg` | Nahaufnahme Moose, Flechten und kleine Pilze auf dem feuchten Waldboden. |

**Hinweis zum Waldprofil:** Die vier antippbaren Punkte sitzen fest bei ungefähr
12 % (Baum), 42 % (Strauch), 68 % (Kraut) und 90 % (Moos) der Bildhöhe. Am besten
passt ein Bild, bei dem die Kronen oben, Sträucher in der oberen Mitte, Kräuter in
der unteren Mitte und Moos ganz unten liegen. (Zur Not verschiebe ich die Punkte
später an dein Bild.)

---

## 3. Station „Frühblüher" (Rennen ums Licht + unter der Erde)

| Datei | Motiv-Prompt |
| --- | --- |
| `wald/fruehblueher-intro.jpg` | Frühlingswald von oben nach unten, weiß-gelber Frühblüher-Teppich am Boden, Lichtstrahlen durch noch kahle Bäume. Querformat 16:10. |
| `wald/fruehblueher-maerz.jpg` | Waldboden im März: oben **kahle Baumkronen**, am Boden Buschwindröschen (weiß), Scharbockskraut (gelb) und Bärlauch. Ohne Beschriftung. Hoch-/Quadratformat. Punkte sitzen bei ca. 12 % (Kronen), 52 % (Buschwindröschen), 60 % (Scharbockskraut), 86 % (Bärlauch). |
| `wald/speicher-zwiebel.jpg` | Eine Zwiebel im Querschnitt (sichtbare Schichten) unter der Erde, kindgerechte Illustration. |
| `wald/speicher-knolle.jpg` | Eine dicke Knolle unter der Erde mit kleinem Austrieb. |
| `wald/speicher-rhizom.jpg` | Ein waagerechtes Rhizom (Wurzelstock) knapp unter der Erde, aus dem mehrere Triebe nach oben wachsen. |

## 4. Station „Wald im Jahreslauf" (die schöne Bildserie)

**Am besten derselbe Waldort viermal** – nur die Jahreszeit ändern, dann passt die Serie zusammen.

| Datei | Motiv-Prompt |
| --- | --- |
| `wald/jahreslauf-intro.jpg` | Stimmungsvoller Waldblick, der Jahreszeiten andeutet. Querformat 16:10. |
| `wald/jahr-fruehling.jpg` | Derselbe Waldort im Frühling: kahle/austreibende Bäume, Frühblüher-Teppich, zartes Grün. |
| `wald/jahr-sommer.jpg` | Derselbe Ort im Sommer: dichtes, sattgrünes Kronendach, schattiger Boden. |
| `wald/jahr-herbst.jpg` | Derselbe Ort im Herbst: buntes Laub, Pilze am Boden, warmes Licht. |
| `wald/jahr-winter.jpg` | Derselbe Ort im Winter: kahle Bäume, kühles Licht, evtl. etwas Schnee. |

## 5. Station „Waldboden – die Recyclinganlage"

| Datei | Motiv-Prompt |
| --- | --- |
| `wald/waldboden-intro.jpg` | Nahaufnahme Waldboden mit Laub, kleinen Pilzen und einem Regenwurm. Querformat 16:10. |
| `wald/boden-profil.jpg` | **Querschnitt durch den Waldboden**: oben Laubstreu, darunter Pilzfäden, ein Regenwurm, unten Wurzeln/Humus. Kindgerecht, ohne Beschriftung. Hoch-/Quadratformat. Punkte bei ca. 12 % (Laub), 40 % (Pilzgeflecht), 62 % (Regenwurm), 87 % (Wurzeln). |
| `wald/boden-pilz.jpg` | Pilze auf dem Waldboden oder auf Totholz. |
| `wald/boden-regenwurm.jpg` | Ein Regenwurm in dunkler Erde zwischen Laub, Makroaufnahme. |
| `wald/boden-assel.jpg` | Kleine Bodentiere im Laub (Assel, Springschwanz, Tausendfüßer), Makro. |
| `wald/boden-bakterien.jpg` | Eine Handvoll dunkler Humuserde – oder stilisierte Bakterien unter dem Mikroskop. |

## 6. Station „Waldpflanzen erkennen" — fertig, nutzt Echtfotos

Diese Station braucht **keine neuen Bilder**. Ich habe sechs echte Pflanzenfotos aus
`flora/images/fotos/` übernommen und als `erk-…jpg` in `images/wald/` abgelegt:
Buschwindröschen, Waldmeister, Sauerklee, Goldnessel, Lerchensporn, Scharbockskraut.
**Bärlauch und Bingelkraut sind wie gewünscht ersetzt** — sie kommen nicht vor.

## 7. Station „Wenn Gäste zu Eindringlingen werden" (Bilder fehlen noch)

| Datei | Motiv-Prompt |
| --- | --- |
| `wald/invasive-intro.jpg` | Dichter Bestand einer wuchernden Pflanze am Bachufer (z. B. rosa Springkraut), der alles andere überwuchert. Querformat 16:10. |
| `wald/invasive-springkraut.jpg` | Drüsiges Springkraut mit rosa Blüten und prallen Samenkapseln am Wasser. |
| `wald/invasive-baerenklau.jpg` | Riesen-Bärenklau, sehr hoch, mit großen weißen Doldenblüten. |
| `wald/invasive-knoeterich.jpg` | Japanischer Staudenknöterich, dichtes hohes Dickicht mit bambusartigen Stängeln. |
| `wald/invasive-goldrute.jpg` | Kanadische Goldrute, gelbes Blütenfeld auf einer Brache. |

## 8. Station „Warum wir den Wald brauchen" (Bilder fehlen noch)

| Datei | Motiv-Prompt |
| --- | --- |
| `wald/nutzen-intro.jpg` | Sonnendurchfluteter Wald, Lichtstrahlen, frische Luft-Stimmung. Querformat 16:10. |
| `wald/nutzen-luft.jpg` | Grüne Baumkronen von unten gegen blauen Himmel (Sauerstoff/Luft). |
| `wald/nutzen-wasser.jpg` | Klarer Bach oder Quelle im Wald (sauberes Wasser). |
| `wald/nutzen-boden.jpg` | Waldboden mit sichtbaren Wurzeln, die die Erde festhalten. |
| `wald/nutzen-klima.jpg` | Kühler, schattiger Wald an einem heißen Sommertag. |
| `wald/nutzen-erholung.jpg` | Wanderweg im Wald, Menschen beim Spazieren/Durchatmen. |

Legen wie immer nach `bio/bio/flora/images/wald/`, ich komprimiere und baue sie ein.
