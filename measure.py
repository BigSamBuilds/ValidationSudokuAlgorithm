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

WARMUP_END = 4   # runs 0–4 = warm‑up, runs 5–9 = steady‑state

# Directory structure for output plots
LEVEL_DIRS = {
    'easy':   'Level_1_easy',
    'medium': 'Level_2_medium',
    'hard':   'Level_3_hard'
}
OUTPUT_BASE = 'statistics_plot'

# ============================================================
# LOAD SOLVER DATA
# ============================================================
df_jit_on  = pd.read_csv(JIT_ON_FILE)
df_jit_off = pd.read_csv(JIT_OFF_FILE)
df_jit_on['jit']  = 'on'
df_jit_off['jit'] = 'off'
df_all = pd.concat([df_jit_on, df_jit_off], ignore_index=True)

# ============================================================
# HELPER: Plot per‑algorithm (JIT ON = split, JIT OFF = flat)
# ============================================================
def plot_per_algorithm(data, title, filename, jit_status):
    """
    For JIT ON  : split warm‑up / steady‑state, with annotations and cutoff.
    For JIT OFF : single flat line across all runs (no artificial split).
    """
    run_stats = data.groupby('run')['time_ns'].agg(['mean', 'std', 'count'])
    run_stats['sem'] = run_stats['std'] / np.sqrt(run_stats['count'])

    means = run_stats['mean'].values
    sems  = run_stats['sem'].values
    runs  = run_stats.index.values
    n     = run_stats['count'].values[0]
    t_val = stats.t.ppf(0.975, n - 1)
    ci_low  = means - t_val * sems
    ci_high = means + t_val * sems

    fig, ax = plt.subplots(figsize=(11, 6))

    if jit_status == 'on':
        # JIT ON – split into warm‑up (orange) and steady‑state (green)
        warm_mask = runs <= WARMUP_END
        steady_mask = runs > WARMUP_END

        ax.plot(runs[warm_mask], means[warm_mask]/1e6, 'o-', color='darkorange',
                linewidth=2.5, markersize=8, label=f'Warm‑up (runs 0–{WARMUP_END})')
        ax.fill_between(runs[warm_mask], ci_low[warm_mask]/1e6, ci_high[warm_mask]/1e6,
                        alpha=0.15, color='orange')

        ax.plot(runs[steady_mask], means[steady_mask]/1e6, 's-', color='green',
                linewidth=2.5, markersize=8, label=f'Steady‑state (runs {WARMUP_END+1}–9)')
        ax.fill_between(runs[steady_mask], ci_low[steady_mask]/1e6, ci_high[steady_mask]/1e6,
                        alpha=0.15, color='green')

        # Cutoff line and annotations
        ax.axvline(x=WARMUP_END + 0.5, color='red', linestyle='--', linewidth=2, alpha=0.7,
                   label=f'Cutoff (run {WARMUP_END+1})')
        y_max = means.max()/1e6
        ax.annotate('WARM‑UP', xy=(2, y_max * 0.95), fontsize=12, fontweight='bold',
                    color='darkorange', ha='center', fontstyle='italic')
        ax.annotate('STEADY‑STATE', xy=(7, y_max * 0.95), fontsize=12, fontweight='bold',
                    color='green', ha='center', fontstyle='italic')

        # Horizontal steady‑state mean
        steady_mean = np.mean(means[steady_mask])
        ax.axhline(steady_mean/1e6, color='green', linestyle=':', linewidth=1.5, alpha=0.6,
                   label=f'Steady‑state mean: {steady_mean/1e6:.3f} ms')

    else:  # JIT OFF – all runs in one colour (red), no split
        ax.plot(runs, means/1e6, 'o-', color='red', linewidth=2.5, markersize=8,
                label='Mean time (all runs)')
        ax.fill_between(runs, ci_low/1e6, ci_high/1e6, alpha=0.12, color='red')
        overall_mean = np.mean(means)
        ax.axhline(overall_mean/1e6, color='darkred', linestyle=':', linewidth=1.5, alpha=0.6,
                   label=f'Overall mean: {overall_mean/1e6:.3f} ms')

    ax.set_xlabel('Run number', fontsize=12)
    ax.set_ylabel('Time (ms)', fontsize=12)
    ax.set_title(title, fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xticks(range(10))
    plt.tight_layout()

    # Ensure output directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {filename}")

# ============================================================
# HELPER: JIT ON vs OFF comparison (all 10 runs, warm‑up marked for JIT ON)
# ============================================================
def plot_jit_comparison(data_on, data_off, title, filename):
    """
    JIT ON (green) vs JIT OFF (red).  
    A vertical dashed line marks where JIT ON stabilises.
    A small "JIT ON" text is placed near the green line at the end.
    """
    def get_stats(data):
        stats = data.groupby('run')['time_ns'].agg(['mean', 'std', 'count'])
        stats['sem'] = stats['std'] / np.sqrt(stats['count'])
        return stats

    stats_on  = get_stats(data_on)
    stats_off = get_stats(data_off)
    n = stats_on['count'].values[0]
    t_val = stats.t.ppf(0.975, n - 1)

    fig, ax = plt.subplots(figsize=(11, 6))

    # JIT ON
    ax.plot(stats_on.index, stats_on['mean']/1e6, 's-', color='green', linewidth=2.5, markersize=8, label='JIT ON')
    ax.fill_between(stats_on.index,
                    (stats_on['mean'] - t_val * stats_on['sem'])/1e6,
                    (stats_on['mean'] + t_val * stats_on['sem'])/1e6,
                    alpha=0.12, color='green')

    # JIT OFF
    ax.plot(stats_off.index, stats_off['mean']/1e6, 'o-', color='red', linewidth=2.5, markersize=8, label='JIT OFF')
    ax.fill_between(stats_off.index,
                    (stats_off['mean'] - t_val * stats_off['sem'])/1e6,
                    (stats_off['mean'] + t_val * stats_off['sem'])/1e6,
                    alpha=0.12, color='red')

    # Cutoff line (legend only, no big text)
    ax.axvline(x=WARMUP_END + 0.5, color='black', linestyle='--', linewidth=2, alpha=0.7,
               label=f'JIT ON steady‑state starts (run {WARMUP_END+1})')

    # Small "JIT ON" label near the green line at the right side
    last_run = stats_on.index[-1]
    last_mean = stats_on.loc[last_run, 'mean'] / 1e6
    ax.text(last_run + 0.2, last_mean, 'JIT ON', color='green', fontsize=10,
            va='center', fontweight='bold')

    # Speedup annotation (unchanged)
    on_steady  = stats_on[stats_on.index > WARMUP_END]['mean'].mean()
    off_steady = stats_off[stats_off.index > WARMUP_END]['mean'].mean()
    speedup = off_steady / on_steady
    ax.text(0.98, 0.92, f'JIT Speedup: {speedup:.1f}×\n(steady‑state)', transform=ax.transAxes,
            fontsize=11, ha='right', va='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    ax.set_xlabel('Run number', fontsize=12)
    ax.set_ylabel('Time (ms)', fontsize=12)
    ax.set_title(title, fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xticks(range(10))
    plt.tight_layout()

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {filename}")

# ============================================================
# HELPER: Puzzle structure analysis
# ============================================================
def plot_puzzle_structure(puzzle_file, difficulty, filename):
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
    given_freq = np.mean(puzzles != 0, axis=0) * 100

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].hist(given_counts, bins=30, color='steelblue', edgecolor='black', alpha=0.7)
    axes[0].axvline(given_counts.mean(), color='red', linestyle='--', linewidth=2,
                    label=f'Mean: {given_counts.mean():.1f}')
    axes[0].set_xlabel('Number of given cells')
    axes[0].set_ylabel('Number of puzzles')
    axes[0].set_title(f'{difficulty.capitalize()} – Given Cells Distribution\n(n={len(puzzles)} puzzles)')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    im = axes[1].imshow(given_freq, cmap='YlOrRd', vmin=0, vmax=100)
    axes[1].set_title(f'{difficulty.capitalize()} – Cell Given Frequency (%)')
    axes[1].set_xticks(range(9))
    axes[1].set_yticks(range(9))
    axes[1].set_xlabel('Column')
    axes[1].set_ylabel('Row')
    for r in range(9):
        for c in range(9):
            axes[1].text(c, r, f'{given_freq[r,c]:.0f}%', ha='center', va='center',
                        fontsize=8, color='black' if given_freq[r,c] < 50 else 'white')
    plt.colorbar(im, ax=axes[1], label='Given frequency (%)')
    plt.tight_layout()

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {filename}")

# ============================================================
# GENERATE: Per‑level, per‑algorithm plots
# ============================================================
print("=" * 60)
print("PER‑LEVEL, PER‑ALGORITHM PLOTS")
print("=" * 60)

for diff in ['easy', 'medium', 'hard']:
    level_dir = f'{OUTPUT_BASE}/{LEVEL_DIRS[diff]}'

    for alg in ['dfs', 'cp']:
        alg_label = 'DFS' if alg == 'dfs' else 'CP+DFS'

        # JIT ON (with warm‑up split)
        data_on = df_all[(df_all['difficulty'] == diff) & (df_all['algorithm'] == alg) & (df_all['jit'] == 'on')]
        plot_per_algorithm(
            data_on,
            f'{diff.capitalize()} – {alg_label} – JIT ON\n(n={len(data_on)//10} puzzles, 10 runs each)',
            f'{level_dir}/{diff}_{alg}_JITon_warmup.png',
            jit_status='on'
        )

        # JIT OFF (flat, no split)
        data_off = df_all[(df_all['difficulty'] == diff) & (df_all['algorithm'] == alg) & (df_all['jit'] == 'off')]
        plot_per_algorithm(
            data_off,
            f'{diff.capitalize()} – {alg_label} – JIT OFF\n(n={len(data_off)//10} puzzles, 10 runs each)',
            f'{level_dir}/{diff}_{alg}_JIToff_warmup.png',
            jit_status='off'
        )

# ============================================================
# JIT ON vs OFF comparison plots
# ============================================================
print("\n" + "=" * 60)
print("JIT ON vs OFF COMPARISON PLOTS")
print("=" * 60)

for diff in ['easy', 'medium', 'hard']:
    level_dir = f'{OUTPUT_BASE}/{LEVEL_DIRS[diff]}'

    for alg in ['dfs', 'cp']:
        alg_label = 'DFS' if alg == 'dfs' else 'CP+DFS'

        data_on  = df_all[(df_all['difficulty'] == diff) & (df_all['algorithm'] == alg) & (df_all['jit'] == 'on')]
        data_off = df_all[(df_all['difficulty'] == diff) & (df_all['algorithm'] == alg) & (df_all['jit'] == 'off')]

        plot_jit_comparison(
            data_on, data_off,
            f'{diff.capitalize()} – {alg_label} – JIT ON vs JIT OFF\n(n={len(data_on)//10} puzzles, 10 runs each)',
            f'{level_dir}/{diff}_{alg}_JIT_comparison.png'
        )

# ============================================================
# PUZZLE STRUCTURE PLOTS
# ============================================================
print("\n" + "=" * 60)
print("PUZZLE STRUCTURE PLOTS")
print("=" * 60)

puzzle_plot_dir = f'{OUTPUT_BASE}/Puzzles_plot'
for diff, filepath in PUZZLE_FILES.items():
    plot_puzzle_structure(filepath, diff, f'{puzzle_plot_dir}/puzzle_structure_{diff}.png')

# ============================================================
# STATISTICAL SUMMARY (unchanged, uses steady‑state runs 5‑9)
# ============================================================
print("\n" + "=" * 60)
print("STATISTICAL SUMMARY")
print("=" * 60)

df_steady = df_all[df_all['run'] > WARMUP_END]
means = df_steady.groupby(['puzzle_id', 'difficulty', 'algorithm', 'jit'])[['time_ns', 'nodes']].mean().reset_index()

for jit_val, jit_label in [('on', 'JIT ON'), ('off', 'JIT OFF')]:
    print(f"\n{jit_label}:")
    sub = means[means['jit'] == jit_val]
    for diff in ['easy', 'medium', 'hard']:
        sub_diff = sub[sub['difficulty'] == diff]
        pivot = sub_diff.pivot(index='puzzle_id', columns='algorithm', values='time_ns')
        t_stat, p_val = stats.ttest_rel(pivot['dfs'], pivot['cp'])
        print(f"  {diff}: n={len(pivot)}, DFS median={pivot['dfs'].median()/1e6:.3f} ms, "
              f"CP median={pivot['cp'].median()/1e6:.3f} ms, t={t_stat:.2f}, p={p_val:.2e}")

print("\n" + "=" * 60)
print("All plots generated successfully!")
print("=" * 60)