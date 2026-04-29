"""
config.py — Configuración centralizada via variables de entorno.

Carga automáticamente el archivo .env si existe.
Todos los módulos del proyecto deben importar sus constantes desde aquí.
"""
import os
from dotenv import load_dotenv

# Carga .env antes de leer cualquier os.getenv()
load_dotenv()

# ── Base de datos ──────────────────────────────────────────────────────────────
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/marketing_db",
)

# ── Presupuestos por canal (en USD) ───────────────────────────────────────────
# Puede sobreescribirse a futuro leyendo de la BD; por ahora es config estática.
PRESUPUESTOS: dict[str, float] = {
    "YouTube":    float(os.getenv("BUDGET_YOUTUBE",    "1500")),
    "Instagram":  float(os.getenv("BUDGET_INSTAGRAM",  "800")),
    "Google Ads": float(os.getenv("BUDGET_GOOGLE_ADS", "1200")),
    "Facebook":   float(os.getenv("BUDGET_FACEBOOK",   "900")),
}

# ── Nichos y keywords de búsqueda ─────────────────────────────────────────────
# Fuente única de verdad: pipeline.py y scraper_discovery.py importan desde aquí.
NICHOS: dict[str, list[str]] = {
    "gaming":     ["gaming latino", "gameplay español", "review juegos", "esports latam"],
    "moda":       ["moda argentina", "outfit ideas español", "fashion haul latam"],
    "fitness":    ["rutina gym español", "ejercicios en casa", "nutricion deportiva"],
    "tecnologia": ["review celulares 2025", "tecnologia español", "unboxing tech latam"],
}

# ── Scraper ────────────────────────────────────────────────────────────────────
SCRAPER_INTERVAL_SECONDS: int = int(os.getenv("SCRAPER_INTERVAL", "3600"))
MAX_RESULTADOS_POR_KEYWORD: int = int(os.getenv("MAX_POR_KEYWORD", "3"))
LINKS_FILE: str = os.getenv("LINKS_FILE", "links.txt")
ARCHIVO_CSV: str = os.getenv("ARCHIVO_CSV", "datos_scraped.csv")
ARCHIVO_HTML: str = os.getenv("ARCHIVO_HTML", "dashboard.html")

# ── Atribución ─────────────────────────────────────────────────────────────────
ATTRIBUTION_WINDOW_HOURS: int = int(os.getenv("ATTRIBUTION_WINDOW_HOURS", "24"))
