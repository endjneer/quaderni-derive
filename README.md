# I quaderni Derive, 2009–2011

*Ventitré quaderni di matematica sperimentale, scritti con un programma che
non esiste più, recuperati byte per byte e riletti con gli occhi di oggi.*

📄 **[Leggi la nota (PDF)](https://github.com/endjneer/quaderni-derive/releases/latest/download/quaderni-derive-nota.pdf)** ·
[English version](https://github.com/endjneer/quaderni-derive/releases/latest/download/derive-notebooks-note.pdf) ·
[Edizione integrale](https://github.com/endjneer/quaderni-derive/releases/latest/download/quaderni-derive-edizione-integrale.pdf) ·
[Pagina](https://endjneer.github.io/quaderni-derive/)

> *English:* between 2009 and 2011 the author used the computer-algebra system
> Derive as a notebook for mathematical experiments. Fifteen years later the
> files could no longer be opened; we decoded their binary format, recovered 792
> expressions and read them again. The thematic note, in English, is
> [`derive-notebooks-note.pdf`](https://github.com/endjneer/quaderni-derive/releases/latest/download/derive-notebooks-note.pdf).

## La storia in breve

Fra il 2009 e il 2011 l'autore ha usato **Derive for Windows**, il sistema di
calcolo simbolico della Texas Instruments, come un taccuino: si scrive
un'espressione, si chiede al programma di semplificarla o di farne il limite,
si cambia un parametro e si guarda che cosa succede. Ne sono rimasti ventitré
file `.dfw`.

Derive è stato ritirato nel 2007 e quei file non si aprivano più. Il loro
formato non è documentato, ma il contenuto non è cifrato: decodificandolo byte
per byte sono riemerse **792 espressioni**. Le abbiamo tradotte in notazione
matematica, verificate numericamente e rilette una per una, chiedendoci ogni
volta: che cosa c'è di vero, che cosa è già noto, che cosa no?

Il risultato sono due documenti: una **nota per temi** di 18 pagine, in
italiano e in inglese, scritta per un lettore matematico, e un'**edizione
integrale** di oltre duecento pagine con tutte le espressioni commentate.

## Che cosa abbiamo trovato

Nessun teorema nuovo di grande portata, va detto subito. Ma alcuni esperimenti
di quegli anni, fatti senza conoscere la letteratura, finiscono esattamente su
pezzi di matematica vera, e in un caso su un problema aperto.

### 1. Una catena di fattoriali che si ferma sul più famoso dei casi eccezionali

Il quaderno `factor.dfw` nota che il prodotto dei fattoriali dei dispari è il
fattoriale di un numero triangolare:

$$1! = 1!,\qquad 1!\,3! = 3!,\qquad 1!\,3!\,5! = 6!,\qquad 1!\,3!\,5!\,7! = 10!$$

e poi si rompe. Perché proprio quattro volte? Ogni passo della catena è un
caso dell'equazione $a!\,b! = c!$, e l'ultimo passo riuscito è

$$6!\cdot 7! = 10!,$$

**l'unica soluzione non banale conosciuta** di quell'equazione. Che sia
l'unica in assoluto è una congettura aperta, attribuita a Surányi (problema
B23 di Guy, problema di Erdős #373). Al passo dopo servirebbe
$11\cdot12\cdot13\cdot14\cdot15 = 9!$, e invece $360\,360 \ne 362\,880$: un
quasi-successo dello 0,7%.

La nota **dimostra** che la catena non si richiude più per nessun $p \ge 4$:
ogni passo manca il bersaglio di un fattore che decresce geometricamente, con
ragione che tende a $e^2/8$, e il divario fra i due membri cresce più che
esponenzialmente.

### 2. L'esponenziale scritto con la tangente del semiangolo

Cinque quaderni contengono pezzi della stessa idea, mai scritta per intero:

$$e^{it} = \frac{1+i\tan(t/2)}{1-i\tan(t/2)},\qquad
e^{t} = \frac{1+\tanh(t/2)}{1-\tanh(t/2)}.$$

Letta sull'asse immaginario dà la gaussiana; seguita fino in fondo porta dritta
alla **frazione continua di Euler** per $e$,

$$\frac{e-1}{e+1} = [0;\,2,6,10,14,\dots],$$

alla dimostrazione di **Lambert** dell'irrazionalità di $e$, agli
**approssimanti di Padé** e alla **trasformazione bilineare** dei filtri
numerici, dove la tangente del semiangolo diventa la precompensazione delle
frequenze. È lo stesso strumento che servirebbe per realizzare in digitale il
filtro elimina-banda progettato in `notch.dfw`.

### 3. La media e il punto medio

`Trasformata T.dfw` applica a quattordici funzioni lo stesso rapporto fra la
media su $[0,t]$ e il valore nel punto medio, e trova lo stesso seno cardinale
per $\sin$, $\cos$ ed $e^{ix}$. Non è un caso: è il **teorema della media per
l'equazione di Helmholtz** in una dimensione, e vale anche il viceversa (le
funzioni con questa proprietà sono esattamente le soluzioni di $f''=\lambda
f$). Curiosità: la media su un segmento ha lo stesso nucleo $\sin(kr)/(kr)$
della media su una sfera in tre dimensioni.

### 4. Il gemello del seno cardinale

In `cosinc.dfw` la funzione $((-1)^x-1)/(\pi x)$ si spezza nel seno cardinale e
in un "gemello", $(1-\cos\pi x)/(\pi x)$. Il gemello è la **trasformata di
Hilbert** del seno cardinale; insieme formano il suo segnale analitico. Il
valore 11,534 che Derive dava per l'integrale del gemello è un artefatto:
l'integrale diverge.

### 5. ReLU e softplus, nel 2010

`mate.dfw` costruisce il gradino di Heaviside con soli logaritmi e valori
assoluti:

$$\frac{1}{x}\ln\frac{|e^x-1|+|e^x+1|}{2} = \frac{\max(x,0)}{x}.$$

Il numeratore è la **ReLU**; la versione "morbida" che compare in un altro
quaderno, $\ln\cosh x$, è parente della **softplus**. Il passaggio dall'una
all'altra ha un nome: **dequantizzazione di Maslov**, la porta della
matematica tropicale.

### 6. Due successioni per $e$ e la loro media

La successione dei quaderni, $\bigl(\sum_{k=0}^{n} n^{-k}\bigr)^n$, sembrava
convergere a $e$ più in fretta di $(1+1/n)^n$. Non è così: hanno lo stesso
errore $e/(2n)$, **con segno opposto**. È la loro media a convergere molto più
in fretta, con errore $11e/(24n^2)$: circa $10^{-14}$ a $n=10^7$.

### 7. Una delta di Dirac nel piano complesso

`delta.dfw` valuta una famiglia che approssima la delta in un punto complesso e
ottiene una funzione ordinaria, $z\,\mathrm{Im}\,z/(2i|z|^3)$. Il calcolo è
giusto, ma il risultato **dipende dalla famiglia scelta**: con altre famiglie
si ottiene zero o infinito. Resta una domanda aperta, ed è presentata come
tale.

### 8. La formula preferita dei quaderni, e le sue varianti

Il quaderno `mate.dfw` torna una quarantina di volte sulla stessa identità:

$$\frac{\cos^2 x-\cos^2 y}{\cos 2x-\cos 2y}=\frac12 \qquad\text{per ogni } x,\,y.$$

E la mette alla prova in tutti i modi possibili:

- **con i seni** il rapporto vale $-\tfrac12$, **con i coseni iperbolici** di
  nuovo $\tfrac12$ (righe #3–#4);
- **con argomenti complessi**, $x\pm iy$, e con coppie di angoli qualsiasi come
  $x\pm ky$, oppure $3x+ky$ e $x$, il risultato non cambia (righe #19–#31); né
  cambia riscrivendo tutto con esponenziali complessi (riga #6);
- **con la triplicazione** la costante si dimezza ancora:

  $$\frac{\cos^3x\,\cos y-\cos^3y\,\cos x}{\cos 3x\,\cos y-\cos 3y\,\cos x}=\frac14;$$

- **con due pesi**, $(\cos^2x-k\cos^2y)/(\cos 2x-l\cos 2y)$ vale ancora
  $\tfrac12$ per ogni $x$, purché $\cos 2y=(1-k)/(k-l)$ (righe #53–#60);
- e diventa perfino una **macchina per π**: poiché il rapporto vale $\tfrac12$
  e $(1/2)!=\sqrt\pi/2$, da due angoli qualsiasi si ottiene

  $$4\left[\left(\frac{\cos^2 x-\cos^2 y}{\cos 2x-\cos 2y}\right)!\,\right]^2=\pi$$

  (righe #67–#71).

**Perché funziona.** $\cos 2\theta=2\cos^2\theta-1$ e
$\cos 3\theta=4\cos^3\theta-3\cos\theta$ sono i polinomi di Chebyshev, e
$\tfrac12$, $\tfrac14$ sono i reciproci dei loro coefficienti direttivi. Nella
versione cubica moltiplicare per l'altro coseno serve a eliminare il termine
$-3\cos\theta$. Dal quarto grado i termini da eliminare sono più di uno e due
angoli non bastano più; ma con più angoli la regola continua per **ogni** $n$.
Posto $c_i=\cos x_i$, con $\lfloor n/2\rfloor+1$ angoli,

$$\det\bigl[\cos n x_i,\; c_i^{\,n-2},\; c_i^{\,n-4},\;\dots\bigr]=2^{\,n-1}\,\det\bigl[c_i^{\,n},\; c_i^{\,n-2},\; c_i^{\,n-4},\;\dots\bigr],$$

perché i termini di grado più basso del polinomio di Chebyshev sono
combinazioni delle altre colonne. Le due identità del quaderno sono i casi
$n=2$ e $n=3$, con due angoli.

L'identità è anche all'origine della **trappola** più istruttiva della
raccolta: siccome vale per ogni valore del parametro, quando il quaderno chiede
a Derive di trovarlo il risolutore numerico risponde comunque con un numero,
$-4{,}999999701$, che non significa nulla.

## Le idee originali

Conviene distinguere due cose.

**Le idee dei quaderni**, cioè dell'autore fra il 2009 e il 2011, nate senza
conoscere la letteratura:

- scrivere l'esponenziale come funzione razionale della tangente del
  semiangolo e leggerlo sull'asse immaginario;
- trattare l'errore come un oggetto con leggi proprie (`teoria.dfw`), che sotto
  un errore comune agli operandi dà il principio delle misure ratiometriche;
- costruire gradini e onde quadre con soli logaritmi e valori assoluti;
- estendere una famiglia approssimante della delta ad argomenti complessi;
- confrontare la media di una funzione con il suo valore nel punto medio;
- cercare regolarità fra prodotti di fattoriali, e misurare di quanto si
  rompono quando si rompono;
- mettere alla prova una stessa identità in tutti i modi possibili: seni,
  coseni iperbolici, argomenti complessi, pesi, perfino il fattoriale (la
  formula preferita, al punto 8).

Sono idee buone: quasi tutte portano a risultati classici, alcuni profondi.
Nessuna è nuova per la matematica, e la nota lo dice esplicitamente.

**Che cosa aggiunge questo lavoro**:

- la **dimostrazione** che la catena dei fattoriali non si richiude per nessun
  $p \ge 4$ (elementare, con una parte finita verificata al calcolatore): non
  l'abbiamo trovata in letteratura;
- il **collegamento** di ciascun quaderno con la matematica nota: Surányi,
  Euler e Lambert, Helmholtz, Hilbert, Maslov, Gel'fand–Šilov e Sato;
- l'osservazione che la formula preferita dei quaderni e la sua versione
  cubica sono i primi due casi di un'identità fra determinanti valida per ogni
  $n$: elementare, ma è la forma giusta della regola che il quaderno intravede;
- la riformulazione precisa della domanda sulla delta complessa: il limite
  della famiglia a rettangolo è $\tfrac12\,\partial_x(z/|z|)$, e non è
  intrinseco;
- la **decodifica del formato `.dfw`**, di cui non abbiamo trovato una
  descrizione pubblica: può servire a chiunque abbia ancora quaderni di Derive
  da aprire;
- un controllo sistematico: **ogni numero citato nella nota è ricalcolato**
  da uno script, a sessanta cifre.

## Gli errori, che sono la parte più istruttiva

Rileggere tutto fa emergere anche gli errori, dell'autore e del programma:

- **Derive sbaglia un limite.** Per $\bigl(\sum_{k=0}^{n} n^{-k}\bigr)^n$
  risponde $1$ invece di $e$. Il quaderno se ne accorge calcolando la
  successione a $n = 9\,999\,999$.
- **Un risolutore numerico risponde sempre.** In `mate.dfw` una trentina di
  righe cercano un parametro $k$ nella formula preferita, che vale per ogni
  $k$. Derive restituisce comunque $k = -4{,}999999701$, identico per
  equazioni diverse: è solo il punto in cui l'iterazione si ferma.
- **Refusi e sviste** in righe battute a mano: in `teoria.dfw #13` un 10 al
  posto di un 5 rompe la simmetria dei coefficienti binomiali; in
  `factor.dfw #5` c'è un fattore 7 di troppo; in `delta.dfw` le trasformate
  scambiano seno e coseno iperbolico.

## I documenti

| PDF nella [release](https://github.com/endjneer/quaderni-derive/releases/latest) | Che cos'è |
|---|---|
| `quaderni-derive-nota.pdf` | **La nota**, in italiano: i sette temi, con enunciati, dimostrazioni, contesto e domande aperte |
| `derive-notebooks-note.pdf` | La stessa nota in inglese |
| `quaderni-derive-edizione-integrale.pdf` | **L'edizione integrale**, in italiano: tutte le 792 espressioni, nell'ordine dei file, tradotte e commentate |

---

## Per chi vuole ricostruire tutto

### Che cosa contiene il repository

| Cartella | Contenuto |
|---|---|
| `source/` | I ventitré file `.dfw` originali, non modificati |
| `tools/` | La pipeline di recupero e gli script di verifica, in Python |
| `commento/` | Il commento dell'edizione integrale, un file JSON per quaderno |
| `tex/` | L'edizione integrale: preambolo, capitoli scritti a mano, disegni TikZ |
| `tex/generato/` | I capitoli prodotti dal generatore (non modificare a mano) |
| `nota/` | La nota per temi: un file per sezione e per lingua (`it/`, `en/`) |
| `figures/` | I grafici, in PDF vettoriale; quelli della nota si chiamano `nota_*` |
| `extracted/` | L'estrazione in JSON e l'esito della verifica numerica |
| `site/` | La pagina di presentazione, in italiano e in inglese |

### La pipeline

```
source/*.dfw
     │
     ├─ tools/dfw_extract.py   ──►  extracted/all.json
     │      analizza il formato binario, estrae testo, indice e origine
     │
     ├─ tools/verify.py        ──►  extracted/verify.json
     │      interpreta ogni identità con mpmath e la valuta in più punti
     │
     ├─ tools/make_figures.py  ──►  figures/*.pdf
     │      ridisegna i grafici a partire dalle formule
     │
     ├─ tools/build_tex.py     ──►  tex/generato/*.tex
     │      unisce espressioni, verifica e commento in capitoli LaTeX
     │
     ├─ tools/verifica_nota.py
     │      ricalcola ogni valore numerico citato nella nota (mpmath, 60 cifre)
     ├─ tools/controlla_testi.py
     │      italiano e inglese coincidono; ogni decimale del testo è verificato
     │
     └─ pdflatex ──►  edizione integrale e nota (it, en)
                       │
                 tools/controlla_pdf.py   font, metadati, log senza errori
```

`tools/derive2tex.py` è il traduttore vero e proprio: un parser a discesa
ricorsiva sulla sintassi di Derive, con reinserimento delle parentesi in base
alla struttura dell'albero e spezzatura automatica delle formule lunghe.

### Compilare

Servono Python 3.12 con i pacchetti di `requirements.txt` e una distribuzione
LaTeX con i pacchetti elencati in `tex/pacchetti-texlive.txt` (oltre a
`scheme-basic`). La stessa lista la usa la CI.

Su sistemi POSIX:

```sh
make            # i tre PDF in dist/, dopo tutti i controlli
make nota       # solo la nota, con le verifiche
make pdf        # solo l'edizione integrale
```

Su Windows:

```powershell
.\build.ps1              # tutto: estrazione, verifica, figure, PDF
.\build.ps1 -SoloPdf     # solo la ricompilazione LaTeX
```

### Pubblicazione

Il workflow `.github/workflows/pubblica.yml` compila i tre PDF a ogni push e
pull request e, su un tag `v*`, crea la release e vi allega i PDF. La pagina
punta a `releases/latest/download/<nome>.pdf`, quindi i link non cambiano fra
una release e l'altra.

La pagina si pubblica solo quando la variabile del repository `PAGINA_ATTIVA`
vale `true` (Settings → Secrets and variables → Actions → Variables), con
"GitHub Actions" scelto come sorgente in Settings → Pages.

### Il formato `.dfw`, in breve

Ricostruito leggendo i byte; il capitolo 2 dell'edizione integrale e
l'appendice A della nota lo documentano.

- Riga di intestazione ASCII con versione e data di salvataggio.
- Byte `0x1A` come separatore, poi le impostazioni di sessione in chiaro
  (`Precision:=Exact`, `Branch:=Principal`, …).
- Una sequenza di record, ciascuno composto da: origine dell'espressione in
  UTF-16LE (`"User"` oppure la chiamata che l'ha prodotta, ad esempio
  `"Simp(Solve(#11,z))"`), indice a 32 bit little-endian, la costante
  `01 00 00 00`, e infine il testo dell'espressione come stringa a lunghezza
  prefissa.
- La lunghezza sta in un byte; se vale `0xFF`, i due byte successivi
  contengono la lunghezza vera a 16 bit. Senza questa regola le espressioni
  lunghe spariscono in silenzio.
- I caratteri non ASCII sono codificati come `0x7F` seguito da quattro cifre
  esadecimali Unicode: `0x7F 30 33 62 35` è `ε`.

### Verifica numerica

`tools/verify.py` interpreta l'albero sintattico con `mpmath` a 20 cifre e
confronta i membri di ogni catena di uguaglianze in quattro punti del piano
complesso. 145 espressioni superano il controllo e nell'edizione integrale
portano un segno di spunta. L'assenza del segno **non** significa che la
formula sia sbagliata: il controllo può non essere applicabile (integrale
indefinito, `SOLVE` da risolvere, indice di somma simbolico), l'identità può
valere solo sull'asse reale o su un ramo, oppure non c'è un'identità da
controllare.

Le affermazioni della nota sono verificate a parte da
`tools/verifica_nota.py`: un controllo o più per ogni valore citato.

## Licenze

- **Codice** (`tools/`, `Makefile`, `build.ps1`, workflow): licenza MIT, file
  [`LICENSE`](LICENSE).
- **Testi, figure e file `.dfw`** (`nota/`, `tex/`, `commento/`, `figures/`,
  `site/`, `source/`): Creative Commons Attribuzione 4.0 Internazionale,
  file [`LICENSE-CC-BY-4.0`](LICENSE-CC-BY-4.0).

Analisi e redazione con l'assistenza di Claude (Anthropic); ogni verifica
numerica è riproducibile dal repository.
