import pandas as pd
from database import cargar_datos_sql

def procesar_y_subir_ventas(path_csv):
    try:
        df = pd.read_csv(path_csv)
        
        # Limpieza básica: quitar nulos en Monto o Canal
        df = df.dropna(subset=['Monto', 'Canal'])
        
        # Convertir fecha a datetime
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        
        # Subir a Postgres
        cargar_datos_sql(df, 'ventas_reales')
        return df
    except Exception as e:
        print(f"❌ Error al procesar CSV: {e}")
        return None

if __name__ == "__main__":
    procesar_y_subir_ventas('ventas.csv')
