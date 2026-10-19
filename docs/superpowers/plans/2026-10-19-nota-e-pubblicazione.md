# Nota per temi e pubblicazione su GitHub — piano di implementazione

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produrre una nota matematica breve in italiano e in inglese sui quaderni Derive, correggere l'edizione integrale, e pubblicare i tre PDF in una GitHub Release con una pagina GitHub Pages bilingue.

**Architecture:** La nota è un `article` LaTeX con un file per sezione e per lingua (`nota/it/`, `nota/en/`), compilata con `pdflatex` accanto all'edizione integrale già esistente in `tex/`. Ogni affermazione numerica è controllata da `tools/verifica_nota.py`; la coerenza fra le due lingue e fra testo e controlli da `tools/controlla_testi.py`. Un unico workflow GitHub Actions compila tutto, pubblica `site/` su Pages dal ramo `main` e allega i PDF alla release sui tag `v*`.

**Tech Stack:** Python 3.12 (numpy, matplotlib, mpmath, pymupdf, pyyaml), pdfLaTeX (TinyTeX in locale, TeX Live in CI), HTML/CSS statici con KaTeX, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-10-19-nota-e-pubblicazione-design.md` — il contenuto matematico di ogni sezione è al §3 della specifica; questo piano non lo ripete.

## Global Constraints

- Nomi dei PDF nella release: `quaderni-derive-nota.pdf` (nota, it), `derive-notebooks-note.pdf` (nota, en), `quaderni-derive-edizione-integrale.pdf` (edizione integrale).
- Link di download: `https://github.com/endjneer/quaderni-derive/releases/latest/download/<nome>.pdf`.
- Licenze: CC BY 4.0 per testi, figure e file `.dfw`; MIT per il codice.
- Riga di trasparenza, italiano: «Analisi e redazione con l'assistenza di Claude (Anthropic); ogni verifica numerica è riproducibile dal repository.» Inglese: «Analysis and writing assisted by Claude (Anthropic); every numerical check can be reproduced from the repository.»
- Nessun teorema presentato come nuovo; niente «elegante», «notevole», «sorprendente» (en: «elegant», «remarkable», «surprising») se non giustificati dall'enunciato.
- Riferimenti ai quaderni solo con le macro `\riga{factor.dfw}{4}` → `factor.dfw #4` e `\righe{gauss.dfw}{1}{5}` → `gauss.dfw #1–5`.
- Figure nuove: nome `nota_*`, nessun testo che non sia matematica; didascalie solo nel LaTeX.
- Bibliografia con `thebibliography` in `nota/bibliografia.tex`; niente biber/bibtex.
- `pdflatex` con `inputenc` utf8: lettere accentate sì, simboli matematici (≤, →, ≈, …) solo in modalità matematica; virgola decimale italiana scritta `{,}`.
- mpmath con `mp.dps = 60` di default nei controlli.
- Python 3.12 sia in `.venv/` sia in CI; dipendenze in `requirements.txt`.
- KaTeX da `cdnjs.cloudflare.com`, versione fissata.
- Commit: `git -c user.name=electroendjneer -c user.email=dayjee@outlook.com commit …`; ogni messaggio termina con
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` e
  `Claude-Session: https://claude.ai/code/session_01AKhZZ6sz4EbfbENCnSMvAr`.
- Niente push, merge, tag o cambio di visibilità senza conferma esplicita dell'autore.
- Niente `sudo`: TinyTeX in `~/.TinyTeX`, `uv` in `~/.local/bin`, ambiente in `.venv/`.
- Non modificare `source/*.dfw` né `extracted/all.json`.
- Lingua del codice: nomi, commenti e messaggi in italiano, come in `tools/`.
- `$SCRATCH` nei comandi indica una cartella temporanea fuori dal repository (lo scratchpad della sessione).

## Review Focus

1. **Le due lingue divergono** (un numero, un'etichetta, una citazione o un riferimento a una riga presente in una sola versione): l'autore si aspetta due versioni equivalenti. → Controlli di coppia in `controlla_testi.py`, Task 2.
2. **Un numero nel testo che nessun controllo verifica**: il lettore si aspetta che ogni decimale citato sia stato calcolato. → Ogni decimale con almeno tre cifre dopo la virgola deve essere registrato con `cita()`, Task 2.
3. **Pacchetti LaTeX presenti in TinyTeX ma assenti in CI**: la build locale passa, quella in CI fallisce. → Un'unica lista `tex/pacchetti-texlive.txt` usata da entrambe (Task 1, Task 14); il primo giro della CI sul branch è il test (Task 14).
4. **Link di download che non corrispondono agli asset** (nome sbagliato, 404 prima della prima release): il lettore clicca e non scarica niente. → `controlla_sito.py` confronta gli URL esatti (Task 13); `make dist` produce esattamente quei nomi (Task 1); controllo con `curl` dopo il tag (Task 15).
5. **PDF con font bitmap Type 3 o senza titolo nei metadati**: sullo schermo appaiono sgranati, e l'anteprima del link non ha titolo. → `controlla_pdf.py` su tutti e tre i PDF a ogni build (Task 1).

---

### Task 1: Ambiente locale e infrastruttura di compilazione

**Files:**
- Create: `requirements.txt`, `tex/pacchetti-texlive.txt`, `tools/controlla_pdf.py`, `nota/preambolo-nota.tex`, `nota/nota-it.tex`, `nota/note-en.tex`, uno scheletro per ogni sezione in `nota/it/` e `nota/en/` (nomi sotto)
- Modify: `Makefile`, `.gitignore`
- Untrack: `tex/derive2010.pdf`

**Interfaces:**
- Produces:
  - `make all` → `make dist`; `make pdf` (edizione integrale), `make nota` (i due PDF della nota), `make verifica-nota` (nel Task 1 un bersaglio vuoto che stampa un messaggio; il Task 2 lo riempie), `make controlli`, `make dist` (copia i tre PDF in `dist/` con i nomi della release), `make pulisci`.
  - `PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python)`, `LATEX ?= pdflatex`.
  - `python tools/controlla_pdf.py PDF [--log LOG] [--pagine MIN MAX]` → codice 1 se: un font è Type 3; il titolo nei metadati è vuoto; il numero di pagine è fuori da [MIN, MAX]; nel log c'è una riga che comincia con `!`, oppure `undefined` in un avviso di riferimento o citazione, oppure `There were undefined references`. Stampa una riga `ok …` o `NO …` per controllo.
  - Coppie di file di sezione (prefisso → it / en): `00-abstract`/`00-abstract`, `01-introduzione`/`01-introduction`, `02-semiangolo`/`02-half-angle`, `03-fattoriali`/`03-factorials`, `04-media`/`04-mean`, `05-cosinc`/`05-cosinc`, `06-gradini`/`06-steps`, `07-e`/`07-e`, `08-delta`/`08-delta`, `09-in-breve`/`09-in-brief`, `10-refusi`/`10-typos`, `A-recupero`/`A-recovery`, `Z-colofone`/`Z-colophon`.
  - Etichette (uguali nelle due lingue): `sec:intro`, `sec:semiangolo`, `sec:fattoriali`, `sec:media`, `sec:cosinc`, `sec:gradini`, `sec:e`, `sec:delta`, `sec:breve`, `sec:refusi`, `app:recupero`; figure `fig:nota_<nome>`; enunciati `prop:<tema>`, `lemma:<tema>`.
  - Macro del preambolo: `\riga{file}{n}`, `\righe{file}{a}{b}`; ambienti `prop`, `lemma`, `oss` con nomi presi da `\nomeprop`, `\nomelemma`, `\nomeoss`, definiti dal file principale di ciascuna lingua; `\graphicspath{{../figures/}}`; stessa palette di `tex/preambolo.tex`.

- [ ] **Step 1: Installare gli strumenti nella home**

`uv`: `curl -LsSf https://astral.sh/uv/install.sh | sh`. Ambiente: `uv venv .venv --python 3.12 && uv pip install --python .venv/bin/python -r requirements.txt`, con `requirements.txt` = `numpy`, `matplotlib`, `mpmath`, `pymupdf`, `pyyaml`. TinyTeX: script ufficiale `install-bin-unix.sh`; `PATH="$HOME/.TinyTeX/bin/x86_64-linux:$PATH"`; `tlmgr install $(grep -v '^#' tex/pacchetti-texlive.txt)`. La lista contiene un pacchetto per riga (nomi CTAN/TeX Live) per tutto ciò che `tex/preambolo.tex` e `nota/preambolo-nota.tex` caricano oltre `scheme-basic`, e si completa al passo 4 aggiungendo ogni pacchetto che il log segnala come mancante.
Verifica: `.venv/bin/python -c "import numpy, matplotlib, mpmath, pymupdf, yaml"` e `pdflatex --version` escono con codice 0.

- [ ] **Step 2: Scrivere `tools/controlla_pdf.py` e provarlo su un log falso**

Run: `printf '! Undefined control sequence.\n' > $SCRATCH/finto.log && .venv/bin/python tools/controlla_pdf.py tex/derive2010.pdf --log $SCRATCH/finto.log; echo $?`
Expected: una riga `NO log: …` e codice `1`. Lo stesso comando senza `--log` e con `--pagine 200 300` → codice `0` (il PDF attuale ha 232 pagine).

- [ ] **Step 3: Scheletro della nota**

`nota-it.tex`/`note-en.tex`: `article` 11pt A4, `babel` (`italian`/`english`), definizione di `\nomeprop` ecc., `\input{preambolo-nota}`, `\hypersetup{pdftitle=…, pdfauthor={Francesco Messina}, pdflang=it|en}`. Titoli dalla specifica §3: «I quaderni Derive, 2009–2011: osservazioni da un taccuino di calcolo simbolico» / «The Derive Notebooks, 2009–2011: Observations from a Computer-Algebra Scratchpad». Data «Ottobre 2026» / «October 2026». Ordine: abstract (00), sezioni 01–10, `\appendix` A, `\input{bibliografia}` (per ora un `thebibliography` vuoto con una voce segnaposto che il Task 3 sostituisce), colofone Z. Ogni file di sezione contiene per ora solo `\section{…}` e `\label{…}`.

- [ ] **Step 4: Makefile, `.gitignore`, PDF fuori dal versionamento**

Il bersaglio `pdf` mantiene i tre passaggi di `pdflatex` ma con `-halt-on-error`, così un errore ferma `make`; `nota` compila i due file principali dentro `nota/`, con tre passaggi ciascuno. `controlli` lancia `controlla_pdf.py` con `--log` su: edizione integrale `--pagine 200 300`, nota it ed en `--pagine 1 40` (al Task 15 diventa `--pagine 15 40`). `dist` copia i tre PDF con i nomi delle Global Constraints. `.gitignore`: `tex/derive2010.pdf`, `nota/*.pdf`, i prodotti intermedi in `nota/`, `dist/`, `.venv/`. Poi `git rm --cached tex/derive2010.pdf`.

- [ ] **Step 5: Verificare la build completa**

Run: `make all`
Expected: codice 0; `dist/` contiene i tre PDF con i nomi esatti; ogni riga di `controlla_pdf.py` dice `ok`.

- [ ] **Step 6: Commit**

`git add` dei file del task e della rimozione di `tex/derive2010.pdf`; messaggio: «Infrastruttura di compilazione per la nota e controlli sui PDF».

---

### Task 2: Verifica numerica, coerenza fra le lingue e §10 «Due refusi e una trappola»

**Files:**
- Create: `tools/verifica_nota.py`, `tools/controlla_testi.py`
- Modify: `Makefile` (bersaglio `verifica-nota`), `nota/it/10-refusi.tex`, `nota/en/10-typos.tex`

**Interfaces:**
- Produces, in `tools/verifica_nota.py`:
  - `controllo(sezione: str)` — decoratore che registra la funzione in `REGISTRO: list[tuple[str, str, Callable[[], None]]]` (sezione, nome = docstring o nome della funzione, funzione). La funzione fallisce sollevando `AssertionError` con un messaggio leggibile.
  - `cita(chiave: str, it: str, en: str) -> None` — registra in `VALORI_CITATI: dict[str, tuple[str, str]]` la forma tipografica esatta di un valore come compare nel `.tex` (`"1{,}2459"` / `"1.2459"`). Si chiama a livello di modulo, accanto ai controlli che verificano quel valore.
  - `vicini(a, b, rel=mp.mpf('1e-40')) -> bool`.
  - `main(argv: list[str]) -> int` — esegue i controlli registrati e stampa `  ok   §N nome` oppure `  NO   §N nome: messaggio`, poi `N controlli, M falliti`; restituisce 1 se M > 0. `--sezione §N` esegue solo quella sezione; `--valori` stampa `VALORI_CITATI` in JSON ed esce.
- Produces, in `tools/controlla_testi.py` (`main() -> int`, codice 1 se un controllo fallisce):
  1. per ogni prefisso della tabella del Task 1 esistono entrambi i file;
  2. per ogni coppia, l'insieme delle `\label{…}`, delle chiavi `\cite{…}` e dei riferimenti `\riga`/`\righe` è identico;
  3. ogni stringa italiana di `VALORI_CITATI` compare in almeno un file `nota/it/*.tex` e ogni stringa inglese in almeno un file `nota/en/*.tex`;
  4. ogni decimale con almeno tre cifre dopo la virgola (italiano: `\d+\{,\}\d{3,}`, inglese: `\d+\.\d{3,}`, fuori dai commenti `%`) è una stringa registrata in `VALORI_CITATI`;
  5. le parole vietate dalle Global Constraints vengono stampate come avviso, senza far fallire il controllo.
- `make verifica-nota` = `verifica_nota.py` seguito da `controlla_testi.py`; `make nota` dipende da `verifica-nota`.

- [ ] **Step 1: Scrivere i controlli del §10 prima del testo**

```python
@controllo('§10')
def teoria_13():
    """teoria #13: con 5 al posto di 10 la riga segue la legge; lo scarto vale 35ε/n³"""
    # legge: ε[(1+x)^7 - 1 - x^7] con x = 1/n; riga #13: 7ε(n^5+3n^4+10n^3+5n^2+3n+1)/n^6
    # verificare con Fraction per n = 2..20 che legge - riga(10→5) == 0 e riga(10) - legge == 35/n^3 (ε = 1)

@controllo('§10')
def factor_5():
    """factor #5: 1!3!5!7!9! - 15! = 2^11·3^6·5^3·7^2, non 7^3"""
    assert prod(factorial(k) for k in (1,3,5,7,9)) - factorial(15) == 2**11*3**6*5**3*7**2

@controllo('§10')
def mate_identita():
    """mate #21: il primo membro vale 1/2 per ogni k: k = -4.999999701 non è una soluzione ma un punto qualunque"""
    # valutare (cos(x+ky)^2-cos(x-ky)^2)/(cos(2x+2ky)-cos(2x-2ky)) in 5 terne (x, y, k) casuali, tutte == 1/2
cita('mate_k', '-4{,}999999701', '-4.999999701')
```

- [ ] **Step 2: Far vedere che i controlli di coerenza falliscono**

Run: `.venv/bin/python tools/verifica_nota.py && .venv/bin/python tools/controlla_testi.py; echo $?`
Expected: `verifica_nota.py` dice `3 controlli, 0 falliti`; `controlla_testi.py` fallisce sul punto 3 (manca `-4{,}999999701`, perché il §10 non è ancora scritto) con codice 1.

- [ ] **Step 3: Scrivere il §10 nelle due lingue** (contenuto: specifica §3, «§10»)

- [ ] **Step 4: Verificare**

Run: `make verifica-nota nota`
Expected: codice 0. Poi `.venv/bin/python tools/pdfpage.py nota/nota-it.pdf $SCRATCH/it <pagine del §10>` (e lo stesso per en): leggere i PNG e controllare impaginazione e formule.

- [ ] **Step 5: Commit** — «Verifica numerica della nota e controlli di coerenza fra le lingue; §10»

---

### Task 3: Bibliografia verificata

**Files:**
- Create: `nota/bibliografia.tex` (sostituisce il segnaposto)

**Interfaces:**
- Produces: chiavi `\bibitem` che i task successivi citano. Elenco candidato (si tolgono quelle non verificabili): `guy2004` (Guy, *Unsolved Problems in Number Theory*, 3ª ed., B23), `eulero1744` (*De fractionibus continuis dissertatio*, E71), `lambert1768`, `gelfand1964` (Gel'fand–Šilov, *Generalized Functions*), `kaneko1988` (*Introduction to Hyperfunctions*), `john1955` (*Plane Waves and Spherical Means*), `courant1962` (Courant–Hilbert vol. II), `king2009` (*Hilbert Transforms*), `litvinov2007` (*Maslov dequantization, idempotent and tropical mathematics*), `borwein2008` (*Mathematics by Experiment*), `oppenheim2010` (*Discrete-Time Signal Processing*), `baker1996` (*Padé Approximants*).

- [ ] **Step 1: Verificare ogni voce** — con la ricerca web, confermare autore, titolo, editore o rivista, anno, edizione, e la sezione o il capitolo dove la nota la cita. Ogni `\bibitem` porta sopra un commento `% verificato: <URL della fonte>`. Una voce non confermata non entra; il task che l'avrebbe citata riformula o dimostra l'affermazione.
- [ ] **Step 2: Verificare** — `make nota`: codice 0. Le voci compaiono nel PDF solo se citate, quindi temporaneamente `\nocite{*}` nel file principale, controllo visivo della pagina della bibliografia, poi rimozione di `\nocite{*}`.
- [ ] **Step 3: Commit** — «Bibliografia della nota, ogni voce verificata»

---

### Tasks 4–10: le sezioni tematiche

Ogni task di sezione segue gli stessi passi; cambiano i controlli, la figura e il contenuto.

- [ ] **Step 1:** aggiungere a `tools/verifica_nota.py` i controlli della sezione (elencati per task), con `cita()` per ogni valore che il testo riporterà.
- [ ] **Step 2:** `.venv/bin/python tools/verifica_nota.py --sezione §N` → tutti `ok`. Un controllo che fallisce va capito prima di scrivere il testo: se l'affermazione della specifica è sbagliata, correggere la specifica (e dirlo all'autore), non il controllo.
- [ ] **Step 3:** se il task prevede una figura, scrivere `fig_nota_<nome>()` in `tools/make_figures.py` con gli helper `nuova()`/`salva()`, nessun `set_title`, legende ed etichette solo matematiche, e aggiungerla alla lista `FIGURE`.
- [ ] **Step 4:** scrivere la sezione in `nota/it/` e poi in `nota/en/`, secondo la specifica §3. L'inglese è prosa matematica naturale, non una traduzione parola per parola, ma con le stesse affermazioni, numeri, etichette, citazioni e riferimenti.
- [ ] **Step 5:** `make verifica-nota nota` → codice 0; rendere in PNG le pagine della sezione (entrambe le lingue) con `tools/pdfpage.py`, leggerle e controllare formule, figura e a capo.
- [ ] **Step 6:** commit — «Nota, §N: <titolo>».

### Task 4: §2 «L'esponenziale e la tangente del semiangolo»

**Files:** `nota/it/02-semiangolo.tex`, `nota/en/02-half-angle.tex`, `tools/verifica_nota.py`, `tools/make_figures.py` (`fig_nota_semiangolo`) · lunghezza 4–5 pagine
**Interfaces:** Consumes: chiavi `eulero1744`, `lambert1768`, `baker1996`, `oppenheim2010` (se verificate). Produces: `\label{prop:semiangolo}`, `fig:nota_semiangolo`.

Controlli (`§2`):
- `exp(1j*t) == (1+1j*u)/(1-1j*u) == (1+1j*u)**2/(1+u**2)` con `u = tan(t/2)`, per t ∈ {0.3, 1, 2.5, −2.9}.
- `exp(t) == (1+τ)/(1−τ)` e `t == log((1+τ)/(1−τ))` con `τ = tanh(t/2)`, per t ∈ {0.5, 1, 3, −2, 10}; `e == (1+tanh(1/2))/(1−tanh(1/2))`.
- `atan #2`: `exp(1j*atan(1j*x)) == sqrt((1−x)/(1+x))` per x ∈ {0.2, 0.7, −0.5}; `gauss #5`: `exp(−x²) == (1−tanh(x²/2))/(1+tanh(x²/2))`.
- gudermanniana `gd(x) = 2*atan(tanh(x/2))`: `tan(gd x) == sinh x`, `sin(gd x) == tanh x`, `cos(gd x) == sech x`, `atan(tanh x) == gd(2x)/2`, per x ∈ {0.3, 1.2, −2}.
- frazione continua di `(e−1)/(e+1)` con `mp.workdps(200)`: i primi 20 quozienti sono `[0] + [4k−2 for k in 1..19]`; di `tanh(1/3)`: i primi 10 sono `[0, 3, 9, 15, …]`.
- con `Fraction`, in 6 valori razionali di t: `(1+τ₂)/(1−τ₂) == (12+6t+t²)/(12−6t+t²)` dove `τ₂ = (t/2)/(1+(t/2)²/3)`; errore di [1/1] diviso t³ ed errore di [2/2] diviso t⁵ convergono (rapporti a t = 1e−3 e 1e−4 uguali entro 1e−3).
- bilineare: con T = 1 e z = e^{iω}, `(z−1)/(z+1) == 1j*tan(ω/2)` per ω ∈ {0.4, 1.5, 3}.
- `cita('tanh_mezzo', '0{,}46211715', '0.46211715')`.

Figura `nota_semiangolo`: (a) cerchio unitario con i punti (1+iu)/(1−iu) per u ∈ {−3, −2.5, …, 3}; (b) |errore relativo| di [1/1], [2/2], [3/3] rispetto a e^t per t ∈ [−3, 3], scala logaritmica.

### Task 5: §3 «Una catena di fattoriali che si spezza»

**Files:** `nota/it/03-fattoriali.tex`, `nota/en/03-factorials.tex`, `tools/verifica_nota.py`, `tools/make_figures.py` (`fig_nota_fattoriali`) · 3–4 pagine
**Interfaces:** Consumes: `guy2004`. Produces: `\label{prop:fattoriali}`, `fig:nota_fattoriali`.

Controlli (`§3`), tutti esatti con interi o `Fraction` salvo dove indicato:
- `P(p) == factorial(T(p+1))` per p = 0..3, e diverso per p = 4; `1!·3! == 3!`, `3!·5! == 6!`, `6!·7! == 10!`.
- `11*12*13*14*15 == 360360`, `factorial(9) == 362880`, `a(4) == Fraction(360360, 362880)`.
- `a(p) < 1` per 4 ≤ p ≤ 100, e il massimo è `a(4)`.
- `(p+1)**2 / (T(p)+1) <= 2 + Fraction(2, p)` per 1 ≤ p ≤ 10⁵.
- identità polinomiale `(2p+5)(2p²+5p+3) − (p²+5p+6)(4p+5) == −5p² − 18p − 15` in 50 interi.
- `g(100) == Fraction(10506, 82012)`; `exp(mpf('2.02')) * g(100) < mpf('0.966')` (mp); `R(p) <= B(p)` per 100 ≤ p ≤ 300 (con R esatto, B in mp).
- `P(p) − factorial(T(p+1)) > 0` per 4 ≤ p ≤ 30.
- `cita` per `0{,}99306`, `0{,}12810`, `0{,}966` (e le forme inglesi).

Dove `T(m) = m(m+1)/2`, `P(p) = ∏_{k=0}^{p}(2k+1)!`, `a(p) = ∏_{j=1}^{p+1}(T(p)+j) / (2p+1)!`, `g(p) = (p+2)(p+3)/(4(p+1)(2p+3))`, `B(p) = exp((p+1)²/(T(p)+1))·g(p)`, `R(p) = a(p+1)/a(p)`.

Figura `nota_fattoriali`: a_p per 1 ≤ p ≤ 60 (punti), con la retta a_p = 1; scala logaritmica in ordinata.

### Task 6: §4 «La media e il punto medio»

**Files:** `nota/it/04-media.tex`, `nota/en/04-mean.tex`, `tools/verifica_nota.py` · 2 pagine, nessuna figura
**Interfaces:** Consumes: `john1955` e/o `courant1962`. Produces: `\label{prop:media}`.

Controlli (`§4`):
- media su [c−h, c+h] con `mp.quad` == `f(c)·sinh(μh)/(μh)` per: f ∈ {sin, cos, x ↦ cos x + 2 sin x, x ↦ e^{ix}} con μ = i; f ∈ {exp, cosh} con μ = 1; f = x ↦ e^{2x} con μ = 2; (c, h) ∈ {(0.7, 0.4), (−1.3, 2.1)}.
- righe `Trasformata T #3–#7`: T[f](t) per t = 1.7 coincide con il secondo membro scritto nel quaderno.
- `T[x^n](1.7) == 2^n/(n+1)` per n = 0..6.
- Bessel: `gamma(3/2)·(2/(kr))^{1/2}·besselj(1/2, kr) == sin(kr)/(kr)` e `gamma(1/2)·(2/(kr))^{−1/2}·besselj(−1/2, kr) == cos(kr)` per kr ∈ {0.5, 2, 7.3}; media sferica in ℝ³ di e^{ik·x}: `quad(lambda θ: exp(1j*k*r*cos θ)*sin θ/2, [0, π]) == sin(kr)/(kr)`.

### Task 7: §5 «Il seno cardinale e il suo gemello»

**Files:** `nota/it/05-cosinc.tex`, `nota/en/05-cosinc.tex`, `tools/verifica_nota.py`, `tools/make_figures.py` (`fig_nota_cosinc`) · 2 pagine
**Interfaces:** Consumes: `king2009`. Produces: `fig:nota_cosinc`.

Convenzione da scrivere nel testo: `Hf(x) = (1/π) p.v. ∫ f(t)/(x−t) dt`. Con questa vale H[sinc] = (1 − cos πx)/(πx), quindi la parte reale di ((−1)^x − 1)/(πx) è −H[sinc] e sinc + iH[sinc] = ∫₀¹ e^{iπxs} ds.

Controlli (`§5`):
- `(power(-1, x) − 1)/(π x) == 1j*quad(lambda s: exp(1j*π*x*s), [0, 1])` per x ∈ {0.3, 1.7, −2.2}; parte immaginaria == `sin(πx)/(πx)`, parte reale == `(cos πx − 1)/(πx)`.
- `(1/π)·quadosc(lambda t: (sinc(x−t) − sinc(x+t))/t, [0, inf], period=2) == (1 − cos πx)/(πx)` per x ∈ {0.3, 1.7}, entro 1e−10.
- I(X) = ∫₀^X (1 − cos πx)/(πx) dx: `|(I(2000) − ln(2000)/π) − (I(1000) − ln(1000)/π)| < 1e−3` e `I(10⁴) > 2.5`.
- `cita` per il valore 11,534 di `cosinc #20`, se il testo lo riporta.

Figura `nota_cosinc`: sin(πx)/(πx) e (1 − cos πx)/(πx) per x ∈ [−6, 6].

### Task 8: §6 «Gradini fatti di logaritmi»

**Files:** `nota/it/06-gradini.tex`, `nota/en/06-steps.tex`, `tools/verifica_nota.py` · 2–3 pagine, nessuna figura nuova
**Interfaces:** Consumes: `litvinov2007`. Produces: `\label{lemma:massimo}`.

Prima di scrivere: rileggere `mate #77–84`, `mate copia` (la sezione su ln cosh) e `u(0)-sign(0)` in `extracted/all.json` e nei relativi `commento/*.json`, per collegare ciascun candidato di u(0) alla famiglia da cui proviene, dove è ricostruibile.

Controlli (`§6`):
- `(abs(a−b) + abs(a+b))/2 == max(abs(a), abs(b))` per 10 coppie reali (segni misti).
- `log((abs(exp(x)−1) + abs(exp(x)+1))/2) == max(x, 0)` per x ∈ {−3, −0.2, 0.1, 4}.
- `log(cosh x) == abs(x) − log 2 + log(1 + exp(−2 abs(x)))` per x ∈ {−5, −0.3, 0.7, 6}.
- `h·log(exp(a/h) + exp(b/h)) − max(a, b)` è compreso fra 0 e `h·log 2` per h = 1e−3 e tre coppie (a, b).
- i sei valori di `u(0)-sign(0) #2–#12` coincidono, entro 1e−9, con le forme chiuse del testo (ln(e−1), ln sinh 1, …), e #11 = 2·#9 esattamente; `cita` per ognuno di quelli riportati.

### Task 9: §7 «Due successioni per e»

**Files:** `nota/it/07-e.tex`, `nota/en/07-e.tex`, `tools/verifica_nota.py`, `tools/make_figures.py` (`fig_nota_e_errori`) · 2 pagine
**Interfaces:** Produces: `\label{prop:e}`, `fig:nota_e_errori`.

Controlli (`§7`), con n = 10⁷ salvo dove indicato:
- `(1+1/n)^n − e` arrotondato a 6 cifre significative == `−1.35914e−7`; `(Σ_{k=0}^{n} n^{−k})^n − e` == `+1.35914e−7` (la somma in forma chiusa `(1 − n^{−n−1})/(1 − 1/n)`); media − e == `1.2459e−14` (5 cifre) e `vicini(media − e, 11e/(24n²), rel=1e−6)`.
- `|n²·((1+1/n)^n/e − 1 + 1/(2n)) − 11/24| < 1e−8` per n = 10⁹; lo stesso con (1−1/n)^{−n} e + 1/(2n).
- `n⁴·(media/e − 1 − 11/(24n²))` a n = 10⁶ e 10⁷ differisce di meno dell'1%: il termine successivo è O(n⁻⁴).
- `(1 − n^{−n−1})^n` dista da 1 meno di 1e−50 per n = 100.
- `e #88–#93`: `(1 + iπ/x)^x` a x = 10⁸ dista da −1 meno di 1e−7.
- `cita` per `1{,}35914`, `1{,}2459` e le forme inglesi.

Figura `nota_e_errori`: |errore| delle due successioni e della media per n da 10 a 10⁸ (mpmath, 60 cifre), scala bilogaritmica; tre serie, pendenze −1, −1, −2.

### Task 10: §8 «Una delta di Dirac fuori dall'asse reale»

**Files:** `nota/it/08-delta.tex`, `nota/en/08-delta.tex`, `tools/verifica_nota.py` · 3 pagine, nessuna figura nuova
**Interfaces:** Consumes: `gelfand1964`, `kaneko1988`; `\ref{sec:semiangolo}` per `delta #41–44`.

Il tono è quello della specifica: una domanda, non un risultato.

Controlli (`§8`), con `dn(z, n) = (1/4)·((1+2nz)/abs(z+1/(2n)) + (1−2nz)/abs(z−1/(2n)))` e `d(z) = z·im(z)/(2j·abs(z)**3)`:
- x reale: `dn(x, n) == n` per |x| < 1/(2n), `== 0` per |x| > 1/(2n) (n = 10, 1000; tre punti per lato).
- `vicini(dn(z, 10**12), d(z), rel=1e−9)` per z ∈ {0.3+0.4j, −1+2j, 2−0.5j}.
- `½·diff(lambda x: (x+1j*y)/abs(x+1j*y), x0) == d(x0+1j*y)` negli stessi punti.
- `d(a·z) == d(z)/abs(a)` per a ∈ {2, −3, 0.5}.
- lorentziana `ε/(π(z²+ε²))` con ε = 1e−8: modulo < 1e−6 negli stessi z.
- gaussiana `exp(−z²/ε²)/(ε√π)` con ε = 0.1: modulo > 1e10 in z = 0.3+0.5j, < 1e−10 in z = 0.5+0.3j.
- `delta #22` == `−1j·d(ω+1j*k)` e `abs(d(ω+1j)) == 1/(2(ω²+1))` per ω ∈ {0, 0.7, −2}, k ∈ {1, 2}.

---

### Task 11: Abstract, introduzione, §9 «In breve», appendice, colofone

**Files:** `nota/it/00-abstract.tex`, `01-introduzione.tex`, `09-in-breve.tex`, `A-recupero.tex`, `Z-colofone.tex` e le cinque controparti in `nota/en/`; `tools/verifica_nota.py`

**Interfaces:** Consumes: tutte le etichette `sec:*` (l'introduzione rimanda a ogni sezione), `borwein2008`.

Contenuti dalla specifica §3. Il colofone contiene autore, data, URL del repository, licenza CC BY 4.0 e la riga di trasparenza esatta delle Global Constraints. L'appendice si basa su `tex/parte1-recupero.tex` e la condensa in 1–2 pagine.

Controlli (`§9`), uno per voce della tabella con un valore:
- `pi − e·log(pi)` e il suo seno iperbolico, alle cifre citate.
- `(π^x + e^x)^{1/x}` a x = 200 dista da π meno di 1e−60; a x = −200 dista da e meno di 1e−60.
- `∏_{n=1}^{k−1}(1/n − 1/k) == Fraction(1, k**(k−1))` per k = 2..12, e i valori di `fattorazionale #2–#12`.
- `Σ 1/p_k#` sui primi 25 primi == `0.70523017179180096514` (20 cifre).
- `quadosc((cos t² + sin t²)/2, [−inf, inf]) == sqrt(pi/2)` (ω = 1).
- `(√2/2)(1/2 + x²) − |x| >= 0` su una griglia, con uguaglianza in |x| = 1/√2.
- `sin(x)^(1/log(1/sin x)) == 1/e` per x ∈ {0.3, 1, 2}.
- radici di (x+1)² = 2ε: distanza `2·sqrt(2ε)` per ε ∈ {1e−2, 1e−6}.
- `teoria2`: il punto x = k(√5 − 1)/4 sta sia su y = (2/k)x² sia su y = −x + k/2 (k = 1, 3); `a = 2^{(n−1)²}k^{1−n}` fa passare y = a xⁿ per (k/2^{n−1}, k/2^{n−1}), per n = 2..6.
- `cita` per ogni valore riportato.

Passi come nei Task 4–10. Il commit è «Nota: abstract, introduzione, §9, appendice, colofone».

---

### Task 12: Correzioni all'edizione integrale

**Files:** `commento/04-e.json`, `commento/15-delta.json`, `commento/18-factor.json`, `commento/10-mate.json`, `commento/14-gauss.json`, `commento/08-atan.json`, `commento/12-cosinc.json`, `commento/16-trasformata-t.json`, `commento/05-pigreco.json`, `tools/make_figures.py` (`fig_e_convergenza`), `tex/derive2010.tex`

Le correzioni sono quelle della tabella al §5 della specifica. Si modificano solo i campi interessati (`intro`, `blocchi[i].testo`/`coda`, `note`, `chiusura`), lasciando intatto il resto del file. I fatti da riportare sono gli stessi già verificati nei Task 4–10.

- [ ] **Step 1: Scrivere i controlli che ora falliscono** — in `tools/controlla_testi.py` una funzione `controlla_edizione_integrale()`, inclusa nel `main`. Per ogni file si cerca nel testo decodificato (`json.load`, poi tutte le stringhe concatenate), quindi le sottostringhe sotto sono LaTeX con una sola barra rovesciata:
  - `04-e.json`: non contiene «converge molto più in fretta»; contiene `\frac{11\mathrm{e}}{24n^2}`;
  - `15-delta.json`: non contiene «l'idea più originale» né «valore numerico concreto»; contiene «lorentziana», «gaussiana» e «iperfunzioni»;
  - `18-factor.json`: contiene «Surányi» e `360\,360`;
  - `10-mate.json`: contiene «gudermanniana» e «vale solo per $n=2$ e $n=3$»;
  - `14-gauss.json`: non contiene «vale da solo il capitolo»; contiene «semiangolo»;
  - `08-atan.json`: contiene «semiangolo»;
  - `12-cosinc.json`: contiene «Hilbert»;
  - `16-trasformata-t.json`: contiene «Helmholtz»;
  - `05-pigreco.json`: non contiene «molto elegante»;
  - `tex/derive2010.tex`: contiene «edizione integrale».

  Run: `.venv/bin/python tools/controlla_testi.py` → fallisce sui punti dell'edizione integrale.
- [ ] **Step 2: Modificare i JSON**, aggiungere in apertura di `tex/derive2010.tex` la nota «edizione integrale; i risultati sono nella nota a parte», e rifare `fig_e_convergenza` in mpmath con la curva della media (titolo interno in italiano, come le altre figure dell'edizione integrale).
- [ ] **Step 3: Verificare** — `make all` → codice 0, `controlla_testi.py` → ok. Rendere in PNG le pagine dei capitoli e, delta, factor, mate, gauss, atan, cosinc, Trasformata T, pigreco nei punti toccati, leggerle e controllare che i caratteri `&`, `%` e `$` siano stati protetti da `build_tex.py`.
- [ ] **Step 4: Commit** — «Edizione integrale: correzioni dopo la revisione matematica»

---

### Task 13: Pagina web

**Files:**
- Create: `site/index.html`, `site/en/index.html`, `site/stile.css`, `tools/controlla_sito.py`

**Interfaces:**
- Consumes: i nomi dei PDF e il formato degli URL dalle Global Constraints; i titoli e l'abstract dai file `nota/*/00-abstract.tex`.
- Produces: `python tools/controlla_sito.py` → codice 1 se un controllo fallisce.

- [ ] **Step 1: Scrivere `controlla_sito.py` e vederlo fallire** (le pagine non esistono). Con `html.parser`, per ciascuna pagina:
  - `<html lang>` vale `it` o `en`;
  - esistono esattamente tre link di download, uguali agli URL delle Global Constraints;
  - c'è un link all'altra lingua e uno al repository;
  - ogni `href` o `src` relativo punta a un file esistente in `site/`;
  - gli script e i fogli di KaTeX vengono da `cdnjs.cloudflare.com/ajax/libs/KaTeX/<versione>/`, con la stessa versione;
  - sono presenti i meta `og:title`, `og:description`, `og:url` (`https://endjneer.github.io/quaderni-derive/` e `…/en/`);
  - c'è la riga di trasparenza nella lingua giusta.
- [ ] **Step 2: Scrivere le pagine** — contenuti come al §7 della specifica: titolo, autore, abstract; i sette temi in due righe ciascuno, con una formula in KaTeX; i tre pulsanti; il colofone. La versione di KaTeX va scelta fra quelle pubblicate su cdnjs da almeno due settimane, controllando con `curl -I` che gli URL rispondano 200. Il CSS ha la palette di `tex/preambolo.tex`, una larghezza massima di circa 42rem, margini laterali di 16px e niente scorrimento orizzontale sotto i 400px; gestisce anche il tema scuro.
- [ ] **Step 3: Verificare** — `controlla_sito.py` → ok; `.venv/bin/python -m http.server -d site` e `curl` di `/` e `/en/` → 200. Per la resa a larghezza di telefono provare Chromium senza interfaccia via `uv pip install playwright && .venv/bin/playwright install chromium`, poi screenshot a 375px e 1280px da leggere. Se Chromium non parte per librerie di sistema mancanti, dirlo all'autore e rimandare il controllo al Task 15, sul telefono.
- [ ] **Step 4: Commit** — «Pagina di presentazione bilingue»

---

### Task 14: Licenze, README, workflow

**Files:**
- Create: `LICENSE` (MIT, titolare Francesco Messina, 2026, con un paragrafo finale che rimanda a `LICENSE-CC-BY-4.0` per testi, figure e file `.dfw`), `LICENSE-CC-BY-4.0` (testo legale ufficiale, scaricato da creativecommons.org), `.github/workflows/pubblica.yml`
- Modify: `README.md` (prodotti, link alla pagina e alle release, pipeline aggiornata con la nota, verifica, licenze), `build.ps1` (compila anche la nota e lancia `verifica_nota.py`/`controlla_testi.py`, come `make`)

**Interfaces:**
- Consumes: `make dist` (Task 1), `requirements.txt`, `tex/pacchetti-texlive.txt`, `site/`.

- [ ] **Step 1: Scrivere il workflow**, come al §8 della specifica.
  - Eventi: `push` su `main` e tag `v*`, `pull_request`, `workflow_dispatch`.
  - Job `build`: checkout; setup-python 3.12 con cache pip; `pip install -r requirements.txt`; installazione di TeX Live con la lista `tex/pacchetti-texlive.txt` (scegliere un'action mantenuta che accetti una lista di pacchetti, verificandone versione e documentazione); `make dist`; `upload-artifact` di `dist/*.pdf`; solo su `main`, `actions/upload-pages-artifact` di `site/`.
  - Job `pages`: `needs: build`, `if: github.ref == 'refs/heads/main'`, `environment: github-pages`, permessi `pages: write` e `id-token: write`, `actions/deploy-pages`.
  - Job `release`: `needs: build`, `if: startsWith(github.ref, 'refs/tags/v')`, permesso `contents: write`; scarica l'artifact e crea la release con i tre PDF e un testo breve bilingue.
  - Permessi di default `contents: read`. Versioni delle action fissate all'ultima versione maggiore, controllata al momento.
- [ ] **Step 2: Controllo statico** — `.venv/bin/python -c "import yaml; d=yaml.safe_load(open('.github/workflows/pubblica.yml')); assert set(d['jobs']) == {'build','pages','release'}"` → codice 0; rilettura dei nomi dei file in `release` contro le Global Constraints.
- [ ] **Step 3: Commit** — «Licenze, README e workflow di pubblicazione»
- [ ] **Step 4: Primo giro della CI sul branch (con conferma)** — chiedere all'autore il permesso di fare push di `nota-e-pubblicazione`. Dopo il push:
  - se il repository è già pubblico, seguire il run con `curl https://api.github.com/repos/endjneer/quaderni-derive/actions/runs?branch=nota-e-pubblicazione`;
  - altrimenti chiedere all'autore l'esito dalla scheda Actions.

  Atteso: `build` verde, `pages` e `release` saltati. Se `build` fallisce per un pacchetto mancante, aggiungerlo a `tex/pacchetti-texlive.txt` e ripetere.

---

### Task 15: Revisione finale e pubblicazione

- [ ] **Step 1: Build pulita** — `make pulisci && make all` → codice 0. In `make controlli`, il numero di pagine della nota passa a `--pagine 15 40`.
- [ ] **Step 2: Lettura integrale** — rendere in PNG tutte le pagine dei due PDF della nota e leggerle. Controllare:
  - impaginazione, figure, a capo;
  - che ogni sezione rispetti lo schema delle convenzioni della specifica;
  - che italiano e inglese dicano le stesse cose;
  - il tono, secondo le Global Constraints.
- [ ] **Step 3: Revisione dell'intero branch** — una revisione indipendente di tutto il diff rispetto a `main`: specifica, matematica, codice.
- [ ] **Step 4: Pubblicazione (ogni passo con conferma esplicita dell'autore)**:
  1. l'autore rende pubblico il repository e imposta Settings → Pages → Source: «GitHub Actions»;
  2. merge di `nota-e-pubblicazione` su `main`, poi push;
  3. tag `v1.0` sul commit di merge, poi push del tag, subito dopo il punto 2: così i link di download funzionano appena la pagina va online.
- [ ] **Step 5: Verifica pubblica**:
  - `curl -sI https://endjneer.github.io/quaderni-derive/` e `…/en/` → 200;
  - `curl -sIL` di ciascuno dei tre URL di download → `200` finale, con `content-type: application/pdf`;
  - la pagina aperta sul telefono dell'autore, se il controllo del Task 13 non è stato possibile.
