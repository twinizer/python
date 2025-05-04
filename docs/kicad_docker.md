# Konwersja plików KiCad przy użyciu Dockera

Twinizer oferuje zaawansowane możliwości konwersji plików KiCad do różnych formatów oraz analizy projektów KiCad przy użyciu Dockera. Ta funkcjonalność jest zintegrowana z projektem `docker-kicad.sh` z katalogu `docker/ready-image`.

## Spis treści

- [Wymagania](#wymagania)
- [Dostępne formaty](#dostępne-formaty)
- [Używanie z CLI](#używanie-z-cli)
- [Używanie w kodzie Python](#używanie-w-kodzie-python)
- [Analiza projektów KiCad](#analiza-projektów-kicad)
- [Przykłady](#przykłady)
- [Rozwiązywanie problemów](#rozwiązywanie-problemów)

## Wymagania

Aby korzystać z funkcji konwersji plików KiCad przy użyciu Dockera, musisz mieć zainstalowane:

1. Docker - [instrukcje instalacji](https://docs.docker.com/get-docker/)
2. Python 3.6 lub nowszy
3. Twinizer (ten projekt)

Docker musi być uruchomiony i dostępny dla użytkownika, który uruchamia Twinizer.

## Dostępne formaty

Twinizer obsługuje konwersję plików KiCad do następujących formatów:

| Format | Opis | Opcje |
|--------|------|-------|
| SVG | Scalable Vector Graphics | - |
| PNG | Portable Network Graphics | - |
| PDF | Portable Document Format | Motyw kolorów, rozmiar papieru, orientacja |
| DXF | Drawing Exchange Format | - |
| HPGL | HP Graphics Language | - |
| PS | PostScript | - |
| EPS | Encapsulated PostScript | - |

## Używanie z CLI

Twinizer udostępnia grupę komend `kicad-docker` do konwersji plików KiCad i analizy projektów:

### Konwersja pliku KiCad

```bash
python -m twinizer kicad-docker convert <plik_wejściowy> [opcje]
```

Opcje:
- `--format`, `-f`: Format wyjściowy (svg, png, pdf, dxf, hpgl, ps, eps), domyślnie: svg
- `--output`, `-o`: Ścieżka pliku wyjściowego
- `--color-theme`, `-c`: Motyw kolorów dla PDF (light, dark), domyślnie: light
- `--paper-size`, `-p`: Rozmiar papieru dla PDF (A4, A3, itp.), domyślnie: A4
- `--orientation`, `-r`: Orientacja strony dla PDF (portrait, landscape), domyślnie: portrait
- `--debug`, `-d`: Włącz tryb debugowania do analizy projektu
- `--verbose`, `-v`: Włącz szczegółowe logowanie

### Analiza projektu KiCad

```bash
python -m twinizer kicad-docker analyze <katalog_projektu> [opcje]
```

Opcje:
- `--format`, `-f`: Format wyjściowy (json, html), domyślnie: html
- `--output`, `-o`: Ścieżka pliku wyjściowego
- `--verbose`, `-v`: Włącz szczegółowe logowanie

### Lista wspieranych formatów

```bash
python -m twinizer kicad-docker formats
```

## Używanie w kodzie Python

Możesz również używać funkcji konwersji plików KiCad bezpośrednio w kodzie Python:

```python
from twinizer.converters.kicad2image import convert_kicad_file, analyze_kicad_project

# Konwersja pliku KiCad do SVG
result = convert_kicad_file(
    input_file="projekt.kicad_sch",
    output_format="svg",
    output_path="projekt.svg"
)

# Konwersja do PDF z niestandardowymi opcjami
result = convert_kicad_file(
    input_file="projekt.kicad_sch",
    output_format="pdf",
    output_path="projekt.pdf",
    color_theme="dark",
    paper_size="A3",
    orientation="landscape"
)

# Analiza projektu KiCad
result = analyze_kicad_project(
    project_dir="katalog_projektu",
    output_format="html",
    output_path="raport.html"
)
```

## Analiza projektów KiCad

Funkcja analizy projektów KiCad pozwala na wykrywanie brakujących zależności w projekcie KiCad, takich jak:

- Brakujące biblioteki symboli
- Brakujące modele 3D
- Brakujące footprinty
- Inne problemy z projektem

Raport analizy może być generowany w formacie JSON lub HTML. Format HTML zawiera interaktywny raport z możliwością filtrowania i sortowania wyników.

## Przykłady

### Przykład 1: Konwersja schematu KiCad do SVG

```bash
python -m twinizer kicad-docker convert projekt.kicad_sch --format svg --output projekt.svg
```

### Przykład 2: Konwersja schematu KiCad do PDF z niestandardowymi opcjami

```bash
python -m twinizer kicad-docker convert projekt.kicad_sch --format pdf --output projekt.pdf --color-theme dark --paper-size A3 --orientation landscape
```

### Przykład 3: Analiza projektu KiCad

```bash
python -m twinizer kicad-docker analyze katalog_projektu --format html --output raport.html
```

### Przykład 4: Konwersja wielu plików KiCad

Zobacz przykładowy skrypt `examples/kicad_docker_conversion.py` dla przykładu konwersji wielu plików KiCad w projekcie.

## Rozwiązywanie problemów

### Problem: Docker nie jest zainstalowany lub uruchomiony

Upewnij się, że Docker jest zainstalowany i uruchomiony. Możesz sprawdzić to komendą:

```bash
docker --version
docker ps
```

### Problem: Brak uprawnień do uruchomienia Dockera

Upewnij się, że użytkownik ma uprawnienia do uruchamiania kontenerów Docker. Możesz dodać użytkownika do grupy docker:

```bash
sudo usermod -aG docker $USER
```

Po wykonaniu tej komendy, wyloguj się i zaloguj ponownie.

### Problem: Konwersja nie działa dla niektórych formatów

Upewnij się, że używasz najnowszej wersji KiCad w kontenerze Docker. Niektóre formaty mogą nie być obsługiwane przez starsze wersje KiCad.

### Problem: Błędy podczas analizy projektu

Upewnij się, że katalog projektu zawiera pliki KiCad (.kicad_sch, .kicad_pcb, .kicad_pro). Analiza projektu wymaga co najmniej jednego pliku projektu KiCad.

---

Więcej informacji na temat konwersji plików KiCad przy użyciu Dockera znajdziesz w [dokumentacji projektu docker-kicad.sh](../docker/ready-image/README.md).
