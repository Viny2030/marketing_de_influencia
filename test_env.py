import yt_dlp

def probar_extraccion(url):
    ydl_opts = {'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Esto extrae info SIN usar APIs de Google
        info = ydl.extract_info(url, download=False)
        print(f"Título: {info.get('title')}")
        print(f"Vistas actuales: {info.get('view_count')}")
        print(f"Fecha (ID para tu ventana de tiempo): {info.get('upload_date')}")

# Probalo con cualquier video
# probar_extraccion("https://www.youtube.com/watch?v=XXXXX")
