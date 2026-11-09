import pytest
from httpx import AsyncClient, ASGITransport
from starlette.testclient import TestClient
from app.main import app
from app.services.geofence import GeofenceService, haversine_distance_m
from app.models.schemas import Coordinates, FlightMode

@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ONLINE"

@pytest.mark.asyncio
async def test_list_drones_and_stats():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Get drones
        resp = await ac.get("/api/v1/drones")
        assert resp.status_code == 200
        drones = resp.json()
        assert len(drones) == 8
        assert drones[0]["drone_id"] == "DRN-801"

        # Get stats
        stats_resp = await ac.get("/api/v1/telemetry/stats")
        assert stats_resp.status_code == 200
        stats = stats_resp.json()
        assert stats["total_drones"] == 8
        assert "avg_battery_pct" in stats

@pytest.mark.asyncio
async def test_mission_command():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Send HOLD command
        hold_resp = await ac.post("/api/v1/drones/DRN-801/mission", json={"command": "HOLD"})
        assert hold_resp.status_code == 200
        assert hold_resp.json()["flight_mode"] == FlightMode.HOVER.value
        assert hold_resp.json()["speed_mps"] == 0.0

        # Send RTH command
        rth_resp = await ac.post("/api/v1/drones/DRN-801/mission", json={"command": "RTH"})
        assert rth_resp.status_code == 200
        assert rth_resp.json()["flight_mode"] == FlightMode.RETURNING_HOME.value

def test_geofence_haversine():
    # Distance between Soetta (-6.1256, 106.6558) and Monas (-6.1754, 106.8272) is approx 19-21 km
    dist = haversine_distance_m(-6.1256, 106.6558, -6.1754, 106.8272)
    assert 18000 < dist < 22000

    # Test proximity inside Halim buffer
    geofence = GeofenceService()
    warning, zone_name, dist_m = geofence.check_proximity(Coordinates(lat=-6.2658, lng=106.8911, alt_m=100.0))
    assert warning is True
    assert "Halim" in zone_name
    assert dist_m < 50.0

def test_websocket_streaming():
    with TestClient(app) as client:
        with client.websocket_connect("/ws/telemetry") as ws:
            # Client connects and stays open
            assert ws is not None
