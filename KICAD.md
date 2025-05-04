

## Jak zainstalować i uruchomić Dockera (jeśli jeszcze nie masz)

- Na Linuxie (np. Ubuntu/Debian) instalacja Dockera to kilka komend:

```bash
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg lsb-release
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io
```

- Sprawdź działanie Dockera komendą:

```bash
sudo docker run hello-world
```

Więcej szczegółów instalacji Dockera znajdziesz w poradnikach[4][5].

## Podsumowanie

- Jeśli chcesz używać KiCada w trybie CLI (np. do eksportu plików), skorzystaj z oficjalnego obrazu KiCad dostępnego na Docker Hub.
- Jeśli chcesz mieć dostęp do pełnego GUI KiCada w Dockerze, użyj obrazu LinuxServer.io, który udostępnia KiCada przez VNC w przeglądarce.
- Uruchomienie GUI wymaga mapowania portów i ustawienia zmiennych środowiskowych.
- GUI w oficjalnym obrazie KiCad nie jest wspierane.
Aby zainstalować i używać KiCada na systemie Fedora, masz kilka opcji:

## Instalacja stabilnej wersji KiCad na Fedorze

1. Najprostszy sposób to instalacja z oficjalnych repozytoriów Fedory:
```bash
sudo dnf install kicad kicad-packages3d kicad-doc
```
- `kicad` – główny program
- `kicad-packages3d` – modele 3D (od wersji 5.0.0 są w osobnym pakiecie)
- `kicad-doc` – dokumentacja

2. Jeśli najnowsza wersja KiCada nie jest jeszcze dostępna w standardowym repozytorium, możesz zainstalować ją z repozytorium testowego:
```bash
sudo dnf --enablerepo=updates-testing install kicad
```

## Aktualizacja lub instalacja najnowszej wersji KiCad 7 przez Copr

- Włącz repozytorium Copr KiCada:
```bash
sudo dnf install dnf-plugins-core
sudo dnf copr enable @kicad/kicad
```

- Następnie zainstaluj lub zaktualizuj KiCada:
  - Jeśli nie miałeś wcześniej KiCada 6:
  ```bash
  sudo dnf install kicad
  ```
  - Jeśli masz KiCada 6 i chcesz zaktualizować do 7:
  ```bash
  sudo dnf upgrade kicad
  ```

- Możesz też zainstalować pakiety 3D i dokumentację tak jak powyżej.

## Instalacja wersji nightly (rozwojowej)

- Aby zainstalować najnowsze buildy rozwojowe:
```bash
sudo dnf install dnf-plugins-core
sudo dnf copr enable @kicad/kicad
sudo dnf install kicad-nightly
sudo dnf install kicad-nightly-packages3d
```

## Alternatywa: instalacja KiCad przez Flatpak

- Fedora wspiera Flatpak, który pozwala na instalację najnowszej wersji KiCad niezależnie od wersji systemu:
```bash
flatpak install flathub org.kicad_pcb.KiCad
flatpak run org.kicad_pcb.KiCad
```

## Dodatkowe informacje

- Możesz także doinstalować narzędzia powiązane, np. `ngspice`:
```bash
sudo dnf install ngspice
```

- Więcej informacji i szczegółowe instrukcje znajdziesz na oficjalnej stronie KiCad dla Fedory[1].

---

Podsumowując, najprościej jest zainstalować KiCada z repozytorium Fedory przez `dnf install kicad`, a jeśli chcesz najnowszą wersję, użyć repozytorium Copr lub Flatpak[1].

Citations:
[1] https://www.kicad.org/download/details/fedora/
[2] https://www.kicad.org/download/linux/
[3] https://snapcraft.io/install/kicad/fedora
[4] https://forum.kicad.info/t/install-ngspice-on-fedora/38354
[5] https://startingelectronics.org/articles/how-to-install-KiCad-Linux/
[6] https://dev-docs.kicad.org/en/build/linux/index.html
[7] https://www.youtube.com/watch?v=tMs9MtY9kH4
[8] https://discussion.fedoraproject.org/t/kicad-kicad-stable/82645

