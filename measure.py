import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv("benchmark_results.csv")

# Use only steady-state runs (after warm-up)
STEADY_START = 5
steady = df[df['run'] >= STEADY_START]

# Compute per-puzzle means
means = steady.groupby(['puzzle_id', 'difficulty', 'algorithm'])[['time_ns', 'nodes']].mean().reset_index()

# Pivot to get DFS and CP as columns
pivot_time = means.pivot(index=['puzzle_id', 'difficulty'], columns='algorithm', values='time_ns')
pivot_nodes = means.pivot(index=['puzzle_id', 'difficulty'], columns='algorithm', values='nodes')

# Add speedup column
pivot_time['speedup'] = pivot_time['dfs'] / pivot_time['cp']

# Analyze per difficulty
for diff in ['easy', 'medium', 'hard']:
    # Filter by the 'difficulty' level in the MultiIndex
    sub_time = pivot_time.xs(diff, level='difficulty')
    sub_nodes = pivot_nodes.xs(diff, level='difficulty')
    
    print(f"\n=== {diff.upper()} ===")
    print(f"Number of puzzles: {len(sub_time)}")
    
    # Paired t-test on time
    t_stat, p_val = stats.ttest_rel(sub_time['dfs'], sub_time['cp'])
    print(f"Paired t-test (time): t = {t_stat:.3f}, p = {p_val:.2e}")
    
    # Median times
    print(f"DFS median time: {sub_time['dfs'].median()/1e6:.2f} ms")
    print(f"CP  median time: {sub_time['cp'].median()/1e6:.2f} ms")
    print(f"Median speedup (DFS/CP): {sub_time['speedup'].median():.2f}x")
    
    # Nodes reduction
    print(f"DFS median nodes: {sub_nodes['dfs'].median():.0f}")
    print(f"CP  median nodes: {sub_nodes['cp'].median():.0f}")
    if sub_nodes['cp'].median() > 0:
        print(f"Node reduction factor: {sub_nodes['dfs'].median() / sub_nodes['cp'].median():.1f}x")

# Boxplot of times per difficulty (log scale)
fig, axes = plt.subplots(1, 3, figsize=(14, 5))
for i, diff in enumerate(['easy', 'medium', 'hard']):
    sub = means[means['difficulty'] == diff]
    sub.boxplot(column='time_ns', by='algorithm', ax=axes[i])
    axes[i].set_title(diff)
    axes[i].set_ylabel("Time (ns)")
    axes[i].set_yscale('log')
plt.suptitle("")
plt.tight_layout()
plt.savefig("time_comparison.png", dpi=150)
print("\nBoxplot saved as time_comparison.png")

# Scatter plot: DFS vs CP time
plt.figure(figsize=(10, 8))
colors = {'easy': 'green', 'medium': 'blue', 'hard': 'red'}
for diff in ['easy', 'medium', 'hard']:
    sub = pivot_time.xs(diff, level='difficulty')
    plt.scatter(sub['dfs']/1e6, sub['cp']/1e6, c=colors[diff], label=diff, alpha=0.6)
plt.plot([0, pivot_time['dfs'].max()/1e6], [0, pivot_time['dfs'].max()/1e6], 'k--', label='Equal time')
plt.xlabel("DFS time (ms)")
plt.ylabel("CP time (ms)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.title("DFS vs CP+DFS Execution Time per Puzzle")
plt.savefig("scatter_comparison.png", dpi=150)
print("Scatter plot saved as scatter_comparison.png")