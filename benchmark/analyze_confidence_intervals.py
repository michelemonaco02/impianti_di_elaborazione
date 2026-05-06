import math
import pandas as pd

# ==========================================================
# analyze_confidence_intervals.py
# ==========================================================
#
# Calcola gli intervalli di confidenza al 95% per la media
# dei tempi di esecuzione del benchmark n-body.
#
# Input:
#   CSV generato da collect_nbody_measurements.sh
#
# Formula:
#   CI = mean ± z * s / sqrt(n)
#
# con z = 1.96 per livello di confidenza 95%.
# ==========================================================

Z_ALPHA_2 = 1.96

INPUT_FILES = [
    "misure_PC1.csv",
    "misure_PC2.csv",  # aggiungilo quando avrai anche il CSV del collega
]

# Se vuoi usare solo le prime 30 osservazioni:
USE_FIRST_N = 30

# Se invece vuoi usare tutte le osservazioni del CSV:
# USE_FIRST_N = None

dfs = []

for file in INPUT_FILES:
    dfs.append(pd.read_csv(file))

df = pd.concat(dfs, ignore_index=True)

required_columns = {"pc", "configurazione", "osservazione", "tempo_s"}

if not required_columns.issubset(df.columns):
    raise ValueError(
        f"Il CSV deve contenere le colonne: {required_columns}. "
        f"Colonne trovate: {set(df.columns)}"
    )

if USE_FIRST_N is not None:
    df = (
        df.sort_values(["pc", "configurazione", "osservazione"])
          .groupby(["pc", "configurazione"], group_keys=False)
          .head(USE_FIRST_N)
    )

rows = []

for (pc, configurazione), group in df.groupby(["pc", "configurazione"]):
    tempi = group["tempo_s"]

    n = len(tempi)
    mean = tempi.mean()
    std = tempi.std(ddof=1)
    standard_error = std / math.sqrt(n)

    ci_lower = mean - Z_ALPHA_2 * standard_error
    ci_upper = mean + Z_ALPHA_2 * standard_error

    rows.append({
        "Gruppo": pc,
        "Configurazione": configurazione,
        "Parametro": "Media",
        "Stima": mean,
        "CI inferiore": ci_lower,
        "CI superiore": ci_upper,
        "1-Alfa": 0.95,
        "N": n
    })

    rows.append({
        "Gruppo": pc,
        "Configurazione": configurazione,
        "Parametro": "Dev std",
        "Stima": std,
        "CI inferiore": "",
        "CI superiore": "",
        "1-Alfa": "",
        "N": n
    })

results = pd.DataFrame(rows)
results = results.sort_values(["Gruppo", "Configurazione", "Parametro"])

print("\n==========================================")
print("Intervalli di confidenza al 95%")
print("==========================================\n")

print(results.to_string(index=False))

results.to_csv("intervalli_confidenza.csv", index=False)

print("\nFile generato:")
print("- intervalli_confidenza.csv")