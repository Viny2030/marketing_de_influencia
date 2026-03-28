import streamlit as st
import requests
import pandas as pd

# 1. Configuración visual del Dashboard
st.set_page_config(page_title="Marketing Attribution Dashboard", layout="wide")

st.title("📊 Attribution Dashboard")
st.markdown("Análisis de ingresos por campaña en tiempo real")

# 2. Configuración de la conexión
# 'api' es el nombre del servicio en tu docker-compose.yml
URL_API = "http://api:8000/report"

try:
    # Llamada a FastAPI
    response = requests.get(URL_API)
    
    if response.status_code == 200:
        res = response.json()
        
        if res:
            # Transformamos el diccionario {campaña: valor} en un DataFrame
            df = pd.DataFrame(list(res.items()), columns=['Campaña', 'Revenue'])
            
            # 3. Visualización de KPIs
            col1, col2 = st.columns(2)
            total_revenue = df['Revenue'].sum()
            mejor_canal = df.loc[df['Revenue'].idxmax(), 'Campaña']
            
            col1.metric("Revenue Total", f"${total_revenue:,.2f}")
            col2.metric("Canal Ganador", mejor_canal)
            
            st.divider()
            
            # 4. Gráfico de barras
            st.subheader("💰 Revenue por campaña")
            st.bar_chart(df.set_index('Campaña'))
            
            # 5. Tabla de datos detallada
            st.subheader("Detalle de Conversión")
            st.table(df.style.format({'Revenue': '${:,.2f}'}))
            
        else:
            st.info("La API está online, pero no se encontraron datos. Asegúrate de ejecutar el procesador.")
            
    else:
        st.error(f"Error al conectar con la API. Código de estado: {response.status_code}")

except Exception as e:
    st.error("⚠️ Error de conexión: No se pudo alcanzar la API.")
    st.info("Verifica que el contenedor 'marketing_api' esté corriendo y que la URL sea 'http://api:8000/report'")
