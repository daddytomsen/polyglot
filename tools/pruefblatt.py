#!/usr/bin/env python3
"""Prüfblatt für die Kuratierung: eine Zeile je Karte, Pakete à 50.
Aufruf: python3 tools/pruefblatt.py a1 3        → Paket 3 (Karten 101–150)
        python3 tools/pruefblatt.py a1 --offen   → nur Karten ohne Thema oder mit Warnung
"""
import json, os, sys
WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
kurz = '--kurz' in sys.argv; argv = [a for a in sys.argv if a != '--kurz']
name = argv[1]; arg = argv[2] if len(argv) > 2 else '1'
d = json.load(open(os.path.join(WURZEL, 'data', f'{name}.json'), encoding='utf-8'))
karten = d['karten']
if arg == '--offen':
    auswahl = [(i, k) for i, k in enumerate(karten) if not k.get('thema') or k.get('warnungen')]
else:
    n = int(arg); auswahl = list(enumerate(karten))[(n - 1) * 50:n * 50]
def zelle(v):
    if not v: return '—'
    return v['w'] + (f"({v['roman']})" if v['roman'] else '') + ('*' if v.get('kuratiert') else '')
for i, k in auswahl:
    w = '' if kurz else '; '.join(x.replace('Bedeutungen, Automatik wählte: ', 'Bed.: ') for x in k.get('warnungen', []))
    print(f"{i+1:3} {k['id']:<22} {k['de'] or '???':<18} " + ' | '.join(zelle(k['sprachen'].get(s)) for s in ['es', 'fr', 'it', 'ja', 'zh']) + (f"   ⚠ {w}" if w else '') + (f"   [{k['thema']}]" if k.get('thema') else ''))
print(f"\n{len(auswahl)} Karten")
