import java.io.*;
import java.util.*;

public class SudokuPuzzleGenerator {
    private int[][] board;
    private Random rand = new Random();

    public SudokuPuzzleGenerator() {
        board = new int[9][9];
    }

    public int[][] generatePuzzle(int targetClues) {
        generateRandomSolution();
        int[][] solution = deepCopy(board);

        List<int[]> allPositions = new ArrayList<>();
        for (int r = 0; r < 9; r++) {
            for (int c = 0; c < 9; c++) {
                allPositions.add(new int[] { r, c });
            }
        }
        Collections.shuffle(allPositions, rand);

        int clues = 81;
        for (int[] pos : allPositions) {
            if (clues <= targetClues)
                break;
            int r = pos[0], c = pos[1];
            int backup = board[r][c];
            board[r][c] = 0;

            if (!hasUniqueSolution(board)) {
                board[r][c] = backup;
            } else {
                clues--;
            }
        }
        return board;
    }

    private void generateRandomSolution() {
        for (int r = 0; r < 9; r++)
            Arrays.fill(board[r], 0);
        solveRandomized(0, 0);
    }

    private boolean solveRandomized(int row, int col) {
        if (row == 9)
            return true;
        if (col == 9)
            return solveRandomized(row + 1, 0);

        List<Integer> nums = new ArrayList<>(Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9));
        Collections.shuffle(nums, rand);
        for (int num : nums) {
            if (isLegal(row, col, num)) {
                board[row][col] = num;
                if (solveRandomized(row, col + 1))
                    return true;
                board[row][col] = 0;
            }
        }
        return false;
    }

    private boolean isLegal(int row, int col, int num) {
        for (int c = 0; c < 9; c++)
            if (board[row][c] == num && c != col)
                return false;
        for (int r = 0; r < 9; r++)
            if (board[r][col] == num && r != row)
                return false;
        int br = row - row % 3, bc = col - col % 3;
        for (int r = br; r < br + 3; r++)
            for (int c = bc; c < bc + 3; c++)
                if (board[r][c] == num && (r != row || c != col))
                    return false;
        return true;
    }

    private boolean hasUniqueSolution(int[][] puzzle) {
        int[][] copy = deepCopy(puzzle);
        SolutionCounter counter = new SolutionCounter();
        return counter.count(copy) == 1;
    }

    private static int[][] deepCopy(int[][] src) {
        int[][] dst = new int[9][9];
        for (int r = 0; r < 9; r++)
            System.arraycopy(src[r], 0, dst[r], 0, 9);
        return dst;
    }

    // ---------- Solution Counter ----------
    private static class SolutionCounter {
        private int count;
        private int[][] board;

        int count(int[][] puzzle) {
            board = deepCopyStatic(puzzle);
            count = 0;
            solve(0, 0);
            return count;
        }

        private void solve(int row, int col) {
            if (count >= 2)
                return;
            if (row == 9) {
                count++;
                return;
            }
            if (col == 9) {
                solve(row + 1, 0);
                return;
            }
            if (board[row][col] != 0) {
                solve(row, col + 1);
                return;
            }

            for (int num = 1; num <= 9; num++) {
                if (isLegalStatic(row, col, num)) {
                    board[row][col] = num;
                    solve(row, col + 1);
                    board[row][col] = 0;
                }
            }
        }

        private boolean isLegalStatic(int row, int col, int num) {
            for (int c = 0; c < 9; c++)
                if (board[row][c] == num && c != col)
                    return false;
            for (int r = 0; r < 9; r++)
                if (board[r][col] == num && r != row)
                    return false;
            int br = row - row % 3, bc = col - col % 3;
            for (int r = br; r < br + 3; r++)
                for (int c = bc; c < bc + 3; c++)
                    if (board[r][c] == num && (r != row || c != col))
                        return false;
            return true;
        }

        private static int[][] deepCopyStatic(int[][] src) {
            int[][] dst = new int[9][9];
            for (int r = 0; r < 9; r++)
                System.arraycopy(src[r], 0, dst[r], 0, 9);
            return dst;
        }
    }

    // ---------- Save/Load Utilities ----------
    public static void savePuzzlesToCSV(List<int[][]> puzzles, String filename) throws IOException {
        try (PrintWriter pw = new PrintWriter(new FileWriter(filename))) {
            for (int idx = 0; idx < puzzles.size(); idx++) {
                int[][] puzzle = puzzles.get(idx);
                for (int r = 0; r < 9; r++) {
                    for (int c = 0; c < 9; c++) {
                        pw.print(puzzle[r][c]);
                        if (c < 8)
                            pw.print(",");
                    }
                    pw.println();
                }
                if (idx < puzzles.size() - 1)
                    pw.println(); // blank line between puzzles
            }
        }
    }

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

    // ---------- Main ----------
    public static void main(String[] args) throws IOException {
        SudokuPuzzleGenerator gen = new SudokuPuzzleGenerator();

        int[] targetClues = { 40, 27, 20 };
        String[] levelNames = { "level1_easy", "level2_medium", "level3_hard" };
        int puzzlesPerLevel = 800; // or 10 for testing

        for (int level = 0; level < 3; level++) {
            List<int[][]> puzzles = new ArrayList<>();
            System.out.println("Generating " + levelNames[level] + " puzzles...");
            for (int i = 0; i < puzzlesPerLevel; i++) {
                int[][] puzzle = gen.generatePuzzle(targetClues[level]);
                // CRITICAL: store a deep copy, because generatePuzzle reuses the same array
                puzzles.add(deepCopy(puzzle));
                if ((i + 1) % 50 == 0) {
                    System.out.println("  Generated " + (i + 1) + " puzzles");
                }
            }
            String filename = levelNames[level] + ".csv";
            savePuzzlesToCSV(puzzles, filename);
            System.out.println("Saved " + puzzles.size() + " puzzles to " + filename);
        }
    }
}