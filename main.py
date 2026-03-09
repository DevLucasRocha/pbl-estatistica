# Importa o FastAPI para criar a API
from fastapi import FastAPI

# Permite servir arquivos estáticos (HTML, CSS, JS)
from fastapi.staticfiles import StaticFiles

# Permite retornar arquivos como resposta
from fastapi.responses import FileResponse

# Biblioteca para trabalhar com planilhas e tabelas
import pandas as pd

# Biblioteca para cálculos matemáticos
import numpy as np

# Biblioteca com funções estatísticas
from scipy import stats

# Middleware para permitir acesso de outros domínios (CORS)
from fastapi.middleware.cors import CORSMiddleware

# Biblioteca para manipular pastas e arquivos
import os


# Cria a aplicação FastAPI
app = FastAPI(title="Auditoria Estatística API")


# Configuração de CORS para permitir acesso externo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Permite qualquer origem
    allow_credentials=True,
    allow_methods=["*"],      # Permite todos os métodos
    allow_headers=["*"],      # Permite todos os headers
)


# Garante que a pasta "static" exista
os.makedirs("static", exist_ok=True)


# Permite acessar arquivos da pasta static pela URL /static
app.mount("/static", StaticFiles(directory="static"), name="static")


# Rota principal que retorna o arquivo HTML
@app.get("/")
def read_root():
    return FileResponse("static/index.html")


# Rota que faz a auditoria estatística
@app.get("/api/auditoria")
def get_auditoria():
    try:

        # Lê a planilha Excel
        df = pd.read_excel("ANEXO PBL 1 ESTATÍSTICA 2026_1 (1).xls", skiprows=2)
        
        # Verifica se existe a coluna "Margem (%)"
        if "Margem (%)" in df.columns:
            margem = df["Margem (%)"].dropna().values
        
        # Caso o nome da coluna seja diferente
        elif len(df.columns) > 4:
            margem = df.iloc[:, 4].dropna().values
        
        # Caso não encontre a coluna
        else:
            return {"error": "Coluna de margem não encontrada"}

        # Verifica se existem dados
        if len(margem) == 0:
            return {"error": "Sem dados disponíveis"}

        # -------- Tendência Central --------

        # Média
        media = float(np.mean(margem))
        
        # Usa apenas valores positivos
        margem_pos = margem[margem > 0]

        # Média geométrica
        media_geom = float(stats.gmean(margem_pos)) if len(margem_pos) > 0 else 0.0

        # Média harmônica
        media_harm = float(stats.hmean(margem_pos)) if len(margem_pos) > 0 else 0.0
        
        # Mediana
        mediana = float(np.median(margem))
        
        # Moda
        modo_result = stats.mode(margem, keepdims=True)
        moda = float(modo_result.mode[0]) if len(modo_result.mode) > 0 else 0.0


        # -------- Medidas de Posição --------

        # Quartis
        q1, q2, q3 = np.percentile(margem, [25, 50, 75])
        
        # Decis
        decis = {f"D{i}": float(np.percentile(margem, i * 10)) for i in range(1, 10)}
        
        # Percentis 10% e 90%
        p10, p90 = np.percentile(margem, [10, 90])


        # -------- Medidas de Dispersão --------

        # Desvio absoluto médio
        mad = float(np.mean(np.abs(margem - media)))

        # Variância
        variancia = float(np.var(margem, ddof=1)) if len(margem) > 1 else 0.0

        # Desvio padrão
        desvio_padrao = float(np.std(margem, ddof=1)) if len(margem) > 1 else 0.0

        # Coeficiente de variação
        cv = (desvio_padrao / media * 100) if media != 0 else 0.0


        # -------- Verificação --------

        # Verifica valores acima de 100
        tem_outlier = bool(np.any(margem > 100))

        # Verifica se o CV é alto
        cv_alto = cv > 30.0
        
        # Define o resultado
        if cv_alto or tem_outlier:
            veredito = "Indícios de Fraude"
        else:
            veredito = "Seguro"


        # Retorna os resultados
        return {
            "tendencia_central": {
                "media": float(media),
                "media_geometrica": float(media_geom),
                "media_harmonica": float(media_harm),
                "mediana": float(mediana),
                "moda": float(moda)
            },
            "posicao": {
                "quartis": {
                    "Q1": float(q1),
                    "Q2": float(q2),
                    "Q3": float(q3)
                },
                "decis": decis,
                "percentis": {
                    "p10": float(p10),
                    "p90": float(p90)
                }
            },
            "dispersao": {
                "desvio_absoluto_medio": float(mad),
                "variancia": float(variancia),
                "desvio_padrao": float(desvio_padrao),
                "coeficiente_variacao": float(cv)
            },
            "verificacao": {
                "cv_alto": cv_alto,
                "tem_outlier": tem_outlier,
                "veredito": veredito
            }
        }

    # Caso aconteça algum erro
    except Exception as e:
        return {"error": str(e)}