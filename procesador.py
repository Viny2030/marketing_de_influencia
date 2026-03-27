import pandas as pd
import yt_dlp
from database import conectar_db
from datetime import datetime, timedelta

def obtener_datos_youtube(url):
    ydl_opts = {'quiet': True, 'no_warnings': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        fecha_raw = info.get('upload_date')
        return info.get('uploader'), datetime.strptime(fecha_raw, '%Y%m%d')

def calcular_atribucion(fecha_video, archivo_ventas):
    df = pd.read_csv(archivo_ventas)
    df['fecha'] = pd.to_datetime(df['fecha'])
    
    ventana_inicio = fecha_video
    ventana_fin = fecha_video + timedelta(hours=48)
    
    # Filtramos las ventas
    ventas_influencer = df[(df['fecha'] >= ventana_inicio) & (df['fecha'] <= ventana_fin)]
    
    # IMPORTANTE: Convertimos a tipos nativos de Python para que la DB los entienda
    conteo = int(len(ventas_influencer))
    total_dinero = float(ventas_influencer['monto'].sum())
    
    return conteo, total_dinero

def actualizar_db(influencer, url, fecha, ventas, monto):
    conn = conectar_db()
    if conn:
        cur = conn.cursor()
        query = """
            INSERT INTO campanas (influencer, url_video, fecha_pub, ventas_atribuidas, monto_total)
            VALUES (%s, %s, %s, %s, %s)
        """
        cur.execute(query, (influencer, url, fecha, ventas, monto))
        conn.commit()
        cur.close()
        conn.close()
        print(f"📊 Reporte Final Guardado: {influencer} generó {ventas} ventas (${monto})")

if __name__ == "__main__":
    link = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    canal, fecha_pub = obtener_datos_youtube(link)
    
    print(f"🤖 Procesando atribución para {canal}...")
    num_ventas, total_dinero = calcular_atribucion(fecha_pub, 'ventas.csv')
    
    actualizar_db(canal, link, fecha_pub, num_ventas, total_dinero)
