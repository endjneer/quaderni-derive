# -*- coding: utf-8 -*-
"""
Genera le figure vettoriali del documento a partire dalle formule dei
quaderni Derive. Ogni funzione produce un PDF in ``figures/``.

Uso:  python make_figures.py [cartella_di_uscita]
"""
import os, sys, math, cmath

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

# --------------------------------------------------------------------------
# Stile comune
# --------------------------------------------------------------------------

BLU = '#1f4e79'
ROSSO = '#b3352b'
VERDE = '#2a7f62'
AMBRA = '#d38b1f'
VIOLA = '#6b4c9a'
GRIGIO = '#8a8f98'
CICLO = [BLU, ROSSO, VERDE, AMBRA, VIOLA]

plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['DejaVu Serif'],
    'mathtext.fontset': 'dejavuserif',
    'font.size': 9,
    'axes.titlesize': 10,
    'axes.labelsize': 9,
    'legend.fontsize': 8,
    'axes.linewidth': 0.7,
    'axes.edgecolor': '#444444',
    'grid.color': '#d8dce1',
    'grid.linewidth': 0.5,
    'xtick.direction': 'in',
    'ytick.direction': 'in',
    'xtick.major.width': 0.7,
    'ytick.major.width': 0.7,
    'figure.dpi': 120,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.02,
    'pdf.fonttype': 42,
})

OUT = 'figures'


def nuova(w=5.6, h=3.2, n=1, **kw):
    fig, ax = plt.subplots(1, n, figsize=(w, h), **kw)
    axes = ax if n > 1 else [ax]
    for a in axes:
        a.grid(True, alpha=0.55)
        a.set_axisbelow(True)
        for s in ('top', 'right'):
            a.spines[s].set_visible(False)
    return fig, ax


def salva(fig, nome):
    path = os.path.join(OUT, nome + '.pdf')
    fig.savefig(path)
    plt.close(fig)
    print('  ', path)


# --------------------------------------------------------------------------
# delta.dfw
# --------------------------------------------------------------------------

def delta_n(x, n):
    """La famiglia di delta.dfw #1, valutata direttamente come da sorgente."""
    x = np.asarray(x, dtype=float)
    a = (1 + 2 * n * x) / np.abs(x + 1.0 / (2 * n))
    b = (1 - 2 * n * x) / np.abs(x - 1.0 / (2 * n))
    return 0.25 * (a + b)


def fig_delta_famiglia():
    fig, ax = nuova(5.8, 3.1)
    x = np.linspace(-1.6, 1.6, 40001)
    for c, n in zip(CICLO, (1, 2, 4, 8)):
        ax.plot(x, delta_n(x, n), color=c, lw=1.3, label=r'$n=%d$' % n)
    ax.set_xlim(-1.6, 1.6)
    ax.set_ylim(-0.4, 9)
    ax.set_xlabel('$x$')
    ax.set_ylabel(r'$\delta_n(x)$')
    ax.set_title(u'La famiglia approssimante: rettangoli di area unitaria')
    ax.legend(frameon=False, ncol=4, loc='upper right')
    ax.annotate(u'altezza $n$, base $1/n$', xy=(0.125, 8), xytext=(0.55, 6.4),
                arrowprops=dict(arrowstyle='->', color=GRIGIO, lw=0.8),
                color='#333333')
    salva(fig, 'delta_famiglia')


def fig_delta_area():
    """Verifica numerica di delta.dfw #2: l'integrale vale 1 per ogni n."""
    fig, ax = nuova(5.4, 2.6)
    ns = np.arange(1, 33)
    aree = []
    for n in ns:
        x = np.linspace(-3, 3, 400001)
        aree.append(np.trapezoid(delta_n(x, n), x))
    ax.plot(ns, aree, 'o-', color=BLU, ms=3.2, lw=1.0)
    ax.axhline(1, color=ROSSO, lw=1.0, ls='--')
    ax.set_ylim(0.9, 1.1)
    ax.set_xlabel('$n$')
    ax.set_ylabel(u'area')
    ax.set_title(u'Area sotto $\\delta_n$: costante e pari a $1$')
    salva(fig, 'delta_area')


def fig_delta_complesso():
    """Il limite della stessa famiglia calcolata su argomento complesso."""
    n = 4000
    g = 241
    xs = np.linspace(-2, 2, g)
    ys = np.linspace(-2, 2, g)
    X, Y = np.meshgrid(xs, ys)
    Z = X + 1j * Y
    with np.errstate(divide='ignore', invalid='ignore'):
        a = (1 + 2 * n * Z) / np.abs(Z + 1.0 / (2 * n))
        b = (1 - 2 * n * Z) / np.abs(Z - 1.0 / (2 * n))
        L = 0.25 * (a + b)
        M = np.abs(L)
    fig, ax = nuova(4.6, 3.6)
    ax.grid(False)
    im = ax.pcolormesh(X, Y, np.clip(M, 0, 3), shading='auto',
                       cmap='magma')
    ax.set_aspect('equal')
    ax.set_xlabel(r'$\mathrm{Re}\,z$')
    ax.set_ylabel(r'$\mathrm{Im}\,z$')
    ax.set_title(u'$|\\delta_n(z)|$ nel piano complesso  ($n=4000$)')
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    salva(fig, 'delta_complesso')


# --------------------------------------------------------------------------
# cosinc.dfw
# --------------------------------------------------------------------------

def fig_sinc_cosinc():
    fig, ax = nuova(5.8, 3.0)
    x = np.linspace(-6, 6, 3001)
    x0 = np.where(np.abs(x) < 1e-9, 1e-9, x)
    sinc = np.sin(np.pi * x0) / (np.pi * x0)
    cosinc = (1 - np.cos(np.pi * x0)) / (np.pi * x0)
    ax.plot(x, sinc, color=BLU, lw=1.3,
            label=r'$\sin(\pi x)/(\pi x)$')
    ax.plot(x, cosinc, color=ROSSO, lw=1.3,
            label=r'$(1-\cos \pi x)/(\pi x)$')
    ax.axhline(0, color='#555555', lw=0.6)
    ax.set_xlabel('$x$')
    ax.set_title(u'Le due componenti di $\\dfrac{(-1)^x-1}{\\pi x}$')
    ax.legend(frameon=False, loc='upper right')
    ax.xaxis.set_major_locator(MultipleLocator(2))
    salva(fig, 'sinc_cosinc')


def fig_cosinc_serie():
    """cosinc.dfw #14-#16: parte reale e immaginaria della serie."""
    fig, ax = nuova(5.8, 3.0)
    x = np.linspace(-4, 4, 1601)
    N = 40
    S = np.zeros_like(x, dtype=complex)
    for n in range(N):
        S += (1j) ** (n + 1) * (np.pi * x) ** n / math.factorial(n + 1)
    x0 = np.where(np.abs(x) < 1e-9, 1e-9, x)
    ax.plot(x, S.imag, color=BLU, lw=2.4, alpha=0.35,
            label=u'somma parziale, parte Im')
    ax.plot(x, np.sin(np.pi * x0) / (np.pi * x0), color=BLU, lw=1.0,
            label=r'$\sin(\pi x)/(\pi x)$')
    ax.plot(x, S.real, color=ROSSO, lw=2.4, alpha=0.35,
            label=u'somma parziale, parte Re')
    ax.plot(x, (np.cos(np.pi * x0) - 1) / (np.pi * x0), color=ROSSO, lw=1.0,
            label=r'$(\cos \pi x - 1)/(\pi x)$')
    ax.set_xlabel('$x$')
    ax.set_title(u'La serie e le sue due forme chiuse')
    ax.legend(frameon=False, fontsize=7.5, ncol=2)
    salva(fig, 'cosinc_serie')


# --------------------------------------------------------------------------
# e.dfw
# --------------------------------------------------------------------------

def fig_e_convergenza():
    fig, ax = nuova(5.6, 3.0)
    xs = np.logspace(0.5, 7, 60)
    cl = np.abs((1 + 1 / xs) ** xs - math.e)
    geo = []
    for x in xs:
        s = x / (x - 1.0)          # somma della serie geometrica 1/x^n
        geo.append(abs(s ** x - math.e))
    ax.loglog(xs, cl, 'o-', color=BLU, ms=3, lw=1.0,
              label=r'$|(1+1/x)^x-\mathrm{e}|$')
    ax.loglog(xs, geo, 's-', color=ROSSO, ms=3, lw=1.0,
              label=r'$|(\sum_n x^{-n})^x-\mathrm{e}|$')
    ax.set_xlabel('$x$')
    ax.set_ylabel(u'errore assoluto')
    ax.set_title(u'Due successioni che tendono a $\\mathrm{e}$')
    ax.legend(frameon=False)
    ax.grid(True, which='both', alpha=0.4)
    salva(fig, 'e_convergenza')


def fig_e_parabola():
    fig, ax = nuova(5.4, 3.2)
    x = np.linspace(2.3, 3.5, 800)
    y = x ** 2 - (math.pi + math.e) * x + math.pi * math.e
    ax.plot(x, y, color=BLU, lw=1.4)
    ax.axhline(0, color='#555555', lw=0.6)
    v = (math.e + math.pi) / 2
    ax.plot([math.e, math.pi], [0, 0], 'o', color=ROSSO, ms=4.5, zorder=5)
    ax.plot([v], [-(math.e - math.pi) ** 2 / 4], 'D', color=VERDE, ms=4,
            zorder=5)
    ax.annotate(r'$\mathrm{e}$', (math.e, 0), textcoords='offset points',
                xytext=(-4, 8), color=ROSSO)
    ax.annotate(r'$\pi$', (math.pi, 0), textcoords='offset points',
                xytext=(2, 8), color=ROSSO)
    ax.annotate(r'vertice $\left(\frac{\mathrm{e}+\pi}{2},'
                r'-\frac{(\mathrm{e}-\pi)^2}{4}\right)$',
                (v, -(math.e - math.pi) ** 2 / 4),
                textcoords='offset points', xytext=(10, -14), color=VERDE,
                fontsize=8)
    ax.set_xlabel('$x$')
    ax.set_title(u'La parabola che ha per radici $\\mathrm{e}$ e $\\pi$')
    salva(fig, 'e_parabola')


# --------------------------------------------------------------------------
# atan.dfw
# --------------------------------------------------------------------------

def fig_atan_cerchio():
    fig, ax = nuova(3.9, 3.6)
    t = np.linspace(0, 2 * np.pi, 400)
    ax.plot(np.cos(t), np.sin(t), color=GRIGIO, lw=0.8, ls='--')
    xs = np.tan(np.linspace(-1.45, 1.45, 33))
    w = (1 + 1j * xs) / np.sqrt(xs ** 2 + 1)
    ax.plot(w.real, w.imag, 'o', color=BLU, ms=3.4)
    for x in (-3, -1, 0, 1, 3):
        z = (1 + 1j * x) / math.sqrt(x * x + 1)
        ax.plot([0, z.real], [0, z.imag], color=ROSSO, lw=0.8, alpha=0.75)
        ax.annotate('$x=%d$' % x, (z.real, z.imag),
                    textcoords='offset points', xytext=(6, 2), fontsize=7.5)
    ax.set_aspect('equal')
    ax.set_xlim(-1.35, 1.7)
    ax.set_ylim(-1.35, 1.35)
    ax.set_xlabel(r'$\mathrm{Re}$')
    ax.set_ylabel(r'$\mathrm{Im}$')
    ax.set_title(u'$\\mathrm{e}^{\\mathrm{i}\\arctan x}$ sul cerchio unitario',
                 fontsize=9)
    salva(fig, 'atan_cerchio')


# --------------------------------------------------------------------------
# cost^2.dfw  (integrali di Fresnel)
# --------------------------------------------------------------------------

def fig_fresnel():
    fig, (a1, a2) = nuova(6.6, 2.9, n=2)
    t = np.linspace(0, 5, 4000)
    a1.plot(t, np.cos(t ** 2), color=BLU, lw=1.0, label=r'$\cos t^2$')
    a1.plot(t, np.sin(t ** 2), color=ROSSO, lw=1.0, label=r'$\sin t^2$')
    a1.set_xlabel('$t$')
    a1.set_title(u'Oscillazione a frequenza crescente')
    a1.legend(frameon=False, loc='lower left', fontsize=7.5)

    tt = np.linspace(-4.2, 4.2, 6000)
    C = np.concatenate([[0], np.cumsum(np.cos(tt[1:] ** 2) * np.diff(tt))])
    S = np.concatenate([[0], np.cumsum(np.sin(tt[1:] ** 2) * np.diff(tt))])
    a2.plot(C, S, color=VIOLA, lw=0.9)
    a2.set_aspect('equal')
    a2.set_xlabel(r'$\int_0^t \cos u^2\,\mathrm{d}u$')
    a2.set_ylabel(r'$\int_0^t \sin u^2\,\mathrm{d}u$')
    a2.set_title(u'La spirale di Cornu')
    salva(fig, 'fresnel')


# --------------------------------------------------------------------------
# gauss.dfw
# --------------------------------------------------------------------------

def fig_gauss_sign():
    fig, ax = nuova(5.8, 3.0)
    t = np.linspace(-3 * np.pi, 3 * np.pi, 6000)
    with np.errstate(all='ignore'):
        num = np.sqrt(2) * np.sin(t)
        den = np.sqrt(np.maximum(np.cos(t) + 1, 0))
        re = -4 * np.floor(0.5 - t / (2 * np.pi)) + np.where(den > 1e-8,
                                                             num / den, np.nan)
    ax.plot(t, re, color=BLU, lw=1.2,
            label=u'parte reale della primitiva')
    ax.plot(t, -np.sqrt(2) * np.sqrt(np.maximum(np.cos(t) + 1, 0)),
            color=ROSSO, lw=1.2, label=u'parte immaginaria')
    ax.set_xlabel('$t$')
    ax.set_title(u'$\\int \\mathrm{sgn}\\!\\left(1+\\mathrm{i}\\tan(t/2)'
                 u'\\right)\\mathrm{d}t$')
    ax.legend(frameon=False, fontsize=7.5)
    salva(fig, 'gauss_sign')


# --------------------------------------------------------------------------
# Trasformata T.dfw
# --------------------------------------------------------------------------

def fig_trasformata_t():
    """I nuclei prodotti dall'operatore di Trasformata T.dfw.

    Pannello di sinistra: le funzioni circolari danno tutte lo stesso
    nucleo sinc. Pannello di destra: l'esponenziale reale da' invece il
    suo analogo iperbolico, che diverge.
    """
    fig, (a1, a2) = nuova(6.6, 2.9, n=2)
    t = np.linspace(0.02, 14, 3000)
    a1.plot(t, np.sin(t / 2) / (t / 2), color=BLU, lw=1.4,
            label=r'$\sin,\ \cos,\ \mathrm{e}^{\mathrm{i}x}$')
    a1.plot(t, np.sin(np.pi * t) / (np.pi * t), color=VERDE, lw=1.2,
            label=r'$\mathrm{e}^{2\pi\mathrm{i}x}$')
    a1.axhline(0, color='#555555', lw=0.6)
    a1.set_xlabel('$t$')
    a1.set_title(u'Nuclei di tipo $\\mathrm{sinc}$')
    a1.legend(frameon=False, fontsize=7.5)

    a2.semilogy(t, np.sinh(t / 2) / (t / 2), color=ROSSO, lw=1.4,
                label=r'$\mathrm{e}^{x}:\ \sinh(t/2)/(t/2)$')
    a2.axhline(1, color=GRIGIO, lw=0.8, ls='--')
    a2.set_xlabel('$t$')
    a2.set_title(u'Nucleo iperbolico')
    a2.legend(frameon=False, fontsize=7.5, loc='lower right')
    a2.grid(True, which='both', alpha=0.4)
    salva(fig, 'trasformata_t')


# --------------------------------------------------------------------------
# pigreco.dfw
# --------------------------------------------------------------------------

def fig_pigreco_identita():
    fig, ax = nuova(5.8, 3.0)
    x = np.concatenate([np.linspace(-4, -0.08, 2500),
                        np.linspace(0.08, 4, 2500)])
    with np.errstate(all='ignore'):
        num = (np.cos(2 * x) - np.cos(2 / x)) * (np.arctan(x)
                                                 + np.arctan(1 / x))
        den = np.cos(x) ** 2 - np.cos(1 / x) ** 2
        y = num / den
    y[np.abs(den) < 1e-6] = np.nan
    ax.plot(x, y, '.', color=BLU, ms=1.6)
    ax.axhline(math.pi, color=ROSSO, lw=1.0, ls='--')
    ax.axhline(-math.pi, color=ROSSO, lw=1.0, ls='--')
    ax.set_ylim(-4.5, 4.5)
    ax.set_xlabel('$x$')
    ax.set_yticks([-math.pi, 0, math.pi])
    ax.set_yticklabels([r'$-\pi$', '$0$', r'$\pi$'])
    ax.set_title(u'Il rapporto vale $\\mathrm{sgn}(x)\\,\\pi$ ovunque')
    salva(fig, 'pigreco_identita')


# --------------------------------------------------------------------------
# sin-cos.dfw
# --------------------------------------------------------------------------

def fig_sincos_pi_e():
    fig, ax = nuova(5.8, 3.0)
    x = np.linspace(-30, 30, 3000)
    k = math.pi - math.e * math.log(math.pi)
    ch = np.cosh(k * x)
    sh = np.sinh(k * x)
    ax.plot(x, ch, color=BLU, lw=1.3, label=r'$\cosh(kx)$')
    ax.plot(x, sh, color=ROSSO, lw=1.3, label=r'$\sinh(kx)$')
    ax.axhline(0, color='#555555', lw=0.6)
    ax.set_xlabel('$x$')
    ax.set_title(u'$k=\\pi-\\mathrm{e}\\ln\\pi = %.10f$' % k)
    ax.legend(frameon=False)
    salva(fig, 'sincos_pi_e')


# --------------------------------------------------------------------------
# teoria.dfw
# --------------------------------------------------------------------------

def fig_teoria_radice_doppia():
    """teoria.dfw #14-#19: la separazione delle radici va come la radice
    quadrata della perturbazione, non come la perturbazione."""
    fig, (a1, a2) = nuova(6.6, 2.9, n=2)

    x = np.linspace(-2.0, 0.0, 1200)
    for c, ee in zip(CICLO, (0.0, 0.01, 0.04)):
        a1.plot(x, (x + 1) ** 2 - 2 * ee, color=c, lw=1.2,
                label=r'$\varepsilon=%.2f$' % ee)
        if ee > 0:
            for s in (-1, 1):
                a1.plot([-1 + s * math.sqrt(2 * ee)], [0], 'o', color=c,
                        ms=4, zorder=5)
    a1.axhline(0, color='#555555', lw=0.6)
    a1.set_ylim(-0.1, 0.35)
    a1.set_xlim(-1.6, -0.4)
    a1.set_xlabel('$x$')
    a1.set_title(u'$(x+1)^2=2\\varepsilon$')
    a1.legend(frameon=False, fontsize=7.5)

    eps = np.logspace(-16, -2, 60)
    a2.loglog(eps, 2 * np.sqrt(2 * eps), color=BLU, lw=1.3,
              label=u'separazione delle radici')
    a2.loglog(eps, eps, color=GRIGIO, lw=1.0, ls='--',
              label=r'$\varepsilon$, per confronto')
    a2.set_xlabel(r'$\varepsilon$')
    a2.set_title(u'Pendenza $1/2$, non $1$')
    a2.legend(frameon=False, fontsize=7.5, loc='upper left')
    a2.grid(True, which='both', alpha=0.4)
    salva(fig, 'teoria_radice_doppia')


# --------------------------------------------------------------------------
# teoria2.dfw
# --------------------------------------------------------------------------

def fig_teoria2():
    fig, ax = nuova(4.6, 4.0)
    k = 1.0
    x = np.linspace(0, 1.05, 600)
    ax.plot(x, x, color=GRIGIO, lw=1.0, label='$y=x$')
    for c, (n, a, xc) in zip(CICLO, [(2, 2 / k, k / 2),
                                     (3, 16 / k ** 2, k / 4),
                                     (4, 512 / k ** 3, k / 8)]):
        ax.plot(x, a * x ** n, color=c, lw=1.3,
                label=r'$y=%s\,x^{%d}$' % (('2', '16', '512')[n - 2], n))
        # la bisettrice secondaria che genera il punto di appoggio
        ax.plot(x, -x + 2.0 ** (2 - n) * k, color=c, lw=0.8, ls='--')
        ax.plot([xc], [xc], 'o', color=c, ms=4.5, zorder=5)
    ax.set_xlim(0, 1.05)
    ax.set_ylim(0, 1.05)
    ax.set_aspect('equal')
    ax.set_xlabel('$x$')
    ax.set_title(u'La famiglia $y=2^{(n-1)^2}k^{1-n}x^n$  ($k=1$)',
                 fontsize=9)
    ax.legend(frameon=False, fontsize=7.5, loc='upper left')
    salva(fig, 'teoria2')


# --------------------------------------------------------------------------
# fx^gx.dfw
# --------------------------------------------------------------------------

def fig_fxgx():
    fig, ax = nuova(5.8, 2.8)
    x = np.linspace(0.02, math.pi - 0.02, 3000)
    s = np.sin(x)
    with np.errstate(all='ignore'):
        y = s ** (1 / np.log(1 / s))
    ax.plot(x, y, color=BLU, lw=1.4, label=r'$\sin(x)^{1/\ln(1/\sin x)}$')
    ax.axhline(1 / math.e, color=ROSSO, lw=1.0, ls='--',
               label=r'$1/\mathrm{e}$')
    ax.set_ylim(0.2, 0.55)
    ax.set_xlabel('$x$')
    ax.set_title(u'Una funzione costante travestita')
    ax.legend(frameon=False)
    salva(fig, 'fxgx')


# --------------------------------------------------------------------------
# limit.dfw
# --------------------------------------------------------------------------

def fig_limit_disug():
    fig, ax = nuova(5.4, 3.0)
    x = np.linspace(-2, 2, 2000)
    ax.plot(x, np.abs(x), color=BLU, lw=1.4, label=r'$|x|$')
    ax.plot(x, math.sqrt(2) / 2 * (0.5 + x ** 2), color=ROSSO, lw=1.4,
            label=r'$\frac{\sqrt{2}}{2}\left(\frac{1}{2}+x^2\right)$')
    for s in (-1, 1):
        ax.plot([s / math.sqrt(2)], [1 / math.sqrt(2)], 'o', color=VERDE,
                ms=4.5, zorder=5)
    ax.annotate(r'contatto in $x=\pm\frac{1}{\sqrt{2}}$',
                (1 / math.sqrt(2), 1 / math.sqrt(2)),
                textcoords='offset points', xytext=(8, -18), color=VERDE,
                fontsize=8)
    ax.set_xlabel('$x$')
    ax.set_title(u'Una maggiorazione tangente')
    ax.legend(frameon=False, loc='upper center')
    salva(fig, 'limit_disug')


# --------------------------------------------------------------------------
# mate.dfw
# --------------------------------------------------------------------------

def fig_mate_onde():
    fig, ax = nuova(6.2, 3.1)
    x = np.linspace(-2, 2, 6000)
    # le prime due espressioni coincidono: la prima e' disegnata spessa
    # e trasparente per lasciare vedere la seconda sopra di essa
    ax.plot(x, np.arccos(np.sin(np.pi * (x - 0.5))) / np.pi, color=BLU,
            lw=3.2, alpha=0.35,
            label=r'$\frac{1}{\pi}\arccos\sin\pi(x-\frac{1}{2})$')
    ax.plot(x, np.abs(2 / np.pi * np.arcsin(np.cos(np.pi * x / 2))),
            color=ROSSO, lw=1.2,
            label=r'$\left|\frac{2}{\pi}\arcsin\cos\frac{\pi x}{2}\right|$')
    with np.errstate(all='ignore'):
        saw = np.arctan(1 / np.tan(-np.pi * (x + 0.5))) / np.pi
    saw = np.where(np.abs(np.diff(np.concatenate([saw[:1], saw]))) > 0.5,
                   np.nan, saw)
    ax.plot(x, saw + 0.5, color=VERDE, lw=1.3,
            label=r'$\frac{1}{\pi}\mathrm{arccot}\tan(-\pi(x+\frac{1}{2}))$')
    ax.set_xlabel('$x$')
    ax.set_ylim(-0.15, 1.35)
    ax.set_title(u'Onde triangolari e a dente di sega da funzioni inverse')
    ax.legend(frameon=False, fontsize=7.5, ncol=3, loc='upper center',
              bbox_to_anchor=(0.5, -0.18))
    salva(fig, 'mate_onde')


def fig_mate_logcosh():
    fig, ax = nuova(5.4, 2.8)
    x = np.linspace(-4, 4, 2000)
    y = np.log((np.abs(np.exp(x) - 1) + np.abs(np.exp(x) + 1)) / 2)
    ax.plot(x, np.abs(x), color=GRIGIO, lw=2.6, alpha=0.45, label=r'$|x|$')
    ax.plot(x, y, color=BLU, lw=1.2,
            label=r'$\ln\frac{|\mathrm{e}^x-1|+|\mathrm{e}^x+1|}{2}$')
    ax.plot(x, np.log(np.cosh(x)), color=ROSSO, lw=1.0, ls='--',
            label=r'$\ln\cosh x$')
    ax.set_xlabel('$x$')
    ax.set_title(u'Tre modi di scrivere (quasi) il valore assoluto')
    ax.legend(frameon=False, fontsize=7.5)
    salva(fig, 'mate_logcosh')


# --------------------------------------------------------------------------
# factor.dfw
# --------------------------------------------------------------------------

def fig_factor():
    fig, ax = nuova(5.6, 3.0)
    ps = list(range(0, 12))
    lp, lf = [], []
    for p in ps:
        s = sum(math.lgamma(2 * n + 2) for n in range(p + 1))
        m = (p + 1) * (p + 2) // 2
        lp.append(s / math.log(10))
        lf.append(math.lgamma(m + 1) / math.log(10))
    ax.plot(ps, lp, 'o-', color=BLU, ms=3.5, lw=1.0,
            label=r'$\prod_{n=0}^{p}(2n+1)!$')
    ax.plot(ps, lf, 's-', color=ROSSO, ms=3.5, lw=1.0,
            label=r'$\left(\frac{(p+1)(p+2)}{2}\right)!$')
    ax.set_xlabel('$p$')
    ax.set_ylabel(u'cifre decimali')
    ax.set_title(u'Due prodotti che partono uguali e poi divergono')
    ax.legend(frameon=False, loc='upper left')
    ax2 = ax.twinx()
    ax2.plot(ps, [a - b for a, b in zip(lp, lf)], '^:', color=VERDE, ms=3.5,
             lw=0.9)
    ax2.set_ylabel(u'differenza (cifre)', color=VERDE)
    ax2.tick_params(axis='y', colors=VERDE)
    ax2.grid(False)
    salva(fig, 'factor')


# --------------------------------------------------------------------------
# fattorazionale.dfw
# --------------------------------------------------------------------------

def fig_fattorazionale():
    fig, ax = nuova(5.4, 2.9)
    ks = list(range(2, 14))
    val, teo = [], []
    for k in ks:
        p = 1.0
        for n in range(1, k):
            p *= (1.0 / n - 1.0 / k)
        val.append(-math.log10(p) if p > 0 else float('nan'))
        teo.append((k - 1) * math.log10(k))
    ax.plot(ks, val, 'o', color=BLU, ms=5, label=u'prodotto calcolato')
    ax.plot(ks, teo, '-', color=ROSSO, lw=1.2,
            label=r'$(k-1)\log_{10}k$')
    ax.set_xlabel('$k$')
    ax.set_ylabel(u'$-\\log_{10}$ del prodotto')
    ax.set_title(u'$\\prod_{n=1}^{k-1}\\left(\\frac{1}{n}-\\frac{1}{k}\\right)'
                 u'=k^{-(k-1)}$')
    ax.legend(frameon=False, loc='upper left')
    salva(fig, 'fattorazionale')


# --------------------------------------------------------------------------
# numeri primi.dfw
# --------------------------------------------------------------------------

def fig_primoriale():
    fig, ax = nuova(5.4, 2.9)
    primi = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53,
             59, 61, 67]
    s, acc, xs = 0.0, [], []
    p = 1.0
    for i, q in enumerate(primi, 1):
        p *= q
        s += 1.0 / p
        acc.append(s)
        xs.append(i)
    ax.semilogy(xs, [abs(a - acc[-1]) + 1e-30 for a in acc], 'o-',
                color=BLU, ms=3.5, lw=1.0)
    ax.set_xlabel(u'numero di termini')
    ax.set_ylabel(u'distanza dal valore finale')
    ax.set_title(u'Somma dei reciproci dei primoriali: '
                 u'convergenza  ($S\\approx%.12f$)' % acc[-1])
    salva(fig, 'primoriale')


# --------------------------------------------------------------------------
# u(0)-sign(0).dfw
# --------------------------------------------------------------------------

def fig_u0():
    fig, ax = nuova(5.6, 2.8)
    e = math.e
    nomi = [r'$\ln(\mathrm{e}-1)$',
            r'$\ln\frac{\mathrm{e}^2-1}{2\mathrm{e}}$',
            r'$\frac{1}{2}\left(\ln\frac{\mathrm{e}^2-1}{2\mathrm{e}}+1\right)$',
            r'$2\ln(\mathrm{e}-1)-1$']
    val = [math.log(e - 1),
           math.log((e ** 2 - 1) / (2 * e)),
           0.5 * (math.log((e ** 2 - 1) / (2 * e)) + 1),
           2 * math.log(e - 1) - 1]
    ax.barh(range(4), val, color=[BLU, VERDE, AMBRA, ROSSO], height=0.55)
    for i, v in enumerate(val):
        ax.text(v + 0.012, i, '%.10f' % v, va='center', fontsize=8)
    ax.set_yticks(range(4))
    ax.set_yticklabels(nomi, fontsize=8.5)
    ax.set_xlim(0, 0.78)
    ax.invert_yaxis()
    ax.set_title(u'Quattro candidati per il valore in $0$')
    salva(fig, 'u0')


# --------------------------------------------------------------------------
# j.dfw
# --------------------------------------------------------------------------

def fig_j_tan():
    fig, ax = nuova(5.6, 2.9)
    x = np.linspace(-2 * np.pi + 0.05, 2 * np.pi - 0.05, 4000)
    with np.errstate(all='ignore'):
        a = (1 - np.cos(x)) / np.sin(x)
        b = (1 + np.cos(x)) / np.sin(x)
    a[np.abs(np.sin(x)) < 1e-3] = np.nan
    b[np.abs(np.sin(x)) < 1e-3] = np.nan
    ax.plot(x, a, color=BLU, lw=1.2,
            label=r'$\frac{1-\cos x}{\sin x}=\tan\frac{x}{2}$')
    ax.plot(x, b, color=ROSSO, lw=1.2,
            label=r'$\frac{1+\cos x}{\sin x}=\cot\frac{x}{2}$')
    ax.plot([0], [0], 'o', color=VERDE, ms=5, zorder=5)
    ax.plot([math.pi], [0], 'o', color=VERDE, ms=5, zorder=5)
    ax.set_ylim(-4, 4)
    ax.set_xlabel('$x$')
    ax.set_title(u'I due rapporti si annullano nei punti studiati')
    ax.legend(frameon=False, fontsize=8, loc='upper left')
    salva(fig, 'j_tan')


# --------------------------------------------------------------------------
# equazioni.dfw
# --------------------------------------------------------------------------

def fig_equazioni_reim():
    """Le curve Re=0 e Im=0 per a z^2 + b z + c = 0 e le loro intersezioni."""
    a, b, c = 1.0, -1.0, 2.5
    g = 601
    xs = np.linspace(-2.2, 2.6, g)
    ys = np.linspace(-2.0, 2.0, g)
    X, Y = np.meshgrid(xs, ys)
    R = a * X ** 2 + b * X - a * Y ** 2 + c
    I = 2 * a * X * Y + b * Y
    fig, ax = nuova(5.0, 3.6)
    cr = ax.contour(X, Y, R, levels=[0], colors=[BLU], linewidths=1.3)
    ci = ax.contour(X, Y, I, levels=[0], colors=[ROSSO], linewidths=1.3)
    r = np.roots([a, b, c])
    ax.plot(r.real, r.imag, 'o', color=VERDE, ms=6, zorder=6)
    ax.set_aspect('equal')
    ax.set_xlabel('$x$')
    ax.set_ylabel('$y$')
    ax.set_title(u'$\\mathrm{Re}=0$ (blu) e $\\mathrm{Im}=0$ (rosso):\n'
                 u'le radici sono le intersezioni', fontsize=9)
    salva(fig, 'equazioni_reim')


# --------------------------------------------------------------------------
# notch.dfw
# --------------------------------------------------------------------------

def fig_notch_bode():
    fig, ax = nuova(5.8, 3.0)
    l, c, f, r = 1e-3, 1e-6, 1e-3, 50.0
    w = np.logspace(3, 6, 2000)
    s = 1j * w
    for gg, col, lab in ((0.0, BLU, '$g=0$'),
                         (1e-7, ROSSO, '$g=10^{-7}$'),
                         (1e-6, VERDE, '$g=10^{-6}$')):
        H = (f * r * (c * l * s ** 2 + 1) /
             (f * l * r * s ** 2 * (c + gg) + f * l * s + r * (f + l)))
        ax.semilogx(w, 20 * np.log10(np.abs(H)), color=col, lw=1.2,
                    label=lab)
    w0 = 1 / math.sqrt(l * c)
    ax.axvline(w0, color=GRIGIO, lw=0.8, ls='--')
    ax.annotate(r'$\omega_n=1/\sqrt{LC}$', (w0, -55),
                textcoords='offset points', xytext=(6, 0), fontsize=8,
                color='#444444')
    ax.set_xlabel(u'$\\omega$  [rad/s]')
    ax.set_ylabel(u'$|H|$  [dB]')
    ax.set_title(u'Risposta del filtro elimina-banda')
    ax.legend(frameon=False, loc='lower left')
    salva(fig, 'notch_bode')


# --------------------------------------------------------------------------

FIGURE = [
    fig_delta_famiglia, fig_delta_area, fig_delta_complesso,
    fig_sinc_cosinc, fig_cosinc_serie,
    fig_e_convergenza, fig_e_parabola,
    fig_atan_cerchio, fig_fresnel, fig_gauss_sign,
    fig_trasformata_t, fig_pigreco_identita, fig_sincos_pi_e,
    fig_teoria_radice_doppia, fig_teoria2, fig_fxgx, fig_limit_disug,
    fig_mate_onde, fig_mate_logcosh,
    fig_factor, fig_fattorazionale, fig_primoriale, fig_u0,
    fig_j_tan, fig_equazioni_reim, fig_notch_bode,
]


def main():
    global OUT
    if len(sys.argv) > 1:
        OUT = sys.argv[1]
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    for f in FIGURE:
        print(f.__name__)
        f()


if __name__ == '__main__':
    main()
