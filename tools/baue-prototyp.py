#!/usr/bin/env python3
"""Schreibt packs/<name>.json (sonst data/<name>.json) in prototyp/index.html zwischen die Marker /*DATA*/ und /*ENDDATA*/."""
import json, os, sys
WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
name = sys.argv[1] if len(sys.argv) > 1 else 'probe'
quelle = os.path.join(WURZEL, 'packs', f'{name}.json')          # schlankes App-Paket bevorzugen
if not os.path.exists(quelle): quelle = os.path.join(WURZEL, 'data', f'{name}.json')
daten = json.load(open(quelle, encoding='utf-8'))
pfad = os.path.join(WURZEL, 'prototyp', 'index.html')
html = open(pfad, encoding='utf-8').read()
a, b = html.index('/*DATA*/') + len('/*DATA*/'), html.index('/*ENDDATA*/')
html = html[:a] + '\nconst DATA = ' + json.dumps(daten, ensure_ascii=False) + ';\n' + html[b:]
open(pfad, 'w', encoding='utf-8').write(html)
print(f'{len(daten["karten"])} Karten in prototyp/index.html eingebettet')
