from typing import List
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from app.models.schemas import (
    DroneTelemetry,
    NoFlyZone,
    FleetStats,
    MissionCommand,
)
from app.services.geofence import GeofenceService
from app.services.telemetry_engine import TelemetryEngine

router = APIRouter()

# Default singletons
geofence_service = GeofenceService()
telemetry_engine = TelemetryEngine(geofence_service)

def get_engine() -> TelemetryEngine:
    return telemetry_engine

def get_geofence() -> GeofenceService:
    return geofence_service

@router.get("/health", tags=["System"])
async def health_check():
    return {"status": "ONLINE", "service": "SkyPulse Drone Radar Engine", "version": "1.0.0"}

@router.get("/api/v1/drones", response_model=List[DroneTelemetry], tags=["Drones"])
async def list_drones(engine: TelemetryEngine = Depends(get_engine)):
    return engine.get_all_telemetry()

@router.get("/api/v1/drones/{drone_id}", response_model=DroneTelemetry, tags=["Drones"])
async def get_drone(drone_id: str, engine: TelemetryEngine = Depends(get_engine)):
    d = engine.get_drone_telemetry(drone_id)
    if not d:
        raise HTTPException(status_code=404, detail=f"Drone {drone_id} not found in active fleet")
    return d

@router.post("/api/v1/drones/{drone_id}/mission", response_model=DroneTelemetry, tags=["Missions"])
async def send_mission_command(drone_id: str, cmd: MissionCommand, engine: TelemetryEngine = Depends(get_engine)):
    res = engine.issue_mission_command(drone_id, cmd)
    if not res:
        raise HTTPException(status_code=404, detail=f"Drone {drone_id} not found")
    return res

@router.get("/api/v1/geofences", response_model=List[NoFlyZone], tags=["Geofencing"])
async def list_geofences(geofence: GeofenceService = Depends(get_geofence)):
    return geofence.get_all_zones()

@router.get("/api/v1/telemetry/stats", response_model=FleetStats, tags=["Telemetry"])
async def get_stats(engine: TelemetryEngine = Depends(get_engine)):
    return engine.get_fleet_stats()

@router.websocket("/ws/telemetry")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    engine = get_engine()
    await engine.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        engine.disconnect(websocket)
    except Exception:
        engine.disconnect(websocket)
