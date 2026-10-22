# -*- coding: utf-8 -*-
"""
Controlli di qualità su un PDF prodotto da pdflatex e, a richiesta, sul suo
log di compilazione.

Fallisce se:
  - un font è di tipo Type 3 (bitmap: sullo schermo appare sgranato);
  - il titolo nei metadati è vuoto (l'anteprima di un link resta senza nome);
  - l'autore nei metadati non è quello indicato con --autore;
  - il numero di pagine è fuori dall'intervallo richiesto;
  - il log contiene un errore, un riferimento o una citazione non definiti.

Uso:  python controlla_pdf.py PDF [--log LOG] [--pagine MIN MAX] [--autore NOME]
"""
import sys, re, argparse

import pymupdf


def problemi_font(doc):
    tipo3 = set()
    for n in range(len(doc)):
        for f in doc.get_page_fonts(n):
            if f[2] == 'Type3':
                tipo3.add(f[3])
    return ['font Type 3: ' + ', '.join(sorted(tipo3))] if tipo3 else []


def problemi_titolo(doc):
    titolo = (doc.metadata or {}).get('title', '').strip()
    return [] if titolo else ['titolo vuoto nei metadati']


def problemi_autore(doc, atteso):
    autore = (doc.metadata or {}).get('author', '').strip()
    return [] if autore == atteso else ['autore %r invece di %r' % (autore, atteso)]


def problemi_pagine(doc, minimo, massimo):
    n = len(doc)
    if minimo <= n <= massimo:
        return []
    return ['%d pagine, attese fra %d e %d' % (n, minimo, massimo)]


NON_DEFINITI = re.compile(
    r'(Reference|Citation) .* undefined|There were undefined references')


def problemi_log(percorso):
    problemi = []
    with open(percorso, encoding='latin-1') as f:
        for riga in f:
            riga = riga.rstrip('\n')
            if riga.startswith('!') or NON_DEFINITI.search(riga):
                problemi.append(riga)
    return problemi


def main(argv):
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument('pdf')
    p.add_argument('--log')
    p.add_argument('--pagine', nargs=2, type=int, metavar=('MIN', 'MAX'))
    p.add_argument('--autore')
    a = p.parse_args(argv)

    doc = pymupdf.open(a.pdf)
    controlli = [('font', problemi_font(doc)),
                 ('titolo', problemi_titolo(doc))]
    if a.pagine:
        controlli.append(('pagine', problemi_pagine(doc, *a.pagine)))
    if a.autore:
        controlli.append(('autore', problemi_autore(doc, a.autore)))
    if a.log:
        controlli.append(('log', problemi_log(a.log)))

    falliti = 0
    for nome, problemi in controlli:
        if problemi:
            falliti += 1
            for pr in problemi:
                print('  NO   %s %s: %s' % (a.pdf, nome, pr))
        else:
            print('  ok   %s %s' % (a.pdf, nome))
    return 1 if falliti else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
