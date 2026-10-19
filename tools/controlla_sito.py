# -*- coding: utf-8 -*-
"""
Controlla le due pagine di presentazione (site/index.html e site/en/index.html).

Per ciascuna pagina:
  - l'attributo lang dell'elemento html;
  - esattamente tre link di download, uguali agli URL della release;
  - un link all'altra lingua e uno al repository;
  - ogni href o src relativo punta a un file esistente in site/;
  - KaTeX da cdnjs, con la stessa versione per tutti i file;
  - i metadati Open Graph og:title, og:description, og:url;
  - la riga di trasparenza nella lingua della pagina.

Inoltre, se esiste dist/ (dopo make dist), deve contenere esattamente i tre PDF
a cui puntano i link di download.

Uso:  python controlla_sito.py
"""
import os, re, sys
from html.parser import HTMLParser

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITO = os.path.join(RADICE, 'site')

REPOSITORY = 'https://github.com/endjneer/quaderni-derive'
RELEASE = REPOSITORY + '/releases/latest/download/'
PDF = ['quaderni-derive-nota.pdf', 'derive-notebooks-note.pdf',
       'quaderni-derive-edizione-integrale.pdf']
PAGINA = 'https://endjneer.github.io/quaderni-derive/'
KATEX = 'https://cdnjs.cloudflare.com/ajax/libs/KaTeX/'

PAGINE = {
    'index.html': dict(
        lang='it', altra='en/', url=PAGINA,
        trasparenza="Analisi e redazione con l'assistenza di Claude (Anthropic); "
                    "ogni verifica numerica è riproducibile dal repository."),
    'en/index.html': dict(
        lang='en', altra='../', url=PAGINA + 'en/',
        trasparenza='Analysis and writing assisted by Claude (Anthropic); '
                    'every numerical check can be reproduced from the repository.'),
}


class Lettore(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lang = None
        self.link = []         # (attributo, valore)
        self.meta = {}
        self.testo = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html':
            self.lang = a.get('lang')
        for chiave in ('href', 'src'):
            if chiave in a:
                self.link.append((tag, a[chiave]))
        if tag == 'meta' and 'property' in a:
            self.meta[a['property']] = a.get('content', '')

    def handle_data(self, data):
        self.testo.append(data)


def controlla(nome, atteso):
    problemi = []
    percorso = os.path.join(SITO, nome)
    if not os.path.exists(percorso):
        return ['manca site/%s' % nome]
    l = Lettore()
    l.feed(open(percorso, encoding='utf-8').read())
    testo = re.sub(r'\s+', ' ', ''.join(l.testo))

    if l.lang != atteso['lang']:
        problemi.append('%s: lang=%r invece di %r' % (nome, l.lang, atteso['lang']))

    download = [v for _, v in l.link if v.startswith(RELEASE)]
    if sorted(download) != sorted(RELEASE + p for p in PDF):
        problemi.append('%s: link di download %s' % (nome, download))

    if not any(v == atteso['altra'] for t, v in l.link if t == 'a'):
        problemi.append('%s: manca il link all\'altra lingua (%s)' % (nome, atteso['altra']))
    if not any(v == REPOSITORY for t, v in l.link if t == 'a'):
        problemi.append('%s: manca il link al repository' % nome)

    cartella = os.path.dirname(percorso)
    for _, v in l.link:
        if re.match(r'^(https?:|mailto:|data:|#)', v):
            continue
        destinazione = os.path.normpath(os.path.join(cartella, v.split('#')[0]))
        if os.path.isdir(destinazione):
            destinazione = os.path.join(destinazione, 'index.html')
        if not os.path.exists(destinazione):
            problemi.append('%s: link relativo rotto %s' % (nome, v))

    katex = [v for _, v in l.link if 'katex' in v.lower()]
    versioni = set(re.findall(r'KaTeX/([0-9.]+)/', ' '.join(katex)))
    if not katex or not all(v.startswith(KATEX) for v in katex) or len(versioni) != 1:
        problemi.append('%s: KaTeX %s' % (nome, katex))

    for proprieta in ('og:title', 'og:description', 'og:url'):
        if not l.meta.get(proprieta):
            problemi.append('%s: manca %s' % (nome, proprieta))
    if l.meta.get('og:url') not in (None, atteso['url']):
        problemi.append('%s: og:url %s' % (nome, l.meta.get('og:url')))

    if atteso['trasparenza'] not in testo:
        problemi.append('%s: manca la riga di trasparenza' % nome)
    return problemi


def controlla_dist():
    """Se dist/ esiste (dopo make dist), contiene esattamente i PDF linkati."""
    dist = os.path.join(RADICE, 'dist')
    if not os.path.isdir(dist):
        return []
    trovati = sorted(os.listdir(dist))
    if trovati != sorted(PDF):
        return ['dist/ contiene %s invece di %s' % (trovati, sorted(PDF))]
    return []


def main():
    problemi = controlla_dist()
    for nome, atteso in PAGINE.items():
        problemi += controlla(nome, atteso)
    for p in problemi:
        print('  NO   ' + p)
    print('controllo del sito: %d problemi' % len(problemi))
    return 1 if problemi else 0


if __name__ == '__main__':
    sys.exit(main())
