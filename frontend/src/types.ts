export type FlightMode = 
  | 'IDLE' 
  | 'EN_ROUTE' 
  | 'HOVER' 
  | 'RETURNING_HOME' 
  | 'CRITICAL_LANDING' 
  | 'COLLISION_AVOIDANCE';

export interface Coordinates {
  lat: number;
  lng: number;
  alt_m: number;
}

export interface NoFlyZone {
  id: string;
  name: string;
  category: 'AIRPORT' | 'MILITARY_BASE' | 'GOVERNMENT' | 'CRITICAL_INFRASTRUCTURE';
  center_lat: number;
  center_lng: number;
  radius_meters: number;
  max_altitude_m: number;
  active: boolean;
}

export interface DroneTelemetry {
  drone_id: string;
  callsign: string;
  model: string;
  battery_pct: number;
  signal_rssi_dbm: number;
  speed_mps: number;
  heading_deg: number;
  coords: {
    lat: number;
    lng: number;
    alt_m: number;
  };
  flight_mode: FlightMode;
  geofence_warning: boolean;
  nearest_no_fly_zone?: string | null;
  distance_to_nfz_m?: number | null;
  last_ping_iso: string;
}

export interface FleetStats {
  total_drones: number;
  active_airborne: number;
  returning_home: number;
  alerts_count: number;
  avg_battery_pct: number;
  avg_speed_mps: number;
  timestamp_iso: string;
}
