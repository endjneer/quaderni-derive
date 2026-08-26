# -*- coding: utf-8 -*-
"""
Verifica numerica delle identita' estratte dai quaderni Derive.

L'albero sintattico prodotto da derive2tex viene interpretato con mpmath:
ogni espressione che al livello piu' esterno e' una catena di uguaglianze
viene valutata in piu' punti casuali del piano complesso e i membri vengono
confrontati. Il risultato per ogni espressione e' uno fra:

    ok        i membri coincidono in tutti i punti provati
    diff      i membri differiscono (identita' falsa, oppure valida solo
              sotto convenzioni non standard o su un dominio ristretto)
    n/d       non valutabile (integrale indefinito, SOLVE, variabile
              simbolica in un indice di somma, funzione non implementata)

Uso:  python verify.py ../extracted/all.json ../extracted/verify.json
"""
import sys, os, json, math, random, cmath

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive2tex as D

import mpmath as mp

mp.mp.dps = 20

# Numero massimo di nodi valutati per singola espressione. Serve a rendere
# la verifica deterministica e a evitare che una serie o un integrale
# patologico blocchino l'intero passaggio.
MAX_STEPS = 400000


class NotEvaluable(Exception):
    pass


class TooExpensive(NotEvaluable):
    pass


# --------------------------------------------------------------------------
# Interprete
# --------------------------------------------------------------------------

UNARY = {
    'SIN': mp.sin, 'COS': mp.cos, 'TAN': mp.tan, 'COT': mp.cot,
    'SEC': mp.sec, 'CSC': mp.csc, 'LN': mp.log, 'SQRT': mp.sqrt,
    'SINH': mp.sinh, 'COSH': mp.cosh, 'TANH': mp.tanh, 'COTH': mp.coth,
    'ASIN': mp.asin, 'ACOS': mp.acos, 'ATAN': mp.atan, 'ACOT': mp.acot,
    'ASINH': mp.asinh, 'ACOSH': mp.acosh, 'ATANH': mp.atanh,
    'ACOTH': mp.acoth, 'ERF': mp.erf, 'GAMMA': mp.gamma,
    'RE': lambda z: mp.mpmathify(z).real,
    'IM': lambda z: mp.mpmathify(z).imag,
    'CONJ': mp.conj,
    'FLOOR': lambda z: mp.floor(z.real if hasattr(z, 'real') else z),
    'ABS': mp.fabs,
    'PHASE': mp.arg,
}


def _abs(z):
    return mp.sqrt(mp.mpc(z).real ** 2 + mp.mpc(z).imag ** 2)


def _sign(z):
    z = mp.mpc(z)
    a = _abs(z)
    if a == 0:
        return mp.mpc(0)
    return z / a


class Budget(object):
    """Contatore di passi condiviso fra le valutazioni annidate."""

    def __init__(self, limit=MAX_STEPS):
        self.left = limit

    def tick(self):
        self.left -= 1
        if self.left <= 0:
            raise TooExpensive('valutazione troppo costosa')


class Interp(object):
    """Valuta un albero Derive in un ambiente di variabili complesse."""

    def __init__(self, env, budget=None):
        self.env = env
        self.budget = budget if budget is not None else Budget()

    def ev(self, n):
        self.budget.tick()
        return getattr(self, 'e_' + n.kind)(n)

    # foglie
    def e_num(self, n):
        return mp.mpf(n.attrs['name'])

    def e_unknown(self, n):
        raise NotEvaluable('?')

    def e_str(self, n):
        raise NotEvaluable('stringa')

    def e_pm(self, n):
        raise NotEvaluable('+-')

    def e_const(self, n):
        v = n.attrs['name']
        if v == '#e':
            return mp.e
        if v == '#i':
            return mp.mpc(0, 1)
        if v == '#pi':
            return mp.pi
        raise NotEvaluable(v)

    def e_var(self, n):
        s = n.attrs['name']
        if s == 'pi':
            return mp.pi
        if s == 'inf':
            return mp.inf
        if s in self.env:
            return self.env[s]
        raise NotEvaluable('variabile ' + s)

    def e_paren(self, n):
        return self.ev(n.kids[0])

    def e_list(self, n):
        return [self.ev(k) for k in n.kids]

    # operatori
    def e_add(self, n):
        return self.ev(n.kids[0]) + self.ev(n.kids[1])

    def e_sub(self, n):
        return self.ev(n.kids[0]) - self.ev(n.kids[1])

    def e_mul(self, n):
        return self.ev(n.kids[0]) * self.ev(n.kids[1])

    def e_div(self, n):
        return self.ev(n.kids[0]) / self.ev(n.kids[1])

    def e_neg(self, n):
        return -self.ev(n.kids[0])

    def e_pos(self, n):
        return self.ev(n.kids[0])

    def e_pow(self, n):
        return mp.power(self.ev(n.kids[0]), self.ev(n.kids[1]))

    def e_fact(self, n):
        return mp.gamma(self.ev(n.kids[0]) + 1)

    def e_rel(self, n):
        raise NotEvaluable('relazione annidata')

    def e_or(self, n):
        raise NotEvaluable('or')

    def e_and(self, n):
        raise NotEvaluable('and')

    def e_not(self, n):
        raise NotEvaluable('not')

    # chiamate
    def e_call(self, n):
        name = n.attrs['name'].upper()
        a = n.kids
        m = getattr(self, 'c_' + name, None)
        if m is not None:
            return m(a)
        if name == 'ABS':
            return _abs(self.ev(a[0]))
        if name == 'SIGN':
            return _sign(self.ev(a[0]))
        if name in UNARY and len(a) == 1:
            return UNARY[name](self.ev(a[0]))
        if name == 'LOG':
            if len(a) == 2:
                return mp.log(self.ev(a[0])) / mp.log(self.ev(a[1]))
            return mp.log(self.ev(a[0]), 10)
        raise NotEvaluable('funzione ' + name)

    def _bind(self, name, val):
        env = dict(self.env)
        env[name] = val
        return Interp(env, self.budget)

    def _fun(self, body, var):
        def f(t):
            return self._bind(var, t).ev(body)
        return f

    def c_INT(self, a):
        if len(a) < 4:
            raise NotEvaluable('integrale indefinito')
        var = a[1].attrs.get('name')
        if var is None:
            raise NotEvaluable('variabile di integrazione')
        lo, hi = self.ev(a[2]), self.ev(a[3])
        f = self._fun(a[0], var)
        with mp.workdps(15):
            if mp.isinf(mp.re(lo)) or mp.isinf(mp.re(hi)):
                # su intervallo illimitato la quadratura adattiva e' spesso
                # instabile: si tronca a un dominio ampio ma finito
                lo = mp.mpf(-60) if mp.isinf(mp.re(lo)) else lo
                hi = mp.mpf(60) if mp.isinf(mp.re(hi)) else hi
            return mp.quad(f, [lo, hi], maxdegree=5)

    def c_DIF(self, a):
        var = a[1].attrs.get('name')
        order = int(self.ev(a[2])) if len(a) >= 3 else 1
        if var not in self.env:
            raise NotEvaluable('derivata simbolica')
        return mp.diff(self._fun(a[0], var), self.env[var], order)

    # numero di termini oltre il quale una serie o un prodotto illimitati
    # vengono troncati, con controllo che la coda sia trascurabile
    TAIL = 1200

    def _bounds(self, a):
        var = a[1].attrs.get('name')
        return var, self.ev(a[2]), self.ev(a[3])

    def c_SUM(self, a):
        if len(a) < 4:
            raise NotEvaluable('somma indefinita')
        var, lo, hi = self._bounds(a)
        f = self._fun(a[0], var)
        if mp.isinf(mp.re(hi)) or mp.isinf(mp.re(lo)):
            if mp.isinf(mp.re(lo)):
                raise NotEvaluable('somma bilatera illimitata')
            start = int(mp.re(lo))
            total, last = mp.mpc(0), mp.mpc(0)
            for k in range(start, start + self.TAIL):
                last = mp.mpc(f(mp.mpf(k)))
                total += last
            if _abs(last) > mp.mpf('1e-12') * max(mp.mpf(1), _abs(total)):
                raise NotEvaluable('serie a convergenza lenta')
            return total
        lo, hi = int(mp.re(lo)), int(mp.re(hi))
        if hi - lo > 20000:
            raise NotEvaluable('somma troppo lunga')
        return mp.fsum(f(mp.mpf(k)) for k in range(lo, hi + 1))

    def c_PRODUCT(self, a):
        if len(a) < 4:
            raise NotEvaluable('prodotto indefinito')
        var, lo, hi = self._bounds(a)
        f = self._fun(a[0], var)
        if mp.isinf(mp.re(hi)):
            raise NotEvaluable('prodotto illimitato')
        lo, hi = int(mp.re(lo)), int(mp.re(hi))
        if hi - lo > 5000:
            raise NotEvaluable('prodotto troppo lungo')
        r = mp.mpc(1)
        for k in range(lo, hi + 1):
            r *= f(mp.mpf(k))
        return r

    def c_LIM(self, a):
        """Limite per campionamento: nessuna estrapolazione simbolica.

        Si valuta la funzione su una successione che tende al punto e si
        accetta il valore solo se gli ultimi due campioni concordano.
        """
        var = a[1].attrs.get('name')
        target = self.ev(a[2]) if len(a) >= 3 else mp.mpf(0)
        f = self._fun(a[0], var)
        direction = 1
        if len(a) >= 4 and D.strip_paren(a[3]).kind == 'neg':
            direction = -1
        if mp.isinf(mp.re(target)):
            sgn = 1 if mp.re(target) > 0 else -1
            probes = [sgn * mp.mpf(10) ** k for k in (5, 6, 7)]
        else:
            probes = [target + direction * mp.mpf(10) ** (-k)
                      for k in (5, 6, 7)]
        vals = []
        for p in probes:
            try:
                vals.append(mp.mpc(f(p)))
            except Exception:
                raise NotEvaluable('limite non campionabile')
        scale = max(mp.mpf(1), _abs(vals[-1]))
        if _abs(vals[-1] - vals[-2]) / scale > mp.mpf('1e-5'):
            raise NotEvaluable('limite non stabilizzato')
        return vals[-1]

    def c_DET(self, a):
        m = D.strip_paren(a[0])
        rows = [[self.ev(c) for c in r.kids] for r in m.kids]
        return mp.det(mp.matrix(rows))

    def c_APPROX(self, a):
        return self.ev(a[0])

    def c_MOD(self, a):
        z = self.ev(a[0])
        return z - mp.floor(z)

    def c_TRIANGULAR(self, a):
        raise NotEvaluable('TRIANGULAR')


# --------------------------------------------------------------------------
# Confronto dei membri di una catena di uguaglianze
# --------------------------------------------------------------------------

RESERVED = {'pi', 'inf', 'unit_circle', 'Real', 'true', 'false',
            'deg', 'e'}


def free_vars(node, bound=None, out=None):
    """Variabili libere: esclude gli indici legati da SUM/PRODUCT/INT/..."""
    if bound is None:
        bound = set()
    if out is None:
        out = set()
    if node.kind == 'var':
        s = node.attrs['name']
        if s not in bound and s not in RESERVED:
            out.add(s)
        return out
    if node.kind == 'call':
        name = node.attrs['name'].upper()
        if name in ('INT', 'SUM', 'PRODUCT', 'DIF', 'LIM') and \
                len(node.kids) >= 2 and node.kids[1].kind == 'var':
            idx = node.kids[1].attrs['name']
            inner = bound | {idx}
            free_vars(node.kids[0], inner, out)
            for k in node.kids[2:]:
                free_vars(k, bound, out)
            if name == 'LIM':
                out.discard(idx)
            return out
    for k in node.kids:
        free_vars(k, bound, out)
    return out


def sample_points(names, rng, n=4):
    pts = []
    for _ in range(n):
        env = {}
        for s in names:
            if s in ('n', 'k', 'm', 'p', 'h', 'j', 'l'):
                env[s] = mp.mpf(rng.randint(2, 7))
            else:
                env[s] = mp.mpc(rng.uniform(0.2, 1.3),
                                rng.uniform(0.15, 0.9))
        pts.append(env)
    return pts


def close(a, b):
    try:
        if isinstance(a, list) or isinstance(b, list):
            return False
        da = _abs(mp.mpc(a) - mp.mpc(b))
        scale = max(mp.mpf(1), _abs(mp.mpc(a)), _abs(mp.mpc(b)))
        return da / scale < mp.mpf('1e-6')
    except Exception:
        return False


def check(src, seed=12345):
    """Verifica una espressione. Ritorna (stato, dettaglio)."""
    try:
        node = D.parse(src)
    except Exception as e:
        return 'n/d', 'parsing: %s' % e
    if node.kind != 'rel' or any(o != '=' for o in node.attrs['ops']):
        return 'n/d', 'non e\' una uguaglianza'
    names = set()
    for k in node.kids:
        free_vars(k, None, names)
    rng = random.Random(seed)
    pts = sample_points(sorted(names), rng) if names else [{}]
    tested = 0
    for env in pts:
        vals = []
        for k in node.kids:
            try:
                vals.append(Interp(env).ev(k))
            except NotEvaluable as e:
                return 'n/d', str(e)
            except (ZeroDivisionError, ValueError, OverflowError,
                    TypeError, AttributeError) as e:
                vals.append(None)
            except Exception as e:
                return 'n/d', '%s: %s' % (type(e).__name__, e)
        good = [v for v in vals if v is not None]
        if len(good) < 2:
            continue
        tested += 1
        for i in range(1, len(good)):
            if not close(good[0], good[i]):
                return 'diff', 'membri diversi in un punto di prova'
    if tested == 0:
        return 'n/d', 'nessun punto valutabile'
    return 'ok', '%d punti' % tested


def main(inp, outp):
    data = json.load(open(inp, encoding='utf-8'))
    res = {}
    tally = {'ok': 0, 'diff': 0, 'n/d': 0}
    for f in data:
        for it in f['items']:
            key = '%s#%d' % (f['file'], it['idx'])
            try:
                st, why = check(it['text'])
            except Exception as e:
                st, why = 'n/d', '%s: %s' % (type(e).__name__, e)
            res[key] = {'stato': st, 'nota': why}
            tally[st] += 1
        print(f['file'], 'fatto', file=sys.stderr)
    json.dump(res, open(outp, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print(tally)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
