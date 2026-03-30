"""
atributtion.py — Motor de atribución probabilística y métricas de ROI.

NOTA: el nombre se conserva por compatibilidad con imports existentes.
Próximo sprint: renombrar a atribucion.py.
"""
import hashlib

import numpy as np
import pandas as pd
from datetime import timedelta


# ── Privacidad ─────────────────────────────────────────────────────────────────

def anonimizar_email(email):
    """Aplica SHA-256 al email para cumplir con GDPR/LGPD."""
    if pd.isna(email):
        return None
    return hashlib.sha256(email.strip().lower().encode()).hexdigest()


# ── Atribución probabilística ──────────────────────────────────────────────────

def calcular_atribucion_probabilistica(df_ventas, df_vistas, ventana_horas=24):
    """
    Para cada venta, busca el impacto más cercano dentro de la ventana y
    calcula un score con decaimiento exponencial (half-life ~8 h).

    df_ventas: columnas esperadas — id, timestamp, click_id (opcional)
    df_vistas: columnas esperadas — timestamp, canal
    """
    atribuciones = []

    for _, venta in df_ventas.iterrows():
        inicio_ventana = venta["timestamp"] - timedelta(hours=ventana_horas)
        impactos = df_vistas[
            (df_vistas["timestamp"] >= inicio_ventana)
            & (df_vistas["timestamp"] <= venta["timestamp"])
        ]

        if impactos.empty:
            continue

        impactos = impactos.copy()
        impactos["diff_horas"] = (
            venta["timestamp"] - impactos["timestamp"]
        ).dt.total_seconds() / 3600

        # Score más alto cuanto más reciente es el impacto respecto a la venta
        impactos["score_influencia"] = np.exp(-impactos["diff_horas"] / 12)

        mejor = impactos.loc[impactos["score_influencia"].idxmax()]

        click_id = venta.get("click_id")
        tipo = "Directa" if (click_id and not pd.isna(click_id)) else "Probabilística"

        atribuciones.append(
            {
                "venta_id": venta["id"],
                "canal": mejor["canal"],
                "score": mejor["score_influencia"],
                "tipo": tipo,
            }
        )

    return pd.DataFrame(atribuciones)


# ── Last-click (modelo simple) ─────────────────────────────────────────────────

def calcular_atribucion_last_click(df_ventas):
    """Modelo last-click: el canal registrado se lleva el 100% del crédito."""
    return df_ventas.groupby("Canal")["Monto"].sum().reset_index()


# ── Métricas de rentabilidad ───────────────────────────────────────────────────

def calcular_metricas_rentabilidad(df_ventas, presupuesto_dict):
    """
    Calcula ROI y CPA por canal.

    df_ventas: columnas Canal, Monto, ID_Venta
    presupuesto_dict: {'YouTube': 1500, 'Instagram': 800, ...}
    """
    resumen = (
        df_ventas.groupby("Canal")
        .agg(Ventas_Totales=("Monto", "sum"), Cantidad_Ventas=("ID_Venta", "count"))
        .reset_index()
    )

    resumen["Inversion"] = resumen["Canal"].map(presupuesto_dict).fillna(0)

    # Evitar división por cero
    resumen["ROI"] = resumen.apply(
        lambda r: (r["Ventas_Totales"] - r["Inversion"]) / r["Inversion"]
        if r["Inversion"] > 0 else float("nan"),
        axis=1,
    )
    resumen["CPA"] = resumen.apply(
        lambda r: r["Inversion"] / r["Cantidad_Ventas"]
        if r["Cantidad_Ventas"] > 0 else float("nan"),
        axis=1,
    )

    return resumen


# ── Ejecución directa ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        ventas = pd.read_csv("ventas.csv", parse_dates=["timestamp"])
        vistas = pd.read_csv("datos_scraped.csv", parse_dates=["timestamp"])

        if "email" in ventas.columns:
            ventas["user_id_hashed"] = ventas["email"].apply(anonimizar_email)
            ventas.drop(columns=["email"], inplace=True)

        resultado = calcular_atribucion_probabilistica(ventas, vistas)

        resumen = resultado.groupby("canal").agg(
            Ventas_Atribuidas=("venta_id", "count"),
            Confianza_Media=("score", "mean"),
        )

        print("### INFLUEMETRIC: REPORTE DE ATRIBUCIÓN ###")
        print(resumen)

        resumen.to_csv("reporte_roi_final.csv")
        print("\n[OK] Reporte guardado en reporte_roi_final.csv")

    except FileNotFoundError as e:
        print(f"[Error] Archivo no encontrado: {e}")
        print("Asegúrate de tener 'ventas.csv' y 'datos_scraped.csv' en la carpeta.")
