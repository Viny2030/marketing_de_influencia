import pandas as pd
import time
from sqlalchemy import create_engine

# Configuración de conexión (Apunta al localhost porque corre desde Windows)
DB_URL = "postgresql://user:password@localhost:5432/marketing_db"

def inyectar_datos():
    try:
        engine = create_engine(DB_URL)
        
        # 1. Leer el CSV real
        df = pd.read_csv('ventas.csv')
        
        # 2. Limpieza rápida
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        df = df.dropna(subset=['Monto', 'Canal'])
        
        # 3. Cargar a la tabla que espera la API
        df.to_sql('ventas_reales', engine, if_exists='replace', index=False)
        
        print(f"✅ ¡Éxito! Se cargaron {len(df)} ventas a la base de datos.")
        
    except Exception as e:
        print(f"❌ Error al inyectar datos: {e}")

if __name__ == "__main__":
    inyectar_datos()
