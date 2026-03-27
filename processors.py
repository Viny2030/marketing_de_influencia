import yt_dlp

def obtener_datos_video(url_video):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url_video, download=False)
        return {
            "titulo": info.get('title'),
            "vistas": info.get('view_count'),
            "fecha_publicacion": info.get('upload_date'),
            "timestamp": info.get('timestamp')  # Esto es oro para tu modelo
        }

# Ejemplo de uso:
# print(obtener_datos_video("https://www.youtube.com/watch?v=XXXXX"))
