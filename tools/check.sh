#!/bin/sh
# Prüfung vor jedem Release: JS-Syntax, JSON, Versionsgleichheit (index.html ↔ sw.js)
set -e
cd "$(dirname "$0")/.."
node -e "const fs=require('fs');const h=fs.readFileSync('index.html','utf8');const m=h.match(/<script>([\s\S]*)<\/script>/);new Function(m[1].replace(/document\./g,'({}).'));" && echo "JS ok"
node -e "require('fs');new Function(require('fs').readFileSync('sw.js','utf8'))" && echo "sw.js ok"
for f in packs/*.json manifest.webmanifest data/korrekturen.json; do python3 -c "import json,sys;json.load(open('$f',encoding='utf-8'))" || { echo "JSON kaputt: $f"; exit 1; }; done; echo "JSON ok"
V1=$(grep -o "const VERSION = '[^']*'" index.html | sed "s/.*'\(.*\)'/\1/")
V2=$(grep -o "polyglot-v[0-9.]*" sw.js | sed 's/polyglot-v//')
[ "$V1" = "$V2" ] && echo "Version $V1 ok" || { echo "Versionen ungleich: index.html $V1, sw.js $V2"; exit 1; }
