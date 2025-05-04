#!/usr/bin/env python3
"""
Moduł do zarządzania zmiennymi środowiskowymi projektu.
Pozwala na odczytywanie i zapisywanie zmiennych do pliku .env
oraz interakcję z użytkownikiem w celu ustawienia wartości zmiennych.
"""

import os
import re
import sys
import shutil
from pathlib import Path
from typing import Dict, Optional, Any


def get_project_root() -> Path:
    """Zwraca ścieżkę do katalogu głównego projektu."""
    # Zakładamy, że ten skrypt znajduje się w katalogu update
    return Path(__file__).parent.parent


def create_env_file_if_not_exists(env_file: Path = None) -> None:
    """
    Tworzy plik .env, jeśli nie istnieje.
    
    Args:
        env_file: Ścieżka do pliku .env. Jeśli None, używa domyślnej ścieżki.
    """
    if env_file is None:
        env_file = get_project_root() / ".env"
    
    if not env_file.exists():
        # Sprawdź, czy istnieje plik .env.example
        env_example = get_project_root() / ".env.example"
        
        if env_example.exists():
            # Kopiuj .env.example do .env
            shutil.copy2(env_example, env_file)
            print(f"Utworzono plik {env_file} na podstawie {env_example}")
        else:
            # Utwórz pusty plik .env
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write("# Konfiguracja projektu\n")
                f.write("PROJECT_NAME=\n")
                f.write("PACKAGE_PATH=\n")
            print(f"Utworzono pusty plik {env_file}")


def load_env_file(env_file: Path = None) -> Dict[str, str]:
    """
    Wczytuje zmienne środowiskowe z pliku .env.
    
    Args:
        env_file: Ścieżka do pliku .env. Jeśli None, używa domyślnej ścieżki.
        
    Returns:
        Słownik ze zmiennymi środowiskowymi.
    """
    if env_file is None:
        env_file = get_project_root() / ".env"
    
    # Utwórz plik .env, jeśli nie istnieje
    create_env_file_if_not_exists(env_file)
    
    env_vars = {}
    
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    
    return env_vars


def save_env_file(env_vars: Dict[str, str], env_file: Path = None) -> None:
    """
    Zapisuje zmienne środowiskowe do pliku .env.
    
    Args:
        env_vars: Słownik ze zmiennymi środowiskowymi.
        env_file: Ścieżka do pliku .env. Jeśli None, używa domyślnej ścieżki.
    """
    if env_file is None:
        env_file = get_project_root() / ".env"
    
    # Utwórz plik .env, jeśli nie istnieje
    create_env_file_if_not_exists(env_file)
    
    # Zachowaj komentarze i formatowanie z istniejącego pliku
    existing_lines = []
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            existing_lines = f.readlines()
    
    # Przygotuj nowe linie z aktualnymi wartościami
    new_lines = []
    processed_keys = set()
    
    for line in existing_lines:
        line = line.rstrip('\n')
        if not line or line.startswith('#'):
            new_lines.append(line)
            continue
        
        if '=' in line:
            key, _ = line.split('=', 1)
            key = key.strip()
            if key in env_vars:
                new_lines.append(f"{key}={env_vars[key]}")
                processed_keys.add(key)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    # Dodaj nowe zmienne, które nie były w pliku
    for key, value in env_vars.items():
        if key not in processed_keys:
            new_lines.append(f"{key}={value}")
    
    # Zapisz plik
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines) + '\n')


def get_env_var(key: str, default: Any = None, prompt: bool = True) -> str:
    """
    Pobiera wartość zmiennej środowiskowej.
    Jeśli zmienna nie istnieje, pyta użytkownika o jej wartość.
    
    Args:
        key: Nazwa zmiennej środowiskowej.
        default: Domyślna wartość, jeśli zmienna nie istnieje.
        prompt: Czy pytać użytkownika o wartość, jeśli zmienna nie istnieje.
        
    Returns:
        Wartość zmiennej środowiskowej.
    """
    env_vars = load_env_file()
    
    if key in env_vars and env_vars[key]:
        return env_vars[key]
    
    if prompt:
        if default:
            value = input(f"Podaj wartość dla {key} [{default}]: ").strip()
            if not value:
                value = default
        else:
            value = input(f"Podaj wartość dla {key}: ").strip()
            while not value:
                print("Wartość nie może być pusta.")
                value = input(f"Podaj wartość dla {key}: ").strip()
    else:
        value = default
    
    if value:
        env_vars[key] = value
        save_env_file(env_vars)
    
    return value


def get_project_name(prompt: bool = True) -> str:
    """
    Pobiera nazwę projektu z pliku .env lub pyproject.toml.
    Jeśli nazwa nie jest zdefiniowana, pyta użytkownika.
    
    Args:
        prompt: Czy pytać użytkownika, jeśli nazwa nie jest zdefiniowana.
        
    Returns:
        Nazwa projektu.
    """
    # Najpierw sprawdź w .env
    project_name = get_env_var("PROJECT_NAME", None, False)
    if project_name:
        return project_name
    
    # Jeśli nie ma w .env, sprawdź w pyproject.toml
    pyproject_path = get_project_root() / "pyproject.toml"
    if pyproject_path.exists():
        with open(pyproject_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Spróbuj znaleźć nazwę projektu za pomocą regex
        match = re.search(r'name\s*=\s*[\'"]([^\'"]+)[\'"]', content)
        if match:
            project_name = match.group(1)
            
            # Zapisz do .env
            env_vars = load_env_file()
            env_vars["PROJECT_NAME"] = project_name
            save_env_file(env_vars)
            
            return project_name
    
    # Jeśli nadal nie ma, zapytaj użytkownika
    if prompt:
        return get_env_var("PROJECT_NAME", "twinizer", True)
    
    # Jeśli wszystko zawiedzie, zwróć domyślną wartość
    return "twinizer"


def get_package_path(prompt: bool = True) -> str:
    """
    Pobiera ścieżkę do katalogu pakietu.
    Jeśli ścieżka nie jest zdefiniowana, próbuje ją wykryć automatycznie.
    
    Args:
        prompt: Czy pytać użytkownika, jeśli ścieżka nie jest zdefiniowana.
        
    Returns:
        Ścieżka do katalogu pakietu (względem katalogu głównego projektu).
    """
    # Najpierw sprawdź w .env
    package_path = get_env_var("PACKAGE_PATH", "", False)
    if package_path:
        return package_path
    
    # Jeśli nie ma w .env, spróbuj wykryć automatycznie
    project_name = get_project_name(False)
    
    # Sprawdź, czy pakiet jest w src/project_name
    src_path = get_project_root() / "src" / project_name
    if src_path.exists():
        package_path = f"src/{project_name}"
        
        # Zapisz do .env
        env_vars = load_env_file()
        env_vars["PACKAGE_PATH"] = package_path
        save_env_file(env_vars)
        
        return package_path
    
    # Sprawdź, czy pakiet jest bezpośrednio w katalogu głównym projektu
    root_path = get_project_root() / project_name
    if root_path.exists():
        package_path = project_name
        
        # Zapisz do .env
        env_vars = load_env_file()
        env_vars["PACKAGE_PATH"] = package_path
        save_env_file(env_vars)
        
        return package_path
    
    # Jeśli nadal nie ma, zapytaj użytkownika
    if prompt:
        return get_env_var("PACKAGE_PATH", project_name, True)
    
    # Jeśli wszystko zawiedzie, zwróć domyślną wartość
    return project_name


def get_version_files():
    """Get a list of files that contain version information."""
    project_name = get_project_name()
    package_path = get_package_path()
    
    # Konwertuj względną ścieżkę pakietu na bezwzględną
    if package_path:
        package_path = os.path.join(get_project_root(), package_path)
    else:
        package_path = os.path.join(get_project_root(), project_name)
    
    # Common files that contain version information
    version_files = [
        os.path.join(get_project_root(), "pyproject.toml"),
    ]
    
    # Dodaj pliki specyficzne dla pakietu
    init_file = os.path.join(package_path, "__init__.py")
    version_file = os.path.join(package_path, "_version.py")
    
    if os.path.exists(init_file):
        version_files.append(init_file)
    
    if os.path.exists(version_file):
        version_files.append(version_file)
    
    # Filter out files that don't exist
    return [f for f in version_files if os.path.exists(f)]


if __name__ == "__main__":
    # Utwórz plik .env, jeśli nie istnieje
    env_file = get_project_root() / ".env"
    create_env_file_if_not_exists(env_file)
    
    # Wypisz informacje o projekcie
    print(f"Nazwa projektu: {get_project_name()}")
    print(f"Ścieżka pakietu: {get_package_path()}")
    print(f"Pliki z wersją: {get_version_files()}")
