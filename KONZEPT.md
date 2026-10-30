# Polyglot – Konzept für eine Fünf-Sprachen-Vokabel-App

Stand 29.10.2026 (spät: Paket A1 und App-Kern 0.1.0 gebaut; Verlauf in `docs/status.md`) · Arbeitstitel „Polyglot“ · Ordner `~/Downloads/polyglot` · Schwester von Voc a Bit (`~/Downloads/wordbox`)

**Die Idee in einem Satz:** Eine Karteikarte ist nicht ein Wort, sondern ein *Begriff* („das Auto“), und sie steigt erst ein Fach auf, wenn der Lernende ihn in allen fünf Sprachen richtig hat – spielerisch, mit Serie, XP und Tagesziel wie bei Duolingo.

Dieses Papier beantwortet drei Fragen: **Woher kommen die Vokabeln** (Kapitel 2), **wie lernt man damit** (3–4) und **wie sieht die App aus und wie wird sie gebaut** (5–7). Kapitel 8 sammelt die Entscheidungen, die bei dir liegen.

---

## 1. Was heute schon da ist

| Was | Wo | Zustand |
|---|---|---|
| **Die App** (Phase 2): Onboarding, Start, Fünf-Bahnen-Runde mit Nachschuss, Ergebnis, Karteikasten, Profil mit Sicherung; PWA mit Service Worker | `index.html`, `sw.js`, `manifest.webmanifest` | Version 0.1.0, im Browser geprüft, iPhone-Test offen |
| Daten-Pipeline, die aus englischen Stichwörtern echte Fünf-Sprachen-Karten baut | `tools/hole-vokabeln.py` | läuft; Prüfblatt `tools/pruefblatt.py`, Einleser `tools/kuratiere.py` |
| **Paket A1: 512 Begriffe in fünf Sprachen** mit Thema, Emoji, Lesung, akzeptierten Varianten | `packs/a1.json`, lesbar `docs/a1-tabelle.md` | fertig, von Thomas noch nicht durchgesehen |
| Kuratierung (16 Paketdateien → Korrekturdatei) | `data/kuratierung/`, `data/korrekturen.json` | 640 Einträge, 122 Karten gestrichen |
| Klickbarer Design-Prototyp: Start, Runde mit fünf Bahnen, Ergebnis, jetzt mit A1-Daten | `prototyp/index.html` | läuft im Browser, geprüft |
| Screenshots | `docs/screenshot-*.jpg` | – |

Prototyp öffnen: Datei `prototyp/index.html` doppelklicken (läuft ohne Server). Ergebnisbildschirm direkt: `index.html#ergebnis`. Am Mac erscheint ein Telefonrahmen, am iPhone füllt die App den Bildschirm.

---

## 2. Woher die Vokabeln kommen (Recherche)

### 2.1 Der Kern: ein Begriff als Drehscheibe, nicht ein Wort

„Auto“ auf Spanisch gibt es nicht *ein* Mal: coche (Spanien), carro (Mittel-/Südamerika), auto (Südkegel), automóvil (neutral). Und „car“ hat im Englischen 17 Bedeutungen (Auto, Waggon, Aufzugskabine …). Wer Wort-zu-Wort übersetzt, mischt Bedeutungen. Darum muss die Pipeline **über eine Bedeutung** gehen: *englisches Stichwort + Bedeutungsglosse → Übersetzungen genau dieser Bedeutung in jede Zielsprache*. Zwei offene Datenquellen können das:

1. **Englisches Wiktionary** (über kaikki.org als fertiges JSON): Jeder englische Eintrag hat je Bedeutung eine Übersetzungstabelle in hunderte Sprachen, mit Lesung (Romaji, Pinyin), Genus, Regions- und Stilmarkern. **Das ist unsere Hauptquelle.**
2. **Wikidata-Lexeme**: Lexeme aller Sprachen zeigen per „Bedeutung = Wikidata-Objekt“ (P5137) auf denselben Begriff, z. B. Q1420 „Automobil“. Lizenz CC0, aber Deckung lückenhaft (Verben schwach). **Zweite Quelle zur Prüfung.**

Beides heute live geprüft: Für „car“ liefert Wiktionary in der Bedeutung „automobile“ 425 Übersetzungen, darunter alle fünf Zielsprachen mit Lesung; Wikidata liefert für Q1420 Lemmata in de, en, es, fr, da, he, … Ergebnis in `data/kaikki/car.jsonl`.

### 2.2 Quellenübersicht

| Quelle | Was drin ist | Lizenz | Rolle bei uns | Geprüft |
|---|---|---|---|---|
| **Wiktionary (en) via kaikki.org** | Übersetzungen je Bedeutung, Lesung, Genus, Region, Stil; 3,2 GB Gesamtdump oder je Wort eine JSONL-Datei | CC BY-SA 3.0 | Hauptquelle für die fünf Zielsprachen + Deutsch | ja, 15 Wörter gezogen |
| **Wikidata-Lexeme** | Lemmata je Sprache, Bedeutung → Begriff (P5137) | CC0 | Gegenprobe, Begriffs-ID, Bilder (P18) | ja, SPARQL für Q1420 |
| **CEFR-J Vocabulary Profile 1.5** + Octanove C1/C2 | ~7 800 englische Stichwörter mit Wortart und Niveau A1–C2 | frei mit Quellenangabe / CC BY-SA 4.0 | **Stufen Grund / Fortgeschritten / Experte** und Stichwortliste als Eingabe der Pipeline | ja, CSV-Format gesehen |
| **FrequencyWords (hermitdave)** | 50 000 häufigste Wortformen je Sprache aus Untertiteln, 60+ Sprachen | MIT | Rang zur Wahl der Hauptform, Ablenker-Kacheln nach Niveau | ja, es/fr/it/ja/zh geladen |
| **Tatoeba** | Millionen Beispielsätze, untereinander als Übersetzungen verknüpft, viele mit Audio | CC BY 2.0 FR | Beispielsätze je Begriff in allen fünf Sprachen (Phase 4) | Lizenz geprüft, Daten nicht geladen |
| **Open Multilingual Wordnet** | Synonymgruppen (Synsets) über ~40 Sprachen verknüpft | je Wordnet CC BY / MIT / Wordnet | Synonyme, Bedeutungsabgleich; Französisch dünn | nur Doku |
| **PanLex** | > 1 Mrd. Übersetzungspaare, 10 000 Varietäten | CC0 | Notnagel bei Lücken, ohne Bedeutungstrennung | nur Doku |
| **Kelly-Listen** | CEFR-gestufte Listen für 9 Sprachen (en, it, zh, ru, …), kein es/fr/ja | widersprüchlich (CC BY 4.0 bis NC-SA), je Datei prüfen | ggf. Italienisch/Chinesisch-Stufung | nur Doku |
| **CEFRLex (EFLLex, FLELex, ELELex)** | CEFR-Häufigkeiten für en, fr, es, nl, sv | CC BY-NC-SA 4.0 | **nur nicht-kommerziell** – im Zweifel weglassen | nur Doku |
| **Lingua Libre / Wikimedia Commons** | Wort-Aufnahmen von Muttersprachlern | CC BY-SA 4.0 | optional statt Sprachsynthese; kein Je-Wort-API, Massen-Download über Commons | nur Doku |
| **OpenMoji / Twemoji** | Emoji-Grafiken als Bildkarten | CC BY-SA 4.0 / CC BY 4.0 | Bild je Begriff (der Prototyp nutzt System-Emoji) | – |
| **LibreLingo** | offener Duolingo-Nachbau, Kurse als YAML | AGPL | nur Vorbild für Kursformat, keine Vokabeldaten für uns | nur Doku |

**Nicht nutzbar:** Duolingo-Inhalte, Oxford 3000/5000 (proprietär), BabelNet (eingeschränkte Lizenz), geteilte Anki-Decks (Lizenz unklar, Qualität schwankt).

**Nicht gefunden:** eine fertige, offene Liste „ein Begriff in fünf Sprachen, nach Niveau sortiert“. Die muss man sich bauen – genau das tut die Pipeline.

### 2.3 Was die Pipeline heute kann und wo sie irrt

Ablauf je Stichwort (`tools/hole-vokabeln.py`):

1. Wiktionary-Eintrag laden (je Wort eine JSONL-Datei von kaikki.org, lokal gecacht in `data/kaikki/`).
2. Übersetzungen nach Bedeutung gruppieren; Bedeutung per Glossen-Stichwort wählen („car;noun;automobile“), sonst die Gruppe mit der besten Sprachdeckung.
3. Je Zielsprache alle Kandidaten einsammeln (Wort, Lesung, Marker), Dubletten zusammenfassen, bei Chinesisch Kurz- und Langzeichen trennen.
4. **Hauptform wählen**: unmarkierte Varianten zuerst, darin die mit dem besten Häufigkeitsrang. Alle anderen bleiben *akzeptierte Antworten*.
5. Deutsch aus derselben Bedeutungsgruppe holen, Artikel aus dem Genus-Marker.
6. `data/korrekturen.json` darüberlegen.

Dazu eine **Regionalpräferenz je Sprache** (`REGION` im Skript, Entscheidung von mir: europäische Standardvarianten, also Spanien, Frankreich, Italien, Festland-China), damit aus coche/carro/auto/automóvil „coche“ wird und nicht das einzige unmarkierte, aber seltene „automóvil“. carro und auto bleiben akzeptierte Antworten.

Ergebnis für 15 Wörter: 75 Zellen, **69 davon automatisch brauchbar**, 6 Zellen in 4 Karten kuratiert (vier falsche Hauptformen aus der Tabelle, dazu 太阳 statt 日 im Chinesischen und die fehlende Lesung „ie“ für 家):

| Wort | Automatik | Richtig | Warum die Automatik irrt |
|---|---|---|---|
| small / es | chico | pequeño | *chico* ist häufig – als „Junge“, nicht als „klein“ |
| drink / es | tomar | beber | *tomar* ist häufig – als „nehmen“ |
| sun / ja | 日 (hi) | 太陽 (taiyō) | 日 ist häufig – als „Tag“ |
| small / ja | 小さな | 小さい | zwei gleichwertige Formen, Häufigkeit zufällig |

Die Lehre: **Häufigkeit einer Wortform ≠ Häufigkeit dieser Bedeutung.** Reine Automatik liefert etwa 90 % und ist als *Vorschlag* exzellent, aber nicht als Endprodukt. Der Weg ist hybrid: Pipeline → Durchsicht je Paket (Claude mit der Bedeutungsglosse vor Augen) → deine Stichprobe → Freigabe. Die Korrekturdatei macht jede Entscheidung nachvollziehbar und wiederholbar.

### 2.4 Lizenz-Konsequenz

Wiktionary-Daten sind CC BY-SA 3.0. Das heißt: Die **Vokabeldatei** (nicht der App-Code) steht unter CC BY-SA und nennt Wiktionary als Quelle, etwa auf einer „Über“-Seite. Kommerzielle Nutzung ist erlaubt. Ergänzungen aus Wikidata (CC0), FrequencyWords (MIT), Tatoeba (CC BY) sind verträglich. **CEFRLex (NC) weglassen**, sobald irgendeine kommerzielle Absicht besteht.

### 2.4a Was der A1-Lauf gezeigt hat

638 Stichwörter → 512 Karten. 122 flogen in der Kuratierung raus: Füllwörter (sir, thing, way), Grußformeln (hello, bye), Dubletten (home/house, present/gift, job/work) und Wörter, deren Hauptbedeutung nicht die A1-Bedeutung ist (saw = Säge, run = Laufmasche, kid = Zicklein). Von 2 560 Zellen habe ich 568 angefasst (22 %), überwiegend Japanisch und Chinesisch, wo die Häufigkeit kurze, mehrdeutige Formen bevorzugt (日 für Tag *und* Sonne, 男 statt 男の人). Drei Pipeline-Fehler kamen erst im Großen ans Licht: Monatsnamen (Groß-/Kleinschreibung im Pfad), Hokkien-Umschriften unter dem Etikett „Chinese“, Wortart „name“ bei Monaten. Hochrechnung für A2 (≈ 1 200 Stichwörter): ein Lauf, 24 Pakete Durchsicht, etwa ein halber Arbeitstag.

### 2.5 Mengengerüst

CEFR-J hat rund 7 800 Stichwörter. Als Pakete: **A1 ≈ 600**, **A2 ≈ 1 200**, **B1 ≈ 2 500** Begriffe. Ein A1-Paket sind 600 × 5 = 3 000 Zellen. Die Pipeline braucht je Wort unter einer Sekunde plus Wartezeit zum Server; ab etwa 1 000 Wörtern ist der 3,2-GB-Gesamtdump einmal herunterzuladen und lokal auszuwerten statt Einzelabrufe. Kuratierung: bei 10 % Korrekturbedarf rund 300 Entscheidungen für A1, in Paketen von 50 gut machbar.

---

## 3. Lernmechanik

### 3.1 Die Karte ist ein Begriff

```
Begriff  = { id, de: "das Auto", emoji, pos, stufe: "A1", thema: "Unterwegs",
             sprachen: { es: {w, roman, akzeptiert[]}, fr: …, it: …, ja: …, zh: … } }
Lernstand je Begriff = { fach 1–5, faellig (Kalendertag),
             sprachen: { es: {r: richtig, x: falsch, s: Serie}, … } }
```

Das Fach hängt am Begriff, die Treffer-Zähler je Sprache. So weiß die App, *welche* Sprache am Begriff hängt, und kann sie gezielt wiederholen.

### 3.2 Die Fünfer-Regel (deine Vorgabe)

Eine Karte steigt nur, wenn **alle fünf Sprachen in derselben Abfrage** richtig sind („Volltreffer“). Sonst:

- Die falschen Sprachen kommen in derselben Runde als **Nachschuss** noch einmal (nur die offenen Bahnen, wie im Prototyp zu sehen).
- Nachgeholt = Karte bleibt im Fach, Fälligkeit heute; nächste Runde neue Chance auf den Aufstieg.
- Falsch im Nachschuss = Karte fällt auf Fach 1 (wie Voc a Bit).

Zu entscheiden (siehe 8): ob es daneben einen **Teil-Aufstieg** geben darf (z. B. vier von fünf → halbe Stufe). Die strenge Regel ist klarer und motivierender, bremst aber bei Japanisch/Chinesisch, wo Lernende meist deutlich schwächer sind als in romanischen Sprachen. Ausgleich im Entwurf: eine **Fokus-Runde** je Sprache (nur Japanisch, 10 Begriffe), die Zähler sammelt, aber keine Fächer ändert.

### 3.3 Karteikasten

Übernommen aus Voc a Bit, dort über zwölf Versionen am Kind eingestellt: 5 Fächer, Lerntempo „Schnell“ (jeden Tag ein Fach, Fach 5 nach vier Tagen, dort 7–14 Tage Ruhe) oder „Langzeit“ (1, 3, 7, 14), **gerechnet in Kalendertagen** ab 0 Uhr, Rundenzusammenstellung mit festen Anteilen (höchstens die Hälfte fällig, dann neu in Paketreihenfolge, heute Richtiges nicht nochmal).

### 3.4 Abfragearten

| Art | Wann | Eingabe |
|---|---|---|
| **Fünf Bahnen** (Kern) | jede Karte | Spanisch/Französisch/Italienisch tippen, Japanisch/Chinesisch per Kachel – umschaltbar auf alles tippen oder alles Kacheln |
| Tippen Japanisch/Chinesisch | Fortgeschrittene | Kana, Kanji, Romaji, Pinyin ohne Töne werden akzeptiert; Kurz- und Langzeichen gleichwertig |
| Hören | ab Fach 2 | Sprachausgabe sagt das Wort in einer Sprache, Lernender wählt den Begriff |
| Rückrichtung | ab Fach 3 | „coche“ → deutscher Begriff + die vier anderen Sprachen |
| Blitz | Tagesquest | eine Sprache, 60 Sekunden, Kacheln |

Tipp-Prüfung wie in Voc a Bit: Groß/Klein egal, Artikel egal, Akzent-Abweichung zählt als „fast richtig“ (zählt, zeigt die genaue Form), ein Tippfehler ab fünf Buchstaben erlaubt, alle akzeptierten Varianten gelten.

### 3.5 Aufbau

Stufe (A1, A2, B1) → Einheit nach Thema (Zuhause, Essen, Unterwegs, Körper, Zeit …) → Lektion mit 15–20 Begriffen. Darstellung als Pfad wie bei Duolingo (Start-Knoten hüpft, erledigte golden, kommende gesperrt). Eine Runde = 5 Karten = 25 Antworten ≈ 3–4 Minuten. Tagesziel „Normal“ = zwei Runden.

---

## 4. Spielmechanik „wie Duolingo“

| Element | Regel | Woher |
|---|---|---|
| **Serie (Streak)** | Der Tag zählt, wenn das **Tagesziel in XP** erreicht ist – nicht beim bloßen Öffnen. Flamme im Kopf, Wochenleiste im Ergebnis, Meilensteine 7/30/100/365 | Duolingo; Voc a Bit zählt bei fertiger Runde |
| **Streak Freeze** | Schützt die Serie bei einem ausgelassenen Tag, höchstens zwei gleichzeitig ausgerüstet, wird automatisch verbraucht, vorher kaufen | Duolingo (zwei Freezes seit 2024) |
| **XP** | knapp wie Voc a Bit 1.3: 2 je richtige Bahn, +10 Volltreffer, +5 Rundenbonus, +10 fehlerfrei. Eine fehlerfreie Runde ≈ 75 XP | Voc a Bit (am Kind kalibriert) |
| **Tagesziel** | 50 / 100 / 150 / 250 XP, Ring auf der Startseite | Duolingo, Voc a Bit |
| **Edelsteine** | +10 je erreichtes Tagesziel, +20 fehlerfreie Runde; kaufen: Freeze (200), Doppel-XP 15 min (100) | Duolingo |
| **Tagesquests** | drei je Tag: „3 Volltreffer“, „10 richtige japanische Antworten“, „eine Runde ohne Fehler“, jeweils Edelsteine | Duolingo |
| **Combo** | Zähler je Runde, Flamme ab 2, Lob ab 5 | Voc a Bit |
| **Abzeichen** | die 15 aus Voc a Bit plus je Sprache („100 richtige auf Japanisch“), „Polyglott“ (ein Begriff in Fach 5) | Voc a Bit |
| **Herzen** | **nicht** vorgesehen – strafende Mechanik, Voc a Bit kommt bewusst ohne aus; als Einstellung denkbar | – |
| **Liga** | Wochen-Liga zu 30 mit Auf-/Abstieg braucht einen Server (Rangliste). Phase 5, mit Supabase wie bei ErstDu, anonymer Spitzname | Duolingo |

Die Reihenfolge hat einen Grund: Alles bis Abzeichen läuft **ohne Server** auf dem Gerät (Prinzip Voc a Bit: kein Konto, keine Daten verschicken). Nur die Liga nicht.

---

## 5. Design

Gezeigt im Prototyp (`prototyp/index.html`, Screenshots in `docs/`):

- **Schrift** Nunito 700–900, die „runde, dicke“ Lern-App-Anmutung; Voc a Bit nutzt Bricolage/Lexend, das darf hier anders sein, da eigene Marke.
- **Farben als Tokens** auf `:root`, hell und dunkel: Grün (Aktion, richtig), Rot (falsch), Blau (Info, Edelsteine), Gold (XP, erledigt), Flamme (Serie), Lila (Begriffs-Chips).
- **3D-Knöpfe** mit 4 px Bodenkante, die beim Drücken einsinken – das Duolingo-Signaturgefühl, ohne eine Grafik zu kopieren.
- **Fortschrittsbalken** mit Glanzstreifen, **Bottom Sheet** für das Ergebnis jeder Karte (grün/rot, mit Erklärung „Französisch kommt gleich noch einmal“).
- **Mikro-Animationen**: „+8 XP“ schwebt auf, falsche Bahnen wackeln, Flamme flackert, Ergebnis-Emoji ploppt, Start-Schild hüpft.
- **Fünf Bahnen** je Karte: Flagge + Sprachkürzel, Eingabe oder Kacheln mit Lesung in Kleinschrift; nach dem Prüfen grün/rot mit Lösung.
- **Startseite**: Serie, Freezes, Edelsteine, Tagesziel-Ring, fünf Sprachen mit Stärkebalken, „Heute“-Karte, Pfad, Karteikasten als Balken, Tab-Leiste (Lernen, Kasten, Liga, Profil).
- **Ergebnis**: drei Kacheln (XP, Genau, Combo), Serien-Karte mit Wochenleiste, Liste der aufgestiegenen Karten.
- Am Mac ein Telefonrahmen (390 × 860), am iPhone Vollbild mit Safe-Areas.

Noch nicht im Prototyp: Kasten-Ansicht, Profil, Shop, Quests, Hör-Abfrage, Onboarding (Sprachen wählen, Tagesziel).

---

## 6. Technik

**Empfehlung: genau wie Voc a Bit.** Eine `index.html` (Vanilla JS, kein Build), Service Worker, Manifest, GitHub Pages, Lernstand in `localStorage`, Sicherung per Teilen-Menü. Vokabelpakete als JSON in `packs/` mit `index.json` und `rev`, wie `lists/` dort. Sprachausgabe über die iOS-Stimmen (es-ES, fr-FR, it-IT, ja-JP, zh-CN sind auf iPhones vorhanden; die App prüft `speechSynthesis.getVoices()` und zeigt bei fehlender Stimme einen Hinweis wie Voc a Bit bei en-GB).

Was aus Voc a Bit 1:1 übernommen werden kann: Karteikasten-Logik mit Kalendertagen, Rundenzusammenstellung, Serie/XP/Level/Abzeichen, Ton-Freischaltung auf iOS, Release-Regel (Cache-Name + Versionsnummer gleichzeitig), `check.sh`, Listen-Sync mit `rev`. Neu: Begriffsmodell mit Sprach-Unterzählern, Fünf-Bahnen-Abfrage, Kacheln, Freeze/Edelsteine/Quests.

Option später: Supabase (Konto per E-Mail-Code, wie ErstDu) für Liga und Geräte-Sync. Erst, wenn die App ohne Server rund läuft.

---

## 7. Fahrplan

| Phase | Inhalt | Ergebnis |
|---|---|---|
| 0 | Entscheidungen aus Kapitel 8 | Festlegungen in `docs/status.md` |
| 1 | **Paket A1**: 600 Stichwörter aus CEFR-J, Pipeline (Gesamtdump statt Einzelabrufe), Durchsicht in 12 Paketen à 50, Korrekturdatei, Themen-Zuordnung, Emoji je Begriff | `packs/a1.json`, CC BY-SA, geprüft |
| 2 | **App-Kern**: Start, Fünf-Bahnen-Runde mit Nachschuss, Karteikasten, Serie, Tagesziel, XP, Sicherung, PWA auf GitHub Pages | nutzbare App mit A1 |
| 3 | **Spielmechanik komplett**: Freeze, Edelsteine, Shop, Tagesquests, Abzeichen, Hör-Abfrage, Rückrichtung, Blitz | Duolingo-Gefühl |
| 4 | **A2, B1**, Beispielsätze aus Tatoeba, Bilder (OpenMoji), Tippen für ja/zh mit Romaji/Pinyin | Inhalt für Monate |
| 5 | optional **Liga + Sync** mit Supabase | Wettbewerb |

Phase 1 und 2 können parallel laufen, weil der Prototyp das Datenformat schon festlegt.

---

## 8. Entscheidungen, die bei dir liegen

1. **Sprachen**: fest die fünf (es, fr, it, ja, zh) – oder wählt der Nutzer seine n Sprachen aus einer Liste? Die Pipeline kann jeden Wiktionary-Sprachcode; die App wird mit variabler Zahl etwas komplexer (Bahnen, Kacheln, Volltreffer-Regel bei 3 oder 7 Sprachen).
2. **Abfragesprache**: Deutsch (wie im Prototyp) – oder Englisch als Drehscheibe, falls dein Bekannter auch Englisch mitlernt?
3. **Fünfer-Regel** streng (nur Volltreffer steigt) oder mit Teil-Aufstieg?
4. **Regionalpräferenz**: Ich habe europäische Standardvarianten gesetzt (Spanien, Frankreich, Italien, Festland-China mit Kurzzeichen; `REGION` in `tools/hole-vokabeln.py`). Wenn dein Bekannter eher Lateinamerika oder Taiwan im Blick hat, ist das eine Zeile. Offen bleibt die Anzeige im Japanischen: Kanji mit Lesung darunter (wie im Prototyp) oder Kana zuerst.
5. **Verbreitung**: privat über GitHub Pages wie Voc a Bit, oder öffentlich/kommerziell? Davon hängt ab, ob NC-Quellen tabu sind (sind sie bei „öffentlich“).
6. **Herzen** ja oder nein; **Liga** jetzt einplanen oder später?
7. **Name** und ob es eine eigene App wird oder ein Modus in Voc a Bit (Empfehlung: eigene App, weil Datenmodell und Zielgruppe andere sind).

---

## Quellen

- kaikki.org, Wiktextract-Daten des englischen Wiktionary: https://kaikki.org/dictionary/English/ · Projekt: https://github.com/tatuylonen/wiktextract
- Wikidata-Lexeme, Eigenschaft „item for this sense“ P5137: https://www.wikidata.org/wiki/Property:P5137 · SPARQL-Beispiele: https://sinaahmadi.github.io/posts/10-essential-sparql-queries-for-lexicographical-data-on-wikidata.html
- CEFR-J Vocabulary Profile / Open Language Profiles: https://github.com/openlanguageprofiles/olp-en-cefrj
- FrequencyWords (OpenSubtitles): https://github.com/hermitdave/FrequencyWords
- Tatoeba, Downloads und Lizenz: https://tatoeba.org/de/downloads · CC0-Hinweis: https://en.wiki.tatoeba.org/articles/show/cc0-contributions
- Open Multilingual Wordnet: https://github.com/omwn/omw-data · Python-Paket `wn`: https://pypi.org/project/wn
- PanLex-Snapshots (CC0): https://panlex.org/snapshot
- Kelly-Listen: https://spraakbanken.gu.se/en/resources/kelly · https://hf.uio.no/iln/english/about/organization/text-laboratory/services/kelly.html
- CEFRLex: https://cental.uclouvain.be/cefrlex · EFLLex-Download (CC BY-NC-SA): https://cental.uclouvain.be/cefrlex/efllex/download/
- Lingua Libre, Datensätze: https://lingualibre.org/wiki/Help:Download_datasets
- UniversalCEFR (Texte, nicht Wörter, nur Forschung): https://universalcefr.github.io/
- LibreLingo: https://github.com/kantord/LibreLingo
- Duolingo zu Streaks: https://blog.duolingo.com/how-duolingo-streak-builds-habit · Streak Freeze (Wiki): https://duolingo.fandom.com/wiki/Shop/Streak_freeze
