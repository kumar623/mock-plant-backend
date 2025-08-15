### **main.py**
import os, random
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import Dict

app = FastAPI(title="Mock Plant Backend")

DEVICE_IDS = [d.strip() for d in os.getenv("DEVICE_IDS","container-001,container-002,container-003").split(",") if d.strip()]

_state: Dict[str, Dict[str, float]] = {}

def _seed(device_id: str):
    base = {
        "ph": round(random.uniform(5.7, 6.3), 2),
        "ec_ms_cm": round(random.uniform(1.6, 2.6), 2),
        "temp_c": round(random.uniform(20.0, 26.0), 1),
        "humidity": round(random.uniform(55, 75), 0),
        "co2_ppm": round(random.uniform(800, 1100), 0),
        "light_ppfd": round(random.uniform(200, 500), 0),
    }
    _state[device_id] = base

def _drift(val: float, mag: float, lo: float, hi: float) -> float:
    v = val + random.uniform(-mag, mag)
    if v < lo: v = lo + abs(v - lo)
    if v > hi: v = hi - abs(v - hi)
    return v

@app.get("/devices")
def devices():
    return {"devices": [{"id": d} for d in DEVICE_IDS]}

@app.get("/telemetry/latest")
def telemetry_latest(device_id: str = Query(...)):
    if device_id not in DEVICE_IDS:
        raise HTTPException(status_code=404, detail="unknown device_id")
    if device_id not in _state:
        _seed(device_id)
    s = _state[device_id]
    s["ph"] = round(_drift(s["ph"], 0.06, 5.2, 6.8), 2)
    s["ec_ms_cm"] = round(_drift(s["ec_ms_cm"], 0.08, 1.0, 3.2), 2)
    s["temp_c"] = round(_drift(s["temp_c"], 0.3, 18.0, 30.0), 1)
    s["humidity"] = round(_drift(s["humidity"], 1.2, 40, 90), 0)
    s["co2_ppm"] = round(_drift(s["co2_ppm"], 25, 600, 1400), 0)
    s["light_ppfd"] = round(_drift(s["light_ppfd"], 15, 100, 800), 0)
    return {"latest": s, "device_id": device_id}

class Setpoints(BaseModel):
    device_id: str
    target_temp_c: float | None = None
    target_humidity: float | None = None
    target_co2_ppm: float | None = None
    target_ph: float | None = None
    target_ec_ms_cm: float | None = None
    target_light_ppfd: float | None = None
    comment: str | None = None

@app.post("/control/setpoints")
def control_setpoints(body: Setpoints):
    if body.device_id not in DEVICE_IDS:
        raise HTTPException(status_code=404, detail="unknown device_id")
    return {"status": "accepted", "applied": False, "echo": body.dict()}

@app.get("/health")
def health():
    return {"ok": True, "devices": DEVICE_IDS}
