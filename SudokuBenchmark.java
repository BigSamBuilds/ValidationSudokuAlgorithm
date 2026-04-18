import SudokuSolverBench.SudokuSolverBench;
import java.io.*;
import java.util.*;

public class SudokuBenchmark {

    public static List<int[][]> loadPuzzlesFromCSV(String filename) throws IOException {
        List<int[][]> puzzles = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(new FileReader(filename))) {
            String line;
            int[][] puzzle = new int[9][9];
            int row = 0;
            while ((line = br.readLine()) != null) {
                if (line.trim().isEmpty()) {
                    if (row == 9) {
                        puzzles.add(puzzle);
                        puzzle = new int[9][9];
                        row = 0;
                    }
                    continue;
                }
                String[] parts = line.split(",");
                for (int c = 0; c < 9; c++) {
                    puzzle[row][c] = Integer.parseInt(parts[c].trim());
                }
                row++;
            }
            if (row == 9)
                puzzles.add(puzzle);
        }
        return puzzles;
    }


    public static void main(String[] args) throws IOException {
        // Paths to your puzzle files
        String[] levels = {"easy", "medium", "hard"};
        String[] files = {"./SudokuPuzzleGenerator/level1_easy.csv", "./SudokuPuzzleGenerator/level2_medium.csv", "./SudokuPuzzleGenerator/level3_hard.csv"};
        
        SudokuSolverBench solver = new SudokuSolverBench();
        //PrintWriter out = new PrintWriter(new FileWriter("benchmark_results.csv"));
        PrintWriter out = new PrintWriter(new FileWriter("benchmark_results_NoJIT.csv"));

        out.println("puzzle_id,difficulty,algorithm,run,time_ns,nodes");
        
        int puzzleId = 0;
        for (int level = 0; level < 3; level++) {
            System.out.println("Loading " + levels[level] + " puzzles...");
            List<int[][]> puzzles = loadPuzzlesFromCSV(files[level]);
            System.out.println("Loaded " + puzzles.size() + " puzzles.");
            
            for (int[][] puzzle : puzzles) {
                // Warm‑up phase (5 runs, no timing)
                for (int w = 0; w < 5; w++) {
                    solver.setBoard(puzzle);
                    solver.solveDFS();
                    solver.setBoard(puzzle);
                    solver.solveWithConstraintPropagation();
                }
                
                // Timed runs – DFS
                for (int run = 0; run < 10; run++) {
                    solver.setBoard(puzzle);
                    long start = System.nanoTime();
                    boolean solved = solver.solveDFS();
                    long time = System.nanoTime() - start;
                    long nodes = solver.getNodesExplored();
                    out.printf("%d,%s,dfs,%d,%d,%d%n", puzzleId, levels[level], run, time, nodes);
                }
                
                // Timed runs – CP+DFS
                for (int run = 0; run < 10; run++) {
                    solver.setBoard(puzzle);
                    long start = System.nanoTime();
                    boolean solved = solver.solveWithConstraintPropagation();
                    long time = System.nanoTime() - start;
                    long nodes = solver.getNodesExplored();
                    out.printf("%d,%s,cp,%d,%d,%d%n", puzzleId, levels[level], run, time, nodes);
                }
                
                puzzleId++;
                if (puzzleId % 10 == 0) {
                    System.out.println("Processed " + puzzleId + " puzzles...");
                }
            }
        }
        out.close();
        System.out.println("Benchmark complete. Results saved to benchmark_results.csv");
    }
}