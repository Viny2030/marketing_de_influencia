import pandas as pd
import hashlib
import numpy as np
from datetime import timedelta

def anonimizar_email(email):
    """Aplica SHA-256 para cumplir con GDPR/LGPD[cite: 24, 662]."""
    if pd.isna(email): return None
    return hashlib.sha256(email.strip().lower().encode()).hexdigest()

def calcular_atribucion_probabilistica(df_ventas, df_vistas, ventana_horas=24):
    """
    Calcula la probabilidad de que una venta haya sido influenciada
    por un video basándose en la cercanía temporal[cite: 1027, 1033].
    """
    atribuciones = []
    
    for _, venta in df_ventas.iterrows():
        # Buscamos impactos en la ventana de tiempo previa a la venta [cite: 67, 122]
        inicio_ventana = venta['timestamp'] - timedelta(hours=ventana_horas)
        impactos = df_vistas[(df_vistas['timestamp'] >= inicio_ventana) & 
                             (df_vistas['timestamp'] <= venta['timestamp'])]
        
        if not impactos.empty:
            # Cuanto más cerca está el posteo de la venta, mayor es el score [cite: 1027]
            impactos = impactos.copy()
            impactos['diff_horas'] = (venta['timestamp'] - impactos['timestamp']).dt.total_seconds() / 3600
            impactos['score_influencia'] = np.exp(-impactos['diff_horas'] / 12) # Decaimiento exponencial [cite: 1027]
            
            mejor_impacto = impactos.loc[impactos['score_influencia'].idxmax()]
            atribuciones.append({
                'venta_id': venta['id'],
                'canal': mejor_impacto['canal'],
                'score': mejor_impacto['score_influencia'],
                'tipo': 'Probabilística' if pd.isna(venta['click_id']) else 'Directa' [cite: 986, 988]
            })
            
    return pd.DataFrame(atribuciones)

# --- FLUJO PRINCIPAL ---
# 1. Carga de datos (Simulando tu estructura de datos_scraped.csv) [cite: 1920]
try:
    ventas = pd.read_csv('ventas.csv', parse_dates=['timestamp'])
    vistas = pd.read_csv('datos_scraped.csv', parse_dates=['timestamp'])
    
    # 2. Anonimización inmediata [cite: 434, 1331]
    ventas['user_id_hashed'] = ventas['email'].apply(anonimizar_email)
    
    # 3. Motor de Atribución [cite: 1037, 1083]
    resultado = calcular_atribucion_probabilistica(ventas, vistas)
    
    # 4. Cálculo de ROI Real [cite: 1385, 1419]
    resumen = resultado.groupby('canal').agg({
        'venta_id': 'count',
        'score': 'mean'
    }).rename(columns={'venta_id': 'Ventas_Atribuidas', 'score': 'Confianza_Media'})
    
    print("### INFLUEMETRIC: REPORTE DE ATRIBUCIÓN ###")
    print(resumen)
    
    # Guardar para el Dashboard [cite: 214]
    resumen.to_csv('reporte_roi_final.csv')
    print("\n[OK] Reporte generado para Railway/Dashboard.")

except FileNotFoundError:
    print("[Error] Asegúrate de tener 'ventas.csv' y 'datos_scraped.csv' en la carpeta.")
