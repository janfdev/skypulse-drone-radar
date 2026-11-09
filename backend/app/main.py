import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router, telemetry_engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Launch background simulation loop
    sim_task = asyncio.create_task(telemetry_engine.run_loop())
    yield
    # Graceful shutdown
    telemetry_engine._running = False
    sim_task.cancel()
    try:
        await sim_task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title="SkyPulse Telemetry & Geofence Engine",
    description="Real-Time Fleet & Drone Telemetry Radar with Geofencing and Dynamic Mission Control",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for Svelte client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8008, reload=True)
