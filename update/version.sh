#!/bin/bash
set -e  # Zatrzymaj skrypt przy pierwszym błędzie

# Wyczyść ekran i pokaż informację o rozpoczęciu procesu
clear
echo "Starting publication process..."

# Pobierz konfigurację projektu
echo "Pobieranie konfiguracji projektu..."
PROJECT_CONFIG=$(python3 -c "
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'update'))
try:
    from env_manager import get_project_name, get_package_path, get_project_root
    
    # Zapytaj użytkownika o nazwę projektu, jeśli nie jest zdefiniowana
    project_name = get_project_name(True)
    package_path = get_package_path(True)
    
    # Pobierz pliki z wersją - używaj tylko pyproject.toml, który jest zwykle dostępny
    version_files = []
    project_root = get_project_root()
    
    # Sprawdź pyproject.toml
    pyproject_path = os.path.join(project_root, 'pyproject.toml')
    if os.path.exists(pyproject_path) and os.access(pyproject_path, os.W_OK):
        version_files.append(pyproject_path)
    
    print(f\"PROJECT_NAME={project_name}\")
    print(f\"PACKAGE_PATH={package_path}\")
    print(f\"VERSION_FILES={';'.join(version_files)}\")
except Exception as e:
    print(f\"PROJECT_NAME=twinizer\")
    print(f\"PACKAGE_PATH=twinizer\")
    print(f\"VERSION_FILES=pyproject.toml\")
    print(f\"# Błąd: {e}\", file=sys.stderr)
")

# Przetwórz konfigurację
eval "$PROJECT_CONFIG"
echo "Nazwa projektu: $PROJECT_NAME"
echo "Ścieżka pakietu: $PACKAGE_PATH"
echo "Pliki z wersją: $VERSION_FILES"

# Sprawdź, czy virtualenv jest już aktywowany
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Tworzenie i aktywacja środowiska wirtualnego..."
    # Utwórz virtualenv, jeśli nie istnieje
    if [ ! -d "venv" ]; then
        python -m venv venv
    fi
    source venv/bin/activate
else
    echo "Środowisko wirtualne już aktywne: $VIRTUAL_ENV"
fi

# Upewnij się, że mamy najnowsze narzędzia
echo "Upgrading build tools..."
pip install --upgrade pip build twine

# Sprawdź, czy jesteśmy w virtualenv
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Błąd: Nie udało się aktywować środowiska wirtualnego!"
    exit 1
fi

# Zainstaluj zależności projektu
echo "Instalacja zależności projektu..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

# Odinstaluj i zainstaluj ponownie pakiet w trybie edycji
echo "Reinstalacja pakietu w trybie deweloperskim..."
pip uninstall -y "$PROJECT_NAME" || true
pip install -e .

# Aktualizacja wersji w plikach źródłowych
echo "Aktualizacja numeru wersji..."
if [ -n "$VERSION_FILES" ]; then
    IFS=';' read -ra FILES <<< "$VERSION_FILES"
    for file in "${FILES[@]}"; do
        if [ -w "$file" ]; then
            echo "Aktualizacja wersji w pliku: $file"
            python update/src.py -f "$file" --type patch || echo "Nie udało się zaktualizować wersji w pliku $file"
        else
            echo "Pominięto plik $file (brak uprawnień do zapisu)"
        fi
    done
else
    echo "Brak plików do aktualizacji wersji"
    echo "Używanie domyślnej wersji z CHANGELOG.md"
fi

# Generowanie wpisu w CHANGELOG.md
echo "Generowanie wpisu w CHANGELOG.md..."
if [ -f "CHANGELOG.md" ] && [ ! -w "CHANGELOG.md" ]; then
    echo "Ostrzeżenie: Brak uprawnień do pliku CHANGELOG.md"
    echo "Tworzenie tymczasowego pliku CHANGELOG.md.new"
    python update/changelog.py --output CHANGELOG.md.new || echo "Nie udało się wygenerować wpisu w CHANGELOG.md"
else
    python update/changelog.py || echo "Nie udało się wygenerować wpisu w CHANGELOG.md"
fi

# Publikacja na GitHub
echo "push changes..."
bash update/git.sh

# Publikacja na PyPI
echo "Publikacja na PyPI..."
bash update/pypi.sh

echo "Proces publikacji zakończony pomyślnie!"
