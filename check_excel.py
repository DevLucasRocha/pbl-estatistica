import pandas as pd

df = pd.read_excel("ANEXO PBL 1 ESTATÍSTICA 2026_1 (1).xls", skiprows=2)
print(df.columns.tolist())
print(df.head())