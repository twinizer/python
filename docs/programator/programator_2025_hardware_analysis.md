# Programator_2025 - Analiza Sprzętowa

## Wprowadzenie

Ten dokument zawiera szczegółową analizę sprzętową projektu Programator_2025, koncentrując się na architekturze sprzętowej, interfejsach, komponentach elektronicznych oraz możliwościach diagnostycznych systemu.

## Architektura sprzętowa

Programator_2025 składa się z dwóch głównych modułów sprzętowych, które współpracują ze sobą w celu zapewnienia pełnej funkcjonalności systemu:

### 1. Moduł TMC_V200 (Jednostka główna)

**Specyfikacja techniczna:**
- **Mikrokontroler:** MSP430x5xx
- **Częstotliwość taktowania:** Konfigurowana do 16 MHz (FLL_FACTOR = 488)
- **Pamięć Flash:** Wbudowana w mikrokontroler
- **Interfejsy komunikacyjne:** UART (19200 bps)
- **Zasilanie:** 3.3V

**Piny I/O:**
- **Wyjścia cyfrowe (BO):** 9 kanałów (Pin_Out00 - Pin_Out08)
- **Wejścia analogowe (AI):** 3 kanały (ADC12INCH_0, ADC12INCH_1, ADC12INCH_2)
- **Piny konfiguracyjne:** Dedykowane piny dla konfiguracji systemowej

### 2. Moduł TMD_V100 (Wyświetlacz)

**Specyfikacja techniczna:**
- **Mikrokontroler:** MSP430x5xx
- **Wyświetlacz:** WH4004A (4 wiersze x 40 znaków)
- **Interfejsy komunikacyjne:** UART (19200 bps)
- **Zasilanie:** 3.3V

**Piny I/O:**
- **Interfejs wyświetlacza:** Dedykowane piny do sterowania wyświetlaczem WH4004A
- **Przyciski:** 7 przycisków (Pin_KEY_1 - Pin_KEY_6, Pin_ENCOD_C)
- **Enkoder obrotowy:** 2 piny (Pin_ENCOD_A, Pin_ENCOD_B)

## Analiza komponentów

### Mikrokontroler MSP430x5xx

Mikrokontroler MSP430x5xx stanowi serce systemu Programator_2025. Jest to energooszczędny mikrokontroler 16-bitowy firmy Texas Instruments, zaprojektowany do zastosowań o niskim poborze mocy.

**Kluczowe cechy:**
- **Architektura:** 16-bitowa RISC
- **Tryby oszczędzania energii:** Liczne tryby LPM (Low Power Mode)
- **Peryferia:** ADC, UART, SPI, I2C, Timer
- **Pamięć:** Flash do programowania, RAM do danych

**Konfiguracja zegarów:**
System wykorzystuje różne źródła zegarowe:
- **MCLK (Main Clock):** Główny zegar systemowy
- **SMCLK (Sub-Main Clock):** Zegar dla peryferiów
- **ACLK (Auxiliary Clock):** Zegar pomocniczy o niskiej częstotliwości

### Wyświetlacz WH4004A

Moduł TMD_V100 wykorzystuje wyświetlacz LCD WH4004A, który oferuje 4 wiersze po 40 znaków każdy.

**Specyfikacja:**
- **Typ:** LCD znakowy
- **Rozdzielczość:** 4 wiersze x 40 znaków
- **Interfejs:** Równoległy
- **Kontroler:** HD44780 lub kompatybilny

### Interfejsy komunikacyjne

System wykorzystuje interfejs UART do komunikacji między modułami oraz z urządzeniami zewnętrznymi.

**Konfiguracja UART:**
- **Prędkość:** 19200 bps
- **Format danych:** 8 bitów danych, brak parzystości, 1 bit stopu
- **Kontrola przepływu:** Brak

## Analiza poboru mocy

Projekt Programator_2025 zawiera mechanizmy optymalizacji poboru energii, wykorzystując różne tryby oszczędzania energii mikrokontrolera MSP430.

**Tryby pracy:**
1. **Tryb aktywny:** Pełna funkcjonalność, najwyższy pobór mocy
2. **Tryb LPM0:** Zatrzymanie CPU, peryferia aktywne
3. **Tryb LPM3:** Zatrzymanie większości zegarów, minimalne peryferia aktywne
4. **Tryb LPM4:** Najniższy pobór mocy, tylko przerwania zewnętrzne mogą wybudzić system

**Typowy pobór prądu:**
- **Tryb aktywny:** ~1-5 mA (zależnie od częstotliwości taktowania)
- **Tryb LPM3:** ~1-10 μA
- **Tryb LPM4:** <1 μA

## Interfejsy diagnostyczne

System Programator_2025 oferuje różne interfejsy diagnostyczne, które ułatwiają debugowanie i programowanie:

### 1. Interfejs JTAG/SBW

Interfejs JTAG (Joint Test Action Group) lub SBW (Spy-Bi-Wire) służy do programowania i debugowania mikrokontrolera MSP430.

**Funkcje:**
- Programowanie pamięci Flash
- Debugowanie kodu w czasie rzeczywistym
- Dostęp do rejestrów i pamięci mikrokontrolera

### 2. Interfejs UART

Interfejs UART służy nie tylko do komunikacji między modułami, ale również do diagnostyki systemu.

**Funkcje diagnostyczne:**
- Wysyłanie komunikatów debugowania
- Monitorowanie stanu systemu
- Sterowanie systemem poprzez komendy tekstowe

## Analiza sygnałów

### Wyjścia cyfrowe (BO)

Moduł TMC_V200 oferuje 9 wyjść cyfrowych (Binary Outputs), które mogą być sterowane indywidualnie.

**Charakterystyka:**
- **Poziomy napięcia:** 0V (stan niski), 3.3V (stan wysoki)
- **Maksymalny prąd:** Zgodny ze specyfikacją mikrokontrolera MSP430 (typowo 8-10 mA)
- **Sterowanie:** Poprzez funkcję `set_BO()`

### Wejścia analogowe (AI)

Moduł TMC_V200 posiada 3 kanały wejść analogowych, które wykorzystują wbudowany przetwornik ADC mikrokontrolera.

**Charakterystyka:**
- **Rozdzielczość:** 12 bitów
- **Zakres napięcia:** 0-3.3V
- **Częstotliwość próbkowania:** Konfigurowana w kodzie
- **Odczyt:** Poprzez funkcję `check_AI()`

### Enkoder obrotowy

Moduł TMD_V100 wykorzystuje enkoder obrotowy jako element interfejsu użytkownika.

**Charakterystyka:**
- **Typ:** Inkrementalny enkoder obrotowy
- **Interfejs:** 2 piny kwadratury (A, B) + przycisk (C)
- **Detekcja:** Wykrywanie kierunku i prędkości obrotu
- **Obsługa:** Poprzez funkcję `check_knob()`

## Diagnostyka i debugowanie

### Narzędzia programistyczne

Projekt zawiera zestaw skryptów ułatwiających programowanie i diagnostykę systemu:

1. **mspdebug.sh** - Instalacja i konfiguracja narzędzia mspdebug
2. **detect.sh** - Wykrywanie i konfiguracja programatora
3. **program.sh** - Programowanie mikrokontrolera

### Diagnostyka sprzętowa

System oferuje różne mechanizmy diagnostyki sprzętowej:

1. **Piny testowe:**
   - Dedykowane piny do monitorowania stanu systemu
   - Możliwość podłączenia oscyloskopu lub analizatora logicznego

2. **Komunikaty diagnostyczne:**
   - Wysyłanie komunikatów przez UART
   - Monitorowanie stanu systemu w czasie rzeczywistym

3. **Wskaźniki LED:**
   - Sygnalizacja stanu systemu
   - Informowanie o błędach

## Rozwiązywanie problemów

### Typowe problemy sprzętowe

| Problem | Możliwa przyczyna | Rozwiązanie |
|---------|------------------|-------------|
| Brak komunikacji UART | Nieprawidłowa konfiguracja | Sprawdź ustawienia UART w pliku konfiguracyjnym |
| Niestabilna praca | Problem z zasilaniem | Sprawdź napięcie zasilania i filtrację |
| Błędy ADC | Zakłócenia sygnału | Dodaj filtrację sygnału wejściowego |
| Problemy z programowaniem | Nieprawidłowe połączenie JTAG/SBW | Sprawdź połączenia programatora |
| Wysoki pobór prądu | Nieprawidłowa konfiguracja trybów LPM | Sprawdź konfigurację PMM w kodzie |

### Procedury diagnostyczne

1. **Weryfikacja zasilania:**
   - Sprawdź napięcie zasilania (powinno wynosić 3.3V ±5%)
   - Sprawdź stabilność napięcia podczas pracy systemu

2. **Weryfikacja komunikacji:**
   - Sprawdź połączenia UART między modułami
   - Monitoruj komunikację za pomocą analizatora protokołów

3. **Weryfikacja programowania:**
   - Użyj skryptu `detect.sh` do weryfikacji połączenia z programatorem
   - Sprawdź poprawność wykrywania mikrokontrolera

## Zalecenia dotyczące rozwoju sprzętowego

1. **Optymalizacja poboru mocy:**
   - Implementacja zaawansowanych algorytmów zarządzania energią
   - Wykorzystanie trybów LPM w większym stopniu

2. **Rozszerzenie interfejsów:**
   - Dodanie komunikacji bezprzewodowej (np. Bluetooth LE)
   - Implementacja interfejsu USB

3. **Zwiększenie niezawodności:**
   - Dodanie zabezpieczeń przeciwprzepięciowych
   - Implementacja mechanizmów watchdog

4. **Rozszerzenie możliwości diagnostycznych:**
   - Dodanie rejestracji zdarzeń (logging)
   - Implementacja zaawansowanej telemetrii

## Wnioski

Analiza sprzętowa projektu Programator_2025 pokazuje, że jest to dobrze zaprojektowany system oparty na mikrokontrolerach MSP430, oferujący szeroki zakres funkcjonalności przy zachowaniu niskiego poboru mocy. Modułowa konstrukcja ułatwia rozbudowę i utrzymanie systemu.

Główne zalety sprzętowe:
- Energooszczędna architektura oparta na MSP430
- Elastyczne interfejsy I/O
- Kompleksowe narzędzia diagnostyczne
- Modułowa konstrukcja

Projekt stanowi solidną podstawę do rozwoju zaawansowanych systemów sterowania, szczególnie w zastosowaniach wymagających niskiego poboru mocy i niezawodnej pracy.
