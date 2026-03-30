import pandas as pd
import matplotlib.pyplot as plt
from database import conectar_db

def generar_reporte_visual():
    conn = conectar_db()
    if conn:
        # Traemos los datos directamente de PostgreSQL
        query = "SELECT influencer, SUM(monto_total) as ingresos FROM campanas GROUP BY influencer ORDER BY ingresos DESC;"
        # Usamos pandas para leer la SQL
        df = pd.read_sql(query, conn)
        conn.close()

        if df.empty:
            print("⚠️ No hay datos en la base de datos para graficar.")
            return

        # Creamos el gráfico
        plt.figure(figsize=(10, 6))
        plt.bar(df['influencer'], df['ingresos'], color='#2ecc71')
        plt.xlabel('Influencers', fontsize=12)
        plt.ylabel('Ingresos Totales ($)', fontsize=12)
        plt.title('Ranking de Retorno de Inversión (ROI)', fontsize=14)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Guardar la imagen
        plt.savefig('reporte_marketing.png')
        print("📊 ¡Éxito! Reporte visual guardado como 'reporte_marketing.png'")

if __name__ == "__main__":
    generar_reporte_visual()
