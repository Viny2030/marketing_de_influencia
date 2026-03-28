import pandas as pd
from sqlalchemy import create_engine

# Configuración para el contenedor de Docker (PostgreSQL)
DB_URL = "postgresql://user:password@localhost:5432/marketing_db"

def get_engine():
    return create_engine(DB_URL)

def cargar_datos_sql(df, tabla):
    engine = get_engine()
    df.to_sql(tabla, engine, if_exists='replace', index=False)
    print(f"✅ Datos cargados en la tabla: {tabla}")

def leer_datos_sql(query):
    engine = get_engine()
    return pd.read_sql(query, engine)
