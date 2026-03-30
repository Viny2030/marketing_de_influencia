import pandas as pd
import plotly.express as px
import os

# --- SECCION 1: datos de ventas/ROI ---
PRESUPUESTOS = {'YouTube': 1500, 'Instagram': 800, 'Google Ads': 1200, 'Facebook': 900}

df_raw = pd.read_csv("ventas.csv")
df_raw.columns = [c.strip().lower() for c in df_raw.columns]
df_raw['canal'] = ['YouTube', 'Instagram', 'Google Ads'][:len(df_raw)]
df_raw['id_venta'] = range(1, len(df_raw)+1)

df = df_raw.groupby('canal').agg(
    Ventas_Totales=('monto', 'sum'),
    Cantidad_Ventas=('id_venta', 'count')
).reset_index()
df['Inversion'] = df['canal'].map(PRESUPUESTOS).fillna(0)
df['ROI'] = (df['Ventas_Totales'] - df['Inversion']) / df['Inversion']
df['CPA'] = df['Inversion'] / df['Cantidad_Ventas']

fig1 = px.bar(df, x='canal', y='Ventas_Totales', title='Ventas por Canal', color='canal')
fig2 = px.bar(df, x='canal', y='ROI', title='ROI por Canal', color='canal')
fig3 = px.bar(df, x='canal', y='CPA', title='CPA por Canal', color='canal')

# --- SECCION 2: datos de influencers scrapeados ---
html_influencers = ""
if os.path.exists("datos_scraped.csv"):
    df_inf = pd.read_csv("datos_scraped.csv")
    df_inf['vistas_M'] = (df_inf['vistas'] / 1_000_000).round(1)
    df_inf['likes_M'] = (df_inf['likes'] / 1_000_000).round(1)
    fig4 = px.bar(df_inf, x='influencer', y='vistas_M', title='Vistas por Influencer (millones)', color='influencer')
    fig5 = px.bar(df_inf, x='influencer', y='likes_M', title='Likes por Influencer (millones)', color='influencer')
    html_influencers = fig4.to_html(full_html=False) + fig5.to_html(full_html=False)
    tabla = df_inf[['influencer','titulo','vistas','likes','fecha_pub','scrapeado_en']].to_html(index=False, border=1)
    html_influencers += f"<h2>Detalle de videos</h2>{tabla}"

with open("dashboard.html", "w", encoding="utf-8") as f:
    f.write("<h1>Marketing Dashboard</h1>")
    f.write("<h2>ROI y Ventas por Canal</h2>")
    f.write(fig1.to_html(full_html=False))
    f.write(fig2.to_html(full_html=False))
    f.write(fig3.to_html(full_html=False))
    f.write("<h2>Influencers Monitoreados</h2>")
    f.write(html_influencers)

print("dashboard.html generado")
