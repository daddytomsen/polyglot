# Status Polyglot

Stand 29.10.2026, spät. Eine neue Session liest zuerst `KONZEPT.md` (Kap. 1 und 8) und diese Datei.

## Phase 2 – App-Kern: fertig (Version 0.1.0, nur im Browser am Mac geprüft, nicht auf dem iPhone)

- `index.html` (587 Zeilen, Vanilla JS, kein Build) + `sw.js` + `manifest.webmanifest` + Icons (`icon.svg`, PNGs aus `tools/baue-icons.py`). Paket wird aus `packs/index.json` geladen (network-first) und in `localStorage` gespiegelt, Lernstand unter `polyglot.prog.v1`.
- Ansichten: Onboarding (Tagesziel, Eingabe), Start (Serie, XP, Tagesziel-Ring, Sprachstärke, Heute, Themen-Auswahl, Karteikasten-Balken), Runde (5 Karten × 5 Bahnen, Tippen/Kacheln/Gemischt, Nachschuss, Bottom Sheet, Vorlesen je Lösung), Ergebnis (XP, Genauigkeit, Combo, Serie mit Wochenleiste, Fach-Wechsel), Kasten (Suche über alle Sprachen, Filter je Fach, Detail mit Zählern je Sprache), Profil (Serie, Einstellungen, Sicherung speichern/laden, Zurücksetzen, Über mit Lizenz).
- Lernlogik wie Voc a Bit 1.12: 5 Fächer, Kalendertage, Tempo Schnell `[0,0,1,1,1,7]` / Langzeit `[0,0,1,3,7,14]` mit Umrechnung beim Umschalten, Runde: höchstens die Hälfte fällig, dann neue in Paketreihenfolge, heute Richtiges nicht nochmal. **Fünfer-Regel:** Volltreffer (alle Bahnen auf einmal) und fällig → ein Fach hoch (neu → Fach 2); eine Bahn falsch → Fach 1, Nachschuss der falschen Bahnen in derselben Runde; Nachschuss richtig → bleibt im Fach, morgen fällig.
- XP: 2 je richtige Bahn, +10 Volltreffer, +5 Runde, +10 fehlerfrei. **Serie zählt, wenn das Tagesziel erreicht ist** (nicht bei bloßer Runde). Konfetti und Ton bei Ziel oder fehlerfreier Runde.
- Antwortprüfung: Groß/Klein, Akzente, Artikel egal; ein Tippfehler ab 5 Zeichen; Romaji/Pinyin ohne Töne gelten; alle Wiktionary-Varianten gelten.
- Geprüft im Browser (375 px, hell und dunkel): zwei komplette Runden, Nachschuss, Aufstieg Fach 1→2, Fälligkeit morgen, Tagesziel → Serie 1, Neustart behält Stand, Kasten-Filter und Detail, Profil. Screenshots `docs/app-*.jpg`. `tools/check.sh` grün.
- Nicht geprüft: iPhone (Ton-Freischaltung, Stimmen ja-JP/zh-CN, Teilen-Menü für die Sicherung, Home-Bildschirm-Installation), Service Worker (läuft nur unter https, also erst auf GitHub Pages).
- Release-Regel wie Voc a Bit: `VERSION` in `index.html` und `CACHE` in `sw.js` gleichzeitig hochzählen, `tools/check.sh` prüft das.


## Phase 1 – Paket A1: fertig (Rohfassung, von Thomas noch nicht durchgesehen)

- Stichwortliste `data/a1-liste.txt`: 638 Einträge aus CEFR-J A1 (alle Verben und Adjektive, 330 Nomen nach Häufigkeit mit Pflichtwörtern Wochentage/Monate/Jahreszeiten/Mahlzeiten, 28 Adverbien von Hand).
- Pipeline `tools/hole-vokabeln.py` sechsmal gelaufen (Cache in `data/kaikki/`, 640 Dateien). Fehler unterwegs behoben: Groß-/Kleinschreibung im kaikki-Pfad (Monate, Wochentage), Mandarin nur aus „Chinese Mandarin“ (bloßes „Chinese“ trägt Hokkien/Dungan), Alias (`mom → mother`), Handeinträge (Juni, November, Mai, März, August, Foto, Telefon …), Lesung ohne neue Hauptform.
- Kuratierung in 16 Dateien `data/kuratierung/paket-*.txt` (666 Zeilen) → `data/korrekturen.json` (640 Einträge): Thema und Emoji für jede Karte, 122 Karten gestrichen (Füllwörter, Dubletten, falsche Bedeutung ohne A1-Wert, Grußformeln), 568 von 2 560 Zellen mit kuratierter Hauptform oder Lesung, 19 Karten komplett von Hand.
- Ergebnis **`packs/a1.json`: 512 Karten** (257 Nomen, 122 Verben, 110 Adjektive, 23 Adverbien), 17 Themen, keine leeren Zellen, keine doppelte deutsche Abfrage, keine zwei identischen Karten. Lesbare Tabelle: `docs/a1-tabelle.md`.
- Prototyp mit dem A1-Paket bestückt (305 KB), im Browser geprüft; Ablenker-Kacheln kommen aus derselben Wortart.

## Entscheidungen (von mir, änderbar)

- Regionalpräferenz europäisch (Spanien, Frankreich, Italien, Festland-China mit Kurzzeichen); Japanisch Kanji mit Lesung.
- Themen: 17 Stück, Liste in `data/kuratierung/THEMEN.md`. „Tun (Verben)“ und „Sonstiges“ sind Sammelbecken.
- Mehrdeutige deutsche Abfragen tragen einen Klammerzusatz („tragen (Kleidung)“ / „tragen (Last)“).
- Verben stehen auf Japanisch in der Wörterbuchform, Chinesisch ohne Partikel; Adjektive auf Japanisch in der い/な-Form, auf Chinesisch meist ohne 的.

## Offen

- Durchsicht durch Thomas: `docs/a1-tabelle.md` überfliegen, Stichprobe 20 Karten. Erwartung: einige Hauptformen sind Geschmackssache (z. B. 犬 vs. 狗 ist korrekt, aber ob „die Erkältung“ A1 ist, ist diskutabel).
- Nicht geprüft: akzeptierte Varianten enthalten alles aus dem Wiktionary, auch Seltenes (z. B. „pupú“ für Auto). Das ist beim Lernen harmlos (wird nur akzeptiert, nie gezeigt), sollte aber vor einer Veröffentlichung einmal gefiltert werden (Stil-Tags „slang/vulgar“ raus).
- Die sieben Entscheidungen aus `KONZEPT.md` Kap. 8 stehen weiter aus.
- Kein Git-Repo angelegt.

## Nächster Schritt

1. Git-Repo anlegen und auf GitHub Pages veröffentlichen (öffentlich, wie `wordbox`); dann iPhone-Test nach der Checkliste aus Voc a Bit (Ton, Stimmen, Sicherung, offline, Home-Bildschirm).
2. Phase 3 Spielmechanik: Streak Freeze, Edelsteine, Tagesquests, Abzeichen, Hör-Abfrage, Rückrichtung.
3. Paket A2 über die Pipeline (`data/a2-liste.txt`, ~1 200 Stichwörter, 24 Pakete Kuratierung).
