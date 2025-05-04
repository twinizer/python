#!/bin/bash

# Skrypt uruchamiający twinizer z automatyczną instalacją pakietu
clear

# Przejdź do katalogu skryptu
cd "$(dirname "$0")"

# Uruchom wrapper Pythona
python run.py "$@"
