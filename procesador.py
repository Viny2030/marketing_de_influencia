import pandas as pd
import yt_dlp
from datetime import datetime, timedelta
import os

class ProcesadorAtribucion:
    def __init__(self, ventana_horas=2):
        self.ventana_horas = ventana_horas
        self.ydl_opts = {'quiet': True, 'no_warnings': True}

    def obtener_hitos_video(self, url_video):
        """Extrae la fecha y hora de publicación real sin APIs de Google."""
        print(f"📡 Conectando con YouTube para analizar: {url_video}")
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url_video, download=False)
                # El timestamp de YouTube es Unix (segundos)
                fecha_pub = datetime.fromtimestamp(info.get('timestamp'))
                return {
                    'titulo': info.get('title'),
                    'fecha_pub': fecha_pub,
                    'vistas': info.get('view_count'),
                    'canal': info.get('uploader')
                }
        except Exception as e:
            print(f"❌ Error al extraer datos de YouTube: {e}")
            return None

    def ejecutar_analisis(self, archivo_excel, url_video):
        # 1. Obtener el 'Trigger' (Influencer)
        datos_video = self.obtener_hitos_video(url_video)
        if not datos_video:
            return

        hora_inicio = datos_video['fecha_pub']
        hora_fin = hora_inicio + timedelta(hours=self.ventana_horas)

        print(f"⏰ Ventana de Atribución: {hora_inicio.strftime('%H:%M')} a {hora_fin.strftime('%H:%M')}")

        # 2. Cargar y procesar ventas
        try:
            # Leemos el Excel (Asegurate que las columnas se llamen 'fecha' y 'monto')
            df = pd.read_excel(archivo_excel)
            df['fecha'] = pd.to_datetime(df['fecha'])
            
            # Filtro de Atribución Directa
            ventas_atribuidas = df[(df['fecha'] >= hora_inicio) & (df['fecha'] <= hora_fin)]
            
            # 3. Resultados
            total_dinero = ventas_atribuidas['monto'].sum()
            cantidad_ventas = len(ventas_atribuidas)
            
            print("\n" + "="*40)
            print(f"📊 REPORTE DE IMPACTO: {datos_video['titulo']}")
            print(f"👤 Influencer: {datos_video['canal']}")
            print(f"📦 Ventas en la ventana: {cantidad_ventas}")
            print(f"💰 ROI Estimado (Monto Atribuido): ${total_dinero:,.2f}")
            print("="*40)

            return ventas_atribuidas

        except FileNotFoundError:
            print(f"❌ No se encontró el archivo: {archivo_excel}")
        except Exception as e:
            print(f"❌ Error procesando el Excel: {e}")

# --- BLOQUE DE PRUEBA DE CAMPO ---
if __name__ == "__main__":
    procesador = ProcesadorAtribucion(ventana_horas=2)
    
    # URL de un video para testear (puedes poner la de tu influencer)
    url_test = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    archivo_test = "ventas_test.xlsx"

    # AUTO-GENERAR EXCEL DE PRUEBA SI NO EXISTE
    if not os.path.exists(archivo_test):
        print("💡 Creando Excel de prueba automático...")
        # Generamos una fecha dinámica basada en el video para que el test SIEMPRE dé positivo
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url_test, download=False)
            t_base = datetime.fromtimestamp(info.get('timestamp'))
        
        df_demo = pd.DataFrame({
            'fecha': [t_base + timedelta(minutes=15), t_base + timedelta(hours=5)],
            'monto': [5500.50, 1200.00]
        })
        df_demo.to_excel(archivo_test, index=False)

    # CORRER MOTOR
    procesador.ejecutar_analisis(archivo_test, url_test)
