import subprocess
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from scipy import stats

# Hämta sökvägen till där skriptet ligger
script_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Script directory: {script_dir}")
# Gå till föräldramappen (EDAA35_Utv-rdering)
parent_dir = os.path.dirname(script_dir)
os.chdir(parent_dir)
print(f"Changed to: {os.getcwd()}")

results_dir = "Lab5/Results"

# Parameters
inFile = "Lab5/data1.txt"
n_inner=600
n_outer=10 # test 10 and 100
algorithm = "Collections_sort"

def plot_confidence(n_outer, all_means, means_of_all_means, ci_upper, ci_lower, results_dir, algorithm, jit_status):
    # Efter att du beräknat konfidensintervallet, plotta resultaten
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, n_outer+1), all_means, 'bo-', label='Medelvärde per körning')
    plt.axhline(y=means_of_all_means, color='r', linestyle='-', label=f'Totalt medelvärde: {means_of_all_means:.2f}')
    plt.axhline(y=ci_upper, color='g', linestyle='--', label=f'KI övre: {ci_upper:.2f}')
    plt.axhline(y=ci_lower, color='g', linestyle='--', label=f'KI nedre: {ci_lower:.2f}')
    plt.fill_between(range(1, n_outer+1), ci_lower, ci_upper, alpha=0.2, color='green')
    plt.xlabel('Körningsnummer')
    plt.ylabel('Medeltid i jämviktsläge (ns)')
    plt.title(f'Medelvärden för {n_outer} körningar med 95% konfidensintervall: {jit_status}')
    plt.legend()
    plt.grid(True, alpha=0.5)
    plt.savefig(f"{results_dir}/{algorithm}_confidence_interval_{n_outer}_runs.pdf")
    plt.show()

def plot_all_jamn(df, jamnvikt_start, df_jamvikt, i, results_dir, description, jit_status):
    # Skapa en figur med två subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    fig.suptitle(f'{jit_status} - Insvängningsförlopp och jämviktsläge', fontsize=16, fontweight='bold')

    # Vänster plot - alla mätningar
    df.plot(ax=ax1)
    ax1.axvline(x=jamnvikt_start, color='r', linestyle='--', label=f'Jämvikt start ({jamnvikt_start})')
    ax1.set_title(f"Körning {i + 1} - Alla mätningar")
    ax1.set_xlabel("Mätning (löpnummer/serial number)")
    ax1.set_ylabel("Tid (ns)")
    ax1.legend()
    ax1.grid(True, alpha=0.5)
    # Höger plot - bara jämviktsläget
    df_jamvikt.plot(ax=ax2)
    ax2.set_title(f"Körning {i + 1} - Jämviktsläge (Zoom in)")
    ax2.set_xlabel("Mätning (löpnummer/serial number)")
    ax2.set_ylabel("Tid (ns)")
    ax2.grid(True, alpha=0.5)
    # plt.title(description)
    plt.tight_layout()
    plt.savefig(f"{results_dir}/{description}_combined.pdf")
    plt.show()

def run_experiment(jit_on, n_outer, jamnvikt_start, jit_status):
    all_means = []
    for i in range(n_outer):
        description = f"{algorithm}_data1_{n_inner}_run{i}"
        resultFile = f"{results_dir}/{description}.csv"

        print(f"  Körning {i+1}/{n_outer}...")

        if jit_on:
            cmd = ["java", "-cp", ".", "Lab5.Measure", inFile, resultFile, str(n_inner)]
        else:
            cmd = ["java", "-Xint", "-cp", ".", "Lab5.Measure", inFile, resultFile, str(n_inner)]
        subprocess.run(cmd)

        df = pd.read_csv(resultFile, index_col=0)
        df_jamvikt = df[jamnvikt_start:]
        if i==0:
            plot_all_jamn(df, jamnvikt_start, df_jamvikt, i, results_dir, description, jit_status)

        steady_state = df[jamnvikt_start:]
        mean_jamnvikt = steady_state.mean().values[0]
        all_means.append(mean_jamnvikt)
    print("\n========================================")
    print(f"\n{jit_status} - Means: {all_means}")
    print("\n========================================")
    return all_means

jamnvikt_start_jit_on = 130    # for JIT on
jamnvikt_start_jit_off = 100   # for JIT off

print("\nRun with JIT")
jit_on = True
means_jit_on = run_experiment(jit_on, n_outer, jamnvikt_start_jit_on, "JIT on")

print("\nRun without JIT")
jit_on = False
means_jit_off = run_experiment(jit_on, n_outer, jamnvikt_start_jit_off, "JIT off")

# Statistics
t_value = stats.t.ppf(0.95, n_outer-1)

mean_on = np.mean(means_jit_on)
std_on = np.std(means_jit_on, ddof=1)
sem_on = stats.sem(means_jit_on)
ci_upper_on = mean_on + t_value * sem_on
ci_lower_on = mean_on - t_value * sem_on

mean_off = np.mean(means_jit_off)
std_off = np.std(means_jit_off, ddof=1)
sem_off = stats.sem(means_jit_off)
ci_upper_off = mean_off + t_value * sem_off
ci_lower_off = mean_off - t_value * sem_off

# Make t-test
t_stat, p_value = stats.ttest_ind(means_jit_on, means_jit_off)

#  95 confidence interval
plot_confidence(n_outer, means_jit_on, mean_on, ci_upper_on, ci_lower_on, results_dir, algorithm, "JIT on")
plot_confidence(n_outer, means_jit_off, mean_off, ci_upper_off, ci_lower_off, results_dir, algorithm, "JIT off")

# Skapa en boxplot för jämförelse
plt.figure(figsize=(10, 6))
plt.boxplot([means_jit_on, means_jit_off], labels=['JIT PÅ', 'JIT AV'])
plt.title('Jämförelse av exekveringstid med och utan JIT')
plt.ylabel('Medeltid i jämviktsläge (ns)')
plt.grid(True, alpha=0.3)

# Lägg till konfidensintervall som punkter med felstaplar
plt.plot(1, mean_on, 'ro', markersize=10, label=f'Medel JIT PÅ: {mean_on:.2f}')
plt.plot(2, mean_off, 'ro', markersize=10, label=f'Medel JIT AV: {mean_off:.2f}')
plt.errorbar([1, 2], [mean_on, mean_off], 
             yerr=[[mean_on - ci_lower_on, mean_off - ci_lower_off], 
                   [ci_upper_on - mean_on, ci_upper_off - mean_off]], 
             fmt='none', color='red', capsize=5)

plt.legend()
plt.savefig(f"{results_dir}/{algorithm}_JIT_comparison_boxplot.pdf")
plt.show()

print("\n========================================")
print("JÄMFÖRELSE: JIT PÅ vs JIT AV")
print(f"Medelvärde JIT PÅ: {np.mean(means_jit_on):.2f} ± {stats.sem(means_jit_on)*stats.t.ppf(0.975, n_outer-1):.2f}")
print(f"Medelvärde JIT AV: {np.mean(means_jit_off):.2f} ± {stats.sem(means_jit_off)*stats.t.ppf(0.975, n_outer-1):.2f}")
print(f"t-statistic: {t_stat}")
print(f"p-värde: {p_value}")

if p_value < 0.05:
    print("Skillnaden är statistiskt signifikant (p < 0.05)")
else:
    print("Ingen statistiskt signifikant skillnad (p >= 0.05)")
print("========================================")