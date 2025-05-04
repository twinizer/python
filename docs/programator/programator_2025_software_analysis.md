# Programator_2025 - Analiza Oprogramowania

## Wprowadzenie

Ten dokument zawiera szczegółową analizę oprogramowania projektu Programator_2025, koncentrując się na architekturze kodu, algorytmach, protokołach komunikacyjnych oraz możliwościach programistycznych systemu.

## Architektura oprogramowania

Projekt Programator_2025 wykorzystuje modułową architekturę oprogramowania, która umożliwia łatwą rozbudowę i utrzymanie kodu. Główne komponenty oprogramowania to:

### 1. Warstwa abstrakcji sprzętowej (HAL)

Warstwa HAL (Hardware Abstraction Layer) zapewnia abstrakcję sprzętową, która izoluje wyższe warstwy oprogramowania od szczegółów implementacji sprzętowej. Dzięki temu możliwe jest łatwe dostosowanie kodu do różnych platform sprzętowych.

**Główne komponenty HAL:**
- **HAL_Board** - Konfiguracja płyty głównej
- **HAL_PMM** - Zarządzanie zasilaniem
- **HAL_UCS** - Konfiguracja zegarów systemowych
- **HAL_RTC** - Obsługa zegara czasu rzeczywistego
- **HAL_UART** - Komunikacja szeregowa
- **HAL_Flash** - Obsługa pamięci Flash

### 2. Sterowniki urządzeń

Sterowniki urządzeń zapewniają interfejs programistyczny do obsługi różnych komponentów sprzętowych.

**Główne sterowniki:**
- **WH4004A** - Sterownik wyświetlacza LCD
- **Disk_IO** - Obsługa pamięci masowej
- **Flash** - Operacje na pamięci Flash
- **UART** - Komunikacja szeregowa

### 3. Biblioteki pomocnicze

Biblioteki pomocnicze zawierają funkcje i struktury danych używane w całym projekcie.

**Główne biblioteki:**
- **msbus** - Protokół komunikacyjny MSBus
- **numberFixedPoint** - Obsługa liczb zmiennoprzecinkowych o stałej precyzji
- **my_string** - Funkcje do obsługi łańcuchów znaków
- **Calendar** - Funkcje kalendarza
- **Fifo** - Implementacja kolejki FIFO

### 4. Aplikacje główne

Aplikacje główne zawierają kod specyficzny dla poszczególnych modułów sprzętowych.

**Główne aplikacje:**
- **TMC_V200/main.c** - Kod główny jednostki centralnej
- **TMD_V100/main.c** - Kod główny modułu wyświetlacza

## Analiza kodu

### Moduł TMC_V200

Główny plik `main.c` modułu TMC_V200 zawiera implementację funkcjonalności jednostki centralnej.

**Kluczowe funkcje:**

1. **Inicjalizacja sprzętu:**
```c
// Konfiguracja zegarów systemowych
SetVCore(PMMCOREV_3);
initClockTo16MHz();

// Inicjalizacja UART
UART_init(UART_SET);

// Inicjalizacja PWM
PWM_init();

// Inicjalizacja ADC
ADC12CTL0 = ADC12SHT0_8 + ADC12ON;
ADC12CTL1 = ADC12SHP;
ADC12IE = 0;
ADC12CTL0 |= ADC12ENC;
```

2. **Obsługa wejść/wyjść:**
```c
// Sterowanie wyjściami cyfrowymi
static void set_BO(unsigned char iBO_No, unsigned char iState) {
  if (iState == 0) {
    switch (iBO_No) {
      case  9: outputPin_set(Pin_Out00); break;
      // ...
    }
  } else {
    switch (iBO_No) {
      case  9: outputPin_reset(Pin_Out00); break;
      // ...
    }
  }
}

// Odczyt wejść analogowych
void check_AI() {
  unsigned int i;
  for (i = 0; i < 3; i++) {
    ADC12CTL0 &= ~ADC12SC;
    ADC12CTL1 &= ~(0xF << 12);
    ADC12CTL1 |= (iAIchannel[i] << 12);
    ADC12CTL0 |= ADC12SC;
    while (ADC12CTL1 & ADC12BUSY);
    iAIval[i] = ADC12MEM0;
  }
}
```

3. **Protokół MSBus:**
```c
// Tablica komend MSBus
static const Tmsbus MsBusRX_raspberry[] = {
  {"SDS:", msbus_set_display_line}, // set display
  {"GDS:", msbus_send_display_line}, // get display
  {"SBO:", msbus_set_BO}, // set binary output
  {"SAO:", msbus_set_AO}, // set analog output
  {"GAI:", msbus_send_AI}, // get analog input
  {"STM:", msbus_set_TM}, // set time
  {"GTM:", msbus_send_TM}, // get time
  {"GKN:", msbus_send_knob}, // get knob
  {"GBT:", msbus_send_buttons}, // get buttons
  {NULL, NULL}
};

// Pętla główna obsługująca protokół MSBus
while (1) {
  if (UART_dataAvailable()) {
    char c = UART_getc();
    if (msbus_rx(&msbus_raspberry, c, sBuffRx, sizeof(sBuffRx), sBuffTx, sizeof(sBuffTx))) {
      UART_puts(sBuffTx);
    }
  }
  // ...
}
```

### Moduł TMD_V100

Główny plik `main.c` modułu TMD_V100 zawiera implementację funkcjonalności modułu wyświetlacza.

**Kluczowe funkcje:**

1. **Obsługa wyświetlacza:**
```c
// Wyświetlanie tekstu na LCD
static const Tmsbus* msbus_set_displayHW_line(const Tmsbus *pMSbus, char *sBuffRx, int iLenRx) {
  unsigned int row = 0; unsigned int col = 0; const char *s = sBuffRx;
  // Parsowanie komendy
  while (*s != 0) {
    if (*s == 'L') {
      s = uFxP_scan(s + 1, &row, 0);
      continue;
    }
    // ...
  }
  display_puts(row, col, s);
  return NULL;
}
```

2. **Obsługa przycisków:**
```c
// Odczyt stanu przycisków
static unsigned int check_buttons() {
  unsigned int iRes = 0;
  unsigned char tmp;
  tmp = PJIN;
  iRes = (~tmp) & ((1<<6) - 1);
  if ((pin_is_set(Pin_KEY_6)) == 0) iRes |= 1 << 6;
  if ((pin_is_set(Pin_ENCOD_C)) == 0) iRes |= 1 << 7;
  return iRes;
}

// Wysyłanie stanu przycisków
static const Tmsbus* msbus_send_buttons(const Tmsbus *pMSbus, char *sBuffTx, int iSizeTx) {
  char *pTx = sBuffTx;
  const char *pS = pMSbus->sCMD;
  unsigned int iBt;
  // ...
  iBt = check_buttons();
  *pTx++ = toHex(iBt >> 12);
  *pTx++ = toHex(iBt >> 8);
  *pTx++ = toHex(iBt >> 4);
  *pTx++ = toHex(iBt);
  *pTx++ = 0; 
  return NULL;
}
```

3. **Obsługa enkodera obrotowego:**
```c
// Odczyt stanu enkodera
void check_knob() {
  static int dir = 0;
  static int cOldEncod_A;
  static int cOldEncod_B;
  int cNewEncod_A;
  int cNewEncod_B;
  cNewEncod_A = pin_is_set(Pin_ENCOD_A);
  cNewEncod_B = pin_is_set(Pin_ENCOD_B);
  // Algorytm dekodowania kwadratury
  if (cOldEncod_A != cNewEncod_A) {
    cOldEncod_A = cNewEncod_A;
    if ((dir == 0) && (cNewEncod_A == 0)) {
      if (cNewEncod_B == 0) dir = +1;
      else                  dir = -1;
    }
  }
  // ...
}
```

## Protokół komunikacyjny MSBus

Protokół MSBus jest kluczowym elementem oprogramowania, umożliwiającym komunikację między modułami oraz z urządzeniami zewnętrznymi.

### Struktura protokołu

Protokół MSBus bazuje na komunikacji tekstowej przez interfejs UART. Każda komenda składa się z:
- **Prefiksu komendy** - identyfikator komendy (np. "SDS:", "GBT:")
- **Parametrów** - opcjonalne parametry komendy
- **Terminatora** - znak końca komendy (null terminator)

### Implementacja protokołu

Protokół MSBus jest zaimplementowany za pomocą tablicy struktur `Tmsbus`, która mapuje prefiksy komend na odpowiednie funkcje obsługi:

```c
typedef struct {
  const char *sCMD;
  const Tmsbus* (*pFunc)(const Tmsbus *pMSbus, char *sBuff, int iLen);
} Tmsbus;

static const Tmsbus MsBusRX0[] = {
  {"SDS:", msbus_set_displayHW_line}, // set display
  {"GKN:", msbus_send_knob},          // get knob
  {"GBT:", msbus_send_buttons},       // get buttons
  {NULL, NULL}
};
```

### Obsługa protokołu

Obsługa protokołu MSBus odbywa się w pętli głównej programu:

```c
while (1) {
  if (UART_dataAvailable()) {
    char c = UART_getc();
    if (msbus_rx(&msbus_raspberry, c, sBuffRx, sizeof(sBuffRx), sBuffTx, sizeof(sBuffTx))) {
      UART_puts(sBuffTx);
    }
  }
  // ...
}
```

Funkcja `msbus_rx` analizuje otrzymane znaki, identyfikuje komendę i wywołuje odpowiednią funkcję obsługi.

## Zarządzanie energią

Projekt Programator_2025 implementuje zaawansowane mechanizmy zarządzania energią, wykorzystując możliwości mikrokontrolera MSP430.

### Tryby oszczędzania energii

Mikrokontroler MSP430 oferuje różne tryby oszczędzania energii (LPM - Low Power Mode):

```c
// Przejście do trybu LPM0 z włączonymi przerwaniami
__bis_SR_register(LPM0_bits + GIE);

// Przejście do trybu LPM3 z włączonymi przerwaniami
__bis_SR_register(LPM3_bits + GIE);
```

### Konfiguracja zegarów

Optymalizacja zużycia energii obejmuje również konfigurację zegarów systemowych:

```c
// Konfiguracja zegarów systemowych
void initClockTo16MHz() {
  // Konfiguracja FLL (Frequency Locked Loop)
  __bis_SR_register(SCG0);
  UCSCTL0 = 0x0000;
  UCSCTL1 = DCORSEL_5;
  UCSCTL2 = FLL_FACTOR | FLLD_1;
  __bic_SR_register(SCG0);
  
  // Czekaj na stabilizację FLL
  __delay_cycles(250000);
}
```

## Obsługa przerwań

System wykorzystuje przerwania do obsługi zdarzeń asynchronicznych, takich jak odbiór danych UART czy zdarzenia czasowe.

### Przerwania UART

```c
// Przerwanie odbioru UART0
#pragma vector=USCI_A0_VECTOR
__interrupt void USCI_A0_ISR(void) {
  switch(__even_in_range(UCA0IV, 4)) {
    case 0: break;                 // Vector 0 - no interrupt
    case 2:                         // Vector 2 - RXIFG
      UART0_rx_isr();
      break;
    case 4: break;                 // Vector 4 - TXIFG
    default: break;
  }
}
```

### Przerwania czasowe

```c
// Przerwanie Timer A0
void __attribute__((interrupt(TIMER0_A0_VECTOR))) TIMER0_A0_ISR(void) {
  board_onTimerA0();
}
```

## Narzędzia programistyczne

Projekt zawiera zestaw skryptów ułatwiających programowanie i debugowanie systemu:

### 1. Skrypt inicjalizacyjny (init.sh)

Skrypt `init.sh` odpowiada za inicjalizację plików konfiguracyjnych:

```bash
#!/bin/bash
# Parametry
BOARD=""
PROJECT_PATH=""

# Parsowanie parametrów
while getopts "b:p:" opt; do
  case $opt in
    b) BOARD="$OPTARG" ;;
    p) PROJECT_PATH="$OPTARG" ;;
    *) echo "Nieznana opcja: -$OPTARG" >&2; exit 1 ;;
  esac
done

# Tworzenie pliku .env
echo "BOARD=$BOARD" > .env
echo "PROJECT_PATH=$PROJECT_PATH" >> .env
```

### 2. Skrypt wykrywania programatora (detect.sh)

Skrypt `detect.sh` wykrywa i konfiguruje programator MSP430:

```bash
#!/bin/bash
# Parametry
ENV_FILE=".env"
FORCE=0
SCAN=0
DEBUG=0

# Parsowanie parametrów
while getopts "e:fsd" opt; do
  case $opt in
    e) ENV_FILE="$OPTARG" ;;
    f) FORCE=1 ;;
    s) SCAN=1 ;;
    d) DEBUG=1 ;;
    *) echo "Nieznana opcja: -$OPTARG" >&2; exit 1 ;;
  esac
done

# Wykrywanie programatora
if [ $SCAN -eq 1 ] || [ $FORCE -eq 1 ]; then
  echo "Wykrywanie programatora..."
  # Kod wykrywania programatora
fi
```

### 3. Skrypt programowania (program.sh)

Skrypt `program.sh` kompiluje i programuje mikrokontroler:

```bash
#!/bin/bash
# Parametry
BOARD=""
VERBOSE=0

# Parsowanie parametrów
while getopts "b:v" opt; do
  case $opt in
    b) BOARD="$OPTARG" ;;
    v) VERBOSE=1 ;;
    *) echo "Nieznana opcja: -$OPTARG" >&2; exit 1 ;;
  esac
done

# Kompilacja i programowanie
echo "Kompilacja dla płyty $BOARD..."
make -C $BOARD clean
make -C $BOARD

echo "Programowanie mikrokontrolera..."
# Kod programowania mikrokontrolera
```

## Analiza algorytmów

### Dekodowanie enkodera obrotowego

Algorytm dekodowania enkodera obrotowego wykorzystuje technikę dekodowania kwadratury:

```c
void check_knob() {
  static int dir = 0;
  static int cOldEncod_A;
  static int cOldEncod_B;
  int cNewEncod_A;
  int cNewEncod_B;
  
  // Odczyt stanu pinów enkodera
  cNewEncod_A = pin_is_set(Pin_ENCOD_A);
  cNewEncod_B = pin_is_set(Pin_ENCOD_B);
  
  // Wykrywanie kierunku obrotu
  if (cOldEncod_A != cNewEncod_A) {
    cOldEncod_A = cNewEncod_A;
    if ((dir == 0) && (cNewEncod_A == 0)) {
      if (cNewEncod_B == 0) dir = +1;
      else                  dir = -1;
    }
  }
  
  // Wykrywanie pełnego kroku
  if (cOldEncod_B != cNewEncod_B) {
    cOldEncod_B = cNewEncod_B;
    if ((dir != 0) && (cNewEncod_B == 0)) {
      if (cNewEncod_A == 0) {
        if (dir < 0) iknob++;
      } else {
        if (dir > 0) iknob--;
      }
      dir = 0;
    }
  }
}
```

### Obsługa wyświetlacza LCD

Algorytm wyświetlania tekstu na LCD:

```c
void display_puts(unsigned int row, unsigned int col, const char *s) {
  // Ograniczenie współrzędnych do zakresu wyświetlacza
  if (row >= DisplayRows) row = DisplayRows - 1;
  if (col >= DisplayCols) col = DisplayCols - 1;
  
  // Obliczenie pozycji w buforze wyświetlacza
  char *pDst = &display[row * DisplayCols + col];
  
  // Kopiowanie tekstu do bufora
  while (*s && col < DisplayCols) {
    *pDst++ = *s++;
    col++;
  }
  
  // Aktualizacja wyświetlacza
  display_update();
}
```

## Zalecenia dotyczące rozwoju oprogramowania

1. **Refaktoryzacja kodu:**
   - Wprowadzenie bardziej modułowej struktury kodu
   - Zastosowanie technik programowania obiektowego (w ramach możliwości języka C)
   - Ujednolicenie konwencji nazewnictwa

2. **Dokumentacja kodu:**
   - Dodanie komentarzy zgodnych ze standardem Doxygen
   - Utworzenie dokumentacji API dla bibliotek
   - Opracowanie diagramów przepływu dla kluczowych algorytmów

3. **Testy jednostkowe:**
   - Implementacja testów dla kluczowych modułów
   - Automatyzacja testów w procesie kompilacji
   - Wprowadzenie testów integracyjnych

4. **Optymalizacja:**
   - Optymalizacja algorytmów pod kątem zużycia energii
   - Redukcja zużycia pamięci
   - Optymalizacja wydajności krytycznych sekcji kodu

5. **Rozszerzenie funkcjonalności:**
   - Implementacja dodatkowych protokołów komunikacyjnych
   - Dodanie obsługi dodatkowych peryferiów
   - Implementacja zaawansowanych algorytmów przetwarzania sygnałów

## Wnioski

Analiza oprogramowania projektu Programator_2025 pokazuje, że jest to dobrze zaprojektowany system z modułową architekturą, która ułatwia rozbudowę i utrzymanie kodu. Wykorzystanie warstwy abstrakcji sprzętowej (HAL) zapewnia przenośność kodu między różnymi platformami sprzętowymi.

Główne zalety oprogramowania:
- Modułowa architektura
- Efektywne zarządzanie energią
- Elastyczny protokół komunikacyjny MSBus
- Kompleksowe narzędzia programistyczne

Projekt stanowi solidną podstawę do rozwoju zaawansowanych systemów sterowania opartych na mikrokontrolerach MSP430, szczególnie w zastosowaniach wymagających niskiego poboru mocy i niezawodnej pracy.
