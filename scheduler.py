"""
scheduler.py — Loop que corre el pipeline automáticamente cada hora.

Uso:
  Correr en background:  python scheduler.py &
  Ver logs:              tail -f pipeline.log
  Detener:               kill $(cat scheduler.pid)

Cambios respecto a la versión anterior:
  - Importa paso_scraping() y paso_dashboard() directamente en vez de
    lanzar un subproceso. Más rápido, menos frágil, sin dependencia del PATH.
  - Intervalo configurable desde config.py / variable de entorno SCRAPER_INTERVAL.
"""
import os
import time
import traceback
from datetime import datetime

from config import SCRAPER_INTERVAL_SECONDS
from pipeline import paso_dashboard, paso_scraping

PID_FILE = "scheduler.pid"

# ── Logging ────────────────────────────────────────────────────────────────────

def log(msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{ts}] SCHEDULER: {msg}"
    print(linea)
    with open("pipeline.log", "a", encoding="utf-8") as f:
        f.write(linea + "\n")


# ── PID ────────────────────────────────────────────────────────────────────────

with open(PID_FILE, "w") as f:
    f.write(str(os.getpid()))

log(f"Scheduler iniciado. PID: {os.getpid()}")
log(f"Ciclo cada {SCRAPER_INTERVAL_SECONDS // 60} minutos.")

# ── Loop principal ─────────────────────────────────────────────────────────────

ciclo = 1
while True:
    log(f"=== CICLO {ciclo} INICIADO ===")
    try:
        paso_scraping()
        paso_dashboard()
        log(f"Ciclo {ciclo} completado OK.")
    except Exception:
        # Captura cualquier excepción sin matar el scheduler
        log(f"Ciclo {ciclo} con errores:\n{traceback.format_exc()}")

    log(f"Próxima ejecución en {SCRAPER_INTERVAL_SECONDS // 60} minutos.")
    ciclo += 1
    time.sleep(SCRAPER_INTERVAL_SECONDS)
