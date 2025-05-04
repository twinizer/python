@echo off
REM Skrypt uruchamiający twinizer z automatyczną instalacją pakietu

REM Przejdź do katalogu skryptu
cd /d "%~dp0"

REM Uruchom wrapper Pythona
python run.py %*
