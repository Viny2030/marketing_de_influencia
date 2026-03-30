import yt_dlp
import csv
import os
from datetime import datetime

NICHOS = {
    "moda": ["moda argentina", "fashion haul", "outfit ideas", "tendencias ropa"],
    "gaming": ["gaming latino", "review juegos", "gameplay español", "esports"],
    "fitness": ["rutina gym", "ejercicios en casa", "nutricion deportiva", "crossfit"],
    "tecnologia": ["review celulares", "tecnologia 2025", "unboxing tech", "inteligencia artificial"]
}

ARCHIVO_CANALES = "canales_descubiertos.csv"
ARCHIVO_LINKS = "links.txt"

def buscar_videos_por_keyword(keyword, max_resultados=5):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'playlist_items': f'1:{max_resultados}',
    }
    url_busqueda = f"ytsearch{max_resultados}:{keyword}"
    resultados = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url_busqueda, download=False)
        for entry in info.get('entries', []):
            if entry:
                resultados.append({
                    'url': f"https://www.youtube.com/watch?v={entry.get('id')}",
                    'titulo': entry.get('title'),
                    'canal': entry.get('uploader') or entry.get('channel'),
                    'keyword': keyword,
                    'nicho': '',
                    'descubierto_en': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
    return resultados

def descubrir_todos_los_nichos(max_por_keyword=3):
    todos = []
    links_nuevos = set()

    # Cargar links existentes para no duplicar
    if os.path.exists(ARCHIVO_LINKS):
        with open(ARCHIVO_LINKS, 'r') as f:
            links_nuevos = set(line.strip() for line in f if line.strip())

    existe_csv = os.path.exists(ARCHIVO_CANALES)
    with open(ARCHIVO_CANALES, 'a', newline='', encoding='utf-8') as f:
        fieldnames = ['url','titulo','canal','keyword','nicho','descubierto_en']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not existe_csv:
            writer.writeheader()

        for nicho, keywords in NICHOS.items():
            print(f"\nBuscando nicho: {nicho.upper()}")
            for kw in keywords:
                print(f"  keyword: {kw}")
                try:
                    resultados = buscar_videos_por_keyword(kw, max_por_keyword)
                    for r in resultados:
                        r['nicho'] = nicho
                        if r['url'] not in links_nuevos:
                            writer.writerow(r)
                            links_nuevos.add(r['url'])
                            todos.append(r)
                            print(f"    + {r['canal']}: {r['titulo'][:50]}")
                except Exception as e:
                    print(f"    Error en '{kw}': {e}")

    # Actualizar links.txt con todos los links descubiertos
    with open(ARCHIVO_LINKS, 'w', encoding='utf-8') as f:
        for link in links_nuevos:
            f.write(link + '\n')

    print(f"\nTotal nuevos videos descubiertos: {len(todos)}")
    print(f"links.txt actualizado con {len(links_nuevos)} links en total")
    return todos

if __name__ == "__main__":
    descubrir_todos_los_nichos(max_por_keyword=3)
