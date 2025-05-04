@echo off
REM Skrypt uruchamiający twinizer z automatyczną instalacją pakietu

REM Przejdź do katalogu skryptu
cd /d "%~dp0"

REM Sprawdź, czy KiCad jest zainstalowany
where kicad >nul 2>&1
if %errorlevel% neq 0 (
    echo KiCad nie jest zainstalowany. Uruchamiam instalator...
    python scripts\install_kicad.py
)

REM Uruchom wrapper Pythona
python run.py %*
