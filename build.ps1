<#
.SYNOPSIS
  Ricostruisce i documenti a partire dai file .dfw: l'edizione integrale
  e la nota nelle due lingue.

.DESCRIPTION
  Esegue in ordine: estrazione dal formato binario, verifica numerica,
  generazione delle figure, composizione dei capitoli, tre passate di
  pdflatex (servono per indice e riferimenti incrociati).

.PARAMETER SoloPdf
  Salta le fasi in Python e ricompila soltanto il LaTeX.

.PARAMETER SaltaVerifica
  Salta la verifica numerica, che e' la fase piu' lenta (qualche minuto).
#>
param(
  [switch]$SoloPdf,
  [switch]$SaltaVerifica
)

$ErrorActionPreference = 'Stop'
$radice = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $radice

# --- interprete Python ------------------------------------------------------
$python = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $python) { throw "python non trovato nel PATH" }

# --- motore LaTeX -----------------------------------------------------------
$pdflatex = (Get-Command pdflatex -ErrorAction SilentlyContinue).Source
if (-not $pdflatex) {
  $candidato = "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe"
  if (Test-Path $candidato) { $pdflatex = $candidato }
  else { throw "pdflatex non trovato: installare MiKTeX o TeX Live" }
}

function Passo($testo) {
  Write-Host ""
  Write-Host "==> $testo" -ForegroundColor Cyan
}

if (-not $SoloPdf) {
  Passo "Estrazione dai file .dfw"
  & $python tools\dfw_extract.py source extracted\all.json |
    Select-Object -Last 1

  if (-not $SaltaVerifica) {
    Passo "Verifica numerica delle identita'"
    & $python tools\verify.py extracted\all.json extracted\verify.json
  } else {
    Write-Host "    verifica saltata su richiesta"
  }

  Passo "Generazione delle figure"
  & $python tools\make_figures.py figures | Select-Object -Last 1

  Passo "Composizione dei capitoli"
  & $python tools\build_tex.py .

  Passo "Verifica delle affermazioni della nota"
  & $python tools\verifica_nota.py | Select-Object -Last 1
  if ($LASTEXITCODE -ne 0) { throw "verifica_nota.py: un controllo e' fallito" }
  & $python tools\controlla_testi.py | Select-Object -Last 1
  if ($LASTEXITCODE -ne 0) { throw "controlla_testi.py: le due lingue non coincidono" }
}

Passo "Compilazione LaTeX (tre passate)"
Push-Location tex
try {
  foreach ($n in 1..3) {
    Write-Host "    passata $n di 3"
    & $pdflatex -interaction=nonstopmode -file-line-error derive2010.tex |
      Out-Null
  }
  $errori = Select-String -Path derive2010.log -Pattern '^!' -ErrorAction SilentlyContinue
  if ($errori) {
    Write-Host ""
    Write-Host "Errori LaTeX:" -ForegroundColor Red
    $errori | ForEach-Object { Write-Host "    $($_.Line)" }
  }
} finally {
  Pop-Location
}

Passo "Compilazione della nota (italiano e inglese)"
Push-Location nota
try {
  foreach ($f in 'nota-it', 'note-en') {
    foreach ($n in 1..3) {
      & $pdflatex -interaction=nonstopmode -file-line-error "$f.tex" | Out-Null
    }
    $errori = Select-String -Path "$f.log" -Pattern '^!' -ErrorAction SilentlyContinue
    if ($errori) { $errori | ForEach-Object { Write-Host "    $($_.Line)" -ForegroundColor Red } }
  }
} finally {
  Pop-Location
}

Passo "I tre PDF con i nomi della release"
$dist = Join-Path $radice 'dist'
New-Item -ItemType Directory -Force -Path $dist | Out-Null
Copy-Item nota\nota-it.pdf (Join-Path $dist 'quaderni-derive-nota.pdf')
Copy-Item nota\note-en.pdf (Join-Path $dist 'derive-notebooks-note.pdf')
Copy-Item tex\derive2010.pdf (Join-Path $dist 'quaderni-derive-edizione-integrale.pdf')

$pdf = Join-Path $radice 'tex\derive2010.pdf'
if (Test-Path $pdf) {
  $kb = [math]::Round((Get-Item $pdf).Length / 1KB)
  Write-Host ""
  Write-Host "Fatto: tex\derive2010.pdf ($kb KB)" -ForegroundColor Green
} else {
  throw "il PDF non e' stato prodotto"
}
