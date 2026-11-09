import asyncio
import math
import random
from datetime import datetime, timezone
from typing import Dict, List, Set, Optional
from fastapi import WebSocket
from app.models.schemas import (
    DroneTelemetry,
    Coordinates,
    FlightMode,
    FleetStats,
    MissionCommand,
)
from app.services.geofence import GeofenceService, haversine_distance_m

class DroneState:
    def __init__(
        self,
        drone_id: str,
        callsign: str,
        model: str,
        lat: float,
        lng: float,
        alt_m: float,
        heading_deg: float,
        speed_mps: float,
        battery_pct: float,
        home_lat: float,
        home_lng: float,
    ):
        self.drone_id = drone_id
        self.callsign = callsign
        self.model = model
        self.lat = lat
        self.lng = lng
        self.alt_m = alt_m
        self.heading_deg = heading_deg
        self.speed_mps = speed_mps
        self.battery_pct = battery_pct
        self.home_lat = home_lat
        self.home_lng = home_lng
        self.signal_rssi = -60
        self.flight_mode = FlightMode.EN_ROUTE
        self.target_lat = lat + random.uniform(-0.04, 0.04)
        self.target_lng = lng + random.uniform(-0.04, 0.04)

class TelemetryEngine:
    def __init__(self, geofence_svc: GeofenceService):
        self.geofence = geofence_svc
        self.active_connections: Set[WebSocket] = set()
        self.drones: Dict[str, DroneState] = {}
        self._running = False
        self._init_fleet()

    def _init_fleet(self):
        # 8 High-spec Autonomous Logistics Drones in Greater Jakarta Corridor
        fleet_data = [
            ("DRN-801", "Valkyrie-1", "AeroVironment Apex-4", -6.1850, 106.8200, 120.0, 45.0, 18.5, 94.0),
            ("DRN-802", "Spectre-2", "DJI FlyCart 30 Pro", -6.2100, 106.8450, 95.0, 130.0, 14.2, 82.5),
            ("DRN-803", "Apex-3", "SkyDio X10 Enterprise", -6.1550, 106.7800, 110.0, 270.0, 16.0, 76.0),
            ("DRN-804", "Ghost-4", "Wingcopter 198 Heavy", -6.2400, 106.8100, 140.0, 90.0, 22.0, 68.0),
            ("DRN-805", "Raptor-5", "EHang Falcon Heavy", -6.2200, 106.8900, 85.0, 315.0, 12.5, 88.0),
            ("DRN-806", "Horizon-6", "Skyports CargoFlyer", -6.1350, 106.7200, 105.0, 180.0, 19.0, 54.0),
            ("DRN-807", "Condor-7", "AeroVironment Apex-4", -6.2800, 106.8300, 130.0, 210.0, 17.5, 41.0),
            ("DRN-808", "Eagle-8", "DJI FlyCart 30 Pro", -6.1950, 106.8700, 115.0, 15.0, 15.0, 91.0),
        ]

        for drone_id, callsign, model, lat, lng, alt, heading, speed, battery in fleet_data:
            self.drones[drone_id] = DroneState(
                drone_id=drone_id,
                callsign=callsign,
                model=model,
                lat=lat,
                lng=lng,
                alt_m=alt,
                heading_deg=heading,
                speed_mps=speed,
                battery_pct=battery,
                home_lat=lat - 0.02,
                home_lng=lng - 0.02,
            )

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    def get_drone_telemetry(self, drone_id: str) -> Optional[DroneTelemetry]:
        d = self.drones.get(drone_id)
        if not d:
            return None
        coords = Coordinates(lat=d.lat, lng=d.lng, alt_m=d.alt_m)
        is_warn, nearest_nfz, dist_nfz = self.geofence.check_proximity(coords)
        return DroneTelemetry(
            drone_id=d.drone_id,
            callsign=d.callsign,
            model=d.model,
            battery_pct=round(d.battery_pct, 1),
            signal_rssi_dbm=d.signal_rssi,
            speed_mps=round(d.speed_mps, 1),
            heading_deg=round(d.heading_deg, 1),
            coords=coords,
            flight_mode=d.flight_mode,
            geofence_warning=is_warn,
            nearest_no_fly_zone=nearest_nfz,
            distance_to_nfz_m=dist_nfz,
            last_ping_iso=datetime.now(timezone.utc).isoformat(),
        )

    def get_all_telemetry(self) -> List[DroneTelemetry]:
        return [self.get_drone_telemetry(did) for did in self.drones if self.get_drone_telemetry(did)]

    def get_fleet_stats(self) -> FleetStats:
        all_t = self.get_all_telemetry()
        total = len(all_t)
        airborne = sum(1 for d in all_t if d.flight_mode in (FlightMode.EN_ROUTE, FlightMode.HOVER))
        rth = sum(1 for d in all_t if d.flight_mode == FlightMode.RETURNING_HOME)
        alerts = sum(1 for d in all_t if d.geofence_warning or d.battery_pct < 25.0)
        avg_bat = sum(d.battery_pct for d in all_t) / total if total > 0 else 0.0
        avg_spd = sum(d.speed_mps for d in all_t) / total if total > 0 else 0.0

        return FleetStats(
            total_drones=total,
            active_airborne=airborne,
            returning_home=rth,
            alerts_count=alerts,
            avg_battery_pct=round(avg_bat, 1),
            avg_speed_mps=round(avg_spd, 1),
            timestamp_iso=datetime.now(timezone.utc).isoformat(),
        )

    def issue_mission_command(self, drone_id: str, cmd: MissionCommand) -> Optional[DroneTelemetry]:
        d = self.drones.get(drone_id)
        if not d:
            return None

        c = cmd.command.upper()
        if c == "RTH":
            d.flight_mode = FlightMode.RETURNING_HOME
            # Turn heading directly to home base
            d.heading_deg = (math.degrees(math.atan2(d.home_lng - d.lng, d.home_lat - d.lat)) + 360) % 360
        elif c == "HOLD":
            d.flight_mode = FlightMode.HOVER
            d.speed_mps = 0.0
        elif c == "RESUME":
            d.flight_mode = FlightMode.EN_ROUTE
            d.speed_mps = 16.0
        elif c == "DIVERT":
            d.flight_mode = FlightMode.COLLISION_AVOIDANCE
            d.heading_deg = (d.heading_deg + 90.0) % 360
            if cmd.target_lat and cmd.target_lng:
                d.target_lat = cmd.target_lat
                d.target_lng = cmd.target_lng

        return self.get_drone_telemetry(drone_id)

    async def broadcast(self, payload: dict):
        if not self.active_connections:
            return
        dead = []
        for ws in self.active_connections:
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

    def tick_simulation(self, delta_sec: float = 0.5):
        """Simulates kinematic motion, battery consumption, and waypoints."""
        for d in self.drones.values():
            if d.flight_mode == FlightMode.IDLE:
                continue

            # Battery drain (0.02% per second when flying, 0.01% in hover)
            drain = 0.01 * delta_sec if d.flight_mode == FlightMode.HOVER else 0.025 * delta_sec
            d.battery_pct = max(0.0, d.battery_pct - drain)

            if d.battery_pct <= 15.0 and d.flight_mode != FlightMode.CRITICAL_LANDING:
                d.flight_mode = FlightMode.RETURNING_HOME

            # If returning home
            if d.flight_mode == FlightMode.RETURNING_HOME:
                dist_to_home = haversine_distance_m(d.lat, d.lng, d.home_lat, d.home_lng)
                if dist_to_home < 30.0:
                    d.flight_mode = FlightMode.IDLE
                    d.speed_mps = 0.0
                    continue
                # Recalculate heading home
                dy = d.home_lat - d.lat
                dx = d.home_lng - d.lng
                d.heading_deg = (math.degrees(math.atan2(dx, dy)) + 360) % 360

            # Kinematic step
            if d.speed_mps > 0:
                rad = math.radians(d.heading_deg)
                dist_m = d.speed_mps * delta_sec
                # 1 degree latitude ~ 111,000 meters
                delta_lat = (dist_m * math.cos(rad)) / 111000.0
                delta_lng = (dist_m * math.sin(rad)) / (111000.0 * math.cos(math.radians(d.lat)))

                d.lat += delta_lat
                d.lng += delta_lng

                # Slight random drift to simulate wind gusts
                d.heading_deg = (d.heading_deg + random.uniform(-1.5, 1.5)) % 360
                d.alt_m = max(50.0, min(200.0, d.alt_m + random.uniform(-0.5, 0.5)))
                d.signal_rssi = int(max(-95, min(-50, d.signal_rssi + random.randint(-1, 1))))

    async def run_loop(self):
        self._running = True
        while self._running:
            self.tick_simulation(0.4)
            # Broadcast latest telemetry packet to all connected clients
            all_telemetry = [t.model_dump() for t in self.get_all_telemetry()]
            stats = self.get_fleet_stats().model_dump()
            payload = {
                "type": "TELEMETRY_BATCH",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "stats": stats,
                "drones": all_telemetry,
            }
            await self.broadcast(payload)
            await asyncio.sleep(0.4)
