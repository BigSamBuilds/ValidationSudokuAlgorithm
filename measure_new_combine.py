import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import os

# ============================================================
# CONFIGURATION
# ============================================================
JIT_ON_FILE  = "benchmark_results_JIT.csv"
JIT_OFF_FILE = "benchmark_results.csv"

PUZZLE_FILES = {
    'easy':   'SudokuPuzzleGenerator/level1_easy.csv',
    'medium': 'SudokuPuzzleGenerator/level2_medium.csv',
    'hard':   'SudokuPuzzleGenerator/level3_hard.csv'
}

WARMUP_END = 4
OUTPUT_BASE = 'statistics_plot/combined'

LEVEL_COLORS = {
    'easy':   '#2ecc71',
    'medium': '#3498db',
    'hard':   '#e74c3c'
}

# ============================================================
# LOAD SOLVER DATA
# ============================================================
df_jit_on  = pd.read_csv(JIT_ON_FILE)
df_jit_off = pd.read_csv(JIT_OFF_FILE)
df_jit_on['jit']  = 'on'
df_jit_off['jit'] = 'off'
df_all = pd.concat([df_jit_on, df_jit_off], ignore_index=True)

# ============================================================
# HELPER: Get run statistics
# ============================================================
def get_run_stats(data):
    run_stats = data.groupby('run')['time_ns'].agg(['mean', 'std', 'count'])
    run_stats['sem'] = run_stats['std'] / np.sqrt(run_stats['count'])
    return run_stats

# ============================================================
# 1. COMBINED PUZZLE STRUCTURE (all levels overlaid)
# ============================================================
print("=" * 60)
print("GENERATING COMBINED PUZZLE STRUCTURE PLOT")
print("=" * 60)

fig, (ax_hist, ax_heat) = plt.subplots(1, 2, figsize=(18, 7))

# --- Combined histogram ---
for diff in ['easy', 'medium', 'hard']:
    puzzle_file = PUZZLE_FILES[diff]
    puzzles = []
    current = []
    with open(puzzle_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line == '':
                if len(current) == 9:
                    puzzles.append(np.array(current))
                current = []
            else:
                current.append([int(x) for x in line.split(',')])
        if len(current) == 9:
            puzzles.append(np.array(current))

    puzzles = np.array(puzzles)
    given_counts = np.sum(puzzles != 0, axis=(1, 2))

    ax_hist.hist(given_counts, bins=25, color=LEVEL_COLORS[diff], alpha=0.5,
                 edgecolor='black', label=f'{diff.capitalize()} (n={len(puzzles)})')
    ax_hist.axvline(given_counts.mean(), color=LEVEL_COLORS[diff], linestyle='--', linewidth=2)

ax_hist.set_xlabel('Number of given cells', fontsize=12)
ax_hist.set_ylabel('Number of puzzles', fontsize=12)
ax_hist.set_title('Given Cells Distribution – All Levels', fontsize=14, fontweight='bold')
ax_hist.legend(fontsize=10)
ax_hist.grid(True, alpha=0.3)

# --- Combined heatmap (average across all levels) ---
all_freqs = []
for diff in ['easy', 'medium', 'hard']:
    puzzle_file = PUZZLE_FILES[diff]
    puzzles = []
    current = []
    with open(puzzle_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line == '':
                if len(current) == 9:
                    puzzles.append(np.array(current))
                current = []
            else:
                current.append([int(x) for x in line.split(',')])
        if len(current) == 9:
            puzzles.append(np.array(current))
    puzzles = np.array(puzzles)
    given_freq = np.mean(puzzles != 0, axis=0) * 100
    all_freqs.append(given_freq)

# Average frequency across all three levels
avg_freq = np.mean(all_freqs, axis=0)

im = ax_heat.imshow(avg_freq, cmap='YlOrRd', vmin=0, vmax=100)
ax_heat.set_title('Average Cell Given Frequency (%) – All Levels', fontsize=14, fontweight='bold')
ax_heat.set_xticks(range(9))
ax_heat.set_yticks(range(9))
ax_heat.set_xlabel('Column', fontsize=12)
ax_heat.set_ylabel('Row', fontsize=12)

for r in range(9):
    for c in range(9):
        ax_heat.text(c, r, f'{avg_freq[r,c]:.0f}%', ha='center', va='center',
                     fontsize=8, color='black' if avg_freq[r,c] < 50 else 'white')

plt.colorbar(im, ax=ax_heat, label='Given frequency (%)')
plt.tight_layout()
os.makedirs(OUTPUT_BASE, exist_ok=True)
plt.savefig(f'{OUTPUT_BASE}/combined_puzzle_structure.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Saved: combined_puzzle_structure.png")

# ============================================================
# 2. COMBINED JIT ON PLOT (all levels overlaid, per algorithm)
# ============================================================
print("\n" + "=" * 60)
print("GENERATING COMBINED JIT ON PLOT")
print("=" * 60)

fig, axes = plt.subplots(2, 1, figsize=(14, 12))

for alg_idx, alg in enumerate(['dfs', 'cp']):
    alg_label = 'DFS' if alg == 'dfs' else 'CP+DFS'
    ax = axes[alg_idx]

    for diff in ['easy', 'medium', 'hard']:
        data = df_all[(df_all['difficulty'] == diff) & (df_all['algorithm'] == alg) & (df_all['jit'] == 'on')]
        run_stats = get_run_stats(data)

        means = run_stats['mean'].values / 1e6
        runs  = run_stats.index.values
        n     = run_stats['count'].values[0]
        t_val = stats.t.ppf(0.975, n - 1)
        ci_low  = (run_stats['mean'].values - t_val * run_stats['sem'].values) / 1e6
        ci_high = (run_stats['mean'].values + t_val * run_stats['sem'].values) / 1e6

        ax.plot(runs, means, 'o-', color=LEVEL_COLORS[diff], linewidth=2, markersize=6,
                label=f'{diff.capitalize()}')
        ax.fill_between(runs, ci_low, ci_high, alpha=0.12, color=LEVEL_COLORS[diff])

        # Steady-state mean
        steady_mean = np.mean(means[runs > WARMUP_END])
        ax.axhline(steady_mean, color=LEVEL_COLORS[diff], linestyle=':', linewidth=1.5, alpha=0.6)

    # Cutoff line
    ax.axvline(x=WARMUP_END + 0.5, color='black', linestyle='--', linewidth=2, alpha=0.7,
               label=f'Steady‑state starts (run {WARMUP_END+1})')

    ax.set_title(f'{alg_label} – JIT ON – All Levels', fontsize=14, fontweight='bold')
    ax.set_xlabel('Run number', fontsize=12)
    ax.set_ylabel('Time (ms)', fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xticks(range(10))

plt.suptitle('JIT ON – All Levels Combined', fontsize=16, fontweight='bold', y=0.998)
plt.tight_layout()
plt.savefig(f'{OUTPUT_BASE}/combined_JITon_warmup.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Saved: combined_JITon_warmup.png")

# ============================================================
# 3. COMBINED JIT OFF PLOT (all levels overlaid, per algorithm)
# ============================================================
print("\n" + "=" * 60)
print("GENERATING COMBINED JIT OFF PLOT")
print("=" * 60)

fig, axes = plt.subplots(2, 1, figsize=(14, 12))

for alg_idx, alg in enumerate(['dfs', 'cp']):
    alg_label = 'DFS' if alg == 'dfs' else 'CP+DFS'
    ax = axes[alg_idx]

    for diff in ['easy', 'medium', 'hard']:
        data = df_all[(df_all['difficulty'] == diff) & (df_all['algorithm'] == alg) & (df_all['jit'] == 'off')]
        run_stats = get_run_stats(data)

        means = run_stats['mean'].values / 1e6
        runs  = run_stats.index.values
        n     = run_stats['count'].values[0]
        t_val = stats.t.ppf(0.975, n - 1)
        ci_low  = (run_stats['mean'].values - t_val * run_stats['sem'].values) / 1e6
        ci_high = (run_stats['mean'].values + t_val * run_stats['sem'].values) / 1e6

        ax.plot(runs, means, 'o-', color=LEVEL_COLORS[diff], linewidth=2, markersize=6,
                label=f'{diff.capitalize()}')
        ax.fill_between(runs, ci_low, ci_high, alpha=0.12, color=LEVEL_COLORS[diff])

        overall_mean = np.mean(means)
        ax.axhline(overall_mean, color=LEVEL_COLORS[diff], linestyle=':', linewidth=1.5, alpha=0.6)

    ax.set_title(f'{alg_label} – JIT OFF – All Levels', fontsize=14, fontweight='bold')
    ax.set_xlabel('Run number', fontsize=12)
    ax.set_ylabel('Time (ms)', fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xticks(range(10))

plt.suptitle('JIT OFF – All Levels Combined', fontsize=16, fontweight='bold', y=0.998)
plt.tight_layout()
plt.savefig(f'{OUTPUT_BASE}/combined_JIToff_warmup.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Saved: combined_JIToff_warmup.png")

# ============================================================
# 4. COMBINED JIT ON vs OFF COMPARISON (overlaid per algorithm)
# ============================================================
print("\n" + "=" * 60)
print("GENERATING COMBINED JIT COMPARISON PLOT")
print("=" * 60)

fig, axes = plt.subplots(2, 1, figsize=(14, 12))

for alg_idx, alg in enumerate(['dfs', 'cp']):
    alg_label = 'DFS' if alg == 'dfs' else 'CP+DFS'
    ax = axes[alg_idx]

    for diff in ['easy', 'medium', 'hard']:
        data_on  = df_all[(df_all['difficulty'] == diff) & (df_all['algorithm'] == alg) & (df_all['jit'] == 'on')]
        data_off = df_all[(df_all['difficulty'] == diff) & (df_all['algorithm'] == alg) & (df_all['jit'] == 'off')]

        stats_on  = get_run_stats(data_on)
        stats_off = get_run_stats(data_off)
        n = stats_on['count'].values[0]
        t_val = stats.t.ppf(0.975, n - 1)

        # JIT ON – solid line
        ax.plot(stats_on.index, stats_on['mean']/1e6, 's-', color=LEVEL_COLORS[diff],
                linewidth=2, markersize=6, label=f'{diff.capitalize()} JIT ON')
        ax.fill_between(stats_on.index,
                        (stats_on['mean'] - t_val * stats_on['sem'])/1e6,
                        (stats_on['mean'] + t_val * stats_on['sem'])/1e6,
                        alpha=0.08, color=LEVEL_COLORS[diff])

        # JIT OFF – dashed line
        ax.plot(stats_off.index, stats_off['mean']/1e6, 'o--', color=LEVEL_COLORS[diff],
                linewidth=2, markersize=6, label=f'{diff.capitalize()} JIT OFF', alpha=0.6)
        ax.fill_between(stats_off.index,
                        (stats_off['mean'] - t_val * stats_off['sem'])/1e6,
                        (stats_off['mean'] + t_val * stats_off['sem'])/1e6,
                        alpha=0.05, color=LEVEL_COLORS[diff])

        # Speedup annotation
        on_steady  = stats_on[stats_on.index > WARMUP_END]['mean'].mean()
        off_steady = stats_off[stats_off.index > WARMUP_END]['mean'].mean()
        speedup = off_steady / on_steady
        ax.text(0.98, 0.95 - alg_idx * 0.08 - ['easy', 'medium', 'hard'].index(diff) * 0.06,
                f'{diff.capitalize()} speedup: {speedup:.1f}×',
                transform=ax.transAxes, fontsize=9, ha='right',
                color=LEVEL_COLORS[diff], fontweight='bold')

    # Cutoff line
    ax.axvline(x=WARMUP_END + 0.5, color='black', linestyle='--', linewidth=2, alpha=0.7,
               label=f'Steady‑state starts (run {WARMUP_END+1})')

    ax.set_title(f'{alg_label} – JIT ON vs JIT OFF – All Levels', fontsize=14, fontweight='bold')
    ax.set_xlabel('Run number', fontsize=12)
    ax.set_ylabel('Time (ms)', fontsize=12)
    ax.legend(fontsize=9, ncol=2)
    ax.grid(True, alpha=0.3)
    ax.set_xticks(range(10))

plt.suptitle('JIT ON vs JIT OFF – All Levels Combined', fontsize=16, fontweight='bold', y=0.998)
plt.tight_layout()
plt.savefig(f'{OUTPUT_BASE}/combined_all_levels_comparison.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Saved: combined_all_levels_comparison.png")

# ============================================================
# STATISTICAL SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("STATISTICAL SUMMARY (steady‑state runs 5–9)")
print("=" * 60)

df_steady = df_all[df_all['run'] > WARMUP_END]
means = df_steady.groupby(['puzzle_id', 'difficulty', 'algorithm', 'jit'])[['time_ns', 'nodes']].mean().reset_index()

for jit_val, jit_label in [('on', 'JIT ON'), ('off', 'JIT OFF')]:
    print(f"\n{jit_label}:")
    sub = means[means['jit'] == jit_val]
    for diff in ['easy', 'medium', 'hard']:
        sub_diff = sub[sub['difficulty'] == diff]
        pivot_time = sub_diff.pivot(index='puzzle_id', columns='algorithm', values='time_ns')
        pivot_nodes = sub_diff.pivot(index='puzzle_id', columns='algorithm', values='nodes')

        t_stat, p_val = stats.ttest_rel(pivot_time['dfs'], pivot_time['cp'])
        print(f"  {diff}: n={len(pivot_time)}")
        print(f"    Time  – DFS median: {pivot_time['dfs'].median()/1e6:.3f} ms, "
              f"CP median: {pivot_time['cp'].median()/1e6:.3f} ms, "
              f"t={t_stat:.2f}, p={p_val:.2e}")

        dfs_nodes_median = pivot_nodes['dfs'].median()
        cp_nodes_median  = pivot_nodes['cp'].median()
        reduction = dfs_nodes_median / cp_nodes_median if cp_nodes_median > 0 else float('nan')
        print(f"    Nodes – DFS median: {dfs_nodes_median:.0f}, "
              f"CP median: {cp_nodes_median:.0f}, "
              f"reduction factor: {reduction:.1f}×")

print("\n" + "=" * 60)
print("All combined plots saved to " + OUTPUT_BASE)
print("=" * 60)