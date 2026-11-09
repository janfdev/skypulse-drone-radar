from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field

class FlightMode(str, Enum):
    IDLE = "IDLE"
    EN_ROUTE = "EN_ROUTE"
    HOVER = "HOVER"
    RETURNING_HOME = "RETURNING_HOME"
    CRITICAL_LANDING = "CRITICAL_LANDING"
    COLLISION_AVOIDANCE = "COLLISION_AVOIDANCE"

class Coordinates(BaseModel):
    lat: float = Field(..., description="Latitude in decimal degrees")
    lng: float = Field(..., description="Longitude in decimal degrees")
    alt_m: float = Field(..., description="Altitude above ground level in meters")

class NoFlyZone(BaseModel):
    id: str
    name: str
    category: str  # AIRPORT, GOVERNMENT, CRITICAL_INFRASTRUCTURE
    center_lat: float
    center_lng: float
    radius_meters: float
    max_altitude_m: float
    active: bool = True

class DroneTelemetry(BaseModel):
    drone_id: str
    callsign: str
    model: str
    battery_pct: float
    signal_rssi_dbm: int
    speed_mps: float
    heading_deg: float
    coords: Coordinates
    flight_mode: FlightMode
    geofence_warning: bool = False
    nearest_no_fly_zone: Optional[str] = None
    distance_to_nfz_m: Optional[float] = None
    last_ping_iso: str

class MissionCommand(BaseModel):
    command: str = Field(..., description="Command type: RTH, HOLD, RESUME, or DIVERT")
    target_lat: Optional[float] = None
    target_lng: Optional[float] = None
    target_alt_m: Optional[float] = None
    reason: Optional[str] = None

class FleetStats(BaseModel):
    total_drones: int
    active_airborne: int
    returning_home: int
    alerts_count: int
    avg_battery_pct: float
    avg_speed_mps: float
    timestamp_iso: str
