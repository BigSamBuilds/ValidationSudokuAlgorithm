import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# =========================
# LOAD DATA
# =========================
df_nojit = pd.read_csv("benchmark_results.csv")
df_jit   = pd.read_csv("benchmark_results_JIT.csv")

df_nojit["jit"] = "Off"
df_jit["jit"] = "On"

df = pd.concat([df_nojit, df_jit], ignore_index=True)

# =========================
# BASIC RESULTS
# =========================
print(df.groupby(["algorithm", "jit"])["time_ns"].mean())

# =========================
# BOXPLOT
# =========================
for algo in df["algorithm"].unique():

    subset = df[df["algorithm"] == algo]

    on = subset[subset["jit"] == "On"]["time_ns"]
    off = subset[subset["jit"] == "Off"]["time_ns"]

    plt.figure(figsize=(8,5))
    plt.boxplot([on, off], labels=["JIT On", "JIT Off"])
    plt.title(f"{algo.upper()} Runtime Comparison")
    plt.ylabel("Time (ns)")
    plt.grid(True, alpha=0.3)
    plt.show()

# =========================
# T-TEST
# =========================
for algo in df["algorithm"].unique():

    subset = df[df["algorithm"] == algo]

    on = subset[subset["jit"] == "On"]["time_ns"]
    off = subset[subset["jit"] == "Off"]["time_ns"]

    t, p = stats.ttest_ind(on, off, equal_var=False)

    print(f"\n{algo.upper()}:")
    print("p-value:", p)