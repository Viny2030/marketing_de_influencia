import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Marketing Dashboard", layout="wide")

st.title("📊 Atribución de Ventas e Inversión")

# Endpoint de tu FastAPI
URL_API = "http://api:8000/api/v1/metrics"

try:
    response = requests.get(URL_API)
    
    if response.status_code == 200:
        raw_data = response.json()
        df = pd.DataFrame(raw_data)

        # Métricas destacadas (KPIs)
        c1, c2, c3 = st.columns(3)
        total_ventas = df['Ventas_Totales'].sum()
        c1.metric("Ingresos Totales", f"${total_ventas:,.2f}")
        c2.metric("Mejor ROI", f"{df['ROI'].max():.2%}")
        c3.metric("Total Conversiones", int(df['Cantidad_Ventas'].sum()))

        st.divider()

        # Gráficos
        col_left, col_right = st.columns(2)
        with col_left:
            st.subheader("ROI por Canal")
            st.bar_chart(df.set_index('Canal')['ROI'])
        
        with col_right:
            st.subheader("CPA por Canal")
            st.bar_chart(df.set_index('Canal')['CPA'])

        st.subheader("Tabla de Datos Crudos de la API")
        st.dataframe(df.style.format({'ROI': '{:.2%}', 'Ventas_Totales': '${:,.2f}', 'CPA': '${:,.2f}'}))

    else:
        st.error(f"Error en la API: {response.status_code}")

except Exception as e:
    st.warning("⚠️ El servidor FastAPI (app.py) no está respondiendo. Ejecútalo con: uvicorn app:app --reload")
