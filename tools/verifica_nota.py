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
# §2  L'esponenziale e la tangente del semiangolo
# ===========================================================================

def _gd(x):
    """Funzione gudermanniana."""
    return 2 * mp.atan(mp.tanh(x / 2))


def _frazione_continua(x, termini):
    """I primi quozienti parziali della frazione continua di x > 0."""
    q = []
    for _ in range(termini):
        a = int(mp.floor(x))
        q.append(a)
        x = 1 / (x - a)
    return q


def _pade_diagonale(n, t):
    """[n/n] di Padé di e^t: P_n(t)/P_n(-t), P_n(t) = sum (2n-k)! n! / ((2n)! k! (n-k)!) t^k."""
    p = lambda t: sum(Fraction(factorial(2 * n - k) * factorial(n),
                               factorial(2 * n) * factorial(k) * factorial(n - k)) * t ** k
                      for k in range(n + 1))
    return p(t) / p(-t)


def _lambert(x, livelli):
    """Convergente della frazione continua di Lambert: tanh x = x/(1+x^2/(3+x^2/(5+...)))."""
    coda = Fraction(2 * livelli - 1)
    for k in range(livelli - 1, 0, -1):
        coda = (2 * k - 1) + x * x / coda
    return x / coda


@controllo('§2')
def cayley():
    """e^{it} = (1+iu)/(1-iu) = (1+iu)^2/(1+u^2) = sgn(1+iu)^2, u = tan(t/2)"""
    for t in map(mp.mpf, ('0.3', '1', '2.5', '-2.9')):
        u = mp.tan(t / 2)
        w = mp.exp(1j * t)
        uguali(w, (1 + 1j * u) / (1 - 1j * u), cosa='t=%s' % t)
        uguali(w, (1 + 1j * u) ** 2 / (1 + u ** 2), cosa='t=%s' % t)
        uguali(w, ((1 + 1j * u) / abs(1 + 1j * u)) ** 2, cosa='t=%s' % t)
        uguali(mp.cos(t), (1 - u ** 2) / (1 + u ** 2))
        uguali(mp.sin(t), 2 * u / (1 + u ** 2))


@controllo('§2')
def gauss_3_4():
    """gauss #2-#4: 1 + tan^2(t/2) = 2/(1+cos t) = d/dt 2 tan(t/2)"""
    for t in map(mp.mpf, ('0.4', '1.9', '-2.2')):
        v = 1 + mp.tan(t / 2) ** 2
        uguali(v, 2 / (1 + mp.cos(t)))
        uguali(v, mp.diff(lambda s: 2 * mp.tan(s / 2), t), rel=mp.mpf('1e-30'))


@controllo('§2')
def tangente_iperbolica():
    """e^s = (1+τ)/(1-τ) e s = ln((1+τ)/(1-τ)), τ = tanh(s/2), per ogni s reale"""
    for s in map(mp.mpf, ('0.5', '1', '3', '-2', '10')):
        tau = mp.tanh(s / 2)
        uguali(mp.exp(s), (1 + tau) / (1 - tau), cosa='s=%s' % s)
        uguali(s, mp.log((1 + tau) / (1 - tau)), cosa='s=%s' % s)
    tau = mp.tanh(mp.mpf(1) / 2)
    uguali(mp.e, (1 + tau) / (1 - tau))
    uguali(tau, (mp.e - 1) / (mp.e + 1))
    assert mp.nstr(tau, 8) == '0.46211716' and str(tau).startswith('0.46211715')


cita('tanh_mezzo', '0{,}46211715', '0.46211715')


@controllo('§2')
def atan_immaginario():
    """atan #2 e #14: e^{i atan(ix)} = sqrt((1-x)/(1+x)), i atan(ix) = ln(1-x) - ln(1-x^2)/2"""
    for x in map(mp.mpf, ('0.2', '0.7', '-0.5')):
        uguali(mp.exp(1j * mp.atan(1j * x)), mp.sqrt((1 - x) / (1 + x)), cosa='x=%s' % x)
        uguali(1j * mp.atan(1j * x), mp.log(1 - x) - mp.log(1 - x ** 2) / 2, cosa='x=%s' % x)
        uguali(1j * mp.atan(1j * x), -mp.atanh(x), cosa='x=%s' % x)


@controllo('§2')
def gaussiana():
    """gauss #5 e #14: e^{-x^2} = (1-tanh(x^2/2))/(1+tanh(x^2/2)); 1+i tan(i x^2/2) è reale positivo"""
    for x in map(mp.mpf, ('0.3', '1', '2.4')):
        th = mp.tanh(x ** 2 / 2)
        uguali(mp.exp(-x ** 2), (1 - th) / (1 + th), cosa='x=%s' % x)
        z = 1 + 1j * mp.tan(1j * x ** 2 / 2)
        uguali(z, 1 - th)
        assert mp.re(z) > 0 and abs(mp.im(z)) < mp.mpf('1e-50')


@controllo('§2')
def gudermanniana():
    """tan gd = sinh, sin gd = tanh, cos gd = sech; atan(tanh x) = gd(2x)/2 (mate #115-#116)"""
    for x in map(mp.mpf, ('0.3', '1.2', '-2')):
        g = _gd(x)
        uguali(mp.tan(g), mp.sinh(x))
        uguali(mp.sin(g), mp.tanh(x))
        uguali(mp.cos(g), mp.sech(x))
        uguali(mp.atan(mp.tanh(x)), _gd(2 * x) / 2)


@controllo('§2')
def eulero_frazione_continua():
    """(e-1)/(e+1) = [0; 2, 6, 10, 14, ...] (20 termini); tanh(1/3) = [0; 3, 9, 15, ...]"""
    with mp.workdps(300):
        q = _frazione_continua((mp.e - 1) / (mp.e + 1), 20)
        assert q == [0] + [4 * k - 2 for k in range(1, 20)], q
        q = _frazione_continua(mp.tanh(mp.mpf(1) / 3), 10)
        assert q == [0] + [3 * (2 * k - 1) for k in range(1, 10)], q


@controllo('§2')
def pade_da_lambert():
    """i convergenti di Lambert per tanh(t/2) danno [1/1], [2/2], [3/3] di Padé di e^t"""
    for t in (Fraction(1, 3), Fraction(-2, 5), Fraction(3), Fraction(7, 4), Fraction(-5)):
        for n in (1, 2, 3):
            tau = _lambert(t / 2, n)
            assert (1 + tau) / (1 - tau) == _pade_diagonale(n, t), (n, t)
    assert _pade_diagonale(2, Fraction(1)) == Fraction(12 + 6 + 1, 12 - 6 + 1)
    assert _pade_diagonale(3, Fraction(1)) == Fraction(120 + 60 + 12 + 1, 120 - 60 + 12 - 1)


@controllo('§2')
def pade_errori():
    """R_1(t) - e^t ~ t^3/12; l'errore di [n/n] è O(t^(2n+1)); |R_n(it)| = 1"""
    for n in (1, 2, 3):
        rapporti = []
        for t in (mp.mpf('1e-4'), mp.mpf('1e-5')):
            r = mp.mpf(_pade_diagonale(n, Fraction(str(t))).numerator) / \
                _pade_diagonale(n, Fraction(str(t))).denominator
            rapporti.append((r - mp.exp(t)) / t ** (2 * n + 1))
        assert vicini(rapporti[0], rapporti[1], rel=mp.mpf('1e-3')), (n, rapporti)
        if n == 1:
            uguali(rapporti[1], mp.mpf(1) / 12, rel=mp.mpf('1e-4'))
    for t in map(mp.mpf, ('0.5', '2', '7')):
        r1 = (1 + 1j * t / 2) / (1 - 1j * t / 2)
        uguali(abs(r1), 1)


@controllo('§2')
def bilineare():
    """con z = e^{iωT}: (z-1)/(z+1) = i tan(ωT/2); con z = e^{sT}: (z-1)/(z+1) = tanh(sT/2)"""
    T = mp.mpf('0.7')
    for w in map(mp.mpf, ('0.4', '1.5', '3')):
        z = mp.exp(1j * w * T)
        uguali((z - 1) / (z + 1), 1j * mp.tan(w * T / 2))
    for s in (mp.mpf('-1.3'), mp.mpc('-0.2', '2.1')):
        z = mp.exp(s * T)
        uguali((z - 1) / (z + 1), mp.tanh(s * T / 2))


# ===========================================================================
# §3  Una catena di fattoriali che si spezza
# ===========================================================================

def _T(m):
    return m * (m + 1) // 2


def _P(p):
    """Prodotto dei fattoriali dei dispari fino a 2p+1."""
    return prod(factorial(2 * k + 1) for k in range(p + 1))


def _a(p):
    """a_p = T_{p+1}! / (T_p! (2p+1)!) = prod_{j=1}^{p+1} (T_p + j) / (2p+1)!"""
    return Fraction(prod(range(_T(p) + 1, _T(p + 1) + 1)), factorial(2 * p + 1))


def _g(p):
    return Fraction((p + 2) * (p + 3), 4 * (p + 1) * (2 * p + 3))


def _B(p):
    """Maggiorazione di a_{p+1}/a_p."""
    return mp.exp(mp.mpf((p + 1) ** 2) / (_T(p) + 1)) * mp.mpf(_g(p).numerator) / _g(p).denominator


@controllo('§3')
def catena_fino_a_3():
    """P_p = T_{p+1}! per p = 0..3 e non per p = 4; i passi 1!3! = 3!, 3!5! = 6!, 6!7! = 10!"""
    for p in range(4):
        assert _P(p) == factorial(_T(p + 1)), p
    assert _P(4) != factorial(_T(5))
    assert factorial(1) * factorial(3) == factorial(3)
    assert factorial(3) * factorial(5) == factorial(6)
    assert factorial(6) * factorial(7) == factorial(10)


@controllo('§3')
def quasi_successo():
    """passo 4: 11·12·13·14·15 = 360360 contro 9! = 362880, a_4 = 0.99306"""
    assert 11 * 12 * 13 * 14 * 15 == 360360 and factorial(9) == 362880
    assert _a(4) == Fraction(360360, 362880)
    assert round(float(_a(4)), 5) == 0.99306


cita('a4', '0{,}99306', '0.99306')
cita('passo4', '360\\,360', '360{,}360')
cita('nove_fatt', '362\\,880', '362{,}880')


@controllo('§3')
def a_minore_di_uno():
    """a_p < 1 per 4 <= p <= 100, con massimo a_4"""
    valori = [_a(p) for p in range(4, 101)]
    assert all(v < 1 for v in valori)
    assert max(valori) == _a(4)


@controllo('§3')
def maggiorazione():
    """(p+1)^2/(T_p+1) <= 2+2/p; g decrescente; e^2.02·g(100) < 0.966; a_{p+1}/a_p <= B(p)"""
    for p in range(1, 100001):
        assert (p + 1) ** 2 * p <= (2 * p + 2) * (_T(p) + 1), p
    for p in range(0, 60):     # identità polinomiale di grado 3: bastano 4 punti
        assert ((2 * p + 5) * (2 * p * p + 5 * p + 3) - (p * p + 5 * p + 6) * (4 * p + 5)
                == -5 * p * p - 18 * p - 15)
    assert _g(100) == Fraction(10506, 82012)
    assert round(float(_g(100)), 5) == 0.1281
    assert mp.exp(mp.mpf('2.02')) * mp.mpf(_g(100).numerator) / _g(100).denominator < mp.mpf('0.966')
    assert _B(100) < mp.mpf('0.966')
    for p in range(100, 301):
        r = _a(p + 1) / _a(p)
        assert mp.mpf(r.numerator) / r.denominator <= _B(p), p


cita('g100', '0{,}12810', '0.12810')
cita('soglia', '0{,}966', '0.966')


@controllo('§3')
def differenze_positive():
    """P_p - T_{p+1}! > 0 per 4 <= p <= 30: il prodotto dei dispari supera il fattoriale"""
    for p in range(4, 31):
        assert _P(p) > factorial(_T(p + 1)), p


@controllo('§3')
def limite_del_rapporto():
    """a_{p+1}/a_p tende a e^2/8 = 0.9236...; a p = 3000 dista meno di 1e-3"""
    p = 3000
    r = mp.mpf(_T(p + 2)) / ((2 * p + 2) * (2 * p + 3))
    for j in range(1, p + 2):
        r *= 1 + mp.mpf(p + 1) / (_T(p) + j)
    assert abs(r - mp.e ** 2 / 8) < mp.mpf('1e-3'), r
    assert mp.nstr(mp.e ** 2 / 8, 4) == '0.9236'


cita('e2_8', '0{,}9236', '0.9236')


# ===========================================================================
# §4  La media e il punto medio
# ===========================================================================

def _media(f, c, h):
    """Media di f su [c-h, c+h]."""
    return mp.quad(f, [c - h, c + h]) / (2 * h)


def _S(z):
    """sinh(z)/z, con valore 1 in 0."""
    return mp.mpf(1) if z == 0 else mp.sinh(z) / z


def _T_op(f, t):
    """Operatore dei quaderni: media su [0, t] divisa per il valore in t/2."""
    return mp.quad(f, [0, t]) / t / f(t / 2)


@controllo('§4')
def media_soluzioni():
    """se f'' = μ² f, la media su [c-h, c+h] vale f(c)·sinh(μh)/(μh)"""
    casi = [
        (mp.sin, 1j), (mp.cos, 1j), (lambda x: mp.cos(x) + 2 * mp.sin(x), 1j),
        (lambda x: mp.exp(1j * x), 1j), (mp.exp, 1), (mp.cosh, 1),
        (lambda x: mp.exp(2 * x), 2), (lambda x: 3 - 5 * x, 0),
    ]
    for f, mu in casi:
        for c, h in ((mp.mpf('0.7'), mp.mpf('0.4')), (mp.mpf('-1.3'), mp.mpf('2.1'))):
            uguali(_media(f, c, h), f(c) * _S(mu * h), rel=mp.mpf('1e-30'),
                   cosa='mu=%s c=%s h=%s' % (mu, c, h))


@controllo('§4')
def trasformata_t_righe():
    """Trasformata T #3-#8: e^x, sin, cos, e^{ix}, e^{2πix}, x^n"""
    t = mp.mpf('1.7')
    uguali(_T_op(mp.exp, t), mp.sinh(t / 2) / (t / 2), rel=mp.mpf('1e-30'))
    for f in (mp.sin, mp.cos, lambda x: mp.exp(1j * x)):
        uguali(_T_op(f, t), mp.sin(t / 2) / (t / 2), rel=mp.mpf('1e-30'))
    uguali(_T_op(lambda x: mp.exp(2j * mp.pi * x), t),
           mp.sin(mp.pi * t) / (mp.pi * t), rel=mp.mpf('1e-30'))
    for n in range(7):
        uguali(_T_op(lambda x: x ** n, t), mp.mpf(2) ** n / (n + 1), rel=mp.mpf('1e-30'))


@controllo('§4')
def media_sferica():
    """media sferica di Helmholtz: n = 1 dà cos(kr), n = 3 dà sin(kr)/(kr)"""
    nucleo = lambda n, z: mp.gamma(mp.mpf(n) / 2) * (2 / z) ** (mp.mpf(n) / 2 - 1) \
        * mp.besselj(mp.mpf(n) / 2 - 1, z)
    for z in map(mp.mpf, ('0.5', '2', '7.3')):
        uguali(nucleo(3, z), mp.sin(z) / z)
        uguali(nucleo(1, z), mp.cos(z))
        # media di e^{i k·x} sulla sfera di raggio r in R^3, con kr = z
        m = mp.quad(lambda th: mp.exp(1j * z * mp.cos(th)) * mp.sin(th) / 2, [0, mp.pi])
        uguali(m, mp.sin(z) / z, rel=mp.mpf('1e-30'))
        # media sull'intervallo in R^1: stesso nucleo
        uguali(_media(lambda x: mp.cos(x), 0, z), mp.sin(z) / z, rel=mp.mpf('1e-30'))


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
