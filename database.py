"""
database.py — Única fuente de verdad para la conexión a PostgreSQL.

Usa config.py para DATABASE_URL.
El Engine es un singleton a nivel de módulo: se crea una sola vez y el pool
de conexiones funciona correctamente en todas las llamadas subsiguientes.
"""
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from config import DATABASE_URL

# ── Singleton del engine ───────────────────────────────────────────────────────
# Se instancia una sola vez al importar el módulo. Así el pool_size=5 tiene
# efecto real: no se crean engines nuevos en cada llamada a get_engine().
_engine: Engine | None = None


def get_engine() -> Engine:
    """Devuelve el Engine singleton. Lo crea la primera vez que se llama."""
    global _engine
    if _engine is None:
        _engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,   # descarta conexiones muertas automáticamente
            pool_size=5,
            max_overflow=10,
        )
    return _engine


def cargar_datos_sql(df: pd.DataFrame, tabla: str, if_exists: str = "replace") -> None:
    """Carga un DataFrame en la tabla indicada."""
    df.to_sql(tabla, get_engine(), if_exists=if_exists, index=False)
    print(f"✅ Datos cargados en la tabla: {tabla}")


def leer_datos_sql(query: str) -> pd.DataFrame:
    """Ejecuta una query SELECT y devuelve un DataFrame."""
    return pd.read_sql(query, get_engine())


def check_connection() -> bool:
    """Verifica que la BD esté disponible. Útil para healthcheck."""
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"❌ DB no disponible: {e}")
        return False
