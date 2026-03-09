from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import pandas as pd
import numpy as np
from scipy import stats
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Auditoria Estatística API")

# Allow CORS for development if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure static folder exists
os.makedirs("static", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

@app.get("/api/auditoria")
def get_auditoria():
    try:
        # Load data
        df = pd.read_excel("ANEXO PBL 1 ESTATÍSTICA 2026_1 (1).xls", skiprows=2)
        
        if "Margem (%)" in df.columns:
            margem = df["Margem (%)"].dropna().values
        elif len(df.columns) > 4:
            # Fallback if the column is slightly renamed in pandas
            margem = df.iloc[:, 4].dropna().values
        else:
            return {"error": "Coluna de margem não encontrada"}

        # If empty
        if len(margem) == 0:
            return {"error": "Sem dados disponíveis"}

        # 1. Tendência Central
        media = float(np.mean(margem))
        
        # Média geométrica and harmônica require positive values strictly
        margem_pos = margem[margem > 0]
        media_geom = float(stats.gmean(margem_pos)) if len(margem_pos) > 0 else 0.0
        media_harm = float(stats.hmean(margem_pos)) if len(margem_pos) > 0 else 0.0
        
        mediana = float(np.median(margem))
        
        modo_result = stats.mode(margem, keepdims=True)
        moda = float(modo_result.mode[0]) if len(modo_result.mode) > 0 else 0.0

        # 2. Posição
        q1, q2, q3 = np.percentile(margem, [25, 50, 75])
        
        decis = {f"D{i}": float(np.percentile(margem, i * 10)) for i in range(1, 10)}
        
        p10, p90 = np.percentile(margem, [10, 90])

        # 3. Dispersão
        mad = float(np.mean(np.abs(margem - media)))
        variancia = float(np.var(margem, ddof=1)) if len(margem) > 1 else 0.0
        desvio_padrao = float(np.std(margem, ddof=1)) if len(margem) > 1 else 0.0
        cv = (desvio_padrao / media * 100) if media != 0 else 0.0

        # 4. Veredito
        tem_outlier = bool(np.any(margem > 100))
        cv_alto = cv > 30.0
        
        if cv_alto or tem_outlier:
            veredito = "Indícios de Fraude"
        else:
            veredito = "Seguro"

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
    except Exception as e:
        return {"error": str(e)}
