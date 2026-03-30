# InflueMetric — Marketing de Influencia

Plataforma de **atribución probabilística** para campañas de influencer marketing.
Scraping de YouTube sin API oficial · Atribución por ventana temporal · Dashboard en tiempo real.

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                     Docker Compose                       │
│                                                          │
│  ┌──────────┐    ┌──────────────┐    ┌───────────────┐  │
│  │ PostgreSQL│◄───│  FastAPI     │◄───│   Streamlit   │  │
│  │  :5432   │    │  app.py :8000│    │  dashboard.py │  │
│  └──────────┘    └──────────────┘    │  :8501        │  │
│                         ▲            └───────────────┘  │
│                         │                                │
│              ┌──────────────────┐                        │
│              │  processors.py   │  (scraper yt-dlp)      │
│              └──────────────────┘                        │
└─────────────────────────────────────────────────────────┘
```

**Módulos principales:**

| Archivo | Rol |
|---|---|
| `config.py` | Variables de entorno centralizadas (DB, presupuestos, scraper) |
| `database.py` | Engine SQLAlchemy único con pool y healthcheck |
| `atributtion.py` | Motor de atribución probabilística + métricas ROI/CPA |
| `app.py` | API REST FastAPI (`/health`, `/api/v1/metrics`) |
| `dashboard.py` | Dashboard Streamlit con fallback CSV |
| `processors.py` | Scraper YouTube vía yt-dlp |
| `graficador.py` | Reporte visual matplotlib (modo DB o `--csv`) |

---

## Setup rápido

### 1. Variables de entorno

```bash
cp .env.example .env
# Editar .env con tus credenciales reales
```

### 2. Levantar con Docker Compose

```bash
docker compose up --build
```

Los servicios se levantan en orden correcto gracias a los healthchecks:
`PostgreSQL → API → Dashboard`

| Servicio | URL |
|---|---|
| API | http://localhost:8000 |
| Healthcheck | http://localhost:8000/health |
| Dashboard | http://localhost:8501 |

### 3. Desarrollo local (sin Docker)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# API
uvicorn app:app --reload

# Dashboard
streamlit run dashboard.py

# Reporte visual offline
python graficador.py --csv ventas.csv
```

---

## Tests

```bash
pytest tests/ -v
```

El CI (GitHub Actions) corre en cada push: lint con `ruff` + todos los tests.

---

## Modelo de atribución

Se usa **atribución probabilística por ventana temporal** con decaimiento exponencial:

```
score = e^(−diff_horas / 12)
```

Cada venta se atribuye al impacto (video/posteo) más cercano en el tiempo
dentro de la ventana configurada (`ATTRIBUTION_WINDOW_HOURS`, default 24 h).

Si la venta tiene `click_id`, se clasifica como **Directa**; si no, como **Probabilística**.

### Métricas calculadas

| Métrica | Fórmula |
|---|---|
| ROI | `(Ventas - Inversión) / Inversión` |
| CPA | `Inversión / Cantidad de Ventas` |

---

## Variables de entorno

| Variable | Default | Descripción |
|---|---|---|
| `DATABASE_URL` | `postgresql://user:password@localhost:5432/marketing_db` | Conexión PostgreSQL |
| `BUDGET_YOUTUBE` | `1500` | Presupuesto canal YouTube (USD) |
| `BUDGET_INSTAGRAM` | `800` | Presupuesto Instagram (USD) |
| `BUDGET_GOOGLE_ADS` | `1200` | Presupuesto Google Ads (USD) |
| `BUDGET_FACEBOOK` | `900` | Presupuesto Facebook (USD) |
| `SCRAPER_INTERVAL` | `3600` | Segundos entre ciclos del scraper |
| `ATTRIBUTION_WINDOW_HOURS` | `24` | Ventana de atribución en horas |

---

## Estructura del proyecto

```
marketing_de_influencia/
├── .env.example              ← copiar a .env
├── .github/workflows/ci.yml  ← GitHub Actions
├── config.py                 ← configuración centralizada
├── database.py               ← engine PostgreSQL
├── atributtion.py            ← motor de atribución
├── app.py                    ← API FastAPI
├── dashboard.py              ← Streamlit dashboard
├── processors.py             ← scraper YouTube
├── graficador.py             ← reportes visuales
├── tests/
│   └── test_atribucion.py   ← 13 tests unitarios
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```
