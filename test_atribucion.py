"""
tests/test_atribucion.py — Tests unitarios del motor de atribución.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from atributtion import (
    anonimizar_email,
    calcular_atribucion_probabilistica,
    calcular_metricas_rentabilidad,
)

PRESUPUESTOS_TEST = {"YouTube": 1000, "Instagram": 500}


def _df_ventas():
    return pd.DataFrame({
        "Canal": ["YouTube", "YouTube", "Instagram"],
        "Monto": [300.0, 700.0, 400.0],
        "ID_Venta": [1, 2, 3],
    })


# ── anonimizar_email ───────────────────────────────────────────────────────────

class TestAnonimizarEmail:
    def test_devuelve_hash_sha256(self):
        h = anonimizar_email("test@example.com")
        assert h is not None and len(h) == 64

    def test_none_devuelve_none(self):
        assert anonimizar_email(None) is None

    def test_normaliza_case_y_espacios(self):
        assert anonimizar_email("User@Example.COM") == anonimizar_email("  user@example.com  ")

    def test_emails_distintos_hashes_distintos(self):
        assert anonimizar_email("a@a.com") != anonimizar_email("b@b.com")


# ── calcular_metricas_rentabilidad ─────────────────────────────────────────────

class TestMetricasRentabilidad:
    def test_roi_cero_cuando_ventas_igual_inversion(self):
        df = calcular_metricas_rentabilidad(_df_ventas(), PRESUPUESTOS_TEST)
        yt = df[df["Canal"] == "YouTube"].iloc[0]
        assert yt["ROI"] == pytest.approx(0.0)

    def test_roi_negativo_cuando_ventas_menor_inversion(self):
        df = calcular_metricas_rentabilidad(_df_ventas(), PRESUPUESTOS_TEST)
        ig = df[df["Canal"] == "Instagram"].iloc[0]
        assert ig["ROI"] == pytest.approx(-0.2)

    def test_cpa_correcto(self):
        df = calcular_metricas_rentabilidad(_df_ventas(), PRESUPUESTOS_TEST)
        yt = df[df["Canal"] == "YouTube"].iloc[0]
        assert yt["CPA"] == pytest.approx(500.0)

    def test_canal_sin_presupuesto_devuelve_nan(self):
        df_extra = pd.concat([_df_ventas(), pd.DataFrame({
            "Canal": ["TikTok"], "Monto": [100.0], "ID_Venta": [4]
        })], ignore_index=True)
        result = calcular_metricas_rentabilidad(df_extra, PRESUPUESTOS_TEST)
        roi = result[result["Canal"] == "TikTok"].iloc[0]["ROI"]
        assert np.isnan(roi)


# ── calcular_atribucion_probabilistica ────────────────────────────────────────

def _ventas(ts_list):
    return pd.DataFrame({
        "id": range(len(ts_list)),
        "timestamp": pd.to_datetime(ts_list),
        "click_id": [None] * len(ts_list),
    })

def _vistas(ts_list, canales):
    return pd.DataFrame({
        "timestamp": pd.to_datetime(ts_list),
        "canal": canales,
    })


class TestAtribucionProbabilistica:
    def test_venta_dentro_ventana_se_atribuye(self):
        t0 = datetime(2024, 5, 20, 20, 0)
        result = calcular_atribucion_probabilistica(
            _ventas([t0 + timedelta(hours=1)]),
            _vistas([t0], ["YouTube"]),
        )
        assert len(result) == 1
        assert result.iloc[0]["canal"] == "YouTube"

    def test_venta_fuera_ventana_no_se_atribuye(self):
        t0 = datetime(2024, 5, 20, 20, 0)
        result = calcular_atribucion_probabilistica(
            _ventas([t0 + timedelta(hours=25)]),
            _vistas([t0], ["YouTube"]),
            ventana_horas=24,
        )
        assert result.empty

    def test_impacto_mas_cercano_gana(self):
        t0 = datetime(2024, 5, 20, 20, 0)
        result = calcular_atribucion_probabilistica(
            _ventas([t0 + timedelta(hours=5)]),
            _vistas([t0, t0 + timedelta(hours=4)], ["Instagram", "YouTube"]),
        )
        assert result.iloc[0]["canal"] == "YouTube"

    def test_tipo_probabilistico_sin_click(self):
        t0 = datetime(2024, 5, 20, 20, 0)
        result = calcular_atribucion_probabilistica(
            _ventas([t0 + timedelta(hours=1)]),
            _vistas([t0], ["Instagram"]),
        )
        assert result.iloc[0]["tipo"] == "Probabilística"

    def test_sin_vistas_resultado_vacio(self):
        t0 = datetime(2024, 5, 20, 20, 0)
        result = calcular_atribucion_probabilistica(
            _ventas([t0]),
            _vistas([], []),
        )
        assert result.empty
