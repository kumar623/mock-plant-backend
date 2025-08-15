# Mock Plant Backend

A tiny FastAPI service that fakes your plant/telemetry API so your Agent Hub can run right now.

## Endpoints
- GET /devices
- GET /telemetry/latest?device_id=container-001
- POST /control/setpoints

## Run locally
```bash
pip install -r requirements.txt
uvicorn main:app --reload
