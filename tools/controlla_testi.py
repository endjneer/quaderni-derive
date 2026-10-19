# -*- coding: utf-8 -*-
"""
Controlla la coerenza dei sorgenti della nota (cartella nota/).

  1. ogni sezione esiste in entrambe le lingue;
  2. etichette, citazioni e riferimenti alle righe dei quaderni coincidono
     fra la versione italiana e quella inglese di ogni sezione;
  3. ogni valore registrato con cita() in verifica_nota.py compare nel testo
     della sua lingua;
  4. ogni decimale con almeno tre cifre dopo la virgola e' un valore
     registrato con cita(), cioe' controllato;
  5. le parole sconsigliate vengono segnalate, senza far fallire il controllo.
  6. ogni citazione ha la sua voce in bibliografia; una voce mai citata
     viene segnalata come avviso.

Uso:  python controlla_testi.py
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verifica_nota as V

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTA = os.path.join(RADICE, 'nota')

COPPIE = [
    ('00-abstract', '00-abstract'),
    ('01-introduzione', '01-introduction'),
    ('02-semiangolo', '02-half-angle'),
    ('03-fattoriali', '03-factorials'),
    ('04-media', '04-mean'),
    ('05-cosinc', '05-cosinc'),
    ('06-gradini', '06-steps'),
    ('07-e', '07-e'),
    ('08-delta', '08-delta'),
    ('09-in-breve', '09-in-brief'),
    ('10-refusi', '10-typos'),
    ('A-recupero', 'A-recovery'),
    ('Z-colofone', 'Z-colophon'),
]

DECIMALE = {
    'it': re.compile(r'\d+\{,\}\d{3,}'),
    'en': re.compile(r'(?<![\d.])\d+\.\d{3,}'),
}

SCONSIGLIATE = {
    'it': ['elegante', 'notevole', 'sorprendente'],
    'en': ['elegant', 'remarkable', 'surprising'],
}


def leggi(percorso):
    """Il sorgente senza i commenti (un % non preceduto da barra rovesciata)."""
    righe = []
    with open(percorso, encoding='utf-8') as f:
        for riga in f:
            righe.append(re.sub(r'(?<!\\)%.*', '', riga))
    return ''.join(righe)


def riferimenti(testo):
    """Etichette, citazioni e righe dei quaderni presenti in un sorgente."""
    etichette = set(re.findall(r'\\label\{([^}]*)\}', testo))
    citazioni = set()
    for gruppo in re.findall(r'\\cite(?:\[[^]]*\])?\{([^}]*)\}', testo):
        citazioni.update(k.strip() for k in gruppo.split(','))
    righe = set('%s#%s' % m for m in re.findall(r'\\riga\{([^}]*)\}\{([^}]*)\}', testo))
    righe |= set('%s#%s-%s' % m for m in
                 re.findall(r'\\righe\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}', testo))
    return {'etichette': etichette, 'citazioni': citazioni, 'righe': righe}


def main():
    problemi, avvisi = [], []
    testi = {'it': {}, 'en': {}}

    # 1. le coppie esistono
    for it, en in COPPIE:
        for lingua, nome in (('it', it), ('en', en)):
            p = os.path.join(NOTA, lingua, nome + '.tex')
            if os.path.exists(p):
                testi[lingua][nome] = leggi(p)
            else:
                problemi.append('manca nota/%s/%s.tex' % (lingua, nome))

    # 2. stessi riferimenti nelle due lingue
    for it, en in COPPIE:
        if it not in testi['it'] or en not in testi['en']:
            continue
        ri, re_ = riferimenti(testi['it'][it]), riferimenti(testi['en'][en])
        for tipo in ri:
            if ri[tipo] != re_[tipo]:
                problemi.append('%s/%s, %s diversi: solo it %s, solo en %s' % (
                    it, en, tipo, sorted(ri[tipo] - re_[tipo]),
                    sorted(re_[tipo] - ri[tipo])))

    # 3. ogni valore citato compare nella sua lingua
    tutto = {l: '\n'.join(testi[l].values()) for l in testi}
    for chiave, (v_it, v_en) in sorted(V.VALORI_CITATI.items()):
        for lingua, v in (('it', v_it), ('en', v_en)):
            if v not in tutto[lingua]:
                problemi.append('valore %s (%s) assente dal testo %s' % (chiave, v, lingua))

    # 4. ogni decimale lungo e' un valore controllato
    registrati = {l: set() for l in testi}
    for v_it, v_en in V.VALORI_CITATI.values():
        registrati['it'].add(v_it)
        registrati['en'].add(v_en)
    for lingua in testi:
        for nome, testo in sorted(testi[lingua].items()):
            for numero in DECIMALE[lingua].findall(testo):
                if not any(numero in v for v in registrati[lingua]):
                    problemi.append('%s/%s: %s non e\' registrato con cita()'
                                    % (lingua, nome, numero))

    # 6. bibliografia: ogni citazione ha una voce; una voce mai citata e'
    #    un avviso (thebibliography la stamperebbe comunque)
    voci = set(re.findall(r'\\bibitem\{([^}]*)\}',
                          leggi(os.path.join(NOTA, 'bibliografia.tex'))))
    for lingua in testi:
        citate = set()
        for testo in testi[lingua].values():
            citate |= riferimenti(testo)['citazioni']
        for k in sorted(citate - voci):
            problemi.append('citazione %s senza voce in bibliografia (%s)' % (k, lingua))
        for k in sorted(voci - citate):
            avvisi.append('voce %s mai citata nel testo %s' % (k, lingua))

    # 5. parole sconsigliate
    for lingua in testi:
        for nome, testo in sorted(testi[lingua].items()):
            for parola in SCONSIGLIATE[lingua]:
                if re.search(r'\b%s' % parola, testo, re.IGNORECASE):
                    avvisi.append('%s/%s: "%s"' % (lingua, nome, parola))

    for a in avvisi:
        print('  avviso   ' + a)
    for p in problemi:
        print('  NO   ' + p)
    print('controllo dei testi: %d problemi, %d avvisi' % (len(problemi), len(avvisi)))
    return 1 if problemi else 0


if __name__ == '__main__':
    sys.exit(main())
