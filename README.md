# Polyglot – Fünf-Sprachen-Vokabeltrainer

Live: **https://daddytomsen.github.io/polyglot/** · Web-App für das iPhone (Safari → „Zum Home-Bildschirm“), eine `index.html`, kein Server, kein Build, Lernstand nur im Gerät. Eine Karteikarte ist ein Begriff und steigt erst auf, wenn er in allen fünf Sprachen richtig ist. Lies zuerst `KONZEPT.md` (Kap. 1 und 8) und `docs/status.md`.

```bash
cd ~/Downloads/polyglot
python3 -m http.server 8080      # dann http://localhost:8080 (Service Worker nur unter https)
tools/check.sh                   # vor jedem Release: JS, JSON, Versionsgleichheit
```

```
index.html             die App (Start, Runde, Kasten, Profil), Version 0.1.0
sw.js, manifest.webmanifest, icon.svg, *.png   Offline-Cache, Home-Bildschirm, Icons (PNGs aus tools/baue-icons.py)
KONZEPT.md             Recherche, Lernmechanik, Spielmechanik, Design, Technik, Fahrplan
docs/status.md         Fortschritt, Entscheidungen, nächster Schritt
packs/a1.json          Paket A1: 512 Begriffe in fünf Sprachen (für die App); packs/index.json
docs/a1-tabelle.md     dasselbe als lesbare Tabelle nach Thema
prototyp/index.html    Design-Prototyp (Vorstufe der App, Daten eingebettet); #ergebnis zeigt den Ergebnisbildschirm
tools/hole-vokabeln.py Pipeline: englische Stichwörter → Fünf-Sprachen-Karten (kaikki.org + FrequencyWords)
tools/pruefblatt.py    Prüfblatt je Paket à 50 Karten für die Kuratierung
tools/kuratiere.py     liest data/kuratierung/*.txt in data/korrekturen.json ein
tools/baue-prototyp.py bettet packs/<name>.json in den Prototyp ein
tools/check.sh         Prüfung vor dem Release
tools/baue-icons.py    zeichnet die PNG-Icons ohne Zusatzbibliotheken
data/a1-liste.txt      638 A1-Stichwörter aus CEFR-J (wort;pos)
data/kuratierung/      Kuratierungszeilen je Paket: id | Thema | Emoji | feld=wert
data/korrekturen.json  kuratierte Hauptformen, Lesungen, Themen; überstimmen die Automatik
data/a1.json           Rohergebnis der Pipeline mit Warnungen und Quellen
data/kaikki/, data/freq/  Download-Cache
docs/                  Screenshots, Probetabelle
```

Pipeline laufen lassen (nur Python 3 und curl nötig):

```bash
cd ~/Downloads/polyglot
python3 tools/hole-vokabeln.py --datei data/a1-liste.txt --name a1   # Rohdaten, Cache in data/kaikki
python3 tools/pruefblatt.py a1 3                                       # Paket 3 prüfen, Zeilen in data/kuratierung/ schreiben
python3 tools/kuratiere.py && python3 tools/hole-vokabeln.py --datei data/a1-liste.txt --name a1
python3 tools/baue-prototyp.py a1
```

Lizenz der Vokabeldaten: CC BY-SA 3.0 (englisches Wiktionary über kaikki.org); Häufigkeiten MIT (hermitdave/FrequencyWords).
