# -*- coding: utf-8 -*-
"""
Controlla ogni affermazione numerica della nota (cartella nota/).

Ogni controllo e' una funzione registrata con @controllo('§N') che fallisce
sollevando un'eccezione con un messaggio leggibile. Ogni valore riportato nel
testo e' registrato con cita(), nella forma tipografica esatta che ha nelle
due lingue: controlla_testi.py verifica poi che compaia davvero nei sorgenti.

Uso:  python verifica_nota.py [--sezione §N] [--valori]
"""
import sys, json, random
from fractions import Fraction
from math import factorial, prod

import mpmath as mp

mp.mp.dps = 60

REGISTRO = []          # (sezione, nome, funzione)
VALORI_CITATI = {}     # chiave -> (forma italiana, forma inglese)


def controllo(sezione):
    """Registra la funzione decorata come controllo della sezione data."""
    def registra(f):
        nome = (f.__doc__ or f.__name__).strip().splitlines()[0]
        REGISTRO.append((sezione, nome, f))
        return f
    return registra


def cita(chiave, it, en):
    """Registra un valore come compare nel .tex italiano e in quello inglese."""
    if chiave in VALORI_CITATI:
        raise ValueError('valore citato due volte: ' + chiave)
    VALORI_CITATI[chiave] = (it, en)


def vicini(a, b, rel=mp.mpf('1e-40')):
    """Uguaglianza a meno di un errore relativo (anche per numeri complessi)."""
    a, b = mp.mpmathify(a), mp.mpmathify(b)
    scala = max(abs(a), abs(b))
    return scala == 0 or abs(a - b) <= rel * scala


def uguali(a, b, rel=mp.mpf('1e-40'), cosa=''):
    """Come vicini(), ma fallisce con un messaggio che riporta i due valori."""
    if not vicini(a, b, rel):
        raise AssertionError('%s%s != %s' % (cosa + ': ' if cosa else '',
                                             mp.nstr(a, 15), mp.nstr(b, 15)))


# ===========================================================================
# §10  Due refusi e una trappola
# ===========================================================================

def _scarto_binomiale(m, n):
    """Legge delle righe teoria #8-#13: (1+x)^m - 1 - x^m con x = 1/n."""
    x = Fraction(1, n)
    return (1 + x) ** m - 1 - x ** m


# teoria #8-#13, coefficiente di ε: m * (polinomio in n) / n^(m-1)
_RIGHE_TEORIA = {
    8:  (2, lambda n: Fraction(1)),
    9:  (3, lambda n: Fraction(n + 1)),
    10: (4, lambda n: n ** 2 + Fraction(3, 2) * n + 1),
    11: (5, lambda n: Fraction(n ** 3 + 2 * n ** 2 + 2 * n + 1)),
    12: (6, lambda n: n ** 4 + Fraction(15, 6) * n ** 3 + Fraction(10, 3) * n ** 2
         + Fraction(15, 6) * n + 1),
    13: (7, lambda n: Fraction(n ** 5 + 3 * n ** 4 + 10 * n ** 3 + 5 * n ** 2
                               + 3 * n + 1)),
}


@controllo('§10')
def teoria_righe_8_12():
    """teoria #8-#12 seguono la legge ε[(1+x)^m - 1 - x^m], x = 1/n"""
    for riga in range(8, 13):
        m, poli = _RIGHE_TEORIA[riga]
        for n in range(2, 21):
            scritto = m * poli(n) / Fraction(n) ** (m - 1)
            assert scritto == _scarto_binomiale(m, n), 'riga %d, n=%d' % (riga, n)


@controllo('§10')
def teoria_13():
    """teoria #13: con 5 al posto di 10 segue la legge; lo scarto vale 35ε/n^3"""
    m, poli = _RIGHE_TEORIA[13]
    for n in range(2, 21):
        scritto = m * poli(n) / Fraction(n) ** 6
        corretto = scritto - m * 5 * Fraction(n) ** 3 / Fraction(n) ** 6
        assert corretto == _scarto_binomiale(m, n), 'n=%d' % n
        assert scritto - _scarto_binomiale(m, n) == Fraction(35, n ** 3), 'n=%d' % n


@controllo('§10')
def factor_5():
    """factor #5: 1!3!5!7!9! - 15! = 2^11 3^6 5^3 7^2, non 7^3"""
    d = prod(factorial(k) for k in (1, 3, 5, 7, 9)) - factorial(15)
    assert d == 2 ** 11 * 3 ** 6 * 5 ** 3 * 7 ** 2
    assert d != 2 ** 11 * 3 ** 6 * 5 ** 3 * 7 ** 3
    assert d == 9144576000


_FATTORIZZAZIONI = {   # factor #6-#15: differenza scritta come prodotto di potenze
    6: '2^18*3^9*5^4*7^3*11^3',
    7: '2^25*3^13*5^6*7^4*11^2*13*7103',
    8: '2^34*3^17*5^8*7^5*11^3*13^2*4013*4261',
    9: '2^41*3^21*5^10*7^6*11^5*13^3*17*8933*22969787',
    10: '2^50*3^26*5^13*7^8*11^6*13^4*17^2*19*3116563*333915299',
    11: '2^64*3^31*5^15*7^10*11^6*13^7*17^3*19^2*251*6184811*13366363319',
    12: '2^74*3^36*5^18*7^12*11^7*13^7*17^4*19^3*23*1543*3529737954001890223489333',
    13: '2^86*3^44*5^21*7^14*11^8*13^7*17^5*19^4*23^2*7527420903061154660844431547708509201',
    14: '2^101*3^50*5^25*7^17*11^9*13^8*17^6*19^5*23^3*267661*669113*96487944706595864404794370019938759',
    15: '2^116*3^58*5^28*7^19*11^10*13^9*17^7*19^6*23^4*29*967*106487*459130657*3283850683*26841959932382587431547457373253',
}


@controllo('§10')
def factor_righe_6_15():
    """factor #6-#15: tutte le altre fattorizzazioni sono esatte"""
    for riga, testo in _FATTORIZZAZIONI.items():
        p = riga - 1
        t = (p + 1) * (p + 2) // 2
        diff = prod(factorial(2 * k + 1) for k in range(p + 1)) - factorial(t)
        val = prod(int(b) ** int(e or 1) for b, e in
                   (f.partition('^')[::2] for f in testo.split('*')))
        assert val == diff, 'riga %d' % riga


cita('factor5_diff', '9\\,144\\,576\\,000', '9{,}144{,}576{,}000')


@controllo('§10')
def mate_identita():
    """mate #21: il primo membro vale 1/2 per ogni k, quindi k = -4.999999701 non dice nulla"""
    rnd = random.Random(10)
    for _ in range(6):
        x, y, k = (mp.mpf(rnd.uniform(-3, 3)) for _ in range(3))
        v = ((mp.cos(x + k * y) ** 2 - mp.cos(x - k * y) ** 2)
             / (mp.cos(2 * x + 2 * k * y) - mp.cos(2 * x - 2 * k * y)))
        uguali(v, mp.mpf(1) / 2, cosa='x=%s y=%s k=%s' % (x, y, k))


cita('mate_k', '-4{,}999999701', '-4.999999701')


# ===========================================================================

def main(argv):
    if '--valori' in argv:
        print(json.dumps(VALORI_CITATI, ensure_ascii=False, indent=1))
        return 0
    sezione = argv[argv.index('--sezione') + 1] if '--sezione' in argv else None
    eseguiti = falliti = 0
    for sez, nome, f in REGISTRO:
        if sezione and sez != sezione:
            continue
        eseguiti += 1
        try:
            f()
            print('  ok   %s %s' % (sez, nome))
        except Exception as e:     # anche un errore di calcolo e' un fallimento
            falliti += 1
            print('  NO   %s %s: %s' % (sez, nome, str(e) or type(e).__name__))
    print('%d controlli, %d falliti' % (eseguiti, falliti))
    if eseguiti == 0:
        print('  nessun controllo per la sezione %s' % sezione)
        return 1
    return 1 if falliti else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
