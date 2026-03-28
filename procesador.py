import pandas as pd
from sqlalchemy import create_engine
import os

# Configuración de conexión
# Usamos localhost porque este script corre desde tu Windows hacia el Docker
DB_URL = "postgresql://user:password@localhost:5432/marketing_db"

def inyectar_datos_csv():
    try:
        # 1. Crear conexión
        engine = create_engine(DB_URL)
        
        # 2. Leer el CSV (asegúrate de que el nombre sea exacto)
        if not os.path.exists('ventas.csv'):
            print("❌ Error: No se encuentra el archivo ventas.csv")
            return

        df = pd.read_csv('ventas.csv')
        
        # 3. Limpieza mínima para que no falle la DB
        # Ajustamos los nombres de columnas si es necesario
        df.columns = [c.lower() for c in df.columns] 
        
        # 4. Cargar a PostgreSQL
        # 'ventas_reales' es la tabla que leerá la API en app.py
        df.to_sql('ventas_reales', engine, if_exists='replace', index=False)
        
        print(f"✅ ¡Éxito! Se han inyectado {len(df)} registros en la base de datos.")

    except Exception as e:
        print(f"❌ Ocurrió un error: {e}")

if __name__ == "__main__":
    inyectar_datos_csv()
