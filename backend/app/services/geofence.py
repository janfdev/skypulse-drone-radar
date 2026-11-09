import math
from typing import List, Tuple, Optional
from app.models.schemas import NoFlyZone, Coordinates

EARTH_RADIUS_METERS = 6371000.0

def haversine_distance_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculates great-circle distance between two GPS coordinates in meters."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lng2 - lng1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return EARTH_RADIUS_METERS * c

# Pre-configured Indonesian Critical Airspaces (e.g. Jakarta FIR / Halim, Soetta, Istana Merdeka, IKN Core)
DEFAULT_NO_FLY_ZONES: List[NoFlyZone] = [
    NoFlyZone(
        id="NFZ-001",
        name="Soekarno-Hatta Int Airport (Restricted Airspace)",
        category="AIRPORT",
        center_lat=-6.1256,
        center_lng=106.6558,
        radius_meters=4500.0,
        max_altitude_m=3000.0,
        active=True
    ),
    NoFlyZone(
        id="NFZ-002",
        name="Halim Perdanakusuma Military Base",
        category="MILITARY_BASE",
        center_lat=-6.2658,
        center_lng=106.8911,
        radius_meters=3500.0,
        max_altitude_m=2000.0,
        active=True
    ),
    NoFlyZone(
        id="NFZ-003",
        name="Istana Merdeka & Government Capitol Zone",
        category="GOVERNMENT",
        center_lat=-6.1702,
        center_lng=106.8249,
        radius_meters=2000.0,
        max_altitude_m=1500.0,
        active=True
    ),
    NoFlyZone(
        id="NFZ-004",
        name="Tanjung Priok Strategic Port Facility",
        category="CRITICAL_INFRASTRUCTURE",
        center_lat=-6.1035,
        center_lng=106.8833,
        radius_meters=2200.0,
        max_altitude_m=1000.0,
        active=True
    ),
]

class GeofenceService:
    def __init__(self, zones: Optional[List[NoFlyZone]] = None):
        self.zones: List[NoFlyZone] = zones or DEFAULT_NO_FLY_ZONES

    def get_all_zones(self) -> List[NoFlyZone]:
        return [z for z in self.zones if z.active]

    def check_proximity(self, coords: Coordinates) -> Tuple[bool, Optional[str], Optional[float]]:
        """
        Returns:
            - is_warning: bool (True if inside zone OR within warning buffer of 400m)
            - nearest_zone_name: Optional[str]
            - min_distance_m: Optional[float]
        """
        if not self.zones:
            return False, None, None

        min_dist: Optional[float] = None
        nearest_zone: Optional[NoFlyZone] = None

        for zone in self.zones:
            if not zone.active:
                continue
            dist = haversine_distance_m(coords.lat, coords.lng, zone.center_lat, zone.center_lng)
            if min_dist is None or dist < min_dist:
                min_dist = dist
                nearest_zone = zone

        if nearest_zone and min_dist is not None:
            # If distance is less than zone radius + 400m buffer
            is_warning = min_dist <= (nearest_zone.radius_meters + 400.0) and coords.alt_m <= nearest_zone.max_altitude_m
            return is_warning, nearest_zone.name, round(min_dist, 1)

        return False, None, None
