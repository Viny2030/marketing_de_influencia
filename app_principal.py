from fastapi import FastAPI, HTTPException
import pandas as pd
from database import get_engine
from atributtion import calcular_metricas_rentabilidad

app = FastAPI(title="Marketing Attribution API")

# Diccionario de presupuestos (Nivel Pro: esto podría ir en una tabla de la DB)
PRESUPUESTOS = {
    'YouTube': 1500, 'Instagram': 800, 'Google Ads': 1200, 'Facebook': 900
}

@app.get("/")
def home():
    return {"message": "API de Atribución Operativa", "status": "success"}

@app.get("/api/v1/metrics")
def get_metrics():
    """Consulta la DB, procesa el ROI y devuelve JSON"""
    try:
        engine = get_engine()
        # Leemos de la tabla que creó el procesador
        df = pd.read_sql("SELECT * FROM ventas_reales", engine)
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No hay datos en la base de datos")

        # Calculamos métricas usando tu lógica de atributtion.py
        data_metrics = calcular_metricas_rentabilidad(df, PRESUPUESTOS)
        
        # Convertimos a JSON orientado a registros
        return data_metrics.to_dict(orient="records")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
