# -*- coding: utf-8 -*-
"""Estrae alcune pagine del PDF come immagini, per il controllo visivo."""
import sys, os
import pymupdf

doc = pymupdf.open(sys.argv[1])
out = sys.argv[2]
os.makedirs(out, exist_ok=True)
for n in [int(x) for x in sys.argv[3:]]:
    p = doc[n - 1]
    pix = p.get_pixmap(dpi=110)
    f = os.path.join(out, 'p%03d.png' % n)
    pix.save(f)
    print(f)
