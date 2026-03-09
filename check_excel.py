# Importa a biblioteca pandas para trabalhar com planilhas
import pandas as pd

# Lê o arquivo Excel ignorando as duas primeiras linhas
df = pd.read_excel("ANEXO PBL 1 ESTATÍSTICA 2026_1 (1).xls", skiprows=2)

# Mostra no terminal o nome de todas as colunas da planilha
print(df.columns.tolist())

# Mostra as primeiras linhas da planilha para visualizar os dados
print(df.head())