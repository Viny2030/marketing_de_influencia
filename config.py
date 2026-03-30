"""
config.py — Configuración centralizada via variables de entorno.
Reemplaza los valores hardcodeados dispersos en database.py, app.py y dashboard.py.
"""
import os

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

# ── Scraper ────────────────────────────────────────────────────────────────────
SCRAPER_INTERVAL_SECONDS: int = int(os.getenv("SCRAPER_INTERVAL", "3600"))
LINKS_FILE: str = os.getenv("LINKS_FILE", "links.txt")

# ── Ventana de atribución (horas) ─────────────────────────────────────────────
ATTRIBUTION_WINDOW_HOURS: int = int(os.getenv("ATTRIBUTION_WINDOW_HOURS", "24"))
