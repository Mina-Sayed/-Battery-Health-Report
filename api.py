from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from battery_report import generate_report

app = FastAPI(
    title="EV Battery Report API",
    description="An API for generating battery health reports from EV diagnostic logs.",
    version="1.0.0"
)

class Cell(BaseModel):
    id: int
    voltage: float
    temp_c: float

class SocReading(BaseModel):
    ts: str
    soc: int

class CycleHistory(BaseModel):
    start_soc: int
    end_soc: int
    energy_kwh: float
    duration_h: float

class BatteryLog(BaseModel):
    vehicle_id: str
    timestamp: str
    nominal_capacity_kwh: float
    measured_capacity_kwh: Optional[float] = None
    pack_voltage: float
    cell_count: int
    cells: List[Cell]
    soc_timeseries: List[SocReading]
    cycle_history: List[CycleHistory]

@app.post("/v1/battery_report", response_model=Dict[str, Any])
async def create_battery_report(log: BatteryLog):
    """
    Accepts raw EV diagnostic data in JSON format and returns a battery health report.
    """
    try:
        report = generate_report(log.dict())
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# To run this API:
# 1. Install dependencies: pip install fastapi uvicorn pydantic
# 2. Run the server: uvicorn api:app --reload
