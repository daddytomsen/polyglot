#!/usr/bin/env python3
"""Baut Fünf-Sprachen-Karten aus offenen Quellen.

Eingabe:  englische Stichwörter (Argumente oder --datei liste.txt, eine Zeile = ein Wort,
          optional "wort;pos;glossen-stichwort", z. B. "run;verb;move swiftly")
Quellen:  kaikki.org (Wiktextract aus dem englischen Wiktionary, CC BY-SA 3.0)
          → Übersetzungen je Bedeutung mit Lesung (Romaji/Pinyin) und Regionalmarkern
          hermitdave/FrequencyWords (OpenSubtitles 2018, MIT) → Häufigkeitsrang je Sprache
Ausgabe:  data/<name>.json  – ein Eintrag je Konzept mit Hauptform + akzeptierten Varianten

Nur Python-Standardbibliothek. Aufruf:
  python3 tools/hole-vokabeln.py car dog house --name probe
"""
import argparse, json, os, subprocess, sys, time, urllib.parse

HIER = os.path.dirname(os.path.abspath(__file__))
WURZEL = os.path.dirname(HIER)
DATEN = os.path.join(WURZEL, 'data')
FREQ = os.path.join(DATEN, 'freq')

# Zielsprachen: Kürzel → (Anzeigename, kaikki-Code, Filter auf das lang-Feld, FrequencyWords-Ordner)
SPRACHEN = {
    'es': ('Spanisch',    'es', None,       'es'),
    'fr': ('Französisch', 'fr', None,       'fr'),
    'it': ('Italienisch', 'it', None,       'it'),
    'ja': ('Japanisch',   'ja', None,       'ja'),
    'zh': ('Chinesisch',  ('zh', 'cmn'), 'Mandarin', 'zh_cn'),   # Mandarin steht mal unter zh, mal unter cmn
}
ARTIKEL = {'masculine': 'der', 'feminine': 'die', 'neuter': 'das'}
STIL_TAGS = {'slang', 'colloquial', 'dated', 'archaic', 'obsolete', 'vulgar', 'childish', 'rare', 'dialectal', 'humorous', 'derogatory', 'literary', 'poetic'}
GRAMMATIK_TAGS = {'masculine', 'feminine', 'neuter', 'common', 'plural', 'singular', 'animate', 'inanimate',
                  'perfective', 'imperfective', 'literally', 'formal', 'informal'}
UA = {'User-Agent': 'polyglot-vokabelpipeline/0.1 (privates Lernprojekt)'}


def hole(url, ziel=None, binaer=False):
    """Lädt eine URL über curl (robuster als urllib hinter Proxys), legt sie unter ziel ab (Cache)."""
    if ziel and os.path.exists(ziel):
        return open(ziel, 'rb').read() if binaer else open(ziel, encoding='utf-8').read()
    r = subprocess.run(['curl', '-sSfL', '--max-time', '90', '-A', UA['User-Agent'], url], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode('utf-8', 'replace').strip() or f'curl-Fehler {r.returncode}')
    roh = r.stdout
    if ziel:
        os.makedirs(os.path.dirname(ziel), exist_ok=True)
        open(ziel, 'wb').write(roh)
    time.sleep(0.3)  # kaikki ist ein Ein-Personen-Projekt, nicht hämmern
    return roh if binaer else roh.decode('utf-8')


def lade_frequenz(kurz):
    """Häufigkeitsrang je Wortform aus FrequencyWords (kleinere Zahl = häufiger)."""
    ordner = SPRACHEN[kurz][3]
    ziel = os.path.join(FREQ, f'{ordner}_50k.txt')
    text = None
    for jahr in ('2018', '2016'):
        url = f'https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/{jahr}/{ordner}/{ordner}_50k.txt'
        try:
            text = hole(url, ziel); break
        except Exception as e:
            fehler = e
    if text is None:
        print(f'  ! keine Frequenzliste für {kurz}: {fehler}', file=sys.stderr)
        return {}
    rang = {}
    for i, zeile in enumerate(text.splitlines(), 1):
        teile = zeile.split()
        if teile and teile[0] not in rang:
            rang[teile[0]] = i
    return rang


def kaikki_eintraege(wort):
    """Alle Wiktionary-Einträge (je Wortart einer) zu einem englischen Wort."""
    w = wort
    pfad = f'{w[0]}/{w[:2]}/{urllib.parse.quote(w)}.jsonl'
    ziel = os.path.join(DATEN, 'kaikki', f'{w}.jsonl')
    text = hole(f'https://kaikki.org/dictionary/English/meaning/{pfad}', ziel)
    return [json.loads(z) for z in text.splitlines() if z.strip()]


def waehle_bedeutung(eintrag, stichwort=None):
    """Gruppiert die Übersetzungen nach Bedeutung und wählt eine Gruppe.

    Regel: Nennt der Aufrufer ein Glossen-Stichwort, gewinnt die erste Gruppe, die es enthält.
    Sonst die Gruppe, die alle Zielsprachen abdeckt und die meisten Übersetzungen hat
    (bei Grundwortschatz fast immer die Hauptbedeutung).
    """
    gruppen = {}
    for t in eintrag.get('translations', []):
        gruppen.setdefault(t.get('sense', ''), []).append(t)
    if not gruppen:
        return None, []
    if stichwort:
        for sinn, ts in gruppen.items():
            if stichwort.lower() in sinn.lower():
                return sinn, ts
    def deckung(ts):
        codes = {t.get('code') for t in ts}
        return sum(1 for s in SPRACHEN.values() if any(c in codes for c in (s[1] if isinstance(s[1], tuple) else (s[1],))))
    sinn = max(gruppen, key=lambda s: (deckung(gruppen[s]), len(gruppen[s])))
    return sinn, gruppen[sinn]


def kandidaten(ts, kurz):
    """Übersetzungen einer Bedeutung für eine Zielsprache, bereinigt."""
    name, code, filt, _ = SPRACHEN[kurz]
    aus = []
    for t in ts:
        codes = code if isinstance(code, tuple) else (code,)
        if t.get('code') not in codes or not t.get('word'):
            continue
        lang = t.get('lang') or ''
        if filt and filt not in lang:   # nur „Chinese Mandarin“; bloßes „Chinese“ trägt Dialekt-Tags (Hokkien, Dungan …)
            continue
        wort = t['word']
        if kurz == 'zh' and ' /' in wort:          # „汽車 /汽车“ → vereinfacht als Hauptform, traditionell als Variante
            trad, simp = [x.strip() for x in wort.split('/', 1)]
            wort, trad_alt = simp, trad
        else:
            trad_alt = None
        tags = [x for x in t.get('tags', []) if x not in GRAMMATIK_TAGS]
        aus.append({'w': wort, 'roman': t.get('roman') or '', 'tags': tags, 'trad': trad_alt})
    # Dubletten (gleiches Wort, andere Region) zusammenfassen
    gesehen, eindeutig = {}, []
    for k in aus:
        if k['w'] in gesehen:
            gesehen[k['w']]['tags'] = sorted(set(gesehen[k['w']]['tags']) | set(k['tags']))
        else:
            gesehen[k['w']] = k; eindeutig.append(k)
    return eindeutig


# Bevorzugte Regionalvariante je Sprache (Entscheidung 29.10.2026): europäische Standardvarianten,
# weil Lernende hierzulande Schul- und Reisesprache dieser Länder lernen. Alle anderen Varianten
# bleiben akzeptierte Antworten, es geht nur um die *angezeigte* Lösung.
REGION = {'es': ['Spain'], 'fr': ['France'], 'it': ['Italy'], 'ja': [], 'zh': ['Mainland-China']}


def waehle_hauptform(kands, rang, kurz):
    """Welche Variante zeigt die App als Lösung? Alle anderen bleiben akzeptierte Antworten.

    Rangfolge: 1. Varianten ohne Marker oder mit Marker der bevorzugten Region (REGION),
    2. darunter die mit dem besten Häufigkeitsrang, 3. Reihenfolge im Wiktionary.
    Varianten mit Stilmarkern (slang, colloquial, dated, …) oder fremder Region kommen danach.
    So wird aus coche/carro/auto/automóvil „coche“, ohne dass carro oder auto als falsch gelten.
    """
    bevorzugt = set(REGION.get(kurz, []))
    def schluessel(k):
        tags = set(k['tags'])
        neutral = 0 if not tags or (tags & bevorzugt and not tags & STIL_TAGS) else 1
        return (neutral, rang.get(k['w'].lower(), 10**9), kands.index(k))
    return min(kands, key=schluessel)


def deutsch(ts, pos):
    """Deutsche Abfrageform aus derselben Bedeutungsgruppe, bei Nomen mit Artikel."""
    for t in ts:
        if t.get('code') == 'de' and t.get('word'):
            art = next((ARTIKEL[x] for x in t.get('tags', []) if x in ARTIKEL), '')
            return (art + ' ' + t['word']).strip() if pos == 'noun' else t['word']
    return ''


def lade_korrekturen():
    """data/korrekturen.json: kuratierte Hauptformen, die die Automatik überstimmen.
    Format: { "<karten-id>": { "es": "coche", "de": "das Auto", "emoji": "🚗" } }"""
    pfad = os.path.join(DATEN, 'korrekturen.json')
    return json.load(open(pfad, encoding='utf-8')) if os.path.exists(pfad) else {}


def baue_karte(wort, pos=None, stichwort=None, raenge=None, korrekturen=None):
    warnungen = []
    kid = f'{pos or "x"}-{wort.lower().replace(" ", "-")}'
    korr = (korrekturen or {}).get(kid, {})
    if korr.get('raus'):
        print(f'  – {wort}: per Kuratierung ausgelassen', file=sys.stderr)
        return None
    if all(korr.get(k) for k in SPRACHEN) and korr.get('de'):      # von Hand vollständig vorgegeben
        karte = {'id': kid, 'en': wort, 'pos': pos, 'sinn': korr.get('sinn', ''), 'quelle': 'manuell', 'de': korr['de'],
                 'sprachen': {k: {'w': korr[k], 'roman': korr.get(k + '_roman', ''), 'tags': [], 'rang': None, 'kuratiert': True, 'akzeptiert': []} for k in SPRACHEN},
                 'warnungen': []}
        if korr.get('thema'): karte['thema'] = korr['thema']
        if korr.get('emoji'): karte['emoji'] = korr['emoji']
        return karte
    quelle = korr.get('alias') or wort                                 # z. B. mom → mother, favorite → favourite
    try:
        alle = [e for e in kaikki_eintraege(quelle) if e.get('translations')]
    except Exception as e:
        print(f'  ! {wort}: {e}', file=sys.stderr)
        return None
    eintraege = [e for e in alle if e.get('pos') == pos] if pos else alle
    if not eintraege and alle:
        eintraege = alle; warnungen.append(f'wortart {pos} fehlt, genommen: {alle[0]["pos"]}')
    if not eintraege:
        print(f'  ! {wort}: keine Übersetzungen gefunden', file=sys.stderr)
        return None
    stichwort = korr.get('sinn') or stichwort
    # Eintrag mit den meisten Übersetzungen nehmen
    eintrag = max(eintraege, key=lambda e: len(e.get('translations', [])))
    sinn, ts = waehle_bedeutung(eintrag, stichwort)
    gruppen = {t.get('sense', '') for t in eintrag.get('translations', [])}
    if len(gruppen) > 1 and not stichwort:
        warnungen.append(f'{len(gruppen)} Bedeutungen, Automatik wählte: {sinn[:60]}')
    karte = {'id': kid, 'en': wort, 'pos': pos or eintrag['pos'],
             'sinn': sinn, 'quelle': f'kaikki.org/dictionary/English/meaning/{quelle[0]}/{quelle[:2]}/{quelle}.html',
             'de': deutsch(ts, eintrag['pos']), 'sprachen': {}, 'warnungen': warnungen}
    if korr.get('thema'): karte['thema'] = korr['thema']
    if korr.get('de'): karte['de'] = korr['de']
    if korr.get('emoji'): karte['emoji'] = korr['emoji']
    if not karte['de']:
        warnungen.append('kein Deutsch in dieser Bedeutungsgruppe')
    for kurz in SPRACHEN:
        kands = kandidaten(ts, kurz)
        if not kands and korr.get(kurz):
            kands = [{'w': korr[kurz], 'roman': korr.get(kurz + '_roman', ''), 'tags': [], 'trad': None}]
        if not kands:
            karte['sprachen'][kurz] = None; warnungen.append(f'{kurz} fehlt')
            continue
        haupt = waehle_hauptform(kands, raenge.get(kurz, {}), kurz)
        if korr.get(kurz):                      # kuratierte Hauptform überstimmt die Automatik
            haupt = next((k for k in kands if k['w'] == korr[kurz]), {'w': korr[kurz], 'roman': korr.get(kurz + '_roman', ''), 'tags': [], 'trad': None})
            haupt = dict(haupt, kuratiert=True)
        if korr.get(kurz + '_roman'):           # kuratierte Lesung, auch ohne neue Hauptform
            haupt = dict(haupt, roman=korr[kurz + '_roman'], kuratiert=True)
        akzeptiert = []
        for k in kands:
            akzeptiert.append(k['w'])
            if k['trad']: akzeptiert.append(k['trad'])
            if k['roman']: akzeptiert.append(k['roman'])
        karte['sprachen'][kurz] = {'w': haupt['w'], 'roman': haupt['roman'], 'tags': haupt['tags'],
                                   'rang': raenge.get(kurz, {}).get(haupt['w'].lower()), 'kuratiert': haupt.get('kuratiert', False),
                                   'akzeptiert': sorted(set(akzeptiert) - {haupt['w']})}
    return karte


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('woerter', nargs='*', help='englische Stichwörter, optional wort;pos;glossen-stichwort')
    ap.add_argument('--datei', help='Textdatei mit einem Stichwort je Zeile')
    ap.add_argument('--name', default='probe', help='Name der Ausgabedatei in data/')
    a = ap.parse_args()
    zeilen = list(a.woerter)
    if a.datei:
        zeilen += [z.strip() for z in open(a.datei, encoding='utf-8') if z.strip() and not z.startswith('#')]
    if not zeilen:
        ap.error('keine Stichwörter')
    print('Frequenzlisten …')
    raenge = {k: lade_frequenz(k) for k in SPRACHEN}
    korrekturen = lade_korrekturen()
    karten = []
    for z in zeilen:
        teile = [t.strip() for t in z.split(';')] + [None, None]
        wort, pos, stich = teile[0], teile[1] or None, teile[2] or None
        print(f'{wort} …')
        k = baue_karte(wort, pos, stich, raenge, korrekturen)
        if k:
            karten.append(k)
            fehlt = [s for s, v in k['sprachen'].items() if not v]
            kurz = '  '.join(f"{s}:{v['w']}" + (f"({v['roman']})" if v and v['roman'] else '') for s, v in k['sprachen'].items() if v)
            print(f'  {k["pos"]:5} {k["de"]:14} {kurz}' + (f'   FEHLT: {fehlt}' if fehlt else ''))
    aus = {'erzeugt': time.strftime('%Y-%m-%d'), 'lizenzhinweis': 'Übersetzungen aus dem englischen Wiktionary via kaikki.org (CC BY-SA 3.0); Häufigkeiten aus hermitdave/FrequencyWords (MIT).',
           'sprachen': {k: v[0] for k, v in SPRACHEN.items()}, 'karten': karten}
    ziel = os.path.join(DATEN, f'{a.name}.json')
    json.dump(aus, open(ziel, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'\n{len(karten)} Karten → {os.path.relpath(ziel, WURZEL)}')


if __name__ == '__main__':
    main()
