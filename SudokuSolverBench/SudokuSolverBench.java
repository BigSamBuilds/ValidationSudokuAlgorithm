package SudokuSolverBench;
import java.util.*;

/**
 * A Sudoku solver class that provides three different solving strategies:
 * 1. DFS with backtracking (pruned) – checks legality before placing a number.
 * 2. True brute-force – tries all combinations and validates only at the end.
 * 3. Constraint Propagation (Regel 0) + DFS – reduces candidates first, then backtracks.
 * 
 * All algorithms operate on the same board instance.
 */
public class SudokuSolverBench {
    private int[][] board;
    private long nodesExplored;
    
    // Candidate sets for constraint propagation (Algorithm 3)
    private Set<Integer>[][] candidates;
    
    @SuppressWarnings("unchecked")
    public SudokuSolverBench() {
        board = new int[9][9];
        candidates = new HashSet[9][9];
        for (int r = 0; r < 9; r++) {
            for (int c = 0; c < 9; c++) {
                candidates[r][c] = new HashSet<>();
            }
        }
    }
    
    public void setBoard(int[][] newBoard) {
        // Deep copy to avoid external modification
        for (int r = 0; r < 9; r++) {
            System.arraycopy(newBoard[r], 0, board[r], 0, 9);
        }
    }
    
    public int[][] getBoard() {
        return board;
    }
    
    public long getNodesExplored() {
        return nodesExplored;
    }
    
    // ----------------------------------------------------------------------
    // 1. DFS with Backtracking (pruned)
    // ----------------------------------------------------------------------
    public boolean solveDFS() {
        for (int r = 0; r < 9; r++) {
            for (int c = 0; c < 9; c++) {
                if (board[r][c] != 0 && !isLegal(r, c, board[r][c])) {
                    return false;
                }
            }
        }
        nodesExplored = 0;
        return dfs(0, 0);
    }
    
    private boolean dfs(int row, int col) {
        nodesExplored++;
        if (row == 9) return true;
        if (col == 9) return dfs(row + 1, 0);
        if (board[row][col] != 0) return dfs(row, col + 1);
        
        for (int num = 1; num <= 9; num++) {
            if (isLegal(row, col, num)) {
                board[row][col] = num;
                if (dfs(row, col + 1)) {
                    return true;
                }
                board[row][col] = 0;
            }
        }
        return false;
    }
    
    // ----------------------------------------------------------------------
    // 2. True Brute-Force (no pruning during search)
    // ----------------------------------------------------------------------
    public boolean bruteForceSolve() {
        for (int r = 0; r < 9; r++) {
            for (int c = 0; c < 9; c++) {
                if (board[r][c] != 0 && !isLegal(r, c, board[r][c])) {
                    return false;
                }
            }
        }
        nodesExplored = 0;
        return bruteForce(0, 0);
    }
    
    private boolean bruteForce(int row, int col) {
        nodesExplored++;
        if (row == 9) {
            return isFullBoardValid();
        }
        if (col == 9) return bruteForce(row + 1, 0);
        if (board[row][col] != 0) return bruteForce(row, col + 1);
        
        for (int num = 1; num <= 9; num++) {
            board[row][col] = num;
            if (bruteForce(row, col + 1)) {
                return true;
            }
            board[row][col] = 0;
        }
        return false;
    }
    
    private boolean isFullBoardValid() {
        for (int r = 0; r < 9; r++) {
            for (int c = 0; c < 9; c++) {
                int val = board[r][c];
                if (val == 0) return false;
                board[r][c] = 0;
                boolean ok = isLegal(r, c, val);
                board[r][c] = val;
                if (!ok) return false;
            }
        }
        return true;
    }
    
    // ----------------------------------------------------------------------
    // 3. Constraint Propagation (Regel 0) + DFS
    // ----------------------------------------------------------------------
    public boolean solveWithConstraintPropagation() {
        // Initial validity check
        for (int r = 0; r < 9; r++) {
            for (int c = 0; c < 9; c++) {
                if (board[r][c] != 0 && !isLegal(r, c, board[r][c])) {
                    return false;
                }
            }
        }
        
        // Initialize candidate sets
        initCandidates();
        
        // Apply Regel 0 repeatedly until no changes
        boolean changed;
        do {
            changed = false;
            for (int r = 0; r < 9; r++) {
                for (int c = 0; c < 9; c++) {
                    if (board[r][c] == 0 && candidates[r][c].size() == 1) {
                        int num = candidates[r][c].iterator().next();
                        board[r][c] = num;
                        removeCandidateFromPeers(r, c, num);
                        changed = true;
                    }
                }
            }
        } while (changed);
        
        // Now solve remaining cells with DFS
        nodesExplored = 0;
        return dfsWithCandidates(0, 0);
    }
    
    private void initCandidates() {
        // Initialize all empty cells with {1..9}
        for (int r = 0; r < 9; r++) {
            for (int c = 0; c < 9; c++) {
                candidates[r][c].clear();
                if (board[r][c] == 0) {
                    for (int num = 1; num <= 9; num++) {
                        candidates[r][c].add(num);
                    }
                }
            }
        }
        
        // Remove candidates based on given numbers
        for (int r = 0; r < 9; r++) {
            for (int c = 0; c < 9; c++) {
                if (board[r][c] != 0) {
                    removeCandidateFromPeers(r, c, board[r][c]);
                }
            }
        }
    }
    
    private void removeCandidateFromPeers(int row, int col, int num) {
        // Row
        for (int c = 0; c < 9; c++) {
            if (c != col && board[row][c] == 0) {
                candidates[row][c].remove(num);
            }
        }
        // Column
        for (int r = 0; r < 9; r++) {
            if (r != row && board[r][col] == 0) {
                candidates[r][col].remove(num);
            }
        }
        // 3x3 box
        int boxRow = row - row % 3;
        int boxCol = col - col % 3;
        for (int r = boxRow; r < boxRow + 3; r++) {
            for (int c = boxCol; c < boxCol + 3; c++) {
                if ((r != row || c != col) && board[r][c] == 0) {
                    candidates[r][c].remove(num);
                }
            }
        }
    }
    
    private boolean dfsWithCandidates(int row, int col) {
        nodesExplored++;
        if (row == 9) return true;
        if (col == 9) return dfsWithCandidates(row + 1, 0);
        if (board[row][col] != 0) return dfsWithCandidates(row, col + 1);
        
        List<Integer> candList = new ArrayList<>(candidates[row][col]);
        for (int num : candList) {
            if (isLegal(row, col, num)) {
                board[row][col] = num;
                Set<Integer>[][] savedCandidates = saveCandidates();
                removeCandidateFromPeers(row, col, num);
                
                if (dfsWithCandidates(row, col + 1)) {
                    return true;
                }
                board[row][col] = 0;
                restoreCandidates(savedCandidates);
            }
        }
        return false;
    }
    
    @SuppressWarnings("unchecked")
    private Set<Integer>[][] saveCandidates() {
        Set<Integer>[][] copy = new HashSet[9][9];
        for (int r = 0; r < 9; r++) {
            for (int c = 0; c < 9; c++) {
                copy[r][c] = new HashSet<>(candidates[r][c]);
            }
        }
        return copy;
    }
    
    private void restoreCandidates(Set<Integer>[][] saved) {
        for (int r = 0; r < 9; r++) {
            for (int c = 0; c < 9; c++) {
                candidates[r][c] = new HashSet<>(saved[r][c]);
            }
        }
    }
    
    // ----------------------------------------------------------------------
    // Legal check
    // ----------------------------------------------------------------------
    private boolean isLegal(int row, int col, int num) {
        for (int c = 0; c < 9; c++) {
            if (board[row][c] == num && c != col) return false;
        }
        for (int r = 0; r < 9; r++) {
            if (board[r][col] == num && r != row) return false;
        }
        int boxRow = row - row % 3;
        int boxCol = col - col % 3;
        for (int r = boxRow; r < boxRow + 3; r++) {
            for (int c = boxCol; c < boxCol + 3; c++) {
                if (board[r][c] == num && (r != row || c != col)) return false;
            }
        }
        return true;
    }
    
    // ----------------------------------------------------------------------
    // Print board
    // ----------------------------------------------------------------------
    public void printBoard() {
        for (int r = 0; r < 9; r++) {
            for (int c = 0; c < 9; c++) {
                System.out.print(board[r][c] + " ");
            }
            System.out.println();
        }
    }
}