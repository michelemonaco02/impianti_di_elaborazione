import pandas as pd
import numpy as np
import math

Z = 1.96
ERROR_LEVEL = 0.10
df = pd.read_csv("misure_precampione_pc_michele.csv")

results = []

for (pc, config), group in df.groupby(["pc", "configurazione"]):
    mean = group["tempo"].mean()
    std = group["tempo"].std(ddof=1)
    current_n = len(group)

    row = {
        "PC": pc,
        "Configurazione": config,
        "Media": mean,
        "Deviazione standard": std,
        "N precampione": current_n,
    }

    for err in ERROR_LEVEL:
        E = err * mean
        n_required = (Z * std / E) ** 2
        row[f"n errore {int(err * 100)}%"] = math.ceil(n_required)

    results.append(row)

out = pd.DataFrame(results)
print(out)

out.to_csv("dimensione_campionaria.csv", index=False)