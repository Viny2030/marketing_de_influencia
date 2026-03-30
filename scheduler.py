"""
Loop infinito que corre pipeline.py cada hora.
Correr en background: python scheduler.py &
Ver logs: tail -f pipeline.log
Detener: kill $(cat scheduler.pid)
"""
import time
import subprocess
import os
from datetime import datetime

PID_FILE = "scheduler.pid"
INTERVALO = 3600  # 1 hora en segundos

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{ts}] SCHEDULER: {msg}"
    print(linea)
    with open("pipeline.log", "a", encoding="utf-8") as f:
        f.write(linea + "\n")

# Guardar PID para poder matarlo despues
with open(PID_FILE, "w") as f:
    f.write(str(os.getpid()))

log(f"Scheduler iniciado. PID: {os.getpid()}")
log(f"Ciclo cada {INTERVALO//60} minutos.")

ciclo = 1
while True:
    log(f"=== CICLO {ciclo} INICIADO ===")
    try:
        resultado = subprocess.run(
            ["python", "pipeline.py"],
            capture_output=True, text=True, encoding="utf-8"
        )
        if resultado.returncode == 0:
            log(f"Ciclo {ciclo} completado OK.")
        else:
            log(f"Ciclo {ciclo} con errores: {resultado.stderr[:200]}")
    except Exception as e:
        log(f"Error ejecutando pipeline: {e}")

    log(f"Proxima ejecucion en {INTERVALO//60} minutos.")
    ciclo += 1
    time.sleep(INTERVALO)
