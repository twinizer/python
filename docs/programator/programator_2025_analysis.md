# Programator_2025 - Analiza i Dokumentacja

## Przegląd projektu

Programator_2025 to zaawansowany system programowania i kontroli urządzeń opartych na mikrokontrolerach MSP430. Projekt składa się z dwóch głównych modułów sprzętowych:

1. **TMC_V200** - Jednostka główna (kontroler)
2. **TMD_V100** - Moduł wyświetlacza

System wykorzystuje architekturę mikrokontrolera MSP430x5xx i jest kompilowany przy użyciu narzędzi GCC dla MSP430.

## Struktura projektu

Projekt zawiera łącznie ponad 120 plików zorganizowanych w następującej strukturze:

```
Programator_2025/
├── TMC_V200/ - Moduł jednostki głównej
├── TMD_V100/ - Moduł wyświetlacza
├── lib/ - Biblioteki wspólne
│   ├── Boards/ - Konfiguracja płyt
│   ├── Display/ - Sterowniki wyświetlacza
│   ├── Interface_txt/ - Interfejs tekstowy
│   ├── Menu/ - System menu
│   ├── MSP430x5xx/ - Sterowniki mikrokontrolera
│   └── my_lib/ - Biblioteki własne
├── Skrypty konfiguracyjne i programujące
└── Pliki wykonywalne i konfiguracyjne
```

## Główne komponenty systemu

### 1. Moduł TMC_V200 (Jednostka główna)

Moduł TMC_V200 pełni rolę jednostki głównej systemu i odpowiada za:

- Komunikację z urządzeniami zewnętrznymi przez interfejs UART
- Obsługę wejść/wyjść cyfrowych i analogowych
- Zarządzanie czasem systemowym (RTC)
- Komunikację z modułem wyświetlacza (TMD_V100)

Główne funkcje modułu TMC_V200:
- Obsługa protokołu komunikacyjnego MSBus
- Sterowanie wyjściami cyfrowymi (BO - Binary Outputs)
- Odczyt wejść analogowych (AI - Analog Inputs)
- Sterowanie wyjściami analogowymi (AO - Analog Outputs)
- Zarządzanie czasem systemowym (TM - Time Management)
- Komunikacja z wyświetlaczem

### 2. Moduł TMD_V100 (Wyświetlacz)

Moduł TMD_V100 odpowiada za interfejs użytkownika i zawiera:

- Wyświetlacz LCD (WH4004A)
- Przyciski sterujące
- Enkoder obrotowy (pokrętło)

Główne funkcje modułu TMD_V100:
- Wyświetlanie informacji na ekranie LCD
- Odczyt stanu przycisków
- Odczyt położenia enkodera obrotowego
- Komunikacja z jednostką główną przez interfejs UART

### 3. Biblioteki systemowe

Projekt zawiera rozbudowany zestaw bibliotek, które można podzielić na następujące kategorie:

#### Biblioteki sprzętowe (HAL - Hardware Abstraction Layer)
- **HAL_Board** - Konfiguracja płyty głównej
- **HAL_PMM** - Zarządzanie zasilaniem (Power Management Module)
- **HAL_UCS** - Konfiguracja zegarów systemowych (Unified Clock System)
- **HAL_RTC** - Zegar czasu rzeczywistego (Real-Time Clock)
- **HAL_UART** - Komunikacja szeregowa
- **HAL_Flash** - Obsługa pamięci Flash

#### Biblioteki wyświetlacza
- **WH4004A** - Sterownik wyświetlacza LCD

#### Biblioteki komunikacyjne
- **msbus** - Protokół komunikacyjny MSBus

#### Biblioteki pomocnicze
- **numberFixedPoint** - Obsługa liczb zmiennoprzecinkowych o stałej precyzji
- **my_string** - Funkcje do obsługi łańcuchów znaków
- **Calendar** - Funkcje kalendarza
- **Fifo** - Implementacja kolejki FIFO

## Protokół komunikacyjny MSBus

System wykorzystuje własny protokół komunikacyjny MSBus do wymiany danych między modułami oraz z urządzeniami zewnętrznymi. Protokół ten bazuje na komunikacji tekstowej przez interfejs UART.

### Główne komendy protokołu MSBus:

#### Moduł TMC_V200:
- **SDS:** - Ustawienie tekstu na wyświetlaczu
- **SBO:** - Sterowanie wyjściami cyfrowymi
- **SAO:** - Sterowanie wyjściami analogowymi
- **STM:** - Ustawienie czasu systemowego
- **GTM:** - Odczyt czasu systemowego
- **GDS:** - Odczyt tekstu z wyświetlacza
- **GAI:** - Odczyt wejść analogowych
- **GKN:** - Odczyt stanu pokrętła
- **GBT:** - Odczyt stanu przycisków

#### Moduł TMD_V100:
- **SDS:** - Wyświetlenie tekstu na LCD
- **GKN:** - Odczyt stanu pokrętła
- **GBT:** - Odczyt stanu przycisków

## Narzędzia programistyczne

Projekt zawiera zestaw skryptów ułatwiających programowanie i konfigurację systemu:

1. **init.sh** - Inicjalizacja plików konfiguracyjnych
2. **detect.sh** - Wykrywanie i konfiguracja programatora
3. **program.sh** - Kompilacja i programowanie mikrokontrolera
4. **mspdebug.sh** - Instalacja narzędzia mspdebug

## Konfiguracja sprzętowa

### Moduł TMC_V200
- Mikrokontroler: MSP430x5xx
- Interfejsy komunikacyjne: UART
- Wejścia/wyjścia:
  - 9 wyjść cyfrowych (BO)
  - 3 wejścia analogowe (AI)
  - Wyjścia analogowe (AO)

### Moduł TMD_V100
- Mikrokontroler: MSP430x5xx
- Wyświetlacz: WH4004A (4 wiersze x 40 znaków)
- Interfejs użytkownika:
  - 7 przycisków
  - Enkoder obrotowy (pokrętło)

## Proces kompilacji i programowania

Proces kompilacji i programowania mikrokontrolerów MSP430 w projekcie Programator_2025 składa się z następujących kroków:

1. **Inicjalizacja konfiguracji**:
   ```bash
   ./init.sh -b TMC_V200 -p /home/tom/github/zlecenia/maski/Programator_2025
   ```

2. **Wykrywanie programatora**:
   ```bash
   ./detect.sh -e .env -f -s
   ```

3. **Kompilacja i programowanie**:
   ```bash
   ./program.sh -b TMC_V200 -v
   ```

## Analiza kodu

### Moduł TMC_V200

Główny plik `main.c` modułu TMC_V200 zawiera:
- Inicjalizację sprzętu (GPIO, UART, ADC)
- Implementację protokołu MSBus
- Obsługę wejść/wyjść cyfrowych i analogowych
- Zarządzanie czasem systemowym
- Komunikację z modułem wyświetlacza

Kluczowe funkcje:
- `set_BO()` - Sterowanie wyjściami cyfrowymi
- `check_AI()` - Odczyt wejść analogowych
- `msbus_send_AI()` - Wysyłanie stanu wejść analogowych
- `msbus_set_display_line()` - Ustawianie tekstu na wyświetlaczu

### Moduł TMD_V100

Główny plik `main.c` modułu TMD_V100 zawiera:
- Inicjalizację wyświetlacza LCD
- Obsługę przycisków i enkodera obrotowego
- Implementację protokołu MSBus
- Komunikację z jednostką główną

Kluczowe funkcje:
- `msbus_set_displayHW_line()` - Wyświetlanie tekstu na LCD
- `check_buttons()` - Odczyt stanu przycisków
- `check_knob()` - Odczyt położenia enkodera obrotowego
- `msbus_send_buttons()` - Wysyłanie stanu przycisków
- `msbus_send_knob()` - Wysyłanie położenia enkodera

## Zalecenia dotyczące rozwoju projektu

1. **Dokumentacja kodu**:
   - Dodanie komentarzy do kluczowych funkcji
   - Utworzenie dokumentacji API dla bibliotek

2. **Testy jednostkowe**:
   - Implementacja testów dla kluczowych modułów
   - Automatyzacja testów w procesie kompilacji

3. **Optymalizacja zużycia energii**:
   - Analiza zużycia energii w różnych trybach pracy
   - Implementacja zaawansowanych trybów oszczędzania energii

4. **Rozszerzenie funkcjonalności**:
   - Dodanie obsługi dodatkowych czujników
   - Implementacja komunikacji bezprzewodowej

## Wnioski

Programator_2025 to kompleksowy system do programowania i kontroli urządzeń opartych na mikrokontrolerach MSP430. Projekt charakteryzuje się modułową strukturą, co ułatwia rozbudowę i utrzymanie kodu. Wykorzystanie własnego protokołu komunikacyjnego MSBus zapewnia elastyczność w komunikacji między modułami oraz z urządzeniami zewnętrznymi.

Główne zalety projektu:
- Modułowa struktura kodu
- Kompletny zestaw narzędzi programistycznych
- Elastyczny protokół komunikacyjny
- Wsparcie dla różnych wersji sprzętowych

Projekt stanowi solidną podstawę do rozwoju zaawansowanych systemów sterowania opartych na mikrokontrolerach MSP430.
