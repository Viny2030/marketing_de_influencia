import pandas as pd
from datetime import datetime, timedelta

# 1. Simulación de Datos de Ventas (Esto luego será tu Excel real)
data_ventas = {
    'timestamp': [
        '2024-05-20 19:30', '2024-05-20 20:15', '2024-05-20 20:45', 
        '2024-05-20 21:10', '2024-05-20 21:30', '2024-05-20 23:00'
    ],
    'monto': [100, 150, 200, 180, 250, 120]
}
df_ventas = pd.DataFrame(data_ventas)
df_ventas['timestamp'] = pd.to_datetime(df_ventas['timestamp'])

# 2. Datos del Posteo (Lo que sacarías con yt-dlp)
hora_posteo = pd.to_datetime('2024-05-20 20:00')
ventana_atribucion = 2  # Horas de impacto estimado

def calcular_impacto(hora_post, df, ventana):
    hora_limite = hora_post + timedelta(hours=ventana)
    
    # Filtramos ventas dentro de la ventana de tiempo post-influencer
    ventas_atribuidas = df[(df['timestamp'] >= hora_post) & (df['timestamp'] <= hora_limite)]
    
    total_ventas = ventas_atribuidas['monto'].sum()
    cantidad = len(ventas_atribuidas)
    
    return total_ventas, cantidad

# 3. Ejecución
total, cant = calcular_impacto(hora_posteo, df_ventas, ventana_atribucion)

print(f"--- Análisis de Atribución ---")
print(f"Posteo realizado a las: {hora_posteo}")
print(f"Ventas encontradas en la ventana de {ventana_atribucion}h: {cant}")
print(f"Monto total atribuido al 'ruido': ${total}")
