"""
Pipeline completo: descubre canales, scrapea datos, genera dashboard.
Correr manualmente: python pipeline.py
Correr automatico: Task Scheduler de Windows apunta a este archivo.
"""
import yt_dlp
import csv
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ── CONFIGURACION ──────────────────────────────────────────────
NICHOS = {
    "gaming":     ["gaming latino", "gameplay español", "review juegos", "esports latam"],
    "moda":       ["moda argentina", "outfit ideas español", "fashion haul latam"],
    "fitness":    ["rutina gym español", "ejercicios en casa", "nutricion deportiva"],
    "tecnologia": ["review celulares 2025", "tecnologia español", "unboxing tech latam"],
}
MAX_POR_KEYWORD = 3
ARCHIVO_CSV     = "datos_scraped.csv"
ARCHIVO_HTML    = "dashboard.html"
LOG_FILE        = "pipeline.log"

# ── LOGGING ────────────────────────────────────────────────────
def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{ts}] {msg}"
    print(linea)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(linea + "\n")

# ── SCRAPING ───────────────────────────────────────────────────
def buscar_videos(keyword, n=3):
    ydl_opts = {"quiet": True, "no_warnings": True, "extract_flat": True}
    url = f"ytsearch{n}:{keyword}"
    resultados = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            for e in info.get("entries", []):
                if e and e.get("id"):
                    resultados.append(f"https://www.youtube.com/watch?v={e['id']}")
    except Exception as ex:
        log(f"  Error buscando '{keyword}': {ex}")
    return resultados

def obtener_metricas(url):
    ydl_opts = {"quiet": True, "no_warnings": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            "url":          url,
            "canal":        info.get("uploader", ""),
            "canal_id":     info.get("channel_id", ""),
            "titulo":       info.get("title", "")[:80],
            "vistas":       info.get("view_count", 0) or 0,
            "likes":        info.get("like_count", 0) or 0,
            "comentarios":  info.get("comment_count", 0) or 0,
            "duracion_seg": info.get("duration", 0) or 0,
            "fecha_pub":    info.get("upload_date", ""),
            "scrapeado_en": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

def paso_scraping():
    log("=== INICIO SCRAPING ===")
    # Cargar URLs ya procesadas para no duplicar
    procesadas = set()
    if os.path.exists(ARCHIVO_CSV):
        df_prev = pd.read_csv(ARCHIVO_CSV, encoding="utf-8")
        procesadas = set(df_prev["url"].tolist())

    nuevos = []
    for nicho, keywords in NICHOS.items():
        log(f"Nicho: {nicho.upper()}")
        for kw in keywords:
            urls = buscar_videos(kw, MAX_POR_KEYWORD)
            for url in urls:
                if url in procesadas:
                    continue
                try:
                    datos = obtener_metricas(url)
                    datos["nicho"] = nicho
                    datos["keyword"] = kw
                    nuevos.append(datos)
                    procesadas.add(url)
                    log(f"  + {datos['canal']}: {datos['titulo'][:45]} | {datos['vistas']:,} vistas")
                except Exception as ex:
                    log(f"  Error en {url}: {ex}")

    if nuevos:
        df_nuevo = pd.DataFrame(nuevos)
        escribir_header = not os.path.exists(ARCHIVO_CSV)
        df_nuevo.to_csv(ARCHIVO_CSV, mode="a", header=escribir_header,
                        index=False, encoding="utf-8")
        log(f"Nuevos registros guardados: {len(nuevos)}")
    else:
        log("Sin registros nuevos en este ciclo.")
    log("=== FIN SCRAPING ===\n")

# ── DASHBOARD ──────────────────────────────────────────────────
def calcular_engagement(row):
    if row["vistas"] > 0:
        return round((row["likes"] + row["comentarios"]) / row["vistas"] * 100, 2)
    return 0

def paso_dashboard():
    log("=== GENERANDO DASHBOARD ===")
    if not os.path.exists(ARCHIVO_CSV):
        log("Sin datos todavia. Corre el scraping primero.")
        return

    df = pd.read_csv(ARCHIVO_CSV, encoding="utf-8", on_bad_lines="skip")
    df = df.dropna(subset=["canal", "vistas"])
    df["vistas"] = df["vistas"].astype(int)
    df["likes"]  = df["likes"].fillna(0).astype(int)
    df["comentarios"] = df["comentarios"].fillna(0).astype(int)
    df["engagement"] = df.apply(calcular_engagement, axis=1)
    df["vistas_M"] = (df["vistas"] / 1_000_000).round(2)

    # Metricas por nicho
    por_nicho = df.groupby("nicho").agg(
        Canales=("canal", "nunique"),
        Vistas_Total=("vistas", "sum"),
        Vistas_Prom=("vistas", "mean"),
        Likes_Prom=("likes", "mean"),
        Engagement_Prom=("engagement", "mean"),
    ).reset_index()
    por_nicho["Vistas_Total_M"] = (por_nicho["Vistas_Total"] / 1e6).round(1)

    # Top canales
    top_canales = df.groupby("canal").agg(
        Videos=("url", "count"),
        Vistas_Total=("vistas", "sum"),
        Engagement_Prom=("engagement", "mean"),
        Nicho=("nicho", "first"),
    ).reset_index().sort_values("Vistas_Total", ascending=False).head(15)

    # Graficos
    fig1 = px.bar(por_nicho, x="nicho", y="Vistas_Total_M",
                  color="nicho", title="Vistas Totales por Nicho (M)",
                  color_discrete_sequence=["#00e5ff","#ff3d6b","#7cff6b","#ffaa00"])

    fig2 = px.bar(por_nicho, x="nicho", y="Engagement_Prom",
                  color="nicho", title="Engagement Rate Promedio por Nicho (%)",
                  color_discrete_sequence=["#00e5ff","#ff3d6b","#7cff6b","#ffaa00"])

    fig3 = px.bar(top_canales.head(10), x="canal", y="Vistas_Total",
                  color="Nicho", title="Top 10 Canales por Vistas Totales")

    fig4 = px.scatter(df[df["vistas"] < df["vistas"].quantile(0.95)],
                      x="vistas", y="engagement", color="nicho",
                      hover_data=["canal", "titulo"],
                      title="Vistas vs Engagement por Video")

    # Tabla top canales
    tabla_html = top_canales[["canal","Nicho","Videos","Vistas_Total","Engagement_Prom"]].copy()
    tabla_html["Vistas_Total"] = tabla_html["Vistas_Total"].apply(lambda x: f"{x:,.0f}")
    tabla_html["Engagement_Prom"] = tabla_html["Engagement_Prom"].apply(lambda x: f"{x:.2f}%")
    tabla_html.columns = ["Canal","Nicho","Videos","Vistas Totales","Engagement Prom"]

    # KPIs
    total_canales = df["canal"].nunique()
    total_vistas  = df["vistas"].sum()
    total_videos  = len(df)
    eng_global    = df["engagement"].mean()
    ultima_act    = df["scrapeado_en"].max()

    # HTML final
    dark = "background:#080b0f;color:#e8edf2;font-family:'DM Sans',sans-serif;"
    card = "background:#0f1419;border:1px solid #1e2a35;padding:1.5rem;flex:1;min-width:150px;"
    kpi_v = "font-size:2rem;font-weight:800;font-family:'Syne',sans-serif;margin-bottom:0.25rem;"
    kpi_l = "font-size:0.65rem;color:#5a7080;letter-spacing:0.1em;text-transform:uppercase;font-family:'DM Mono',monospace;"

    with open(ARCHIVO_HTML, "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html><html><head><meta charset='UTF-8'>
<link href='https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Mono&family=DM+Sans:wght@300;400&display=swap' rel='stylesheet'>
<title>InfluMetric Dashboard</title>
<style>
  body {{ {dark} margin:0; padding:2rem; }}
  h1 {{ font-family:'Syne',sans-serif; font-weight:800; font-size:2rem; letter-spacing:-0.03em; margin-bottom:0.25rem; }}
  h1 span {{ color:#00e5ff; }}
  .meta {{ font-family:'DM Mono',monospace; font-size:0.7rem; color:#5a7080; margin-bottom:2rem; }}
  .kpis {{ display:flex; gap:1px; background:#1e2a35; border:1px solid #1e2a35; margin-bottom:2rem; flex-wrap:wrap; }}
  .kpi {{ {card} }}
  .kv {{ {kpi_v} }}
  .kl {{ {kpi_l} }}
  .chart-row {{ display:grid; grid-template-columns:1fr 1fr; gap:1.5rem; margin-bottom:1.5rem; }}
  .chart-box {{ background:#0f1419; border:1px solid #1e2a35; padding:1.5rem; }}
  table {{ width:100%; border-collapse:collapse; font-size:0.82rem; }}
  th {{ font-family:'DM Mono',monospace; font-size:0.62rem; color:#5a7080; letter-spacing:0.08em; text-transform:uppercase; padding:0 1rem 0.75rem 0; text-align:left; border-bottom:1px solid #1e2a35; font-weight:400; }}
  td {{ padding:0.75rem 1rem 0.75rem 0; color:#8fa3b0; border-bottom:1px solid rgba(30,42,53,0.5); }}
  td:first-child {{ color:#e8edf2; font-weight:500; }}
  @media(max-width:700px) {{ .chart-row {{ grid-template-columns:1fr; }} }}
</style></head><body>
<h1>Influ<span>Metric</span> — Dashboard en Vivo</h1>
<div class='meta'>Ultima actualizacion: {ultima_act} &nbsp;|&nbsp; Datos reales via yt-dlp</div>
<div class='kpis'>
  <div class='kpi'><div class='kl'>Canales monitoreados</div><div class='kv' style='color:#00e5ff'>{total_canales}</div></div>
  <div class='kpi'><div class='kl'>Videos scrapeados</div><div class='kv'>{total_videos:,}</div></div>
  <div class='kpi'><div class='kl'>Vistas totales</div><div class='kv' style='color:#ff3d6b'>{total_vistas/1e6:.1f}M</div></div>
  <div class='kpi'><div class='kl'>Engagement global</div><div class='kv' style='color:#7cff6b'>{eng_global:.2f}%</div></div>
  <div class='kpi'><div class='kl'>Nichos activos</div><div class='kv' style='color:#ffaa00'>{df["nicho"].nunique()}</div></div>
</div>
<div class='chart-row'>
  <div class='chart-box'>{fig1.to_html(full_html=False, include_plotlyjs='cdn')}</div>
  <div class='chart-box'>{fig2.to_html(full_html=False, include_plotlyjs=False)}</div>
</div>
<div class='chart-row'>
  <div class='chart-box'>{fig3.to_html(full_html=False, include_plotlyjs=False)}</div>
  <div class='chart-box'>{fig4.to_html(full_html=False, include_plotlyjs=False)}</div>
</div>
<div class='chart-box' style='margin-bottom:1.5rem'>
  <div style='font-family:DM Mono,monospace;font-size:0.62rem;color:#5a7080;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:1rem'>Top Canales por Vistas</div>
  {tabla_html.to_html(index=False, border=0, classes='', justify='left')}
</div>
</body></html>""")

    log(f"Dashboard generado: {ARCHIVO_HTML}")
    log("=== FIN DASHBOARD ===\n")

# ── MAIN ───────────────────────────────────────────────────────
if __name__ == "__main__":
    paso_scraping()
    paso_dashboard()
    print("\nListo. Abri dashboard.html en tu browser.")
