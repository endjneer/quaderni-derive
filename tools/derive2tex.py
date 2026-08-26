# -*- coding: utf-8 -*-
"""
Traduttore dalla sintassi lineare di Derive 6 a LaTeX.

Il modulo espone due funzioni:

    to_latex(src)   -> corpo matematico (da inserire fra $ ... $)
    to_display(src) -> ambiente di visualizzazione completo, che spezza
                       automaticamente le espressioni troppo lunghe

Grammatica riconosciuta (precedenza crescente):

    or_expr    := and_expr { 'OR' and_expr }
    and_expr   := not_expr { 'AND' not_expr }
    not_expr   := [ 'NOT' ] rel_expr
    rel_expr   := add_expr { ('='|'/='|'<'|'<='|'>'|'>=') add_expr }
    add_expr   := mul_expr { ('+'|'-') mul_expr }
    mul_expr   := unary { ('*'|'/') unary }
    unary      := [ '-' | '+' ] power
    power      := postfix [ '^' unary ]            (associativo a destra)
    postfix    := atom { '!' }
    atom       := numero | identificatore | costante | chiamata
                | '(' or_expr ')' | '[' lista ']' | stringa
"""
import re

# --------------------------------------------------------------------------
# Analisi lessicale
# --------------------------------------------------------------------------

TOKEN_RE = re.compile(r"""
      (?P<space>\s+)
    | (?P<number>\d+\.\d+|\.\d+|\d+)
    | (?P<hash>\#[A-Za-z]+|\#\d+)
    | (?P<string>"[^"]*")
    | (?P<name>[A-Za-z_\u00c0-\u024f\u0370-\u03ff][A-Za-z0-9_\u00c0-\u024f\u0370-\u03ff]*'?)
    | (?P<unknown>\?)
    | (?P<op><=|>=|/=|[-+*/^=<>!,()\[\]])
""", re.VERBOSE)

KEYWORDS = {'OR', 'AND', 'NOT'}


class Tok(object):
    __slots__ = ('kind', 'val')

    def __init__(self, kind, val):
        self.kind, self.val = kind, val

    def __repr__(self):
        return '%s(%r)' % (self.kind, self.val)


def tokenize(src):
    toks, i, n = [], 0, len(src)
    while i < n:
        m = TOKEN_RE.match(src, i)
        if not m:
            raise SyntaxError('carattere inatteso %r' % src[i])
        i = m.end()
        kind = m.lastgroup
        if kind == 'space':
            continue
        val = m.group()
        if kind == 'name' and val.upper() in KEYWORDS:
            kind, val = 'op', val.upper()
        toks.append(Tok(kind, val))
    toks.append(Tok('eof', ''))
    return toks


# --------------------------------------------------------------------------
# Albero sintattico
# --------------------------------------------------------------------------

class Node(object):
    def __init__(self, kind, *kids, **attrs):
        self.kind = kind
        self.kids = list(kids)
        self.attrs = attrs

    def __repr__(self):
        return 'Node(%s,%r,%r)' % (self.kind, self.kids, self.attrs)


class Parser(object):
    REL = ('<=', '>=', '/=', '=', '<', '>')

    def __init__(self, toks):
        self.t, self.p = toks, 0

    def peek(self):
        return self.t[self.p]

    def next(self):
        t = self.t[self.p]
        self.p += 1
        return t

    def accept(self, val):
        if self.t[self.p].kind == 'op' and self.t[self.p].val == val:
            self.p += 1
            return True
        return False

    def expect(self, val):
        if not self.accept(val):
            raise SyntaxError('atteso %r, trovato %r' % (val, self.peek()))

    def parse(self):
        e = self.or_expr()
        if self.peek().kind != 'eof':
            raise SyntaxError('token residuo %r' % (self.peek(),))
        return e

    def or_expr(self):
        e = self.and_expr()
        while self.accept('OR'):
            e = Node('or', e, self.and_expr())
        return e

    def and_expr(self):
        e = self.not_expr()
        while self.accept('AND'):
            e = Node('and', e, self.not_expr())
        return e

    def not_expr(self):
        if self.accept('NOT'):
            return Node('not', self.not_expr())
        return self.rel_expr()

    def rel_expr(self):
        parts = [self.add_expr()]
        ops = []
        while self.peek().kind == 'op' and self.peek().val in self.REL:
            ops.append(self.next().val)
            parts.append(self.add_expr())
        if not ops:
            return parts[0]
        return Node('rel', *parts, ops=ops)

    def add_expr(self):
        e = self.mul_expr()
        while self.peek().kind == 'op' and self.peek().val in '+-':
            op = self.next().val
            e = Node('add' if op == '+' else 'sub', e, self.mul_expr())
        return e

    def mul_expr(self):
        e = self.unary()
        while self.peek().kind == 'op' and self.peek().val in '*/':
            op = self.next().val
            e = Node('mul' if op == '*' else 'div', e, self.unary())
        return e

    def unary(self):
        if self.accept('-'):
            return Node('neg', self.unary())
        if self.accept('+'):
            return Node('pos', self.unary())
        return self.power()

    def power(self):
        base = self.postfix()
        if self.accept('^'):
            return Node('pow', base, self.unary())
        return base

    def postfix(self):
        e = self.atom()
        while self.accept('!'):
            e = Node('fact', e)
        return e

    def atom(self):
        t = self.next()
        if t.kind == 'number':
            return Node('num', name=t.val)
        if t.kind == 'unknown':
            return Node('unknown')
        if t.kind == 'string':
            lit = t.val[1:-1]
            # Derive usa la stringa "+-" come prefisso: "+-"inf  ->  +-inf
            if lit in ('+-', '-+') and self.peek().kind in (
                    'name', 'number', 'hash') or (
                    lit in ('+-', '-+') and self.peek().kind == 'op'
                    and self.peek().val == '('):
                return Node('pm', self.unary())
            return Node('str', name=lit)
        if t.kind == 'hash':
            return Node('const', name=t.val)
        if t.kind == 'name':
            if self.accept('('):
                args = []
                if not self.accept(')'):
                    args.append(self.or_expr())
                    while self.accept(','):
                        args.append(self.or_expr())
                    self.expect(')')
                return Node('call', *args, name=t.val)
            return Node('var', name=t.val)
        if t.kind == 'op' and t.val == '(':
            e = self.or_expr()
            self.expect(')')
            return Node('paren', e)
        if t.kind == 'op' and t.val == '[':
            items = []
            if not self.accept(']'):
                items.append(self.or_expr())
                while self.accept(','):
                    items.append(self.or_expr())
                self.expect(']')
            return Node('list', *items)
        raise SyntaxError('atomo inatteso %r' % (t,))


def parse(src):
    return Parser(tokenize(src)).parse()


# --------------------------------------------------------------------------
# Resa in LaTeX
# --------------------------------------------------------------------------

GREEK = {u'\u03b5': r'\varepsilon', u'\u03c9': r'\omega',
         u'\u03b4': r'\delta', u'\u03c0': r'\pi',
         u'\u00f9': r'\mathrm{U}'}

CONSTS = {'#e': r'\mathrm{e}', '#i': r'\mathrm{i}', '#pi': r'\pi',
          '#nan': r'\mathrm{NaN}'}

NAMED = {'pi': r'\pi', 'inf': r'\infty', 'deg': r'^{\circ}',
         'unit_circle': r'\mathbb{S}^{1}', 'Real': r'\mathrm{Real}',
         'true': r'\mathrm{vero}', 'false': r'\mathrm{falso}'}

SIMPLE_FUNC = {
    'SIN': r'\sin', 'COS': r'\cos', 'TAN': r'\tan', 'COT': r'\cot',
    'SEC': r'\sec', 'CSC': r'\csc', 'LN': r'\ln',
    'SINH': r'\sinh', 'COSH': r'\cosh', 'TANH': r'\tanh', 'COTH': r'\coth',
    'ASIN': r'\arcsin', 'ACOS': r'\arccos', 'ATAN': r'\arctan',
    'ACOT': r'\operatorname{arccot}', 'ASEC': r'\operatorname{arcsec}',
    'ASINH': r'\operatorname{arcsinh}', 'ACOSH': r'\operatorname{arccosh}',
    'ATANH': r'\operatorname{artanh}', 'ACOTH': r'\operatorname{arcoth}',
    'ERF': r'\operatorname{erf}', 'SIGN': r'\operatorname{sgn}',
    'RE': r'\operatorname{Re}', 'IM': r'\operatorname{Im}',
    'MOD': r'\operatorname{mod}', 'TRIANGULAR': r'\operatorname{tri}',
    'GAMMA': r'\Gamma', 'CONJ': r'\operatorname{conj}', 'PHASE': r'\arg',
}

# funzioni per cui e' lecito scrivere l'esponente sul nome: sin^2(x)
POWER_ON_NAME = set(SIMPLE_FUNC) - {'RE', 'IM', 'MOD', 'TRIANGULAR', 'CONJ'}

PREC = {'or': 1, 'and': 2, 'not': 3, 'rel': 4, 'add': 5, 'sub': 5,
        'mul': 6, 'div': 6, 'neg': 7, 'pos': 7, 'pow': 8, 'fact': 9}
ATOM_PREC = 10

RELSYM = {'=': '=', '/=': r'\neq', '<': '<', '>': '>',
          '<=': r'\leq', '>=': r'\geq'}


def strip_paren(n):
    while n.kind == 'paren':
        n = n.kids[0]
    return n


# Funzioni che si compongono come grandi operatori: il loro corpo si estende
# a destra, quindi vanno racchiuse fra parentesi quando fanno da base di una
# potenza o da fattore sinistro di un prodotto.
BIG_OPS = {'SUM', 'PRODUCT', 'INT', 'LIM', 'DIF'}


def is_big(n):
    m = strip_paren(n)
    return m.kind == 'call' and m.attrs['name'].upper() in BIG_OPS


def prec(n):
    """Precedenza effettiva del nodo.

    Le parentesi presenti nel sorgente Derive vengono ignorate: la resa
    LaTeX reinserisce solo quelle richieste dalla struttura, perche' molte
    diventano superflue una volta usati \\frac, \\sqrt e gli esponenti.
    """
    return PREC.get(strip_paren(n).kind, ATOM_PREC)


def is_numeric_leaf(n):
    return strip_paren(n).kind == 'num'


def is_numeric_like(n):
    """Vero per 5, 2^11, 7! e simili: fra due di questi serve il punto."""
    m = strip_paren(n)
    if m.kind == 'num':
        return True
    if m.kind in ('pow', 'fact'):
        return is_numeric_like(m.kids[0])
    return False


def esc_name(s):
    """Rende un identificatore: lettera greca, nome noto o testo corsivo."""
    if s in GREEK:
        return GREEK[s]
    if s in NAMED:
        return NAMED[s]
    if s.endswith("'"):
        return esc_name(s[:-1]) + "'"
    if len(s) == 1:
        return s
    return r'\mathit{%s}' % s.replace('_', r'\_')


class Renderer(object):
    def wrap(self, node, minprec):
        s = self.render(node)
        if prec(node) < minprec:
            return r'\left(%s\right)' % s
        return s

    def render(self, n):
        return getattr(self, 'r_' + n.kind)(n)

    # -- foglie --------------------------------------------------------
    def r_num(self, n):
        return n.attrs['name']

    def r_str(self, n):
        v = n.attrs['name']
        return r'\pm' if v in ('+-', '-+') else r'\text{%s}' % v

    def r_unknown(self, n):
        return r'\mathrm{?}'

    def r_pm(self, n):
        return r'\pm %s' % self.wrap(n.kids[0], 7)

    def r_const(self, n):
        v = n.attrs['name']
        return CONSTS.get(v, r'\mathtt{%s}' % v.replace('#', r'\#'))

    def r_var(self, n):
        return esc_name(n.attrs['name'])

    def r_paren(self, n):
        return self.render(n.kids[0])

    def r_list(self, n):
        if all(k.kind == 'list' for k in n.kids) and n.kids:
            rows = [' & '.join(self.render(c) for c in r.kids) for r in n.kids]
            return r'\begin{bmatrix} %s \end{bmatrix}' % r' \\ '.join(rows)
        return r'\left[\, %s \,\right]' % r',\; '.join(
            self.render(k) for k in n.kids)

    # -- operatori -----------------------------------------------------
    def r_or(self, n):
        return r'%s \;\lor\; %s' % (self.wrap(n.kids[0], 1),
                                    self.wrap(n.kids[1], 2))

    def r_and(self, n):
        return r'%s \;\land\; %s' % (self.wrap(n.kids[0], 2),
                                     self.wrap(n.kids[1], 3))

    def r_not(self, n):
        return r'\lnot %s' % self.wrap(n.kids[0], 3)

    def r_rel(self, n):
        out = [self.wrap(n.kids[0], 5)]
        for op, k in zip(n.attrs['ops'], n.kids[1:]):
            out.append(RELSYM[op])
            out.append(self.wrap(k, 5))
        return ' '.join(out)

    def r_add(self, n):
        return '%s + %s' % (self.wrap(n.kids[0], 5), self.wrap(n.kids[1], 6))

    def r_sub(self, n):
        return '%s - %s' % (self.wrap(n.kids[0], 5), self.wrap(n.kids[1], 6))

    def r_neg(self, n):
        return '-%s' % self.wrap(n.kids[0], 6)

    def r_pos(self, n):
        return '+%s' % self.wrap(n.kids[0], 6)

    def r_mul(self, n):
        a, b = n.kids
        left = self.wrap(a, 6)
        if is_big(a):
            left = r'\left(%s\right)' % self.render(a)
        right = self.wrap(b, 7)
        # il punto esplicito serve solo quando la giustapposizione sarebbe
        # ambigua, cioe' fra due quantita' puramente numeriche
        if is_numeric_like(a) and is_numeric_like(b):
            return r'%s \cdot %s' % (left, right)
        return r'%s\, %s' % (left, right)

    def r_div(self, n):
        num, den = n.kids
        # -pi/2 si legge meglio come -\frac{\pi}{2} che come \frac{-\pi}{2}
        sign = ''
        rn = strip_paren(num)
        if rn.kind == 'neg':
            sign, num = '-', rn.kids[0]
        return r'%s\frac{%s}{%s}' % (sign, self.render(num),
                                     self.render(den))

    def r_pow(self, n):
        base, expo = n.kids
        rb = strip_paren(base)
        if rb.kind == 'call' and rb.attrs['name'].upper() in POWER_ON_NAME:
            inner = r',\, '.join(self.render(k) for k in rb.kids)
            return r'%s^{%s}\!\left(%s\right)' % (
                SIMPLE_FUNC[rb.attrs['name'].upper()],
                self.render(expo), inner)
        if is_big(base):
            b = r'\left(%s\right)' % self.render(base)
        else:
            b = self.wrap(base, 9)
        return r'%s^{%s}' % (b, self.render(expo))

    def r_fact(self, n):
        return r'%s!' % self.wrap(n.kids[0], 9)

    # -- chiamate ------------------------------------------------------
    def r_call(self, n):
        name = n.attrs['name'].upper()
        a = n.kids
        f = getattr(self, 'f_' + name, None)
        if f is not None:
            return f(a)
        if name in SIMPLE_FUNC:
            return r'%s\!\left(%s\right)' % (
                SIMPLE_FUNC[name], r',\, '.join(self.render(k) for k in a))
        return r'\operatorname{%s}\!\left(%s\right)' % (
            name.capitalize(), r',\, '.join(self.render(k) for k in a))

    def f_SQRT(self, a):
        return r'\sqrt{%s}' % self.render(a[0])

    def f_ABS(self, a):
        return r'\left|%s\right|' % self.render(a[0])

    def f_FLOOR(self, a):
        return r'\left\lfloor %s \right\rfloor' % self.render(a[0])

    def f_CEILING(self, a):
        return r'\left\lceil %s \right\rceil' % self.render(a[0])

    def f_LOG(self, a):
        if len(a) == 2:
            return r'\log_{%s}\!\left(%s\right)' % (self.render(a[1]),
                                                    self.render(a[0]))
        return r'\log\!\left(%s\right)' % self.render(a[0])

    def f_INT(self, a):
        if len(a) >= 4:
            return r'\int_{%s}^{%s} %s \,\mathrm{d}%s' % (
                self.render(a[2]), self.render(a[3]),
                self.wrap(a[0], 5), self.render(a[1]))
        if len(a) == 2:
            return r'\int %s \,\mathrm{d}%s' % (self.wrap(a[0], 5),
                                                self.render(a[1]))
        return r'\int %s \,\mathrm{d}x' % self.wrap(a[0], 5)

    def f_DIF(self, a):
        if len(a) >= 3:
            k = self.render(a[2])
            return (r'\frac{\mathrm{d}^{%s}}{\mathrm{d}%s^{%s}}'
                    r'\!\left[%s\right]') % (k, self.render(a[1]), k,
                                             self.render(a[0]))
        return r'\frac{\mathrm{d}}{\mathrm{d}%s}\!\left[%s\right]' % (
            self.render(a[1]), self.render(a[0]))

    def f_LIM(self, a):
        arrow = ''
        if len(a) >= 4:
            d = strip_paren(a[3])
            if d.kind == 'num' and d.attrs.get('name') == '1':
                arrow = '^{+}'
            elif d.kind == 'neg':
                arrow = '^{-}'
        target = self.render(a[2]) if len(a) >= 3 else '0'
        return r'\lim_{%s \to %s%s} %s' % (
            self.render(a[1]), target, arrow, self.wrap(a[0], 6))

    def f_SUM(self, a):
        if len(a) >= 4:
            return r'\sum_{%s=%s}^{%s} %s' % (
                self.render(a[1]), self.render(a[2]), self.render(a[3]),
                self.wrap(a[0], 6))
        return r'\sum %s' % self.wrap(a[0], 6)

    def f_PRODUCT(self, a):
        if len(a) >= 4:
            return r'\prod_{%s=%s}^{%s} %s' % (
                self.render(a[1]), self.render(a[2]), self.render(a[3]),
                self.wrap(a[0], 6))
        return r'\prod %s' % self.wrap(a[0], 6)

    def f_DET(self, a):
        m = strip_paren(a[0])
        if m.kind == 'list' and m.kids and all(r.kind == 'list'
                                               for r in m.kids):
            rows = [' & '.join(self.render(c) for c in r.kids)
                    for r in m.kids]
            return r'\begin{vmatrix} %s \end{vmatrix}' % r' \\ '.join(rows)
        return r'\det\!\left(%s\right)' % self.render(a[0])

    def f_IF(self, a):
        if len(a) == 2:
            return r'\begin{cases} %s & \text{se } %s \end{cases}' % (
                self.render(a[1]), self.render(a[0]))
        if len(a) >= 3:
            return (r'\begin{cases} %s & \text{se } %s \\ '
                    r'%s & \text{altrimenti} \end{cases}') % (
                self.render(a[1]), self.render(a[0]), self.render(a[2]))
        return r'\operatorname{If}\!\left(%s\right)' % self.render(a[0])

    def _named(self, label, a):
        return r'\operatorname{%s}\!\left(%s\right)' % (
            label, r',\; '.join(self.render(k) for k in a))

    def f_SOLVE(self, a):
        return self._named('Solve', a)

    def f_NSOLVE(self, a):
        return self._named('NSolve', a)

    def f_APPROX(self, a):
        return self._named('Approx', a)

    def f_FACTOR(self, a):
        return self._named('Factor', a)


def to_latex(src):
    """Traduce una espressione Derive nel corpo LaTeX corrispondente."""
    return Renderer().render(parse(src))


# --------------------------------------------------------------------------
# Impaginazione delle espressioni lunghe
# --------------------------------------------------------------------------

def flatten_add(node, sign=1, out=None):
    """Scompone una somma nei suoi termini con segno (senza entrare
    nelle parentesi)."""
    if out is None:
        out = []
    if node.kind == 'add':
        flatten_add(node.kids[0], sign, out)
        flatten_add(node.kids[1], sign, out)
    elif node.kind == 'sub':
        flatten_add(node.kids[0], sign, out)
        flatten_add(node.kids[1], -sign, out)
    else:
        out.append((sign, node))
    return out


def flatten_or(node, out=None):
    if out is None:
        out = []
    if node.kind == 'or':
        flatten_or(node.kids[0], out)
        flatten_or(node.kids[1], out)
    else:
        out.append(node)
    return out


def render_side(node, budget):
    """Rende un membro spezzandolo su piu' righe se supera il budget."""
    r = Renderer()
    s = r.render(node)
    if len(s) <= budget:
        return [s]
    terms = flatten_add(node)
    if len(terms) < 2:
        return [s]
    # L'operatore che unisce due termini viene ripetuto all'inizio della
    # riga di continuazione: spezzare senza riportarlo cambierebbe il senso
    # della formula.
    lines, cur = [], ''
    for i, (sg, t) in enumerate(terms):
        piece = r.wrap(t, 6)
        segno = '-' if sg < 0 else ('+' if i > 0 else '')
        if not cur:
            cur = (segno + ' ' if segno else '') + piece
        else:
            cur += ' %s %s' % (segno, piece)
        if len(cur) > budget and i < len(terms) - 1:
            lines.append(cur)
            cur = ''
    if cur:
        lines.append(cur)
    return [l for l in lines if l.strip()]


def _relation_rows(node, budget):
    """Righe di un ambiente align* per una catena di relazioni."""
    rows = []
    parts = render_side(node.kids[0], budget)
    rows.append('& ' + parts[0])
    for extra in parts[1:]:
        rows.append(r'&\qquad ' + extra)
    for op, k in zip(node.attrs['ops'], node.kids[1:]):
        parts = render_side(k, budget)
        rows.append('%s\\;& %s' % (RELSYM[op], parts[0]))
        for extra in parts[1:]:
            rows.append(r'&\qquad ' + extra)
    return rows


def to_display(src, budget=150):
    """Ambiente LaTeX completo per l'espressione, con a capo automatici."""
    node = parse(src)
    r = Renderer()
    whole = r.render(node)
    if len(whole) <= budget:
        return '\\[\n%s\n\\]' % whole

    if node.kind == 'or':
        rows = []
        for i, alt in enumerate(flatten_or(node)):
            body = ' \\\\\n&\\qquad '.join(render_side(alt, budget))
            prefix = '&' if i == 0 else '\\lor\\quad &'
            rows.append('%s %s' % (prefix, body))
        return '\\begin{align*}\n%s\n\\end{align*}' % ' \\\\[3pt]\n'.join(rows)

    if node.kind == 'rel':
        return '\\begin{align*}\n%s\n\\end{align*}' % \
            ' \\\\\n'.join(_relation_rows(node, budget))

    parts = render_side(node, budget)
    if len(parts) == 1:
        return '\\[\n%s\n\\]' % parts[0]
    return '\\begin{align*}\n& %s\n\\end{align*}' % \
        ' \\\\\n&\\qquad '.join(parts)
