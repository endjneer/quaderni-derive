<#
.SYNOPSIS
  Ricostruisce l'intero documento a partire dai file .dfw.

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

$pdf = Join-Path $radice 'tex\derive2010.pdf'
if (Test-Path $pdf) {
  $kb = [math]::Round((Get-Item $pdf).Length / 1KB)
  Write-Host ""
  Write-Host "Fatto: tex\derive2010.pdf ($kb KB)" -ForegroundColor Green
} else {
  throw "il PDF non e' stato prodotto"
}
