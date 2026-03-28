import streamlit as st
import requests
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Marketing Attribution Pro", layout="wide")

st.title("📊 Atribución de Ventas e Inversión")
st.markdown("Visualización de datos en tiempo real desde la API")

# IMPORTANTE: Dentro de Docker, usamos el nombre del servicio 'api'
# Si pruebas fuera de Docker, cambia 'api' por 'localhost'
URL_API = "http://api:8000/report"

try:
    response = requests.get(URL_API)
    
    if response.status_code == 200:
        data = response.json()
        
        # Convertimos el diccionario de la API a DataFrame
        # La API devuelve: {"campaña": valor, ...}
        df = pd.DataFrame(list(data.items()), columns=['Campaña', 'Revenue'])
        
        # Si el DF no está vacío, calculamos métricas
        if not df.empty:
            # Métricas destacadas (KPIs)
            c1, c2, c3 = st.columns(3)
            total_revenue = df['Revenue'].sum()
            mejor_campaña = df.loc[df['Revenue'].idxmax(), 'Campaña']
            
            c1.metric("Revenue Total", f"${total_revenue:,.2f}")
            c2.metric("Mejor Campaña", mejor_campaña)
            c3.metric("Campañas Activas", len(df))

            st.divider()

            # Gráficos
            col_left, col_right = st.columns(2)
            
            with col_left:
                st.subheader("💰 Revenue por Campaña")
                st.bar_chart(df.set_index('Campaña'))
            
            with col_right:
                st.subheader("📈 Distribución de Ingresos")
                # Gráfico circular simple usando st.write con los datos
                st.write(df)

            st.divider()
            st.subheader("📋 Datos Detallados (API Response)")
            st.dataframe(df.style.format({'Revenue': '${:,.2f}'}))
        else:
            st.info("La API respondió correctamente, pero no hay datos de conversiones aún.")

    else:
        st.error(f"❌ Error en la API: Código {response.status_code}")
        st.info("Asegúrate de haber inyectado datos con el procesador.")

except Exception as e:
    st.error("⚠️ No se pudo conectar con el servidor FastAPI.")
    st.info(f"Detalle técnico: {e}")
    st.markdown("""
    **Pasos de solución:**
    1. Revisa que el contenedor `marketing_api` esté corriendo (`docker ps`).
    2. Verifica que la URL en el código sea `http://api:8000/report`.
    """)
