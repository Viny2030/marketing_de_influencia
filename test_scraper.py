import os
from processors import obtener_datos_video, guardar_csv
import pandas as pd

# Limpiar CSV viejo antes de cada corrida
if os.path.exists("datos_scraped.csv"):
    os.remove("datos_scraped.csv")

with open('links.txt', 'r') as f:
    links = [line.strip() for line in f if line.strip()]

for link in links:
    try:
        datos = obtener_datos_video(link)
        guardar_csv(datos)
        print(f"OK: {datos['influencer']} | Vistas: {datos['vistas']}")
    except Exception as e:
        print(f"Error: {e}")

print("Guardado en datos_scraped.csv")
