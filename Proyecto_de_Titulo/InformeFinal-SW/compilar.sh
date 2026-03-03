#!/bin/bash
# Compilar informe DOMU
# Uso: ./compilar.sh         (compilación rápida, 1 pasada)
#      ./compilar.sh full    (compilación completa con bibliografía)

export PATH="/Library/TeX/texbin:$PATH"
cd "$(dirname "$0")"

TEX="acuna_rivas-informe-SW"

if [ "$1" = "full" ]; then
    echo "=== Compilación completa (pdflatex + bibtex + 2x pdflatex) ==="
    pdflatex -interaction=nonstopmode "$TEX.tex"
    bibtex "$TEX" 2>/dev/null
    pdflatex -interaction=nonstopmode "$TEX.tex"
    pdflatex -interaction=nonstopmode "$TEX.tex"
else
    echo "=== Compilación rápida (1 pasada) ==="
    pdflatex -interaction=nonstopmode "$TEX.tex"
fi

if [ -f "$TEX.pdf" ]; then
    echo ""
    echo "PDF generado: $TEX.pdf ($(du -h "$TEX.pdf" | cut -f1))"
    open "$TEX.pdf"
else
    echo "ERROR: No se generó el PDF"
    exit 1
fi
