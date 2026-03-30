"""
dashboard.py — Dashboard Streamlit de atribución de marketing.

Lee los datos desde:
  1. PostgreSQL (producción, si DATABASE_URL está configurado)
  2. CSV local ventas.csv (fallback para desarrollo)
"""
import streamlit as st
import pandas as pd

from config import PRESUPUESTOS
from atributtion import calcular_metricas_rentabilidad

st.set_page_config(page_title="InflueMetric Dashboard", layout="wide")
st.title("📊 InflueMetric — Attribution Dashboard")


# ── Carga de datos ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)  # cachea 5 minutos para no saturar la BD
def cargar_datos() -> tuple[pd.DataFrame, str]:
    """Intenta cargar desde BD; cae en CSV si no hay conexión."""
    try:
        from database import get_engine, check_connection
        if check_connection():
            engine = get_engine()
            df = pd.read_sql("SELECT * FROM ventas_reales", engine)
            return df, "PostgreSQL"
    except Exception:
        pass

    # Fallback: CSV local
    try:
        df = pd.read_csv("ventas.csv")
        df.columns = [c.strip() for c in df.columns]
        # Normalizar nombres de columna al esquema esperado
        rename_map = {}
        for col in df.columns:
            low = col.lower()
            if low == "monto":
                rename_map[col] = "Monto"
            elif low == "canal":
                rename_map[col] = "Canal"
            elif low in ("id_venta", "id"):
                rename_map[col] = "ID_Venta"
        df.rename(columns=rename_map, inplace=True)

        # Si no hay columna Canal, avisar
        if "Canal" not in df.columns:
            st.warning("⚠️ ventas.csv no tiene columna 'Canal'. Los datos pueden ser incompletos.")
        if "ID_Venta" not in df.columns:
            df["ID_Venta"] = range(1, len(df) + 1)

        return df, "CSV local"
    except FileNotFoundError:
        return pd.DataFrame(), "Sin fuente"


df_raw, fuente = cargar_datos()

# ── Estado de la fuente ────────────────────────────────────────────────────────

col_estado, col_refresh = st.columns([4, 1])
with col_estado:
    icon = "🟢" if fuente == "PostgreSQL" else ("🟡" if fuente == "CSV local" else "🔴")
    st.caption(f"{icon} Fuente de datos: **{fuente}**")
with col_refresh:
    if st.button("🔄 Actualizar"):
        st.cache_data.clear()
        st.rerun()

if df_raw.empty:
    st.error("❌ No se pudieron cargar datos. Verificá la conexión a la BD o el archivo ventas.csv.")
    st.stop()

# ── Métricas ───────────────────────────────────────────────────────────────────

df = calcular_metricas_rentabilidad(df_raw, PRESUPUESTOS)

# KPIs en la parte superior
total_ventas = df["Ventas_Totales"].sum()
roi_promedio = df["ROI"].mean()
mejor_canal = df.loc[df["ROI"].idxmax(), "Canal"] if not df.empty else "N/A"

k1, k2, k3 = st.columns(3)
k1.metric("💰 Ventas Totales", f"${total_ventas:,.0f}")
k2.metric("📈 ROI Promedio", f"{roi_promedio:.1%}")
k3.metric("🏆 Mejor Canal", mejor_canal)

st.divider()

# ── Gráficos ───────────────────────────────────────────────────────────────────

col1, col2 = st.columns(2)

with col1:
    st.subheader("💰 Ventas Totales por Canal")
    st.bar_chart(df.set_index("Canal")["Ventas_Totales"])

with col2:
    st.subheader("📈 ROI por Canal")
    st.bar_chart(df.set_index("Canal")["ROI"])

st.subheader("📋 Tabla de Métricas Completa")
st.dataframe(
    df.style.format({
        "Ventas_Totales": "${:,.0f}",
        "Inversion": "${:,.0f}",
        "ROI": "{:.1%}",
        "CPA": "${:,.2f}",
    }),
    use_container_width=True,
)

# ── Descarga ───────────────────────────────────────────────────────────────────

csv_export = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Descargar métricas CSV",
    data=csv_export,
    file_name="metricas_roi.csv",
    mime="text/csv",
)
