#!/usr/bin/env python3
"""Liest Kuratierungszeilen ein und schreibt sie in data/korrekturen.json.

Zeilenformat (data/kuratierung/*.txt), Felder durch |, Leerfelder erlaubt:
  id | Thema | Emoji | feld=wert, feld=wert
Felder: es fr it ja zh (Hauptform), es_roman…zh_roman (Lesung), de (deutsche Abfrageform),
        sinn (Glossen-Stichwort zur Bedeutungswahl), raus=1 (Karte aus dem Paket nehmen).
Beispiel:  noun-bank | Einkaufen & Geld | 🏦 | sinn=financial
"""
import glob, json, os, sys
WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pfad = os.path.join(WURZEL, 'data', 'korrekturen.json')
korr = json.load(open(pfad, encoding='utf-8'))
dateien = sys.argv[1:] or sorted(glob.glob(os.path.join(WURZEL, 'data', 'kuratierung', '*.txt')))
n = 0
for datei in dateien:
    for zeile in open(datei, encoding='utf-8'):
        zeile = zeile.strip()
        if not zeile or zeile.startswith('#'): continue
        teile = [t.strip() for t in zeile.split('|')] + ['', '', '']
        kid, thema, emoji, felder = teile[0], teile[1], teile[2], teile[3]
        e = korr.setdefault(kid, {})
        if thema: e['thema'] = thema
        if emoji: e['emoji'] = emoji
        for f in filter(None, [x.strip() for x in felder.split(',')]):
            if '=' not in f: print(f'  ! {datei}: Feld ohne =: {f} in {kid}', file=sys.stderr); continue
            k, v = f.split('=', 1); e[k.strip()] = v.strip()
        n += 1
json.dump(korr, open(pfad, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'{n} Zeilen aus {len(dateien)} Dateien → data/korrekturen.json ({len(korr)} Einträge)')
