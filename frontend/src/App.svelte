<script lang="ts">
  import { onMount } from 'svelte';
  import type { DroneTelemetry, FleetStats, NoFlyZone } from './types';
  import RadarDisplay from './components/RadarDisplay.svelte';
  import TelemetryCards from './components/TelemetryCards.svelte';
  import DroneDetailPanel from './components/DroneDetailPanel.svelte';
  import FleetListTable from './components/FleetListTable.svelte';

  // Svelte 5 Runes for Fine-Grained Reactive State
  let drones = $state<DroneTelemetry[]>([]);
  let stats = $state<FleetStats | null>(null);
  let geofences = $state<NoFlyZone[]>([]);
  let selectedDroneId = $state<string | null>('DRN-801');
  let wsConnected = $state<boolean>(false);
  let currentTime = $state<string>(new Date().toISOString().slice(11, 19) + ' UTC');

  // $derived rune for current selected drone
  let selectedDrone = $derived(
    drones.find((d) => d.drone_id === selectedDroneId) ?? (drones[0] ?? null)
  );

  // Backend API URL (dynamic host so it works locally and across VPS network)
  const API_HOST = typeof window !== 'undefined' ? window.location.hostname : '127.0.0.1';
  const API_BASE = `http://${API_HOST}:8008`;
  const WS_URL = `ws://${API_HOST}:8008/ws/telemetry`;

  // Fetch initial geofences & fleet state
  async function loadInitialData() {
    try {
      const [geoRes, droneRes, statRes] = await Promise.all([
        fetch(`${API_BASE}/api/v1/geofences`),
        fetch(`${API_BASE}/api/v1/drones`),
        fetch(`${API_BASE}/api/v1/telemetry/stats`),
      ]);
      if (geoRes.ok) geofences = await geoRes.json();
      if (droneRes.ok) drones = await droneRes.json();
      if (statRes.ok) stats = await statRes.json();
    } catch (err) {
      console.warn('Initial data load warning:', err);
    }
  }

  // Connect WebSocket for 20Hz Telemetry Stream
  function initWebSocket() {
    let ws: WebSocket;
    let reconnectTimer: any;

    function connect() {
      ws = new WebSocket(WS_URL);

      ws.onopen = () => {
        wsConnected = true;
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'TELEMETRY_BATCH') {
            drones = data.drones;
            stats = data.stats;
          }
        } catch (e) {
          console.error('Error parsing telemetry frame:', e);
        }
      };

      ws.onclose = () => {
        wsConnected = false;
        reconnectTimer = setTimeout(connect, 2000);
      };

      ws.onerror = () => {
        ws.close();
      };
    }

    connect();

    return () => {
      clearTimeout(reconnectTimer);
      if (ws) ws.close();
    };
  }

  // Send Mission Command (RTH, HOLD, RESUME, DIVERT)
  async function handleSendCommand(droneId: string, command: string) {
    try {
      const res = await fetch(`${API_BASE}/api/v1/drones/${droneId}/mission`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command }),
      });
      if (res.ok) {
        const updated = await res.json();
        // Optimistic local update
        drones = drones.map((d) => (d.drone_id === updated.drone_id ? updated : d));
      }
    } catch (e) {
      console.error('Failed to issue mission command:', e);
    }
  }

  // Setup Lifecycle onMount
  onMount(() => {
    loadInitialData();
    const cleanupWs = initWebSocket();

    const clockTimer = setInterval(() => {
      currentTime = new Date().toISOString().slice(11, 19) + ' UTC';
    }, 1000);

    return () => {
      cleanupWs();
      clearInterval(clockTimer);
    };
  });
</script>

<div class="min-h-screen bg-[#060911] text-slate-100 flex flex-col antialiased">
  <!-- Top Command HUD Navigation Bar -->
  <header class="border-b border-slate-800 bg-[#090e1a]/80 backdrop-blur sticky top-0 z-50 px-4 py-2.5">
    <div class="max-w-7xl mx-auto flex items-center justify-between">
      
      <!-- Brand & Tactical Identity -->
      <div class="flex items-center gap-3">
        <div class="size-8 rounded-lg bg-cyan-950 border border-cyan-500/40 flex items-center justify-center text-cyan-400 font-bold shadow-lg shadow-cyan-500/10">
          ⚡
        </div>
        <div>
          <div class="flex items-center gap-2">
            <span class="text-sm font-bold tracking-wider font-mono text-slate-100">SKYPULSE</span>
            <span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
              SVELTE 5 + FASTAPI
            </span>
          </div>
          <p class="text-[10px] font-mono text-slate-400">AUTONOMOUS FLEET & DRONE TELEMETRY RADAR</p>
        </div>
      </div>

      <!-- Live Stream Status Indicators -->
      <div class="flex items-center gap-4 text-xs font-mono">
        <!-- WebSocket Status Indicator -->
        <div class="flex items-center gap-2 px-2.5 py-1 rounded-md bg-slate-900 border border-slate-800">
          <span class="size-2 rounded-full {wsConnected ? 'bg-emerald-400 animate-pulse' : 'bg-red-500'}"></span>
          <span class="{wsConnected ? 'text-emerald-400' : 'text-red-400'}">
            {wsConnected ? 'STREAMING 20Hz' : 'DISCONNECTED'}
          </span>
        </div>

        <!-- Airspace Sector -->
        <div class="hidden sm:flex items-center gap-2 px-2.5 py-1 rounded-md bg-slate-900 border border-slate-800 text-slate-300">
          <span class="text-slate-500">SECTOR:</span>
          <span>JAKARTA TMA (FIR)</span>
        </div>

        <!-- Clock -->
        <div class="hidden md:block font-mono text-cyan-400 font-bold px-2 py-1 bg-cyan-950/40 rounded border border-cyan-900">
          {currentTime}
        </div>
      </div>
    </div>
  </header>

  <!-- Main Cockpit Viewport -->
  <main class="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 space-y-5">
    
    <!-- Top Telemetry KPI Cards -->
    <TelemetryCards {stats} />

    <!-- Center Radar & Cockpit Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5 items-stretch">
      <!-- 2 Columns: Polar Radar Display -->
      <div class="lg:col-span-2 flex flex-col justify-center">
        <RadarDisplay 
          {drones} 
          {geofences} 
          {selectedDroneId} 
          onSelectDrone={(id) => (selectedDroneId = id)} 
        />
      </div>

      <!-- 1 Column: Selected Drone Detail & Mission Command -->
      <div class="lg:col-span-1">
        <DroneDetailPanel 
          drone={selectedDrone} 
          onSendCommand={handleSendCommand} 
        />
      </div>
    </div>

    <!-- Bottom: Fleet Directory Table -->
    <FleetListTable 
      {drones} 
      {selectedDroneId} 
      onSelectDrone={(id) => (selectedDroneId = id)} 
    />

  </main>

  <!-- Cockpit Footer -->
  <footer class="border-t border-slate-800/80 py-3 text-center text-[11px] font-mono text-slate-500">
    SKYPULSE v1.0.0 · Powered by Svelte 5 Runes ($state, $derived) & FastAPI Async Engine
  </footer>
</div>
