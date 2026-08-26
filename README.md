# I quaderni Derive

Recupero, traduzione e commento di ventitré sessioni di lavoro prodotte fra il
2009 e il 2011 con **Derive for Windows 6**, il sistema di calcolo simbolico
della Texas Instruments.

Derive è stato dismesso nel 2007 e non gira più sui sistemi operativi attuali:
i file `.dfw` erano diventati illeggibili. Il contenuto matematico, però, non è
cifrato — le espressioni sono memorizzate come testo, nella stessa sintassi
lineare della riga di comando. Questo repository contiene il codice che le
riporta alla luce e il documento che ne esce.

**Risultato:** `tex/derive2010.pdf` — 232 pagine, 792 espressioni tradotte in
notazione matematica, commentate una per una, con 27 figure e la verifica
numerica di ogni identità verificabile.

## Che cosa contiene il repository

| Cartella | Contenuto |
|---|---|
| `source/` | I ventitré file `.dfw` originali, non modificati |
| `tools/` | La pipeline di recupero, in Python |
| `commento/` | Il commento redazionale, un file JSON per quaderno |
| `tex/` | Preambolo, capitoli scritti a mano, disegni TikZ, documento finale |
| `tex/generato/` | I capitoli prodotti dal generatore (non modificare a mano) |
| `figures/` | I 27 grafici, in PDF vettoriale |
| `extracted/` | L'estrazione in JSON e l'esito della verifica numerica |

## La pipeline

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
     └─ tools/build_tex.py     ──►  tex/generato/*.tex
            unisce espressioni, verifica e commento in capitoli LaTeX
                                │
                          pdflatex ──►  tex/derive2010.pdf
```

`tools/derive2tex.py` è il traduttore vero e proprio: un parser a discesa
ricorsiva sulla sintassi di Derive, con reinserimento delle parentesi in base
alla struttura dell'albero e spezzatura automatica delle formule lunghe.

## Compilare

Servono Python 3 con `numpy`, `matplotlib`, `mpmath`, e una distribuzione
LaTeX (testato con MiKTeX su Windows).

```powershell
.\build.ps1              # tutto: estrazione, verifica, figure, PDF
.\build.ps1 -SoloPdf     # solo la ricompilazione LaTeX
```

Su sistemi POSIX:

```sh
make
```

## Il formato `.dfw`, in breve

Ricostruito leggendo i byte; il capitolo 2 del PDF lo documenta per esteso.

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

## Che cosa è saltato fuori

Oltre alla matematica dei quaderni — una delta di Dirac estesa al piano
complesso, la gaussiana ricavata dalla parametrizzazione razionale del cerchio,
la formula di Eulero ottenuta come limite, il gradino di Heaviside costruito
con soli logaritmi e valori assoluti — la rilettura ha isolato anche due
refusi, entrambi in righe battute a mano:

- `teoria.dfw` **#13**: un coefficiente `10` al posto di `5`, che rompe la
  simmetria binomiale delle cinque righe precedenti; lo scarto dalla formula
  corretta vale esattamente `35ε/n³`.
- `factor.dfw` **#5**: `7³` al posto di `7²`, cioè un fattore sette di troppo.
  Tutte le fattorizzazioni prodotte da Derive, nello stesso file, sono esatte.

Una terza cosa, emersa rileggendo `teoria.dfw`: il simbolo `ε` vi ha **due
significati diversi**. Nelle prime sette righe è un errore relativo comune a
tutti gli operandi, e sotto quella lettura tutte e sette sono esatte — compresa
la #4, che dice che il quoziente lo cancella, il che è vero solo per errori di
modo comune ed è il principio delle misure ratiometriche. Nelle righe #8–#13
ε è invece il fattore di scala di una quantità algebrica: quello che vi si
calcola non è l'errore su `x^m` ma lo scarto di `(1+x)^m` da `x^m + 1`. Le due
letture coincidono solo per `m = 2`, che è probabilmente ciò che ha tenuto
insieme le due metà del quaderno.

E una trappola che vale la pena conoscere: in `mate.dfw` una trentina di
espressioni inseguono la soluzione di un'equazione che è un'identità, e quindi
soddisfatta da qualunque valore. Il numero `−4.999999701` che Derive
restituisce non è una soluzione, è il punto in cui l'iterazione numerica si è
fermata.

## Verifica numerica

`tools/verify.py` interpreta l'albero sintattico con `mpmath` a 20 cifre e
confronta i membri di ogni catena di uguaglianze in quattro punti del piano
complesso. 145 espressioni superano il controllo e nel PDF portano un segno di
spunta.

L'assenza del segno **non** significa che la formula sia sbagliata: nella
maggior parte dei casi significa che il controllo non era applicabile —
integrale indefinito, `SOLVE` da risolvere, indice di somma simbolico, oppure
un'espressione che non era affatto un'identità. Dove una formula merita un
commento, il commento sta nel testo.

## Licenza

Il contenuto matematico e i file `.dfw` sono dell'autore. Il codice della
pipeline è a disposizione per chiunque debba aprire altri file Derive.
