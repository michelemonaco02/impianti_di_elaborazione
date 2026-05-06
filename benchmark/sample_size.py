import math
import pandas as pd

# ==========================================================
# sample_size.py
# ==========================================================
#
# Scopo:
#   Legge il CSV generato dallo script collect_nbody_measurements.sh
#   e calcola, per ogni configurazione del benchmark, la dimensione
#   campionaria richiesta n per diversi livelli di errore.
#
# Formula:
#   n = (z_alpha/2 * s / E)^2
#
# Dove:
#   z_alpha/2 = 1.96 per intervallo di confidenza al 95%
#   s = deviazione standard campionaria
#   E = errore massimo ammissibile = percentuale * media campionaria
#
# ==========================================================

Z_ALPHA_2 = 1.96

# Errori desiderati rispetto alla media: 10% e 5%
ERROR_LEVELS = [0.10, 0.05]

# Cambia questo nome se il tuo file CSV ha un nome diverso
INPUT_FILE = "misure_PC1.csv"

df = pd.read_csv(INPUT_FILE)

# Controllo colonne attese
required_columns = {"pc", "configurazione", "osservazione", "tempo_s"}

if not required_columns.issubset(df.columns):
    raise ValueError(
        f"Il CSV deve contenere le colonne: {required_columns}. "
        f"Colonne trovate: {set(df.columns)}"
    )

pc_name = df["pc"].iloc[0]

summary_rows = []

for configurazione, group in df.groupby("configurazione"):
    tempi = group["tempo_s"]

    mean = tempi.mean()
    std = tempi.std(ddof=1)
    n_obs = len(tempi)

    row = {
        "Configurazione": configurazione,
        "Osservazioni raccolte": n_obs,
        "Media": mean,
        "Deviazione standard": std,
    }

    for error in ERROR_LEVELS:
        E = error * mean
        n_required = (Z_ALPHA_2 * std / E) ** 2
        row[f"Errore {int(error * 100)}%"] = math.ceil(n_required)

    summary_rows.append(row)

summary = pd.DataFrame(summary_rows)

# Ordina le configurazioni in modo crescente
summary = summary.sort_values(by="Configurazione")

print("\n==========================================")
print(f"Analisi dimensione campionaria - {pc_name}")
print("==========================================\n")

print(summary.to_string(index=False))

# Tabella compatta in stile elaborato
compact = pd.DataFrame({
    "Errore % (Rispetto alla Media)": [
        "Errore 10%",
        "Errore 5%"
    ]
})

for _, row in summary.iterrows():
    config = row["Configurazione"]

    compact[f"{config} iterazioni"] = [
        f"{int(row['Errore 10%'])} prove",
        f"{int(row['Errore 5%'])} prove"
    ]

print("\n==========================================")
print("Tabella finale")
print("==========================================\n")

print(compact.to_string(index=False))

# Salvataggi
summary.to_csv(f"dimensione_campionaria_dettaglio_{pc_name}.csv", index=False)
compact.to_csv(f"dimensione_campionaria_tabella_{pc_name}.csv", index=False)

print("\nFile generati:")
print(f"- dimensione_campionaria_dettaglio_{pc_name}.csv")
print(f"- dimensione_campionaria_tabella_{pc_name}.csv")