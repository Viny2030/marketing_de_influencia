"""
scheduler.py — Corre el pipeline todos los días a las 3:00 AM.

Uso:
  Iniciar en background:  python scheduler.py &
  Ver logs:               tail -f pipeline.log
  Detener:                kill $(cat scheduler.pid)

Lógica:
  - Al arrancar calcula cuántos segundos faltan para la próxima 3:00 AM.
  - Duerme hasta ese momento, corre el pipeline, y vuelve a dormir 24 hs.
  - Si el proceso arranca después de las 3 AM, espera al día siguiente.
  - Captura cualquier excepción sin matar el proceso, para que siga corriendo
    aunque falle un ciclo.
"""
import os
import time
import traceback
from datetime import datetime, timedelta

from pipeline import paso_dashboard, paso_scraping

PID_FILE = "scheduler.pid"
HORA_EJECUCION = 3   # 3:00 AM


# ── Helpers ────────────────────────────────────────────────────────────────────

def log(msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{ts}] SCHEDULER: {msg}"
    print(linea)
    with open("pipeline.log", "a", encoding="utf-8") as f:
        f.write(linea + "\n")


def segundos_hasta_proximas_3am() -> float:
    """Devuelve los segundos que faltan para la próxima 3:00:00 AM."""
    ahora = datetime.now()
    proxima = ahora.replace(hour=HORA_EJECUCION, minute=0, second=0, microsecond=0)
    if ahora >= proxima:
        # Ya pasaron las 3 AM de hoy → apuntar al día siguiente
        proxima += timedelta(days=1)
    segundos = (proxima - ahora).total_seconds()
    return segundos


# ── PID ────────────────────────────────────────────────────────────────────────

with open(PID_FILE, "w") as f:
    f.write(str(os.getpid()))

log(f"Scheduler iniciado. PID: {os.getpid()}")
log(f"El pipeline correrá todos los días a las {HORA_EJECUCION:02d}:00 AM.")

# ── Loop principal ─────────────────────────────────────────────────────────────

ciclo = 1
while True:
    espera = segundos_hasta_proximas_3am()
    horas  = int(espera // 3600)
    minutos = int((espera % 3600) // 60)
    log(f"Próxima ejecución en {horas}h {minutos}m (ciclo {ciclo}).")

    time.sleep(espera)

    log(f"=== CICLO {ciclo} — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    try:
        paso_scraping()
        paso_dashboard()
        log(f"Ciclo {ciclo} completado OK.")
    except Exception:
        log(f"Ciclo {ciclo} con errores:\n{traceback.format_exc()}")

    ciclo += 1
    # Pequeña pausa para no re-disparar en el mismo minuto
    time.sleep(60)
