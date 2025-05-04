#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Przykład użycia konwertera KiCad Docker w projekcie twinizer.

Ten przykład pokazuje, jak używać modułu kicad2image do konwersji
plików KiCad do różnych formatów oraz analizy projektów KiCad.
"""

import os
import sys
import argparse
from pathlib import Path

# Dodaj ścieżkę do katalogu src, aby można było zaimportować moduły twinizer
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from twinizer.converters.kicad2image import (
    convert_kicad_file,
    analyze_kicad_project,
    list_supported_formats
)
from rich.console import Console
from rich.table import Table

console = Console()


def convert_example(input_file, output_format="svg"):
    """
    Przykład konwersji pliku KiCad do wybranego formatu.
    
    Args:
        input_file: Ścieżka do pliku KiCad (.sch, .kicad_sch, .kicad_pcb)
        output_format: Format wyjściowy (svg, png, pdf, dxf, hpgl, ps, eps)
    """
    console.print(f"[bold cyan]Przykład konwersji pliku KiCad do formatu {output_format}[/bold cyan]")
    
    # Określ ścieżkę wyjściową
    output_path = f"{os.path.splitext(input_file)[0]}.{output_format}"
    
    # Parametry specyficzne dla formatu PDF
    color_theme = "light"
    paper_size = "A4"
    orientation = "portrait"
    
    # Konwersja pliku
    result = convert_kicad_file(
        input_file=input_file,
        output_format=output_format,
        output_path=output_path,
        color_theme=color_theme,
        paper_size=paper_size,
        orientation=orientation,
        verbose=True
    )
    
    if result:
        console.print(f"[green]Konwersja zakończona sukcesem![/green]")
        console.print(f"Plik wyjściowy: [cyan]{result}[/cyan]")
    else:
        console.print("[red]Konwersja nie powiodła się.[/red]")


def analyze_example(project_dir):
    """
    Przykład analizy projektu KiCad.
    
    Args:
        project_dir: Ścieżka do katalogu projektu KiCad
    """
    console.print(f"[bold cyan]Przykład analizy projektu KiCad[/bold cyan]")
    
    # Określ ścieżkę wyjściową dla raportu HTML
    output_path = os.path.join(project_dir, "analysis_report.html")
    
    # Analiza projektu
    result = analyze_kicad_project(
        project_dir=project_dir,
        output_format="html",
        output_path=output_path,
        verbose=True
    )
    
    if result:
        console.print(f"[green]Analiza zakończona sukcesem![/green]")
        console.print(f"Raport HTML: [cyan]{result}[/cyan]")
        
        # Próba otwarcia raportu HTML w przeglądarce
        try:
            import webbrowser
            webbrowser.open(f"file://{os.path.abspath(result)}")
        except Exception as e:
            console.print(f"[yellow]Nie można otworzyć przeglądarki: {e}[/yellow]")
    else:
        console.print("[red]Analiza nie powiodła się.[/red]")


def batch_convert_example(project_dir, output_format="svg"):
    """
    Przykład konwersji wielu plików KiCad w projekcie.
    
    Args:
        project_dir: Ścieżka do katalogu projektu KiCad
        output_format: Format wyjściowy (svg, png, pdf, dxf, hpgl, ps, eps)
    """
    console.print(f"[bold cyan]Przykład konwersji wielu plików KiCad do formatu {output_format}[/bold cyan]")
    
    # Znajdź wszystkie pliki KiCad w katalogu projektu
    kicad_files = []
    for ext in [".sch", ".kicad_sch", ".kicad_pcb"]:
        kicad_files.extend(list(Path(project_dir).glob(f"**/*{ext}")))
    
    if not kicad_files:
        console.print(f"[yellow]Nie znaleziono plików KiCad w katalogu {project_dir}[/yellow]")
        return
    
    console.print(f"Znaleziono [green]{len(kicad_files)}[/green] plików KiCad do konwersji")
    
    # Konwersja każdego pliku
    for file_path in kicad_files:
        console.print(f"Konwersja pliku: [cyan]{file_path}[/cyan]")
        
        # Określ ścieżkę wyjściową
        output_path = f"{os.path.splitext(file_path)[0]}.{output_format}"
        
        # Konwersja pliku
        result = convert_kicad_file(
            input_file=str(file_path),
            output_format=output_format,
            output_path=str(output_path),
            verbose=False
        )
        
        if result:
            console.print(f"  ✓ [green]Sukces![/green] Plik wyjściowy: [cyan]{result}[/cyan]")
        else:
            console.print(f"  ✗ [red]Błąd![/red] Konwersja pliku {file_path} nie powiodła się")


def show_formats():
    """
    Wyświetla listę wspieranych formatów wyjściowych.
    """
    console.print("[bold cyan]Wspierane formaty wyjściowe[/bold cyan]")
    
    formats = list_supported_formats()
    
    # Utwórz tabelę z formatami
    table = Table()
    table.add_column("Format", style="cyan")
    table.add_column("Opis", style="green")
    table.add_column("Domyślny", style="yellow")
    table.add_column("Opcje", style="blue")
    
    # Dodaj wiersze do tabeli
    for fmt in formats:
        default = "✓" if fmt.get("default", False) else ""
        options = ", ".join(fmt.get("options", []))
        table.add_row(fmt["format"], fmt["description"], default, options)
    
    console.print(table)


def main():
    """
    Główna funkcja przykładu.
    """
    parser = argparse.ArgumentParser(description="Przykład użycia konwertera KiCad Docker w projekcie twinizer")
    parser.add_argument("--convert", type=str, help="Konwertuj plik KiCad do wybranego formatu")
    parser.add_argument("--format", type=str, default="svg", help="Format wyjściowy (svg, png, pdf, dxf, hpgl, ps, eps)")
    parser.add_argument("--analyze", type=str, help="Analizuj projekt KiCad")
    parser.add_argument("--batch", type=str, help="Konwertuj wszystkie pliki KiCad w katalogu")
    parser.add_argument("--formats", action="store_true", help="Wyświetl wspierane formaty wyjściowe")
    
    args = parser.parse_args()
    
    if args.formats:
        show_formats()
    elif args.convert:
        convert_example(args.convert, args.format)
    elif args.analyze:
        analyze_example(args.analyze)
    elif args.batch:
        batch_convert_example(args.batch, args.format)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
