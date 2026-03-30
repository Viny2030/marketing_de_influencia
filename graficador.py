"""
graficador.py — Genera reporte visual de ROI por influencer/canal.

Uso:
    python graficador.py                    # lee de PostgreSQL
    python graficador.py --csv ventas.csv   # lee de CSV (modo offline)
"""
import argparse
import sys

import matplotlib
matplotlib.use("Agg")  # backend sin GUI, seguro en Docker/CI
import matplotlib.pyplot as plt
import pandas as pd

from database import get_engine, check_connection


def _leer_desde_db() -> pd.DataFrame:
    """Lee datos de campañas desde PostgreSQL."""
    engine = get_engine()
    query = """
        SELECT influencer, SUM(monto_total) AS ingresos
        FROM campanas
        GROUP BY influencer
        ORDER BY ingresos DESC
    """
    return pd.read_sql(query, engine)


def _leer_desde_csv(path: str) -> pd.DataFrame:
    """Lee datos desde un CSV local (modo offline/dev)."""
    df = pd.read_csv(path)
    df.columns = [c.lower() for c in df.columns]
    # Adaptar columnas a lo que espera el graficador
    col_canal = next((c for c in df.columns if "canal" in c or "influencer" in c), df.columns[0])
    col_monto = next((c for c in df.columns if "monto" in c or "ingreso" in c), df.columns[1])
    return (
        df.groupby(col_canal)[col_monto]
        .sum()
        .reset_index()
        .rename(columns={col_canal: "influencer", col_monto: "ingresos"})
        .sort_values("ingresos", ascending=False)
    )


def generar_reporte_visual(df: pd.DataFrame, output: str = "reporte_marketing.png") -> None:
    """Genera y guarda el gráfico de barras de ROI."""
    if df.empty:
        print("⚠️  No hay datos para graficar.")
        return

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(df["influencer"], df["ingresos"], color="#2ecc71", edgecolor="#27ae60")

    # Etiquetas de valor sobre cada barra
    for bar in bars:
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + df["ingresos"].max() * 0.01,
            f"${bar.get_height():,.0f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    ax.set_xlabel("Influencer / Canal", fontsize=12)
    ax.set_ylabel("Ingresos Totales ($)", fontsize=12)
    ax.set_title("Ranking de Retorno de Inversión (ROI)", fontsize=14)
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    plt.savefig(output, dpi=150)
    plt.close(fig)
    print(f"📊 Reporte visual guardado como '{output}'")


def main():
    parser = argparse.ArgumentParser(description="Generador de reportes InflueMetric")
    parser.add_argument("--csv", help="Ruta a CSV local (modo offline)", default=None)
    parser.add_argument("--output", help="Nombre del archivo de salida", default="reporte_marketing.png")
    args = parser.parse_args()

    if args.csv:
        print(f"📂 Leyendo datos desde CSV: {args.csv}")
        df = _leer_desde_csv(args.csv)
    else:
        if not check_connection():
            print("❌ No se pudo conectar a la base de datos.")
            print("   Usá --csv <archivo> para modo offline.")
            sys.exit(1)
        print("🔗 Conectado a PostgreSQL. Leyendo campañas...")
        df = _leer_desde_db()

    generar_reporte_visual(df, output=args.output)


if __name__ == "__main__":
    main()
