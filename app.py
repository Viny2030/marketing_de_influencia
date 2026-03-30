"""
app.py — API REST de atribución de marketing con FastAPI.

Endpoints:
  GET /           → estado general
  GET /health     → healthcheck (DB + versión)
  GET /api/v1/metrics → métricas de ROI por canal
"""
from fastapi import FastAPI, HTTPException
import pandas as pd

from config import PRESUPUESTOS, DATABASE_URL
from database import get_engine, check_connection
from atributtion import calcular_metricas_rentabilidad

app = FastAPI(
    title="InflueMetric Attribution API",
    version="1.0.0",
    description="API de atribución de marketing de influencia",
)


@app.get("/")
def home():
    return {"message": "API de Atribución Operativa", "status": "success", "version": "1.0.0"}


@app.get("/health")
def health():
    """Healthcheck: verifica conexión a la BD y devuelve estado del servicio."""
    db_ok = check_connection()
    return {
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else "unreachable",
        "version": "1.0.0",
    }


@app.get("/api/v1/metrics")
def get_metrics():
    """Consulta ventas_reales en la BD, calcula ROI/CPA y devuelve JSON."""
    if not check_connection():
        raise HTTPException(status_code=503, detail="Base de datos no disponible")

    try:
        engine = get_engine()
        df = pd.read_sql("SELECT * FROM ventas_reales", engine)

        if df.empty:
            raise HTTPException(status_code=404, detail="No hay datos en la base de datos")

        metricas = calcular_metricas_rentabilidad(df, PRESUPUESTOS)
        return metricas.to_dict(orient="records")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
