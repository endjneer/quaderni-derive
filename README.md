# I quaderni Derive, 2009–2011

Recupero, traduzione e commento di ventitré sessioni di lavoro prodotte fra il
2009 e il 2011 con **Derive for Windows 6**, il sistema di calcolo simbolico
della Texas Instruments, e una nota che ne raccoglie i risultati per temi.

**Pagina:** <https://endjneer.github.io/quaderni-derive/> ·
**PDF:** [ultima release](https://github.com/endjneer/quaderni-derive/releases/latest)

> *English:* recovery, translation and commentary of twenty-three Derive for
> Windows notebooks (2009–2011). The thematic note is available in English as
> `derive-notebooks-note.pdf` in the latest release; the integral edition is in
> Italian.

## I documenti

| PDF nella release | Che cos'è |
|---|---|
| `quaderni-derive-nota.pdf` | **La nota**, in italiano: sette temi in cui gli esperimenti dei quaderni toccano matematica nota, con enunciati, dimostrazioni, contesto e domande aperte |
| `derive-notebooks-note.pdf` | La stessa nota in inglese |
| `quaderni-derive-edizione-integrale.pdf` | **L'edizione integrale**, in italiano: tutte le 792 espressioni, nell'ordine dei file, ciascuna tradotta in notazione matematica e commentata |

I PDF non sono versionati: li produce la CI a ogni tag `v*` e li allega alla
release.

## Che cosa contiene il repository

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

## Compilare

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

## Pubblicazione

Il workflow `.github/workflows/pubblica.yml` compila i tre PDF a ogni push e
pull request; dal ramo `main` pubblica `site/` su GitHub Pages; su un tag `v*`
crea la release e vi allega i PDF. La pagina punta a
`releases/latest/download/<nome>.pdf`, quindi i link non cambiano fra una
release e l'altra.

La pagina si pubblica solo quando la variabile del repository `PAGINA_ATTIVA`
vale `true` (Settings → Secrets and variables → Actions → Variables): va
impostata dopo aver reso pubblico il repository e scelto "GitHub Actions" come
sorgente in Settings → Pages.

## Il formato `.dfw`, in breve

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

## Che cosa è saltato fuori

Nessun teorema nuovo, ma sette temi che toccano matematica nota, discussi
nella nota:

- l'esponenziale scritto con la tangente del semiangolo, che attraversa cinque
  quaderni e porta alla frazione continua di Euler per *e*, agli approssimanti
  di Padé e alla trasformazione bilineare dei filtri numerici;
- una catena di fattoriali, `1!·3!·5!·7! = 10!`, il cui ultimo passo è
  `6!·7! = 10!`, l'unica soluzione non banale conosciuta di `a!·b! = c!`; la
  nota dimostra che la catena non si richiude più;
- il teorema della media per l'equazione di Helmholtz, la trasformata di
  Hilbert del seno cardinale, la dequantizzazione di Maslov, una successione
  per *e* il cui errore si cancella nella media con quella classica;
- una delta di Dirac valutata fuori dall'asse reale: i conti sono corretti,
  ma il risultato dipende dalla famiglia approssimante.

La rilettura ha isolato anche alcuni errori, senza pretesa di completezza: due
refusi in righe battute a mano (`teoria.dfw #13`, `factor.dfw #5`), alcune
sviste nelle trasformate di `delta.dfw` (#22–#27, #43), una svista corretta
dall'autore stesso (`notch.dfw #15`) e diverse risposte sbagliate di Derive: un
limite in `e.dfw`, un integrale divergente in `cosinc.dfw`, una "soluzione" che
non risolve in `teoria.dfw` e una "soluzione" numerica di un'identità in
`mate.dfw`.

## Verifica numerica

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
