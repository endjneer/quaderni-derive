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
    # il semipiano sinistro va nel disco unitario: un filtro stabile resta stabile
    for s in (mp.mpc('-0.1', '3'), mp.mpc('-2', '-1'), mp.mpf('-0.5')):
        assert abs((1 + s / 2) / (1 - s / 2)) < 1, s


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
    assert _g(100) < Fraction(12811, 100000)        # maggiorante, non arrotondamento
    assert mp.exp(mp.mpf('2.02')) * mp.mpf('0.12811') < mp.mpf('0.966')
    assert _B(100) < mp.mpf('0.966')
    for p in range(100, 301):
        r = _a(p + 1) / _a(p)
        assert mp.mpf(r.numerator) / r.denominator <= _B(p), p


cita('g100', '0{,}12811', '0.12811')
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


@controllo('§3')
def crescita_del_rapporto():
    """P_p/T_{p+1}! = prod 1/a_q cresce più che esponenzialmente: il suo logaritmo è quadratico in p"""
    L = lambda p: sum(-mp.log(mp.mpf(_a(q).numerator) / _a(q).denominator) for q in range(4, p + 1))
    l20, l40, l80 = L(20), L(40), L(80)
    assert l40 / l20 > 3 and l80 / l40 > 3, (l20, l40, l80)     # lineare darebbe circa 2
    uguali(mp.exp(L(12)), mp.mpf(_P(12)) / factorial(_T(13)), rel=mp.mpf('1e-40'))


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
# §5  Il seno cardinale e il suo gemello
# ===========================================================================

def _sinc(x):
    return mp.mpf(1) if x == 0 else mp.sin(mp.pi * x) / (mp.pi * x)


@controllo('§5')
def cosinc_forma_integrale():
    """((-1)^x - 1)/(πx) = i ∫_0^1 e^{iπxs} ds; Im = sinc, Re = (cos πx - 1)/(πx)"""
    for x in map(mp.mpf, ('0.3', '1.7', '-2.2')):
        F = (mp.power(-1, x) - 1) / (mp.pi * x)
        uguali(F, 1j * mp.quad(lambda s: mp.exp(1j * mp.pi * x * s), [0, 1]),
               rel=mp.mpf('1e-30'))
        uguali(mp.im(F), _sinc(x))
        uguali(mp.re(F), (mp.cos(mp.pi * x) - 1) / (mp.pi * x))


@controllo('§5')
def cosinc_serie_e_limite():
    """cosinc #14-#16 e #28: la serie sum i^{n+1}(πx)^n/(n+1)! e il limite in 0 che vale i"""
    for x in map(mp.mpf, ('0.4', '2.5')):
        serie = mp.nsum(lambda n: 1j ** (n + 1) * (mp.pi * x) ** n / mp.factorial(n + 1), [0, mp.inf])
        uguali(serie, (mp.power(-1, x) - 1) / (mp.pi * x), rel=mp.mpf('1e-30'))
    h = mp.mpf('1e-30')
    assert abs((mp.power(-1, h) - 1) / (mp.pi * h) - 1j) < mp.mpf('1e-25')
    uguali(mp.diff(lambda x: mp.power(-1, x), mp.mpf('0.37')) / (mp.pi * mp.power(-1, mp.mpf('0.37'))),
           1j, rel=mp.mpf('1e-30'))


@controllo('§5')
def hilbert_del_sinc():
    """con Hf(x) = (1/π) vp ∫ f(t)/(x-t) dt vale H[sinc](x) = (1 - cos πx)/(πx)"""
    for x in map(mp.mpf, ('0.3', '1.7')):
        with mp.workdps(30):
            g = lambda t: (_sinc(x - t) - _sinc(x + t)) / t
            H = mp.quadosc(g, [0, mp.inf], period=2) / mp.pi
            atteso = (1 - mp.cos(mp.pi * x)) / (mp.pi * x)
            assert abs(H - atteso) < mp.mpf('1e-10'), (x, H, atteso)


@controllo('§5')
def gemello_non_integrabile():
    """∫_0^X (1 - cos πx)/(πx) dx cresce come ln(X)/π: nessun valore finito"""
    with mp.workdps(30):
        I = lambda X: mp.quad(lambda x: (1 - mp.cos(mp.pi * x)) / (mp.pi * x), mp.linspace(0, X, int(X) + 1))
        d1 = I(1000) - mp.log(1000) / mp.pi
        d2 = I(2000) - mp.log(2000) / mp.pi
        assert abs(d1 - d2) < mp.mpf('1e-3'), (d1, d2)
        assert I(10000) > mp.mpf('2.5')


cita('cosinc20', '11{,}534', '11.534')


# ===========================================================================
# §6  Gradini fatti di logaritmi
# ===========================================================================

@controllo('§6')
def lemma_massimo():
    """(|a-b| + |a+b|)/2 = max(|a|, |b|) per a, b reali"""
    rnd = random.Random(6)
    for _ in range(10):
        a, b = (mp.mpf(rnd.uniform(-5, 5)) for _ in range(2))
        uguali((abs(a - b) + abs(a + b)) / 2, max(abs(a), abs(b)))


@controllo('§6')
def gradino_e_segno():
    """mate #77, #80, #81: ln((|e^x-1|+|e^x+1|)/2) = max(x,0), da cui gradino e segno"""
    for x in map(mp.mpf, ('-3', '-0.2', '0.1', '4')):
        L = mp.log((abs(mp.exp(x) - 1) + abs(mp.exp(x) + 1)) / 2)
        assert abs(L - max(x, 0)) < mp.mpf('1e-50'), x
        H = L / x
        assert H == (1 if x > 0 else 0) or abs(H - (1 if x > 0 else 0)) < mp.mpf('1e-50')
        L2 = mp.log((abs(mp.exp(2 * x) - 1) + abs(mp.exp(2 * x) + 1)) / 2)
        assert abs(L2 / x - 1 - mp.sign(x)) < mp.mpf('1e-50')
        assert abs(2 * L / x - 1 - mp.sign(x)) < mp.mpf('1e-50')


@controllo('§6')
def log_cosh():
    """mate copia #88-#89: ln cosh x = |x| - ln 2 + ln(1 + e^{-2|x|})"""
    for x in map(mp.mpf, ('-5', '-0.3', '0.7', '6')):
        uguali(mp.log(mp.cosh(x)), abs(x) - mp.log(2) + mp.log(1 + mp.exp(-2 * abs(x))))


@controllo('§6')
def dequantizzazione():
    """max(a,b) <= h ln(e^{a/h} + e^{b/h}) <= max(a,b) + h ln 2"""
    h = mp.mpf('1e-3')
    for a, b in ((1, 2), (-3, 0.5), (0.25, 0.25)):
        a, b = mp.mpf(a), mp.mpf(b)
        v = h * mp.log(mp.exp(a / h) + mp.exp(b / h))
        assert max(a, b) <= v <= max(a, b) + h * mp.log(2), (a, b, v)


@controllo('§6')
def valore_nel_salto():
    """h ln((1+e^{x/h})/2)/x tende a 1/2 in x = 0; (1+tanh(x/h+1))/2 vale (1+tanh 1)/2 = 0.8808 in 0"""
    for h in map(mp.mpf, ('1', '0.1', '0.01')):
        x = mp.mpf('1e-25')
        v = h * mp.log((1 + mp.exp(x / h)) / 2) / x
        assert abs(v - mp.mpf(1) / 2) < mp.mpf('1e-20'), (h, v)
        for y in (mp.mpf('0.5'), mp.mpf('-0.5')):     # e converge al gradino fuori da 0
            g = h * mp.log((1 + mp.exp(y / h)) / 2) / y
            if h == mp.mpf('0.01'):
                assert abs(g - (1 if y > 0 else 0)) < mp.mpf('0.03'), (y, g)
    assert mp.nstr((1 + mp.tanh(1)) / 2, 4) == '0.8808'


cita('tanh1', '0{,}8808', '0.8808')


@controllo('§6')
def u0_sign0():
    """u(0)-sign(0) #2-#12: ln(e-1), ln sinh 1, (ln sinh 1 + 1)/2, 2 ln(e-1) - 1 e le differenze"""
    u1, s2 = mp.log(mp.e - 1), mp.log(mp.sinh(1))
    uguali(mp.log((mp.e ** 2 - 1) / (2 * mp.e)), s2)
    for valore, atteso in ((u1, '0.5413248546'), (s2, '0.1614393615'),
                           ((s2 + 1) / 2, '0.5807196807'), (2 * u1 - 1, '0.08264970922'),
                           ((s2 + 1) / 2 - u1, '0.03939482617'),
                           (s2 - (2 * u1 - 1), '0.07878965234')):
        assert abs(valore - mp.mpf(atteso)) < mp.mpf('1e-10'), (valore, atteso)
    uguali(s2 - (2 * u1 - 1), 2 * ((s2 + 1) / 2 - u1))


cita('u1', '0{,}5413', '0.5413')
cita('s2', '0{,}1614', '0.1614')


# ===========================================================================
# §7  Due successioni per e
# ===========================================================================

def _classica(n):
    return (1 + 1 / n) ** n


def _geometrica(n):
    """La successione dei quaderni: (sum_{k=0}^{n} n^{-k})^n, in forma chiusa."""
    return ((1 - n ** (-n - 1)) / (1 - 1 / n)) ** n


@controllo('§7')
def errori_a_dieci_milioni():
    """a n = 10^7: errori -1.35914e-7 e +1.35914e-7; media 1.2459e-14 = 11e/(24n^2)"""
    n = mp.mpf(10) ** 7
    a, b = _classica(n) - mp.e, _geometrica(n) - mp.e
    assert mp.nstr(a, 6) == '-1.35914e-7', a
    assert mp.nstr(b, 6) == '1.35914e-7', b
    m = (a + b) / 2
    assert mp.nstr(m, 5) == '1.2459e-14', m
    uguali(m, 11 * mp.e / (24 * n ** 2), rel=mp.mpf('1e-6'))


cita('err_e', '1{,}35914', '1.35914')
cita('media_e', '1{,}2459', '1.2459')


@controllo('§7')
def riga_75():
    """e #72-#75: a n = 9999999 la successione dei quaderni dista 1.359141174e-7 da e"""
    n = mp.mpf(9999999)
    b = _geometrica(n) - mp.e
    assert abs(b - mp.mpf('1.359141174e-7')) < mp.mpf('1e-16'), b
    assert mp.nstr(_geometrica(n), 10) == '2.718281964'


cita('riga75', '1{,}359141174', '1.359141174')


@controllo('§7')
def sviluppi_asintotici():
    """(1+1/n)^n = e(1 - 1/(2n) + 11/(24n^2) + ...), (1-1/n)^{-n} = e(1 + 1/(2n) + 11/(24n^2) + ...)"""
    n = mp.mpf(10) ** 9
    c1 = n ** 2 * (_classica(n) / mp.e - 1 + 1 / (2 * n))
    c2 = n ** 2 * ((1 - 1 / n) ** (-n) / mp.e - 1 - 1 / (2 * n))
    assert abs(c1 - mp.mpf(11) / 24) < mp.mpf('1e-8'), c1
    assert abs(c2 - mp.mpf(11) / 24) < mp.mpf('1e-8'), c2


@controllo('§7')
def media_senza_potenze_dispari():
    """nella media le potenze dispari di 1/n si cancellano: il resto è O(n^-4)"""
    resto = []
    for n in (mp.mpf(10) ** 6, mp.mpf(10) ** 7):
        m = (_classica(n) + (1 - 1 / n) ** (-n)) / 2
        resto.append(n ** 4 * (m / mp.e - 1 - mp.mpf(11) / (24 * n ** 2)))
    assert vicini(resto[0], resto[1], rel=mp.mpf('1e-2')), resto


@controllo('§7')
def troncamento_e_limite():
    """(1 - n^{-n-1})^n ~ 1; il limite di (sum_{k=0}^n n^{-k})^n è e, non 1 come dice Derive (#30, #71)"""
    with mp.workdps(120):
        n = mp.mpf(100)
        assert abs((1 - n ** (-n - 1)) ** n - 1) < mp.mpf('1e-50')
    assert abs(_geometrica(mp.mpf(10) ** 6) - mp.e) < mp.mpf('1e-5')


@controllo('§7')
def eulero_come_limite():
    """e #88-#93: (1+iπ/x)^x -> -1, (1+2iπ/x)^x -> 1, (1+iπ/(2x))^x -> i"""
    x = mp.mpf(10) ** 10      # lo scarto è circa c^2/(2x)
    for c, atteso in ((mp.pi, -1), (2 * mp.pi, 1), (mp.pi / 2, 1j)):
        assert abs((1 + 1j * c / x) ** x - atteso) < mp.mpf('1e-7'), c


# ===========================================================================
# §8  Una delta di Dirac fuori dall'asse reale
# ===========================================================================

def _dn(z, n):
    """La famiglia di delta.dfw #1."""
    a = 1 / (2 * mp.mpf(n))
    return ((1 + 2 * n * z) / abs(z + a) + (1 - 2 * n * z) / abs(z - a)) / 4


def _d(z):
    """Il suo limite fuori dall'origine: z Im z / (2i |z|^3)."""
    return z * mp.im(z) / (2j * abs(z) ** 3)


_PUNTI = (mp.mpc('0.3', '0.4'), mp.mpc(-1, 2), mp.mpc(2, '-0.5'))


@controllo('§8')
def rettangoli():
    """delta #1-#3: per x reale la famiglia vale n per |x| < 1/(2n) e 0 fuori"""
    for n in (10, 1000):
        a = mp.mpf(1) / (2 * n)
        for x in (-a / 2, a / 3, mp.mpf(0)):
            uguali(_dn(x, n), n)
        for x in (-3 * a, 2 * a, mp.mpf(5)):
            assert abs(_dn(x, n)) < mp.mpf('1e-50'), (n, x)


@controllo('§8')
def limite_complesso():
    """delta #4: per z non reale la famiglia tende a z Im z/(2i|z|^3) = ½ ∂x(z/|z|)"""
    for z in _PUNTI:
        uguali(_dn(z, 10 ** 12), _d(z), rel=mp.mpf('1e-9'))
        y = mp.im(z)
        dx = mp.diff(lambda x: (x + 1j * y) / abs(x + 1j * y), mp.re(z)) / 2
        uguali(dx, _d(z), rel=mp.mpf('1e-30'))


@controllo('§8')
def proprieta_del_limite():
    """δ(az) = δ(z)/|a| per a reale; delta #6-#7: δ(z) + δ(iz) = 1/(2|z|), δ(iz) - δ(z) = z^2/(2|z|^3)"""
    for z in _PUNTI:
        for a in (2, -3, mp.mpf('0.5')):
            uguali(_d(a * z), _d(z) / abs(a))
        uguali(_d(z) + _d(1j * z), 1 / (2 * abs(z)))
        uguali(_d(1j * z) - _d(z), z ** 2 / (2 * abs(z) ** 3))


@controllo('§8')
def famiglie_diverse():
    """la lorentziana tende a 0 fuori dall'asse; la gaussiana diverge dove |Im z| > |Re z|"""
    eps = mp.mpf('1e-8')
    for z in _PUNTI:
        assert abs(eps / (mp.pi * (z ** 2 + eps ** 2))) < mp.mpf('1e-6'), z
    eps = mp.mpf('0.05')      # esponente -Re(z^2)/eps^2 = ±64 nei due punti
    g = lambda z: mp.exp(-z ** 2 / eps ** 2) / (eps * mp.sqrt(mp.pi))
    assert abs(g(mp.mpc('0.3', '0.5'))) > mp.mpf('1e10')
    assert abs(g(mp.mpc('0.5', '0.3'))) < mp.mpf('1e-10')


@controllo('§8')
def trasformata_esponenziale():
    """delta #22 = -i δ(ω+ik); delta #24: |δ(ω+i)| = 1/(2(ω^2+1))"""
    for w in map(mp.mpf, ('0', '0.7', '-2')):
        for k in (1, 2):
            R = mp.sqrt(k ** 2 + w ** 2)
            riga22 = (k ** 2 - 1j * k * w) / (2j * R ** 3)
            uguali(riga22, -1j * _d(w + 1j * k))
        uguali(abs(_d(w + 1j)), 1 / (2 * (w ** 2 + 1)))



@controllo('§8')
def righe_25_27_e_43():
    """delta #25-#26 scambiano seno e coseno iperbolico; #43 è falsa; #41 e #44 sono corrette"""
    for w in map(mp.mpf, ('0.4', '-1.7')):
        for k in (1, 3):
            R3 = mp.sqrt(k ** 2 + w ** 2) ** 3
            sinh_vero = (_d(w + 1j * k) - _d(w - 1j * k)) / 2
            cosh_vero = (_d(w + 1j * k) + _d(w - 1j * k)) / 2
            riga25 = k ** 2 / (2 * R3)              # scritta come trasformata di sinh
            riga26 = -1j * k * w / (2 * R3)         # scritta come trasformata di cosh
            uguali(riga25, cosh_vero)
            uguali(riga26, sinh_vero)
            assert not vicini(riga25, sinh_vero, rel=mp.mpf('1e-6'))
    for x in map(mp.mpf, ('0.3', '1.1')):
        u = mp.tan(x)
        uguali(mp.exp(2j * x), (1 + 1j * u) ** 2 / (1 + u ** 2))                       # #41
        riga43 = -mp.sin(x) * abs(mp.cos(x)) * (1 + 1j * u) / (mp.cos(x) ** 2 * abs(1 + u))
        assert not vicini(riga43, mp.exp(1j * x), rel=mp.mpf('1e-3')), x               # #43
        v = mp.tan(x / 2)
        uguali(mp.exp(1j * x), (1 + 1j * v) ** 2 / (1 + v ** 2))                       # #44
    assert mp.exp(0) == 1     # in x = 0 la #43 dà 0


# ===========================================================================
# §9  In breve
# ===========================================================================

@controllo('§9')
def teoria_modo_comune():
    """teoria #1-#7, lettura ricostruita: con x -> x(1+ε), y -> y(1+ε) il quoziente cancella ε"""
    x, y, eps = mp.mpf('1.7'), mp.mpf('0.6'), mp.mpf('1e-3')
    X, Y = x * (1 + eps), y * (1 + eps)
    uguali((X + Y) / (x + y), 1 + eps)
    uguali((X * Y) / (x * y), (1 + eps) ** 2)
    uguali((X / Y) / (x / y), 1)
    uguali(X ** (mp.mpf(1) / 3) / x ** (mp.mpf(1) / 3), (1 + eps) ** (mp.mpf(1) / 3))


@controllo('§9')
def teoria_radice_doppia():
    """teoria #14-#19: le radici di (x+1)^2 = 2ε distano 2 sqrt(2ε)"""
    for eps in (mp.mpf('1e-2'), mp.mpf('1e-6')):
        r = mp.polyroots([1, 2, 1 - 2 * eps])
        uguali(abs(r[0] - r[1]), 2 * mp.sqrt(2 * eps), rel=mp.mpf('1e-30'))


@controllo('§9')
def teoria_decimale():
    """teoria #22-#27: 10^{-x(x+1)/2} = 1/(10^{x+1}-1) ha una radice in 1.99971; x = 10 non lo è"""
    f = lambda x: x * (x + 1) / 2 * mp.log(10) - mp.log(10 ** (x + 1) - 1)
    r = mp.findroot(f, 2)
    # Derive (#25) mostra 1.999710103: le cifre sono troncate, non arrotondate
    assert abs(r - mp.mpf('1.999710103')) < mp.mpf('2e-9'), r
    assert abs(f(mp.mpf(10))) > 10


cita('teoria_radice', '1{,}99971', '1.99971')


@controllo('§9')
def teoria2_aurea():
    """teoria2: y = (2/k)x^2 e y = -x + k/2 si incontrano in x = k(sqrt5-1)/4; a = 2^{(n-1)^2} k^{1-n}"""
    for k in (mp.mpf(1), mp.mpf(3)):
        x = k * (mp.sqrt(5) - 1) / 4
        uguali(2 / k * x ** 2, -x + k / 2)
        for n in range(2, 7):
            p = k / 2 ** (n - 1)
            uguali(2 ** ((n - 1) ** 2) / k ** (n - 1) * p ** n, p)


@controllo('§9')
def pi_ed_e():
    """sin-cos e e #56-#69: e^{πx}/π^{ex} = e^{kx}, k = π - e ln π = 0.029894..., sinh k = 0.029898..."""
    k = mp.pi - mp.e * mp.log(mp.pi)
    x = mp.mpf('1.3')
    uguali(mp.exp(mp.pi * x) / mp.pi ** (mp.e * x), mp.exp(k * x))
    assert str(k).startswith('0.029894'), k
    assert str(mp.sinh(k)).startswith('0.029898'), mp.sinh(k)
    uguali(mp.exp(mp.pi) / mp.pi ** mp.e, mp.exp(k))
    assert abs(mp.sinh(k) - mp.mpf('0.02989865915')) < mp.mpf('1e-11')


cita('k_pie', '0{,}029894', '0.029894')
cita('sinh_k', '0{,}029898', '0.029898')


@controllo('§9')
def e_parabola():
    """e #37-#45: la parabola con radici e e π racchiude un'area (π-e)^3/6"""
    a = mp.quad(lambda x: -(x - mp.e) * (x - mp.pi), [mp.e, mp.pi])
    uguali(a, (mp.pi - mp.e) ** 3 / 6, rel=mp.mpf('1e-30'))


@controllo('§9')
def pigreco():
    """pigreco: (π^x+e^x)^{1/x} -> π, e; 4((1/2)!)^2 = π; #22 vale sgn(x) π; #14-#15"""
    # lo scarto è circa (e/π)^x / x: a x = 400 vale ~1e-28
    assert abs((mp.pi ** 400 + mp.e ** 400) ** (mp.mpf(1) / 400) - mp.pi) < mp.mpf('1e-25')
    assert abs((mp.pi ** -400 + mp.e ** -400) ** (mp.mpf(-1) / 400) - mp.e) < mp.mpf('1e-25')
    uguali(4 * mp.gamma(mp.mpf(3) / 2) ** 2, mp.pi)
    for x in map(mp.mpf, ('0.7', '-1.9', '3.3')):
        v = ((mp.cos(2 * x) - mp.cos(2 / x)) * (mp.atan(x) + mp.atan(1 / x))
             / (mp.cos(x) ** 2 - mp.cos(1 / x) ** 2))
        uguali(v, mp.sign(x) * mp.pi)
    for x in range(1, 9):
        assert prod(x + n for n in range(x + 1)) == factorial(2 * x) // factorial(x - 1)


@controllo('§9')
def fattorazionale():
    """fattorazionale #1-#12: prod_{n=1}^{k-1}(1/n - 1/k) = k^{1-k}"""
    valori = [2, 9, 64, 625, 7776, 117649, 2097152, 43046721, 1000000000, 25937424601, 743008370688]
    for k, v in zip(range(2, 13), valori):
        p = prod(Fraction(1, n) - Fraction(1, k) for n in range(1, k))
        assert p == Fraction(1, k ** (k - 1)) == Fraction(1, v), k


@controllo('§9')
def primoriali():
    """numeri primi: la somma dei reciproci dei primoriali vale 0.70523017179..."""
    primi = [p for p in range(2, 200) if all(p % q for q in range(2, int(p ** 0.5) + 1))]
    s, pr = Fraction(0), 1
    for p in primi[:19]:
        pr *= p
        s += Fraction(1, pr)
    tot, pr = mp.mpf(0), 1
    for p in primi:
        pr *= p
        tot += mp.mpf(1) / pr
    assert str(tot).startswith('0.70523017179180096514'), tot
    assert abs(mp.mpf(s.numerator) / s.denominator - tot) < mp.mpf('1e-26')


cita('primoriali', '0{,}7052301717', '0.7052301717')


@controllo('§9')
def primoriali_irrazionale():
    """se s = a/b, b·sum_{k>n} P_n/P_k sarebbe un intero in (0, b/(p_{n+1}-1)): basta p_{n+1} > b+1"""
    primi = [p for p in range(2, 400) if all(p % q for q in range(2, int(p ** 0.5) + 1))]
    for n in (3, 10, 40):
        coda, prodotto = mp.mpf(0), mp.mpf(1)
        for p in primi[n:n + 25]:
            prodotto *= p
            coda += 1 / prodotto
        assert 0 < coda < mp.mpf(1) / (primi[n] - 1), n


@controllo('§9')
def fresnel():
    """cost^2 #19-#20: ∫ (cos ωt^2 + sin ωt^2)/2 dt su R = sqrt(π/(2ω))"""
    with mp.workdps(30):
        for w in (mp.mpf(1), mp.mpf('2.5')):
            f = lambda t: (mp.cos(w * t ** 2) + mp.sin(w * t ** 2)) / 2
            v = 2 * mp.quadosc(f, [0, mp.inf], zeros=lambda n: mp.sqrt(n * mp.pi / w))
            assert abs(v - mp.sqrt(mp.pi / (2 * w))) < mp.mpf('1e-12'), (w, v)


@controllo('§9')
def limit_disuguaglianza():
    """limit #1: |x| <= (sqrt2/2)(1/2 + x^2), con uguaglianza in |x| = 1/sqrt2"""
    for i in range(-400, 401):
        x = mp.mpf(i) / 100
        assert mp.sqrt(2) / 2 * (mp.mpf(1) / 2 + x ** 2) - abs(x) >= 0
    x = 1 / mp.sqrt(2)
    assert abs(mp.sqrt(2) / 2 * (mp.mpf(1) / 2 + x ** 2) - x) < mp.mpf('1e-50')


@controllo('§9')
def fx_gx():
    """fx^gx: sin(x)^{1/ln(1/sin x)} = 1/e"""
    for x in map(mp.mpf, ('0.3', '1', '2')):
        uguali(mp.sin(x) ** (1 / mp.log(1 / mp.sin(x))), 1 / mp.e)


@controllo('§9')
def equazioni():
    """equazioni: Im p(x+iy)/y tende a p'(x) per y -> 0 (gradi 2, 3, 4)"""
    rnd = random.Random(9)
    for grado in (2, 3, 4):
        c = [mp.mpf(rnd.uniform(-3, 3)) for _ in range(grado + 1)]
        p = lambda z: mp.polyval(c, z)
        x, y = mp.mpf('0.37'), mp.mpf('1e-20')
        uguali(mp.im(p(x + 1j * y)) / y, mp.diff(p, x), rel=mp.mpf('1e-30'))


@controllo('§9')
def notch_15_16():
    """notch: la riga #16 coincide con la funzione di trasferimento #4; la #15 ha una r di troppo"""
    rnd = random.Random(15)
    for _ in range(4):
        c, l, f, g, r = (mp.mpf(rnd.uniform(0.5, 3)) for _ in range(5))
        s = mp.mpc(rnd.uniform(-1, 1), rnd.uniform(0.5, 3))
        h4 = f * r * (c * l * s ** 2 + 1) / (f * l * r * s ** 2 * (c + g) + f * l * s + r * (f + l))
        h16 = c / (g + c) * (s ** 2 + 1 / (l * c)) / (s ** 2 + s / (r * (c + g)) + (l + f) / (l * f) / (c + g))
        h15 = c / (g + c) * (s ** 2 + 1 / (l * c)) / (s ** 2 + s / (r * (c + g)) + r * (l + f) / (l * f) / (c + g))
        uguali(h16, h4)
        assert not vicini(h15, h4, rel=mp.mpf('1e-6'))


@controllo('§9')
def sudoku():
    """Sudoku #1-#2: la griglia è un sudoku valido e il suo determinante vale -2975130"""
    g = [[9, 1, 3, 7, 8, 6, 5, 4, 2], [4, 8, 7, 5, 2, 3, 1, 9, 6], [2, 6, 5, 4, 1, 9, 3, 8, 7],
         [8, 5, 6, 3, 7, 4, 2, 1, 9], [7, 9, 2, 1, 6, 5, 4, 3, 8], [3, 4, 1, 2, 9, 8, 7, 6, 5],
         [6, 3, 4, 9, 5, 7, 8, 2, 1], [5, 2, 9, 8, 4, 1, 6, 7, 3], [1, 7, 8, 6, 3, 2, 9, 5, 4]]
    cifre = set(range(1, 10))
    assert all(set(r) == cifre for r in g)
    assert all(set(r[j] for r in g) == cifre for j in range(9))
    assert all(set(g[3 * a + i][3 * b + j] for i in range(3) for j in range(3)) == cifre
               for a in range(3) for b in range(3))
    with mp.workdps(40):
        assert mp.nint(mp.det(mp.matrix(g))) == -2975130


cita('sudoku_det', '2\\,975\\,130', '2{,}975{,}130')


@controllo('§9')
def j_limite():
    """j #3: (1 - cos x)/sin x tende a 0 per x -> 0, non a i"""
    assert abs((1 - mp.cos(mp.mpf('1e-20'))) / mp.sin(mp.mpf('1e-20'))) < mp.mpf('1e-19')


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
# Sintesi (README e pagina): l'identità del mezzo di mate.dfw e le sue varianti
# ===========================================================================

def _angoli(n, seme):
    rnd = random.Random(seme)
    return [mp.mpf(rnd.uniform(0.1, 3)) for _ in range(n)]


@controllo('sintesi')
def identita_del_mezzo():
    """mate #2-#4, #19-#31: cos² dà 1/2, sin² dà -1/2, cosh² dà 1/2, anche con angoli complessi"""
    for a, b in (_angoli(2, 1), _angoli(2, 2), (mp.mpc('0.4', '0.9'), mp.mpc('1.1', '-0.3'))):
        D = mp.cos(2 * a) - mp.cos(2 * b)
        uguali((mp.cos(a) ** 2 - mp.cos(b) ** 2) / D, mp.mpf(1) / 2)
        uguali((mp.sin(a) ** 2 - mp.sin(b) ** 2) / D, -mp.mpf(1) / 2)
        uguali((mp.cosh(a) ** 2 - mp.cosh(b) ** 2) / (mp.cosh(2 * a) - mp.cosh(2 * b)), mp.mpf(1) / 2)


@controllo('sintesi')
def identita_esponenziale():
    """mate #6: la versione con gli esponenziali complessi vale ancora 1/2"""
    for x, y in (_angoli(2, 3), _angoli(2, 4)):
        e = lambda t: mp.exp(1j * t)
        num = (e(2 * x) - e(2 * y) + mp.sin(y) ** 2 - mp.sin(x) ** 2
               + 2j * (e(y) * mp.sin(y) - e(x) * mp.sin(x)))
        den = e(2 * x) - e(2 * y) + 1j * (mp.sin(2 * y) - mp.sin(2 * x))
        uguali(num / den, mp.mpf(1) / 2)


@controllo('sintesi')
def triplicazione():
    """mate #5: con la triplicazione la costante diventa 1/4"""
    for x, y in (_angoli(2, 5), _angoli(2, 6)):
        num = mp.cos(x) ** 3 * mp.cos(y) - mp.cos(y) ** 3 * mp.cos(x)
        den = mp.cos(3 * x) * mp.cos(y) - mp.cos(3 * y) * mp.cos(x)
        uguali(num / den, mp.mpf(1) / 4)


@controllo('sintesi')
def due_pesi():
    """mate #53-#60: (cos²x - k cos²y)/(cos 2x - l cos 2y) = 1/2 per ogni x se cos 2y = (1-k)/(k-l)"""
    y, l = mp.mpf('0.8'), mp.mpf('2.5')
    k = (l * mp.cos(2 * y) + 1) / (2 * mp.cos(y) ** 2)          # riga #54
    uguali(mp.cos(2 * y), (1 - k) / (k - l))                    # riga #60
    for x in _angoli(4, 7):
        uguali((mp.cos(x) ** 2 - k * mp.cos(y) ** 2) / (mp.cos(2 * x) - l * mp.cos(2 * y)),
               mp.mpf(1) / 2)


@controllo('sintesi')
def macchina_per_pi():
    """mate #67-#71: (1/2)! = sqrt(π)/2, quindi 4·(rapporto)!² = π per ogni x, y"""
    for x, y in (_angoli(2, 8), _angoli(2, 9)):
        r = (mp.cos(x) ** 2 - mp.cos(y) ** 2) / (mp.cos(2 * x) - mp.cos(2 * y))
        uguali(4 * mp.factorial(r) ** 2, mp.pi, rel=mp.mpf('1e-35'))


@controllo('sintesi')
def determinanti_di_chebyshev():
    """per ogni n, con floor(n/2)+1 angoli: det[cos n x_i, c_i^(n-2), ...] = 2^(n-1) det[c_i^n, c_i^(n-2), ...]"""
    for n in range(2, 12):
        m = n // 2 + 1
        xs = _angoli(m, 100 + n)
        cs = [mp.cos(x) for x in xs]
        gradi = [n - 2 * j for j in range(1, m)]
        A = mp.matrix([[mp.cos(n * x)] + [c ** g for g in gradi] for x, c in zip(xs, cs)])
        B = mp.matrix([[c ** n] + [c ** g for g in gradi] for c in cs])
        uguali(mp.det(A), 2 ** (n - 1) * mp.det(B), rel=mp.mpf('1e-30'), cosa='n=%d' % n)


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
