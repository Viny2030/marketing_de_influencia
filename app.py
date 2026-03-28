from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from db import insert_event, insert_conversion, get_data
from attribution import run_attribution

app = FastAPI()

# =========================
# MODELOS
# =========================

class Event(BaseModel):
    device_id: str
    campaign_id: str
    timestamp: datetime

class Conversion(BaseModel):
    user_id: str
    value: float
    timestamp: datetime

# =========================
# ENDPOINTS
# =========================

@app.post("/track")
def track_event(event: Event):
    insert_event(event.device_id, event.campaign_id, event.timestamp)
    return {"status": "event stored"}

@app.post("/conversion")
def track_conversion(conv: Conversion):
    insert_conversion(conv.user_id, conv.value, conv.timestamp)
    return {"status": "conversion stored"}

@app.get("/report")
def report():
    data = get_data()
    results = run_attribution(data)
    return results
