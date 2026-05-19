import pandas as pd
from scipy.stats import levene

# ==========================================================
# analyze_levene_10000.py
# ==========================================================
#
# Scopo:
#   Eseguire il test di Levene solo per la configurazione
#   a 10000 iterazioni, cioè l'unica configurazione per cui
#   gli intervalli di confidenza dei due PC risultano
#   parzialmente sovrapposti.
#
# Ipotesi del test:
#   H0: le varianze dei due gruppi sono uguali
#   H1: le varianze dei due gruppi sono diverse
#
# Regola decisionale:
#   p-value >= 0.05  -> non rigetto H0
#                       -> varianze compatibili
#                       -> useremo two-sample t-test pooled
#
#   p-value < 0.05   -> rigetto H0
#                       -> varianze diverse
#                       -> useremo Welch t-test / unpooled
#
# Input:
#   misure_PC1.csv
#   misure_PC2.csv
#
# Colonne attese:
#   pc,configurazione,osservazione,tempo_s,...
# ==========================================================

ALPHA = 0.05
TARGET_CONFIG = 10000

INPUT_FILES = [
    "misure_PC1.csv",
    "misure_PC2.csv",
]

# Usa solo le prime 30 osservazioni per coerenza con CI e report.
# Metti None se vuoi usare tutte le osservazioni disponibili.
USE_FIRST_N = 30

df = pd.concat([pd.read_csv(file) for file in INPUT_FILES], ignore_index=True)

required_columns = {"pc", "configurazione", "osservazione", "tempo_s"}

if not required_columns.issubset(df.columns):
    raise ValueError(
        f"Il CSV deve contenere le colonne: {required_columns}. "
        f"Colonne trovate: {set(df.columns)}"
    )

# Usiamo eventualmente solo le prime N osservazioni per ogni PC-configurazione
if USE_FIRST_N is not None:
    df = (
        df.sort_values(["pc", "configurazione", "osservazione"])
          .groupby(["pc", "configurazione"], group_keys=False)
          .head(USE_FIRST_N)
    )

# Filtra solo la configurazione di interesse
df_config = df[df["configurazione"] == TARGET_CONFIG]

if df_config.empty:
    raise ValueError(
        f"Nessun dato trovato per la configurazione {TARGET_CONFIG}."
    )

pc_values = {}

for pc, pc_group in df_config.groupby("pc"):
    pc_values[pc] = pc_group["tempo_s"].values

if "PC1" not in pc_values or "PC2" not in pc_values:
    raise ValueError(
        f"Per la configurazione {TARGET_CONFIG} servono dati sia per PC1 sia per PC2."
    )

stat, p_value = levene(pc_values["PC1"], pc_values["PC2"], center="median")

if p_value >= ALPHA:
    decisione = "Non rigetto H0"
    conclusione = "Varianze compatibili"
    test_successivo = "Two-sample t-test pooled"
else:
    decisione = "Rigetto H0"
    conclusione = "Varianze diverse"
    test_successivo = "Welch t-test / unpooled"

results = [{
    "Configurazione": TARGET_CONFIG,
    "Test": "Levene",
    "Statistica": stat,
    "p-value": p_value,
    "Alpha": ALPHA,
    "Decisione": decisione,
    "Conclusione": conclusione,
    "Test successivo": test_successivo,
    "N PC1": len(pc_values["PC1"]),
    "N PC2": len(pc_values["PC2"]),
}]

out = pd.DataFrame(results)

print("\n======================================================")
print(f"Test di Levene per configurazione {TARGET_CONFIG}")
print("======================================================\n")

print(out.to_string(index=False))

out.to_csv("test_levene_10000.csv", index=False)

print("\nFile generato:")
print("- test_levene_10000.csv")