#!/bin/bash
# Rigenera Appunti_Teoria_Completo.pdf dai file 01-08.md.
# Richiede: pandoc, MiKTeX (xelatex), font Cambria/Cambria Math/Consolas/Segoe UI Symbol.
set -e
cd "$(dirname "$0")"

PANDOC="/c/Users/aless/AppData/Local/Microsoft/WinGet/Packages/JohnMacFarlane.Pandoc_Microsoft.Winget.Source_8wekyb3d8bbwe/pandoc-3.10/pandoc.exe"
XELATEX="/c/Users/aless/AppData/Local/Programs/MiKTeX/miktex/bin/x64/xelatex.exe"

cat > combined.md << 'YAMLEOF'
---
title: "Sistemi Intelligenti --- Appunti di Teoria"
author: "Corso di Sistemi Intelligenti, Cristina Baroglio --- Università di Torino"
date: "Moduli 1--8"
---

YAMLEOF
for f in 01-introduzione-e-agenti.md 02-ricerca.md 03-giochi.md 04-csp.md \
         05-logica-proposizionale.md 06-logica-primo-ordine.md \
         07-ontologie-pianificazione.md 08-machine-learning.md; do
  cat "$f" >> combined.md
  printf '\n\n' >> combined.md
done

"$PANDOC" combined.md -o Appunti_Teoria_Completo.pdf \
  --pdf-engine="$XELATEX" \
  -V documentclass=report \
  -V fontsize=11pt \
  -V papersize=a4 \
  --toc --toc-depth=2 \
  -H preamble.tex \
  --highlight-style=tango

echo "OK: Appunti_Teoria_Completo.pdf rigenerato."
