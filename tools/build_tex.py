# -*- coding: utf-8 -*-
"""
Genera i capitoli LaTeX del documento.

Legge:
  extracted/all.json      espressioni estratte dai .dfw
  extracted/verify.json   esito della verifica numerica
  commento/*.json         commento redazionale, un file per quaderno

Scrive:
  tex/generato/<slug>.tex un capitolo per quaderno
  tex/generato/indice.tex l'elenco degli \\input nell'ordine scelto
  tex/generato/prospetto.tex  la tabella riassuntiva dei quaderni

Uso:  python build_tex.py <radice_progetto>
"""
import os, sys, json, glob, io, re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive2tex as D


def escape_text(s):
    """Protegge i caratteri speciali di LaTeX nel testo discorsivo."""
    out = []
    i = 0
    while i < len(s):
        c = s[i]
        if c == '$':                      # matematica in linea: passa intatta
            j = s.find('$', i + 1)
            if j < 0:
                out.append(r'\$')
                i += 1
                continue
            out.append(s[i:j + 1])
            i = j + 1
            continue
        if s.startswith('\\[', i):        # matematica in display: idem
            j = s.find('\\]', i + 2)
            if j < 0:
                out.append('\\[')
                i += 2
                continue
            out.append(s[i:j + 2])
            i = j + 2
            continue
        m = re.match(r'\\begin\{([A-Za-z*]+)\}', s[i:])
        if m:                             # ambiente LaTeX: passa intatto,
            fine = '\\end{%s}' % m.group(1)   # comprese le & di tabella
            j = s.find(fine, i)
            if j >= 0:
                out.append(s[i:j + len(fine)])
                i = j + len(fine)
                continue
        if c == '\\':                     # comando LaTeX esplicito
            m = re.match(r'\\[A-Za-z]+', s[i:])
            if m:
                out.append(m.group())
                i += len(m.group())
                continue
        # la tilde resta com'e': nel commento serve come spazio unificatore
        # (capitolo~\ref{...}), non come carattere letterale
        out.append({'#': r'\#', '%': r'\%', '&': r'\&', '_': r'\_',
                    '^': r'\textasciicircum{}'}.get(c, c))
        i += 1
    return ''.join(out)


def slug(nome):
    s = nome[:-4] if nome.lower().endswith('.dfw') else nome
    s = s.replace('^', '').replace(' ', '-').replace('(', '')
    s = s.replace(')', '').replace('_', '-').replace('.', '-')
    return s.lower()


BADGE = {'ok': r'\verificata', 'diff': '', 'n/d': ''}


def chapter(meta, items, verifica):
    """Costruisce il testo LaTeX di un capitolo."""
    L = []
    A = L.append
    A('%% generato automaticamente da tools/build_tex.py --- non modificare')
    A(r'\chapter{%s}' % escape_text(meta['titolo']))
    A(r'\label{cap:%s}' % slug(meta['file']))
    A(r'\quaderno{%s}{%s}{%d}' % (escape_text(meta['file']),
                                  escape_text(meta.get('data', '')),
                                  len(items)))
    A('')
    A(escape_text(meta['intro']))
    A('')

    per_idx = {it['idx']: it for it in items}
    note = {int(k): v for k, v in meta.get('note', {}).items()}
    figure = meta.get('figure', [])
    fig_dopo = {}
    for f in figure:
        fig_dopo.setdefault(f['dopo'], []).append(f)

    usati = set()
    for b in meta['blocchi']:
        A(r'\section{%s}' % escape_text(b['titolo']))
        if b.get('testo'):
            A('')
            A(escape_text(b['testo']))
            A('')
        for idx in range(b['da'], b['a'] + 1):
            it = per_idx.get(idx)
            if it is None:
                continue
            usati.add(idx)
            A(formula(it, verifica, note.get(idx)))
            for f in fig_dopo.get(idx, []):
                A(figura(f))
        if b.get('coda'):
            A('')
            A(escape_text(b['coda']))
            A('')

    restanti = [it for it in items if it['idx'] not in usati]
    if restanti:
        A(r'\section{Espressioni rimanenti}')
        for it in restanti:
            A(formula(it, verifica, note.get(it['idx'])))

    if meta.get('chiusura'):
        A(r'\section*{In sintesi}')
        A(r'\addcontentsline{toc}{section}{In sintesi}')
        A('')
        A(escape_text(meta['chiusura']))
        A('')
    return '\n'.join(L)


def formula(it, verifica, nota):
    key = it['_key']
    st = verifica.get(key, {}).get('stato', 'n/d')
    corpo = D.to_display(it['text'])
    origine = escape_text(it['origin'] or 'User')
    out = [r'\begin{espr}{%d}{%s}{%s}' % (it['idx'], origine, BADGE[st]),
           corpo,
           r'\end{espr}']
    if nota:
        out.append(escape_text(nota))
        out.append('')
    return '\n'.join(out)


def figura(f):
    """Una figura: un PDF prodotto da make_figures, oppure un disegno
    TikZ scritto a mano in tex/tikz/<nome>.tex."""
    if f.get('tikz'):
        corpo = r'  \input{tikz/%s}' % f['file']
    else:
        corpo = (r'  \includegraphics[width=%.2f\linewidth]'
                 r'{../figures/%s.pdf}') % (f.get('larghezza', 0.86),
                                            f['file'])
    return '\n'.join([
        r'\begin{figure}[htbp]',
        r'  \centering',
        corpo,
        r'  \caption{%s}' % escape_text(f['didascalia']),
        r'  \label{fig:%s}' % f['file'],
        r'\end{figure}',
    ])


def prospetto(dati, verifica, ordine, meta_per_file):
    righe = []
    tot_e = tot_v = 0
    for nome in ordine:
        f = next(x for x in dati if x['file'] == nome)
        n = len(f['items'])
        v = sum(1 for it in f['items']
                if verifica.get('%s#%d' % (nome, it['idx']),
                                {}).get('stato') == 'ok')
        tot_e += n
        tot_v += v
        data = meta_per_file[nome].get('data', '')
        righe.append(r'\texttt{%s} & %s & %d & %d & \pageref{cap:%s} \\'
                     % (escape_text(nome), escape_text(data), n, v,
                        slug(nome)))
    corpo = '\n'.join(righe)
    return '\n'.join([
        r'\begin{longtable}{@{}l l r r r@{}}',
        r'\toprule',
        r'\textbf{File} & \textbf{Data di salvataggio} & '
        r'\textbf{Espr.} & \textbf{Verif.} & \textbf{Pag.} \\',
        r'\midrule',
        r'\endfirsthead',
        r'\toprule',
        r'\textbf{File} & \textbf{Data di salvataggio} & '
        r'\textbf{Espr.} & \textbf{Verif.} & \textbf{Pag.} \\',
        r'\midrule',
        r'\endhead',
        corpo,
        r'\midrule',
        r'\textbf{Totale} & & \textbf{%d} & \textbf{%d} & \\' % (tot_e, tot_v),
        r'\bottomrule',
        r'\end{longtable}',
    ])


def main(radice):
    dati = json.load(open(os.path.join(radice, 'extracted/all.json'),
                          encoding='utf-8'))
    vpath = os.path.join(radice, 'extracted/verify.json')
    verifica = json.load(open(vpath, encoding='utf-8')) \
        if os.path.exists(vpath) else {}

    for f in dati:
        for it in f['items']:
            it['_key'] = '%s#%d' % (f['file'], it['idx'])

    per_nome = {f['file']: f for f in dati}
    gen = os.path.join(radice, 'tex', 'generato')
    if not os.path.isdir(gen):
        os.makedirs(gen)

    commenti = sorted(glob.glob(os.path.join(radice, 'commento', '*.json')))
    ordine, meta_per_file = [], {}
    inputs = []
    for c in commenti:
        meta = json.load(open(c, encoding='utf-8'))
        nome = meta['file']
        if nome not in per_nome:
            print('  ! nessun sorgente per', nome)
            continue
        f = per_nome[nome]
        meta.setdefault('data', f['header'].split(' on ')[-1])
        ordine.append(nome)
        meta_per_file[nome] = meta
        testo = chapter(meta, f['items'], verifica)
        dest = os.path.join(gen, slug(nome) + '.tex')
        io.open(dest, 'w', encoding='utf-8').write(testo + '\n')
        inputs.append(r'\input{generato/%s}' % slug(nome))
        print('  ', dest, len(f['items']), 'espressioni')

    io.open(os.path.join(gen, 'indice.tex'), 'w', encoding='utf-8') \
        .write('\n'.join(inputs) + '\n')
    io.open(os.path.join(gen, 'prospetto.tex'), 'w', encoding='utf-8') \
        .write(prospetto(dati, verifica, ordine, meta_per_file) + '\n')

    mancanti = [f['file'] for f in dati if f['file'] not in meta_per_file]
    if mancanti:
        print('  ! quaderni senza commento:', ', '.join(mancanti))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '.')
