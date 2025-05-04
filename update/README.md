# update/

Skrypty do aktualizacji wersji, zarządzania zmianami i publikacji pakietu.

## Zawartość
- `version.sh` — główny skrypt do aktualizacji wersji i publikacji pakietu
- `src.py` — skrypt do aktualizacji numeru wersji w plikach źródłowych
- `changelog.py` — skrypt do generowania i aktualizacji pliku CHANGELOG.md
- `git.sh` — skrypt do publikacji nowej wersji na GitHub
- `pypi.sh` — skrypt do publikacji pakietu na PyPI
- `env_manager.py` — moduł do zarządzania konfiguracją projektu
- `config.py` — moduł konfiguracyjny dla skryptów aktualizacyjnych

## Konfiguracja projektu

Konfiguracja projektu jest przechowywana w pliku `.env` w głównym katalogu projektu. Plik ten jest tworzony automatycznie przy pierwszym uruchomieniu skryptów, na podstawie pliku `.env.example`.

Dostępne zmienne konfiguracyjne:
- `PROJECT_NAME` — nazwa projektu
- `PACKAGE_PATH` — ścieżka do katalogu pakietu (względem katalogu głównego projektu)

Jeśli plik `.env` nie istnieje lub zmienne nie są zdefiniowane, skrypty spróbują wykryć wartości automatycznie lub zapytają użytkownika.

## Użycie

Aby zaktualizować wersję i opublikować pakiet:

```bash
# Uruchom główny skrypt aktualizacji
bash update/version.sh
```

Skrypt wykona następujące operacje:
1. Wczyta konfigurację projektu z pliku `.env` lub zapyta użytkownika
2. Utworzy i aktywuje środowisko wirtualne
3. Zaktualizuje numer wersji w plikach źródłowych
4. Wygeneruje wpis w CHANGELOG.md
5. Opublikuje zmiany na GitHub
6. Opublikuje pakiet na PyPI

## Rozwiązywanie problemów

Jeśli podczas publikacji na GitHub pojawi się błąd:
```
Updates were rejected because the remote contains work that you do not have locally
```

Należy wykonać `git pull` przed ponownym uruchomieniem skryptu:
```bash
git pull
bash update/version.sh
```

Jeśli tag już istnieje:
```
fatal: tag 'vX.Y.Z' already exists
```

Należy usunąć istniejący tag przed ponownym uruchomieniem skryptu:
```bash
git tag -d vX.Y.Z
git push origin --delete vX.Y.Z
bash update/version.sh
```

## Zarządzanie konfiguracją

Aby ręcznie utworzyć lub zaktualizować plik `.env`:

```bash
python update/env_manager.py
```

Skrypt wyświetli aktualną konfigurację projektu i utworzy plik `.env`, jeśli nie istnieje.
