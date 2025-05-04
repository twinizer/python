#!/usr/bin/env python3
"""
Skrypt do automatycznej instalacji KiCad w różnych systemach operacyjnych.
Wspiera: Ubuntu/Debian, Fedora, Arch Linux, macOS i Windows.
"""

import os
import platform
import subprocess
import sys
import shutil
import tempfile
from pathlib import Path


def is_tool_installed(name):
    """Sprawdza, czy narzędzie jest zainstalowane w systemie."""
    return shutil.which(name) is not None


def is_kicad_installed():
    """Sprawdza, czy KiCad jest już zainstalowany."""
    if platform.system() == "Windows":
        # Sprawdź typowe lokalizacje instalacji KiCad na Windows
        common_paths = [
            r"C:\Program Files\KiCad\bin\kicad.exe",
            r"C:\Program Files (x86)\KiCad\bin\kicad.exe",
        ]
        return any(os.path.exists(path) for path in common_paths) or is_tool_installed("kicad")
    else:
        # Na Linux/macOS sprawdź, czy kicad jest dostępny w PATH
        return is_tool_installed("kicad") or is_tool_installed("kicad-cli")


def is_docker_available():
    """Sprawdza, czy Docker jest dostępny w systemie."""
    try:
        subprocess.run(
            ["docker", "--version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            check=True
        )
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def run_command(command, shell=False):
    """Uruchamia komendę i wyświetla jej wyjście."""
    print(f"Wykonuję: {' '.join(command) if isinstance(command, list) else command}")
    
    try:
        if shell:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
        else:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
        
        # Wyświetlaj wyjście w czasie rzeczywistym
        for line in iter(process.stdout.readline, ''):
            print(line.strip())
        
        process.stdout.close()
        return_code = process.wait()
        
        if return_code != 0:
            print(f"Komenda zakończyła się błędem (kod: {return_code})")
            return False
        return True
    
    except Exception as e:
        print(f"Błąd podczas wykonywania komendy: {e}")
        return False


def install_kicad_ubuntu():
    """Instaluje KiCad na Ubuntu/Debian."""
    print("Instalacja KiCad na Ubuntu/Debian...")
    
    # Najpierw spróbuj z PPA (najnowsza wersja)
    commands = [
        ["sudo", "add-apt-repository", "-y", "ppa:kicad/kicad-7.0-releases"],
        ["sudo", "apt-get", "update"],
        ["sudo", "apt-get", "install", "-y", "kicad"]
    ]
    
    for cmd in commands:
        if not run_command(cmd):
            # Jeśli PPA nie zadziała, spróbuj z repozytoriów standardowych
            print("Instalacja z PPA nie powiodła się, próbuję z repozytoriów standardowych...")
            if not run_command(["sudo", "apt-get", "install", "-y", "kicad"]):
                return False
    
    return True


def install_kicad_fedora():
    """Instaluje KiCad na Fedora."""
    print("Instalacja KiCad na Fedora...")
    return run_command(["sudo", "dnf", "install", "-y", "kicad", "kicad-packages3d"])


def install_kicad_arch():
    """Instaluje KiCad na Arch Linux."""
    print("Instalacja KiCad na Arch Linux...")
    return run_command(["sudo", "pacman", "-S", "--noconfirm", "kicad"])


def install_kicad_macos():
    """Instaluje KiCad na macOS przy użyciu Homebrew."""
    print("Instalacja KiCad na macOS...")
    
    # Sprawdź, czy Homebrew jest zainstalowany
    if not is_tool_installed("brew"):
        print("Homebrew nie jest zainstalowany. Instaluję Homebrew...")
        brew_install_cmd = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        if not run_command(brew_install_cmd, shell=True):
            return False
    
    # Instaluj KiCad
    return run_command(["brew", "install", "--cask", "kicad"])


def install_kicad_windows():
    """Instaluje KiCad na Windows."""
    print("Instalacja KiCad na Windows...")
    
    # URL do najnowszej wersji KiCad
    kicad_url = "https://downloads.kicad.org/kicad/windows/explore/stable"
    
    # Pobierz stronę z listą plików
    try:
        import urllib.request
        import re
        
        print(f"Pobieram listę dostępnych wersji z {kicad_url}...")
        with urllib.request.urlopen(kicad_url) as response:
            html = response.read().decode('utf-8')
        
        # Znajdź najnowszy instalator 64-bit
        pattern = r'href="([^"]+kicad-[^"]+win64[^"]+\.exe)"'
        matches = re.findall(pattern, html)
        
        if not matches:
            print("Nie znaleziono instalatora KiCad.")
            return False
        
        # Pobierz pierwszy (najnowszy) instalator
        installer_url = matches[0]
        if not installer_url.startswith('http'):
            installer_url = f"https://downloads.kicad.org{installer_url}"
        
        # Pobierz instalator
        temp_dir = tempfile.gettempdir()
        installer_path = os.path.join(temp_dir, "kicad_installer.exe")
        
        print(f"Pobieram instalator KiCad z {installer_url}...")
        urllib.request.urlretrieve(installer_url, installer_path)
        
        # Uruchom instalator
        print(f"Uruchamiam instalator KiCad...")
        os.startfile(installer_path)
        
        print("Instalator KiCad został uruchomiony. Postępuj zgodnie z instrukcjami na ekranie.")
        print("Po zakończeniu instalacji, uruchom ponownie skrypt.")
        return True
        
    except Exception as e:
        print(f"Błąd podczas instalacji KiCad: {e}")
        print("Proszę zainstalować KiCad ręcznie ze strony: https://www.kicad.org/download/windows/")
        return False


def install_docker():
    """Instaluje Docker na różnych systemach."""
    system = platform.system()
    
    if system == "Linux":
        # Sprawdź dystrybucję
        try:
            with open('/etc/os-release') as f:
                os_release = f.read()
                
            if 'ID=ubuntu' in os_release or 'ID=debian' in os_release:
                print("Instalacja Docker na Ubuntu/Debian...")
                commands = [
                    ["sudo", "apt-get", "update"],
                    ["sudo", "apt-get", "install", "-y", "ca-certificates", "curl", "gnupg"],
                    ["sudo", "install", "-m", "0755", "-d", "/etc/apt/keyrings"],
                    'sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc',
                    'echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null',
                    ["sudo", "apt-get", "update"],
                    ["sudo", "apt-get", "install", "-y", "docker-ce", "docker-ce-cli", "containerd.io"]
                ]
                
                for cmd in commands:
                    if isinstance(cmd, str):
                        if not run_command(cmd, shell=True):
                            return False
                    else:
                        if not run_command(cmd):
                            return False
                
                # Dodaj użytkownika do grupy docker
                run_command(["sudo", "usermod", "-aG", "docker", os.environ.get('USER', '')])
                print("Docker został zainstalowany. Wyloguj się i zaloguj ponownie, aby zastosować zmiany w grupach.")
                return True
                
            elif 'ID=fedora' in os_release:
                print("Instalacja Docker na Fedora...")
                commands = [
                    ["sudo", "dnf", "install", "-y", "dnf-plugins-core"],
                    ["sudo", "dnf", "config-manager", "--add-repo", "https://download.docker.com/linux/fedora/docker-ce.repo"],
                    ["sudo", "dnf", "install", "-y", "docker-ce", "docker-ce-cli", "containerd.io"]
                ]
                
                for cmd in commands:
                    if not run_command(cmd):
                        return False
                
                # Uruchom i włącz usługę Docker
                run_command(["sudo", "systemctl", "start", "docker"])
                run_command(["sudo", "systemctl", "enable", "docker"])
                
                # Dodaj użytkownika do grupy docker
                run_command(["sudo", "usermod", "-aG", "docker", os.environ.get('USER', '')])
                print("Docker został zainstalowany. Wyloguj się i zaloguj ponownie, aby zastosować zmiany w grupach.")
                return True
                
            elif 'ID=arch' in os_release:
                print("Instalacja Docker na Arch Linux...")
                if not run_command(["sudo", "pacman", "-S", "--noconfirm", "docker"]):
                    return False
                
                # Uruchom i włącz usługę Docker
                run_command(["sudo", "systemctl", "start", "docker"])
                run_command(["sudo", "systemctl", "enable", "docker"])
                
                # Dodaj użytkownika do grupy docker
                run_command(["sudo", "usermod", "-aG", "docker", os.environ.get('USER', '')])
                print("Docker został zainstalowany. Wyloguj się i zaloguj ponownie, aby zastosować zmiany w grupach.")
                return True
        
        except Exception as e:
            print(f"Nie udało się określić dystrybucji Linux: {e}")
            print("Proszę zainstalować Docker ręcznie: https://docs.docker.com/engine/install/")
            return False
    
    elif system == "Darwin":  # macOS
        print("Instalacja Docker na macOS...")
        
        # Sprawdź, czy Homebrew jest zainstalowany
        if not is_tool_installed("brew"):
            print("Homebrew nie jest zainstalowany. Instaluję Homebrew...")
            brew_install_cmd = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
            if not run_command(brew_install_cmd, shell=True):
                return False
        
        # Instaluj Docker Desktop
        return run_command(["brew", "install", "--cask", "docker"])
    
    elif system == "Windows":
        print("Instalacja Docker na Windows...")
        print("Proszę zainstalować Docker Desktop ręcznie ze strony:")
        print("https://www.docker.com/products/docker-desktop/")
        return False
    
    else:
        print(f"Nieobsługiwany system operacyjny: {system}")
        return False


def setup_docker_kicad():
    """Konfiguruje skrypt Docker do konwersji plików KiCad."""
    print("Konfiguracja skryptu Docker do konwersji plików KiCad...")
    
    # Ścieżka do katalogu głównego projektu
    project_root = Path(__file__).resolve().parent.parent.parent
    docker_script_dir = project_root / "docker" / "ready-image"
    
    if not docker_script_dir.exists():
        print(f"Katalog {docker_script_dir} nie istnieje.")
        return False
    
    # Sprawdź, czy skrypt docker-kicad.sh istnieje
    docker_script = docker_script_dir / "docker-kicad.sh"
    if not docker_script.exists():
        print(f"Skrypt {docker_script} nie istnieje.")
        return False
    
    # Nadaj uprawnienia wykonywania
    try:
        docker_script.chmod(docker_script.stat().st_mode | 0o111)  # Dodaj uprawnienia wykonywania
        print(f"Nadano uprawnienia wykonywania dla {docker_script}")
        return True
    except Exception as e:
        print(f"Błąd podczas nadawania uprawnień: {e}")
        return False


def main():
    """Główna funkcja instalacyjna."""
    print("=" * 60)
    print("Instalator KiCad")
    print("=" * 60)
    
    # Sprawdź, czy KiCad jest już zainstalowany
    if is_kicad_installed():
        print("KiCad jest już zainstalowany w systemie.")
    else:
        print("KiCad nie jest zainstalowany. Rozpoczynam instalację...")
        
        # Identyfikuj system operacyjny i zainstaluj KiCad
        system = platform.system()
        
        if system == "Linux":
            # Identyfikuj dystrybucję Linux
            try:
                with open('/etc/os-release') as f:
                    os_release = f.read()
                
                if 'ID=ubuntu' in os_release or 'ID=debian' in os_release:
                    install_kicad_ubuntu()
                elif 'ID=fedora' in os_release:
                    install_kicad_fedora()
                elif 'ID=arch' in os_release:
                    install_kicad_arch()
                else:
                    print(f"Nieobsługiwana dystrybucja Linux. Proszę zainstalować KiCad ręcznie.")
                    print("Alternatywnie, możesz użyć Docker do konwersji plików KiCad.")
            
            except Exception as e:
                print(f"Nie udało się określić dystrybucji Linux: {e}")
                print("Proszę zainstalować KiCad ręcznie lub użyć Docker.")
        
        elif system == "Darwin":  # macOS
            install_kicad_macos()
        
        elif system == "Windows":
            install_kicad_windows()
        
        else:
            print(f"Nieobsługiwany system operacyjny: {system}")
    
    # Sprawdź, czy Docker jest dostępny
    if not is_docker_available():
        print("\nDocker nie jest zainstalowany. Docker umożliwia konwersję plików KiCad bez instalacji KiCad.")
        
        install_docker_prompt = input("Czy chcesz zainstalować Docker? (t/n): ").lower()
        if install_docker_prompt in ['t', 'tak', 'y', 'yes']:
            install_docker()
    else:
        print("\nDocker jest już zainstalowany.")
        
        # Konfiguruj skrypt Docker
        setup_docker_kicad()
    
    print("\nKonfiguracja zakończona.")
    print("Możesz teraz używać KiCad lub skryptu Docker do konwersji plików KiCad.")
    print("=" * 60)


if __name__ == "__main__":
    main()
