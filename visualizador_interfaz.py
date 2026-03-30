# REEMPLAZÁ dashboard.py entero con esto:
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Marketing Dashboard", layout="wide")
st.title("📊 Attribution Dashboard")

from atributtion import calcular_metricas_rentabilidad

PRESUPUESTOS = {'YouTube': 1500, 'Instagram': 800, 'Google Ads': 1200, 'Facebook': 900}

df_raw = pd.read_csv("ventas.csv")
df_raw.columns = [c.lower() for c in df_raw.columns]

# ventas.csv no tiene columna Canal ni ID_Venta → las simulamos
df_raw['canal'] = ['YouTube', 'Instagram', 'Google Ads'][:len(df_raw)]
df_raw['id_venta'] = range(1, len(df_raw)+1)
df_raw.rename(columns={'monto': 'Monto', 'canal': 'Canal', 'id_venta': 'ID_Venta'}, inplace=True)

df = calcular_metricas_rentabilidad(df_raw, PRESUPUESTOS)

st.subheader("💰 Ventas Totales por Canal")
st.bar_chart(df.set_index('Canal')['Ventas_Totales'])

st.subheader("📈 ROI por Canal")
st.bar_chart(df.set_index('Canal')['ROI'])

st.subheader("📋 Tabla de Métricas")
st.dataframe(df)
