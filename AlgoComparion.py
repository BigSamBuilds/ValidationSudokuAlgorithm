import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# Load data
#df = pd.read_csv("C:/Users/Tonny/OneDrive/Dokument/SudokuValidationUtvardering/ValidationSudokuAlgorithm/benchmark_results.csv")

df = pd.read_csv("C:/Users/Tonny/OneDrive/Dokument/SudokuValidationUtvardering/ValidationSudokuAlgorithm/benchmark_results_JIT.csv")

# Plotting
def plot_confidence(label, means):
    mean = np.mean(means)
    sem = stats.sem(means)
    t = stats.t.ppf(0.975, len(means) - 1)

    ci_low = mean - t * sem
    ci_high = mean + t * sem

    plt.figure(figsize=(8, 5))

    plt.plot(means, 'bo-', label="Run means")
    plt.axhline(mean, color='r', label=f"Mean: {mean:.2f}")
    plt.axhline(ci_low, color='g', linestyle='--')
    plt.axhline(ci_high, color='g', linestyle='--')

    plt.fill_between(range(len(means)), ci_low, ci_high, alpha=0.2)

    plt.title(f"{label} - 95% CI")
    plt.xlabel("Run")
    plt.ylabel("Time (ns)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()

# Grouping algos
algorithms = df["algorithm"].unique()

all_results = {}

for algo in algorithms:
    data = df[df["algorithm"] == algo]

    # mean per run (det viktiga steget)
    run_means = data.groupby("run")["time_ns"].mean().values

    all_results[algo] = run_means

    print("\n====================")
    print(f"Algorithm: {algo}")
    print(f"Mean: {np.mean(run_means):.2f} ns")
    print("====================")

    plot_confidence(algo, run_means)

# Boxplot comparison
plt.figure(figsize=(10, 6))

plt.boxplot(all_results.values(), labels=all_results.keys())

plt.title("Algorithm comparison (mean time per run)")
plt.ylabel("Time (ns)")
plt.grid(True, alpha=0.3)

plt.show()

# Stats, p and  t-values
if len(all_results) >= 2:
    keys = list(all_results.keys())

    t_stat, p_value = stats.ttest_ind(all_results[keys[0]], all_results[keys[1]])

    print("\nT-test:")
    print(f"{keys[0]} vs {keys[1]}")
    print("t-stat:", t_stat)
    print("p-value:", p_value)

    if p_value < 0.05:
        print("Significant difference")
    else:
        print("No significant difference")