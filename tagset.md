# Tagset

## 1 Commands

| Tag   | Erklärung                         | Beispiel      |
| ----- |:---------------------------------:| -------------:|
| CA    | arithmetische Commands            | ABS, SQR      |
| CS    | String-basierte Commands          | ASC, LEFT$    |
| CI    | I/O-basierte Commands             | CLOSE, INPUT  |
| CV    | spezifische Variablendeklaration  | CLR, DATA     |
| CD    | Funktionsdeklaration              | DEF           |
| CC    | File-Run Control                  | RUN, STOP     |
| CP    | Program Control                   | GOTO, FOR     |
| CE    | Editor                            | LOAD, SAVE    |
| CM    | Memory                            | NEW           |
| CR    | System                            | PEEK, POKE    |

## 2 Operatoren

| Tag   | Erklärung                         | Beispiel      |
| ----- |:---------------------------------:| -------------:|
| OA    | arithmetische Operatoren          | +, *          |
| OR    | relationale Operatoren            | <=, =         |
| OL    | logische Operatoren               | AND, OR       |
| OS    | Zuweisungsoperator                | =             |
| OU    | Unäre Operatoren                  | -, +          |

## 3 Konstanten

| Tag   | Erklärung                         | Beispiel      |
| ----- |:---------------------------------:| -------------:|
| TA    | arithmetische Konstanten          | PI            |

## 4 Systemvariablen

| Tag   | Erklärung                         | Beispiel      |
| ----- |:---------------------------------:| -------------:|
| YT    | Zeit-basierte Systemvariablen     | ti, ti$       |
| YI    | I/O-basierte Systemvariablen      | st            |

## 5 Variablen

| Tag   | Erklärung                         | Beispiel      |
| ----- |:---------------------------------:| -------------:|
| VR    | Variable mit Type reele Zahl      | i, a          |
| VI    | Variable mit Type integer Zahl    | i%, a%        |
| VS    | Variable mit Type String          | s$, h$        |
| VAR   | Variable mit reelen Zahlen Array  | i(4), a(7)    |
| VAI   | Variable mit integer Zahlen Array | i%(4), a%(7)  |
| VAS   | Variable mit String Array         | s$(4), a$(7)  |

## 6 Zahlen

| Tag   | Erklärung                         | Beispiel      |
| ----- |:---------------------------------:| -------------:|
| NR    | reele Zahl                        | 3.512, .7     |
| NI    | integer Zahl                       | 3, 0         |

## 7 Strings

| Tag   | Erklärung                         | Beispiel      |
| ----- |:---------------------------------:| -------------:|
| SC    | Kommentar                         | Copyright by  |
| SL    | String                            | "Hallo"       |

## 8 Interpunktion

| Tag   | Erklärung                         | Beispiel      |
| ----- |:---------------------------------:| -------------:|
| PC    | Doppelpunkt, Statement Trenner    | :             |
| PP    | Klammern                          | (, )          |
| PT    | Variabeltyp, Sigil                | $, %          |
| PB    | Punkt/Boolean                     | .             |
| PS    | Separatoren                       | , ;           |
| PO    | Andere Interpunktionen            | -, @, #       |

## 9 Data

| Tag   | Erklärung                         | Beispiel      |
| ----- |:---------------------------------:| -------------:|
| D     | opcode-mnemonische Tabelle        | a,!,r         |
