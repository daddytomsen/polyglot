#!/usr/bin/env python3
"""Zeichnet die App-Icons als PNG ohne Zusatzbibliotheken (gleiches Motiv wie icon.svg):
Farbverlauf grün→blau, weiße Scheibe mit blauem Ring, fünf farbige Punkte für fünf Sprachen."""
import struct, zlib, os, math
WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def png(w, h, px):
    raw = b''.join(b'\x00' + bytes(px[y]) for y in range(h))
    def chunk(t, d): return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b'')
def mix(a, b, t): return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))
def icon(n):
    G, B, W = (0x58, 0xcc, 0x02), (0x1c, 0xb0, 0xf6), (255, 255, 255)
    dots = [(0xff, 0xc8, 0x00), (0xff, 0x4b, 0x4b), W, (0xce, 0x82, 0xff), (0xff, 0x96, 0x00)]
    cx, cy, r = n / 2, n * 0.46, n * 0.25
    rows = []
    for y in range(n):
        row = []
        for x in range(n):
            c = mix(G, B, (x + y) / (2 * n))
            d = math.hypot(x + .5 - cx, y + .5 - cy)
            if d < r: c = W if d < r * 0.62 or d > r * 0.8 else B          # weiße Scheibe mit blauem Ring
            for i, col in enumerate(dots):
                if math.hypot(x + .5 - n * (0.1875 + i * 0.15625), y + .5 - n * 0.8125) < n * 0.055: c = col
            row.extend(c)
        rows.append(row)
    return png(n, n, rows)
for name, n in [('icon-512.png', 512), ('icon-192.png', 192), ('apple-touch-icon.png', 180)]:
    open(os.path.join(WURZEL, name), 'wb').write(icon(n)); print(name, n)
