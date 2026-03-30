"""
database.py — Única fuente de verdad para la conexión a PostgreSQL.
Usa config.py para DATABASE_URL; elimina credenciales hardcodeadas.
"""
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from config import DATABASE_URL


def get_engine() -> Engine:
    """Devuelve un Engine SQLAlchemy con pool de conexiones y pre-ping."""
    return create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )


def cargar_datos_sql(df, tabla: str, if_exists: str = "replace") -> None:
    """Carga un DataFrame en la tabla indicada."""
    engine = get_engine()
    df.to_sql(tabla, engine, if_exists=if_exists, index=False)
    print(f"✅ Datos cargados en la tabla: {tabla}")


def leer_datos_sql(query: str) -> pd.DataFrame:
    """Ejecuta una query SELECT y devuelve un DataFrame."""
    engine = get_engine()
    return pd.read_sql(query, engine)


def check_connection() -> bool:
    """Verifica que la BD esté disponible. Útil para healthcheck."""
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"❌ DB no disponible: {e}")
        return False
