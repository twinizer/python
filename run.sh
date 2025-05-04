#!/bin/bash

# Skrypt uruchamiający twinizer z automatyczną instalacją pakietu
clear

# Przejdź do katalogu skryptu
cd "$(dirname "$0")"

# Sprawdź, czy KiCad jest zainstalowany
if ! command -v kicad &> /dev/null && ! command -v kicad-cli &> /dev/null; then
    echo "KiCad nie jest zainstalowany. Uruchamiam instalator..."
    python scripts/install_kicad.py
fi

# Uruchom wrapper Pythona
python run.py "$@"
