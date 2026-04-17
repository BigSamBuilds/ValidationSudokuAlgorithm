# Sudoku Solver Benchmark

Detta projekt jämför två algoritmer för att lösa Sudoku-pussel:
1. **DFS med backtracking (pruned)** – enkel rekursiv sökning som endast placerar giltiga siffror.
2. **Constraint Propagation + DFS (Regel 0)** – reducerar kandidatmängder innan backtracking.

Målet är att undersöka hur exekveringstid och antal sökta noder påverkas av pusslets svårighetsgrad samt av JIT-kompilering i Java.

## Projektstruktur

```
.
├── SudokuSolverBench.java          # Implementering av båda algoritmerna
├── SudokuPuzzleGenerator.java      # Genererar unika Sudoku-pussel (easy, medium, hard)
├── SudokuBenchmark.java            # Kör prestandatester och sparar rådata till CSV
├── measure.py                      # Analyserar CSV-data, utför t-test och skapar grafer
├── SudokuPuzzleGenerator/          # Katalog med genererade pussel
│   ├── level1_easy.csv
│   ├── level2_medium.csv
│   └── level3_hard.csv
├── SudokuSolverBench/              # Kompilerad solver-klass
├── benchmark_results.csv           # Rådata från körning med JIT aktiverad
├── time_comparison.png             # Boxplot över exekveringstider per svårighetsgrad
├── scatter_comparison.png          # Spridningsdiagram DFS vs CP+DFS
├── README.md                       # Denna fil
└── .gitignore                      # Ignorerar temporära filer
```

## Kom igång

### Förutsättningar
- Java 17 eller senare (OpenJDK rekommenderas)
- Python 3.8+ med paketen `pandas`, `numpy`, `scipy`, `matplotlib`

Installera Python-beroenden:
```bash
pip install pandas numpy scipy matplotlib
```

### Generera Sudoku-pussel (valfritt)
Om du vill återskapa pusslen, kör:
```bash
cd SudokuPuzzleGenerator
javac SudokuPuzzleGenerator.java
java SudokuPuzzleGenerator
```
**OBS:** Att generera 800 pussel per nivå tar flera timmar. Redan genererade CSV-filer finns i katalogen `SudokuPuzzleGenerator/`.

### Kör benchmark (JIT på)
```bash
javac SudokuBenchmark.java
java SudokuBenchmark
```
Resultatet sparas i `benchmark_results.csv`. Förväntad körtid: ~1–2 timmar för 800×3 pussel.

### Kör benchmark (JIT av)
För att mäta utan JIT-kompilering, använd flaggan `-Xint`:
```bash
java -Xint -cp . SudokuBenchmark
```
(Redigera gärna `SudokuBenchmark.java` så att utdatafilen heter `jit_off_results.csv`.)

### Analysera resultaten
```bash
python3 measure.py
```
Skriptet läser `benchmark_results.csv` och:
- Beräknar mediantider och nodantal per svårighetsgrad
- Utför parade t‑test mellan algoritmerna
- Skapar boxplot och spridningsdiagram

## Resultat (exempel från en körning)

| Svårighetsgrad | DFS tid (ms) | CP+DFS tid (ms) | p‑värde | DFS noder | CP noder |
|----------------|--------------|-----------------|---------|-----------|----------|
| Easy           | 0.02         | 0.04            | <0.001  | 206       | 91       |
| Medium         | 0.63         | 24.98           | <0.001  | 8 030     | 3 261    |
| Hard           | 2.69         | 137.89          | <0.001  | 30 986    | 16 120   |

**Slutsatser:**
- DFS är signifikant snabbare på samtliga svårighetsgrader.
- Constraint Propagation halverar antalet sökta noder, men overheaden gör metoden långsammare i praktiken på dessa pussel.
- JIT-kompilering ger en tydlig prestandavinst (se separat JIT‑off‑körning).

## Forskningsfrågor

1. Hur påverkas exekveringstiden av DFS jämfört med Constraint Propagation + DFS?
2. Vad blir skillnaden i exekveringstid med respektive utan JIT?
3. Finns det någon skillnad i exekveringstid mellan olika svårighetsgrader?

## Författare

Projektarbete i kursen Utvärdering av programvarusystem, våren 2026.  
Gruppmedlemmar: [Dina namn här]

## Licens

Detta projekt använder MIT-licensen – se [LICENSE](LICENSE) för detaljer.
