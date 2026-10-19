# Nota sui quaderni Derive e pubblicazione su GitHub — design

- **Data:** 2026-10-19
- **Branch:** `nota-e-pubblicazione`
- **Stato:** approvato in conversazione, in attesa di revisione della specifica scritta

## 1. Obiettivo

Rendere condivisibile il materiale dei quaderni Derive 2009–2011 con **un lettore
matematico** (professore o ricercatore a cui chiedere un parere), tramite una
pagina GitHub da cui si scaricano i PDF, allegati a una **GitHub Release**.

Il PDF attuale (`tex/derive2010.pdf`, 232 pagine) è un'edizione critica ordinata
per file: esaustiva, ma lo spunto interessante è sepolto fra centinaia di righe
di routine. Il nuovo documento principale è una **nota breve, ordinata per temi**,
onesta su cosa è noto e cosa no.

### Decisioni prese con l'autore

| Tema | Decisione |
|---|---|
| Pubblico | Un matematico: breve, rigoroso, contesto bibliografico |
| Lingue | Nota in italiano **e** in inglese; pagina web in entrambe |
| Edizione integrale | Resta, corretta, come secondo PDF della release (solo italiano) |
| Visibilità | Il repository `endjneer/quaderni-derive` diventa pubblico (lo fa l'autore) |
| Approccio | Nota in LaTeX + pagina statica leggera + release automatica con GitHub Actions |
| Trasparenza | Riga nel colofone e sulla pagina sull'assistenza di Claude (Anthropic) |
| Licenze | CC BY 4.0 per testi, figure e file `.dfw`; MIT per il codice |
| PDF generati | Escono dal versionamento; li produce la CI e stanno nella release |

### Criteri di successo

1. Un matematico che apre la pagina capisce in un minuto che cosa sono i quaderni
   e quali sono i temi che valgono la lettura, e scarica il PDF in un clic.
2. Ogni affermazione matematica della nota è dimostrata, abbozzata con un
   argomento completo, citata da una fonte verificata, oppure dichiarata aperta.
3. Ogni affermazione numerica della nota è controllata da uno script eseguito
   in CI, che fa fallire la build se un valore non torna.
4. Il tag `v1.0` produce una release con tre PDF; la pagina li scarica tramite
   link stabili.

## 2. Prodotti

| Prodotto | File nella release | Sorgente |
|---|---|---|
| Nota, italiano (~20–30 pp.) | `quaderni-derive-nota.pdf` | `nota/nota-it.tex` |
| Nota, inglese | `derive-notebooks-note.pdf` | `nota/note-en.tex` |
| Edizione integrale, italiano | `quaderni-derive-edizione-integrale.pdf` | `tex/derive2010.tex` |
| Pagina web it + en | GitHub Pages | `site/` |

## 3. La nota

Classe `article`, A4, 11 pt, stessa palette dell'edizione integrale. Le due
versioni linguistiche hanno la stessa struttura e lo stesso contenuto
matematico; una sezione per file (`nota/it/NN-nome.tex`, `nota/en/NN-name.tex`).

### Convenzioni

- I riferimenti ai quaderni hanno la forma `factor.dfw #4` e rimandano
  all'edizione integrale.
- Ogni sezione segue lo schema: che cosa fa il quaderno → enunciato pulito →
  dimostrazione o abbozzo → contesto in letteratura → che cosa resta aperto.
- Nessun teorema è presentato come nuovo. Il tono è quello di una nota, non di
  una celebrazione: niente "elegante", "notevole", "sorprendente" se non
  giustificati dall'enunciato.
- Le sezioni 2–8 sono numerate come qui sotto; la §1 è l'introduzione.

### Struttura

**Abstract.** Che cos'è il materiale (taccuini di matematica sperimentale con
Derive 6, recuperati da un formato binario dismesso); che cosa *non* si afferma
(nessun teorema nuovo); che cosa si offre (sette temi con il loro contesto, uno
dei quali tocca un problema aperto, con una dimostrazione completa per il caso
considerato).

**§1 Introduzione** (1–2 pp.). Metodo, cronologia 2009–2011, come si leggono i
riferimenti, la verifica numerica, rimando all'Appendice A e all'edizione
integrale.

**§2 L'esponenziale e la tangente del semiangolo**
(`gauss #1–5`, `atan #1–14`, `cosinc #1–3`, `delta #41–44`, `mate #111–122`).
Contenuto richiesto:
- e^{it} = (1+iu)/(1−iu) con u = tan(t/2), |t| < π: la trasformata di Cayley
  manda la retta reale sul cerchio unitario privato di −1. Forma dei quaderni:
  (1+iu)²/(1+u²) = sgn(1+iu)², con 1+u² = d/dt (2 tan(t/2)) (`gauss #3–4`).
  Parametrizzazione razionale del cerchio e terne pitagoriche per u razionale.
- Sull'asse immaginario: e^{t} = (1+τ)/(1−τ) con τ = tanh(t/2), per ogni t
  reale; equivalentemente t = ln((1+τ)/(1−τ)) = 2 artanh τ. `atan #2`
  (e^{i·atan(ix)} = √((1−x)/(1+x))) è la stessa formula vista dall'altro lato;
  la gaussiana di `gauss #5` è il caso t = x².
- In particolare e = (1+tanh ½)/(1−tanh ½).
- La gudermanniana gd(x) = 2 arctan(tanh(x/2)): tan(gd x) = sinh x,
  sin(gd x) = tanh x, cos(gd x) = sech x. Le equazioni di `mate #115–122`
  (tanh x = tan(kx) e affini) si risolvono con essa: kx = arctan(tanh x) = gd(2x)/2.
- Euler (1737): tanh ½ = (e−1)/(e+1) = [0; 2, 6, 10, 14, …]; più in generale
  tanh(1/n) = [0; n, 3n, 5n, …]. Frazione continua di Lambert per tanh;
  irrazionalità di e^r per r razionale non nullo (e di π tramite tan), enunciata
  con riferimento, senza dimostrazione.
- Troncando: tanh(t/2) ≈ t/2 dà (1+t/2)/(1−t/2); il convergente successivo dà
  (1+t/2+t²/12)/(1−t/2+t²/12). Sono gli approssimanti di Padé diagonali [1/1] e
  [2/2] di e^t; il fatto generale si enuncia con riferimento.
- Ingegneria: la trasformazione bilineare (Tustin) z = (1+sT/2)/(1−sT/2) è la
  formula esatta z = e^{sT} = (1+tanh(sT/2))/(1−tanh(sT/2)) con tanh(sT/2)
  sostituito da sT/2; la precompensazione Ω = (2/T) tan(ωT/2) è la tangente del
  semiangolo. Collegamento esplicito con `notch.dfw`. Cenno alla rapidità in
  relatività (fattore Doppler e^η = (1+tanh(η/2))/(1−tanh(η/2))).
- Figura `nota_semiangolo`: (a) punti (1+iu)/(1−iu) per u equispaziati sul
  cerchio; (b) errore relativo di [1/1], [2/2], [3/3] rispetto a e^t.

**§3 Una catena di fattoriali che si spezza** (`factor.dfw`).
Contenuto richiesto:
- Enunciato: P_p := ∏_{k=0}^{p} (2k+1)! =? T_{p+1}!, con T_m = m(m+1)/2.
  Vale per p = 0,1,2,3.
- Forma passo per passo: il passo p è T_p!·(2p+1)! = T_{p+1}!, cioè un caso
  dell'equazione a!·b! = c!. p = 1 e p = 2 sono soluzioni banali; **p = 3 è
  6!·7! = 10!, l'unica soluzione non banale conosciuta** (Guy, UPINT, B23;
  congettura di Surányi).
- Il quasi-successo: al passo 4, 11·12·13·14·15 = 360360 contro 9! = 362880.
- **Proposizione.** Per ogni p ≥ 4 vale P_p > T_{p+1}!: la catena non si
  richiude mai più e lo scarto cresce. Dimostrazione: con
  a_p = T_{p+1}!/(T_p!(2p+1)!) si ha P_p/T_{p+1}! = (P_{p−1}/T_p!)/a_p, quindi
  basta a_p < 1 per p ≥ 4. Verifica esatta per 4 ≤ p ≤ 100 (massimo
  a_4 = 0,99306); per p ≥ 100,
  a_{p+1}/a_p = T_{p+2}·∏_{j=1}^{p+1}(1+(p+1)/(T_p+j)) / ((2p+2)(2p+3))
  ≤ exp((p+1)²/(T_p+1))·(p+2)(p+3)/(4(p+1)(2p+3)) ≤ e^{2,02}·0,12810 < 0,966,
  perché (p+1)²/(T_p+1) ≤ 2 + 2/p ≤ 2,02 e il secondo fattore è decrescente
  (il numeratore della sua derivata è −5p² − 18p − 15) e vale 0,12810 in p = 100.
  Il segno positivo delle differenze calcolate da Derive è coerente.
- Il refuso `factor.dfw #5`: 7³ al posto di 7².
- Figura `nota_fattoriali`: a_p in funzione di p (la figura `factor`
  dell'edizione integrale ha testo in italiano e non si riusa).

**§4 La media e il punto medio** (`Trasformata T.dfw`).
- T[f](t) = (1/t)∫_0^t f / f(t/2).
- **Proposizione.** Se f'' = λf (λ ∈ ℂ, μ² = λ), la media di f su [c−h, c+h] è
  f(c)·sinh(μh)/(μh) (con valore 1 per μ = 0); per λ = −1 si ottiene sin h/h.
  Dimostrazione con f = Ae^{μx} + Be^{−μx} e la parità di sinh(μh)/(μh) in μ.
  Spiega le righe #3–#7; le potenze danno 2^n/(n+1) (#8).
- Contesto: teorema della media per l'equazione di Helmholtz. In ℝⁿ la media
  sferica di una soluzione di Δu + k²u = 0 è u(x)·Γ(n/2)(2/(kr))^{n/2−1}J_{n/2−1}(kr);
  per n = 1 dà cos(kr) (i due estremi), per n = 3 dà sin(kr)/(kr): la media su
  un intervallo in dimensione 1 ha lo stesso nucleo della media sferica in
  dimensione 3.

**§5 Il seno cardinale e il suo gemello** (`cosinc.dfw`).
- ((−1)^x − 1)/(πx) = (e^{iπx} − 1)/(πx) = i∫_0^1 e^{iπxs} ds, con il ramo
  principale dichiarato nel file.
- Parte immaginaria: sin(πx)/(πx); parte reale: (cos πx − 1)/(πx). La seconda è,
  a meno del segno fissato dalla convenzione scelta nel testo, la trasformata di
  Hilbert della prima; insieme formano il segnale analitico, cioè la
  trasformata di Fourier del rettangolo unilatero [0, 1].
- (1 − cos πx)/(πx) non è integrabile su [0, ∞) (divergenza logaritmica): il
  valore 11,534 di `cosinc #20` è un artefatto numerico.
- Figura `nota_cosinc`: le due componenti, senza testo (la figura
  `sinc_cosinc` dell'edizione integrale ha il titolo in italiano).

**§6 Gradini fatti di logaritmi** (`mate`, `mate copia`, `u(0)-sign(0)`).
- Lemma: (|a−b| + |a+b|)/2 = max(|a|, |b|). Quindi
  ln((|e^x−1| + |e^x+1|)/2) = max(x, 0) e H(x) = max(x, 0)/x per x ≠ 0.
- ln cosh x = |x| − ln 2 + ln(1 + e^{−2|x|}) (`mate copia`).
- Contesto: log-sum-exp, lim_{h→0} h·ln(e^{a/h} + e^{b/h}) = max(a, b)
  (dequantizzazione di Maslov, matematica tropicale); softplus e ReLU.
- Il valore di un gradino nel punto di salto dipende dalla famiglia regolare di
  cui è limite; i candidati di `u(0)-sign(0)` si discutono in questa luce,
  dichiarando che le loro forme chiuse sono ricostruite dai valori.

**§7 Due successioni per e** (`e.dfw`).
- **Proposizione.** (1+1/n)^n = e(1 − 1/(2n) + 11/(24n²) + O(n⁻³)) e
  (1−1/n)^{−n} = e(1 + 1/(2n) + 11/(24n²) + O(n⁻³)). Poiché la seconda è la
  prima con n → −n, nella media si cancellano tutte le potenze dispari:
  la media vale e(1 + 11/(24n²) + O(n⁻⁴)).
- La successione dei quaderni, (∑_{k=0}^{n} n^{−k})^n, differisce da
  (1−1/n)^{−n} per il fattore (1 − n^{−n−1})^n, trascurabile.
- Numeri a n = 10⁷: errori −1,35914·10⁻⁷ e +1,35914·10⁻⁷; media 1,2459·10⁻¹⁴.
- Chiusura: la formula di Eulero come limite di (1 + iπ/x)^x (`e #88–93`).
- Figura `nota_e_errori`: |errore| in scala bilogaritmica delle due successioni
  e della media (pendenze −1, −1, −2), calcolata in precisione arbitraria.

**§8 Una delta di Dirac fuori dall'asse reale** (`delta.dfw`). Presentata come
domanda, non come risultato.
- La famiglia: per x reale, δ_n(x) = ¼[(1+2nx)/|x+1/(2n)| + (1−2nx)/|x−1/(2n)|]
  vale n per |x| < 1/(2n) e 0 per |x| > 1/(2n): un rettangolo scritto con due
  funzioni segno.
- Per z non reale: lim δ_n(z) = ½ ∂_x(z/|z|) = z·Im z/(2i|z|³) (`delta #4`);
  vale δ(az) = δ(z)/|a| per a reale non nullo.
- **Non è intrinseca:** la famiglia lorentziana ε/(π(z²+ε²)) tende a 0 per
  z non reale; la gaussiana e^{−z²/ε²}/(ε√π) diverge dove |Im z| > |Re z|.
  Il "valore" di δ(ω+ik), e quindi delle trasformate di `delta #22–27`, dipende
  dalla scelta della famiglia.
- Dove la domanda ha senso in modo rigoroso: funzionali analitici su funzioni
  test intere (Gel'fand–Šilov), dove F[e^{kt}] = 2π δ(ω + ik) è la valutazione
  in un punto complesso; iperfunzioni di Sato, dove δ è rappresentata da
  −1/(2πiz). In nessuno dei due casi δ ha valori puntuali.
- La verifica di `delta #48–51` è coerente con la linearità e non distingue fra
  le famiglie.

**§9 In breve.** Tabella, una o due righe per voce, ogni voce corretta e con
riferimento alle righe:
`teoria #1–7` (errore relativo di modo comune, misure ratiometriche — lettura
ricostruita, dichiarata come tale); `teoria #14–19` (radice doppia, separazione
∝ √ε); `teoria2` (curve y = a xⁿ, sezione aurea, a = 2^{(n−1)²}k^{1−n});
`sin-cos` (k = π − e ln π ≈ 0,0299); `pigreco #24–26` ((πˣ+eˣ)^{1/x} → π, e);
`pigreco #22` (identità ridotta a cos 2a − cos 2b = 2(cos²a − cos²b) e
arctan x + arctan(1/x) = sgn(x)π/2); `fattorazionale` (∏(1/n − 1/k) = k^{1−k});
`numeri primi` (somma dei reciproci dei primoriali 0,70523017179…, irrazionale);
`cost^2` (Fresnel, √(π/(2ω))); `limit` (|x| ≤ (√2/2)(½ + x²), uguaglianza in
|x| = 1/√2); `equazioni`; `notch`; `Sudoku`; `j`; `fx^gx` (u^{1/ln(1/u)} = 1/e).

**§10 Due refusi e una trappola.** `teoria #13` (coefficiente 10 al posto di 5,
scarto 35ε/n³); `factor #5` (7³ al posto di 7²); `mate #21–48` (la "soluzione"
k = −4,999999701 di un'identità è il punto in cui il risolutore numerico si
ferma).

**Appendice A — Il recupero.** Il formato `.dfw` in una pagina, la pipeline,
la verifica numerica, rimando al repository.

**Colofone.** Autore, data, repository, licenza CC BY 4.0, riga di trasparenza:
"Analisi e redazione con l'assistenza di Claude (Anthropic); ogni verifica
numerica è riproducibile dal repository." (traduzione equivalente in inglese).

**Bibliografia** (`thebibliography`, niente biber). Candidati: Guy, *Unsolved
Problems in Number Theory* (B23); Euler, *De fractionibus continuis
dissertatio*; Lambert (1768); Gel'fand–Šilov, *Generalized Functions*; Kaneko,
*Introduction to Hyperfunctions*; John, *Plane Waves and Spherical Means*;
Courant–Hilbert vol. II; King, *Hilbert Transforms*; Litvinov, *Maslov
dequantization, idempotent and tropical mathematics*; Borwein–Bailey,
*Mathematics by Experiment*; Oppenheim–Schafer, *Discrete-Time Signal
Processing*; Baker–Graves-Morris, *Padé Approximants*. **Ogni voce si include
solo dopo averne verificato autore, titolo, editore, anno e, dove citata, la
sezione;** una voce non verificabile si toglie e l'affermazione che sostiene si
riformula o si dimostra.

## 4. Verifica delle affermazioni della nota

Nuovo script `tools/verifica_nota.py` (mpmath, precisione ≥ 50 cifre), eseguito
in CI dopo la verifica esistente. Esce con codice ≠ 0 al primo controllo fallito
e stampa un riepilogo. Controlla almeno:

- §2: identità di Cayley e della tangente iperbolica in punti campione; frazione
  continua di (e−1)/(e+1) per 20 termini; uguaglianza fra il convergente di
  Lambert al secondo livello e [2/2] di Padé (sviluppo in serie fino a t⁵);
  identità della gudermanniana.
- §3: P_p = T_{p+1}! per p ≤ 3; a_p < 1 esatto per 4 ≤ p ≤ 100; la
  maggiorazione per p ≥ 100 calcolata a p = 100 e, come controllo di
  coerenza, sulla griglia 100 ≤ p ≤ 10⁵; 360360 e 362880; la
  fattorizzazione corretta di `factor #5`.
- §4: medie numeriche contro i nuclei sinc e sinhc; il caso n = 3 della media
  sferica (formula di Bessel contro sin(kr)/(kr)).
- §5: trasformata di Hilbert del sinc in alcuni punti, con la convenzione
  scritta nel testo; crescita logaritmica di ∫_0^X (1 − cos πx)/(πx).
- §6: il lemma del massimo e la formula di ln cosh in punti campione.
- §7: gli sviluppi asintotici e i tre numeri a n = 10⁷.
- §8: il limite della famiglia a rettangolo in punti complessi contro
  z·Im z/(2i|z|³); lorentziana → 0; gaussiana divergente dove |Im z| > |Re z|.
- §9: ogni valore numerico citato in tabella.

## 5. Correzioni all'edizione integrale

| File | Correzione |
|---|---|
| `commento/04-e.json` | Tolta l'affermazione falsa sulla convergenza più rapida; errori ±e/(2n), media con errore 11e/(24n²) |
| `tools/make_figures.py` (`e_convergenza`) | Calcolo in precisione arbitraria; aggiunta la curva della media |
| `commento/15-delta.json` | Dipendenza dalla famiglia (lorentziana, gaussiana); tolti "l'idea più originale" e il "valore numerico concreto" della trasformata; rimando a funzionali analitici e iperfunzioni |
| `commento/18-factor.json` | 6!·7! = 10!, Surányi, quasi-successo 360360/362880, rimando alla proposizione della nota |
| `commento/10-mate.json` | La costante 2^{1−n} solo per n = 2, 3 (per n ≥ 4 Chebyshev ha due termini inferiori); gradino = ReLU(x)/x; gudermanniana per `#115–122` |
| `commento/14-gauss.json`, `commento/08-atan.json` | Collegamento alla tangente del semiangolo; tolto "vale da solo il capitolo" |
| `commento/12-cosinc.json` | Nota sulla trasformata di Hilbert |
| `commento/16-trasformata-t.json` | Nota sul teorema della media per Helmholtz |
| `commento/05-pigreco.json` | Ridimensionato "molto elegante" |
| `tex/derive2010.tex` | Nota iniziale: è l'edizione integrale, i risultati sono nella nota |

Il resto del commento non si tocca.

## 6. Figure

- Le figure dell'edizione integrale restano come sono (titoli interni in
  italiano), salvo `e_convergenza`.
- Le figure nuove della nota si chiamano `nota_*`, non hanno testo diverso da
  formule ed etichette matematiche, e servono a entrambe le lingue; le
  didascalie stanno nel LaTeX. Sono generate da `tools/make_figures.py`.

## 7. Pagina web

- `site/index.html` (italiano) e `site/en/index.html` (inglese), collegate fra
  loro; un CSS condiviso; nessun passo di build.
- Contenuto: titolo, autore, abstract; i sette temi in due righe ciascuno con
  una formula; tre pulsanti di download; link al repository e alla pipeline;
  colofone con licenza e riga di trasparenza.
- Formule con KaTeX da cdnjs, versione fissata.
- Link ai PDF nella forma
  `https://github.com/endjneer/quaderni-derive/releases/latest/download/<nome>.pdf`.
- Metadati Open Graph per l'anteprima quando il link viene condiviso.
- Deve funzionare a larghezza di telefono.

## 8. Build e CI

### Repository

```
nota/
  preambolo-nota.tex
  nota-it.tex   note-en.tex
  it/NN-*.tex   en/NN-*.tex
tex/                       edizione integrale (invariata nella struttura)
site/                      index.html, en/index.html, stile.css
figures/                   figure condivise, comprese le nota_*
tools/verifica_nota.py
.github/workflows/pubblica.yml
LICENSE                    MIT (codice) + rimando a LICENSE-CC-BY-4.0
LICENSE-CC-BY-4.0          testi, figure, file .dfw
docs/superpowers/          specifica e piano
```

- `Makefile`: nuovi bersagli `nota` (i due PDF della nota) e
  `verifica-nota`; `all` costruisce i tre PDF. `build.ps1` si estende allo
  stesso modo, così l'autore può compilare anche su Windows.
- `tex/derive2010.pdf` esce dal versionamento (`git rm --cached`) ed entra in
  `.gitignore`, insieme ai PDF della nota e a `.venv/`.

### Workflow `.github/workflows/pubblica.yml`

- Eventi: push su `main`, tag `v*`, pull request, avvio manuale.
- **build** (sempre): checkout; Python con numpy, matplotlib, mpmath;
  estrazione, verifica, figure, capitoli; `tools/verifica_nota.py`; TeX Live
  con i pacchetti richiesti dai due preamboli; compilazione dei tre PDF;
  controllo del log (nessun errore, nessun riferimento o citazione non
  definiti); PDF rinominati come al §2 e caricati come artifact.
- **pages** (solo `main`): pubblica `site/` con `actions/upload-pages-artifact`
  e `actions/deploy-pages`.
- **release** (solo tag `v*`): crea la release e vi allega i tre PDF.
- Permessi minimi per job; versioni delle action fissate e controllate al
  momento dell'implementazione.

### Azioni a carico dell'autore

1. Rendere pubblico il repository.
2. Settings → Pages → Source: "GitHub Actions".
3. Autorizzare push del branch, merge e tag `v1.0` (non si fanno senza conferma).

## 9. Verifica prima della pubblicazione

- Ambiente locale senza `sudo`: TinyTeX in `~/.TinyTeX` (stesso `pdflatex`
  della CI) e `uv` per l'ambiente Python in `.venv/`.
- `make all` senza errori LaTeX, senza riferimenti o citazioni non definiti;
  `tools/verifica_nota.py` superato.
- Ispezione visiva di ogni pagina dei due PDF della nota e delle pagine toccate
  dell'edizione integrale, rese in PNG con `tools/pdfpage.py`.
- Pagina web servita in locale; controllo dei link interni, della resa delle
  formule e della larghezza da telefono.
- Rilettura finale della nota inglese contro quella italiana: stesse
  affermazioni, stessi numeri, stessi riferimenti.
- Il primo giro della CI avviene sul branch (job build); pages e release solo
  dopo il merge e il tag, su conferma dell'autore.

## 10. Fuori scopo

- Traduzione in inglese dell'edizione integrale.
- Riscrittura del commento riga per riga oltre le correzioni del §5.
- Ricerca matematica nuova oltre la proposizione del §3.
- Dominio personalizzato per la pagina.
- Cambiare la visibilità del repository (lo fa l'autore).
