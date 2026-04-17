import SudokuSolverBench.SudokuSolverBench;

public class testNoSample {
        static int[][] veryEasyPuzzle = {
                        { 0, 0, 4, 6, 7, 8, 9, 1, 2 },
                        { 6, 7, 2, 1, 9, 5, 3, 4, 8 },
                        { 1, 9, 8, 3, 4, 2, 5, 6, 7 },
                        { 8, 5, 0, 7, 6, 1, 4, 2, 3 },
                        { 4, 2, 6, 8, 0, 3, 7, 9, 1 },
                        { 7, 1, 3, 9, 2, 0, 8, 5, 6 },
                        { 9, 6, 1, 5, 0, 7, 2, 8, 4 },
                        { 2, 8, 7, 4, 1, 9, 6, 3, 5 },
                        { 0, 0, 0, 2, 0, 6, 1, 7, 9 }
        };

        static int[][] easyPuzzle = {
                        { 5, 3, 0, 0, 7, 0, 0, 0, 0 },
                        { 6, 0, 0, 1, 9, 5, 0, 0, 0 },
                        { 0, 9, 8, 0, 0, 0, 0, 6, 0 },
                        { 8, 0, 0, 0, 6, 0, 0, 0, 3 },
                        { 4, 0, 0, 8, 0, 3, 0, 0, 1 },
                        { 7, 0, 0, 0, 2, 0, 0, 0, 6 },
                        { 0, 6, 0, 0, 0, 0, 2, 8, 0 },
                        { 0, 0, 0, 4, 1, 9, 0, 0, 5 },
                        { 3, 4, 5, 2, 8, 6, 1, 7, 9 }
        };
        static int[][] mediumPuzzle = {
                        { 0, 0, 0, 2, 6, 0, 7, 0, 1 },
                        { 6, 8, 0, 0, 7, 0, 0, 9, 0 },
                        { 1, 9, 0, 0, 0, 4, 5, 0, 0 },
                        { 8, 2, 0, 1, 0, 0, 0, 4, 0 },
                        { 0, 0, 4, 6, 0, 2, 9, 0, 0 },
                        { 0, 5, 0, 0, 0, 3, 0, 2, 8 },
                        { 0, 0, 9, 3, 0, 0, 0, 7, 4 },
                        { 0, 4, 0, 0, 5, 0, 0, 3, 6 },
                        { 7, 0, 3, 0, 1, 8, 0, 0, 0 }
        };

        static int[][] hardPuzzle = {
                        { 0, 0, 0, 6, 0, 0, 4, 0, 0 },
                        { 7, 0, 0, 0, 0, 3, 6, 0, 0 },
                        { 0, 0, 0, 0, 9, 1, 0, 8, 0 },
                        { 0, 0, 0, 0, 0, 0, 0, 0, 0 },
                        { 0, 5, 0, 1, 8, 0, 0, 0, 3 },
                        { 0, 0, 0, 3, 0, 6, 0, 4, 5 },
                        { 0, 4, 0, 2, 0, 0, 0, 6, 0 },
                        { 9, 0, 3, 0, 0, 0, 0, 0, 0 },
                        { 0, 2, 0, 0, 0, 0, 1, 0, 0 }
        };

        static int[][] hard17 = {
                        { 0, 0, 0, 0, 0, 0, 0, 1, 2 },
                        { 0, 0, 0, 0, 3, 5, 0, 0, 0 },
                        { 0, 0, 0, 6, 0, 0, 0, 7, 0 },
                        { 7, 0, 0, 0, 0, 0, 3, 0, 0 },
                        { 0, 0, 0, 4, 0, 0, 8, 0, 0 },
                        { 1, 0, 0, 0, 0, 0, 0, 0, 0 },
                        { 0, 0, 0, 1, 2, 0, 0, 0, 0 },
                        { 0, 8, 0, 0, 0, 0, 0, 4, 0 },
                        { 0, 5, 0, 0, 0, 0, 6, 0, 0 }
        };

        public static void main(String[] args) {
                SudokuSolverBench solver = new SudokuSolverBench();

                // Test with the easy puzzle
                int[][] puzzle = hard17; // or mediumPuzzle / hardPuzzle

                solver.setBoard(puzzle);
                System.out.println("Original board:");
                solver.printBoard();

                // ---- Test DFS with backtracking ----
                long start = System.nanoTime();
                boolean solved = solver.solveDFS();
                long time = System.nanoTime() - start;

                System.out.println("\nDFS solved: " + solved);
                System.out.println("Time: " + time / 1_000_000.0 + " ms");
                System.out.println("Nodes explored: " + solver.getNodesExplored());
                solver.printBoard();

                // After resetting the board
                solver.setBoard(puzzle);
                start = System.nanoTime();
                boolean solvedCP = solver.solveWithConstraintPropagation();
                long timeCP = System.nanoTime() - start;

                System.out.println("Constraint Propagation + DFS solved: " + solvedCP);
                System.out.println("Time: " + timeCP / 1_000_000.0 + " ms");
                System.out.println("Nodes: " + solver.getNodesExplored());
                solver.printBoard();

                // // Reset board for brute-force
                // solver.setBoard(puzzle);
                // // ---- Test true brute-force ----
                // start = System.nanoTime();
                // solved = solver.bruteForceSolve();
                // time = System.nanoTime() - start;

                // System.out.println("\nBrute-force solved: " + solved);
                // System.out.println("Time: " + time / 1_000_000.0 + " ms");
                // System.out.println("Nodes explored: " + solver.getNodesExplored());
                // solver.printBoard();
        }
}