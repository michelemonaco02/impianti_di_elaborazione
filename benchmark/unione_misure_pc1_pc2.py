import pandas as pd

df1 = pd.read_csv("misure_PC1.csv")
df2 = pd.read_csv("misure_PC2.csv")

df = pd.concat([df1, df2], ignore_index=True)

df.to_csv("misure_PC1_PC2.csv", index=False)