<script lang="ts">
  import { onMount } from 'svelte';
  import type { DroneTelemetry, FleetStats, NoFlyZone } from './types';
  import RadarDisplay from './components/RadarDisplay.svelte';
  import TelemetryCards from './components/TelemetryCards.svelte';
  import DroneDetailPanel from './components/DroneDetailPanel.svelte';
  import FleetListTable from './components/FleetListTable.svelte';
  import ThemeToggle from './components/ThemeToggle.svelte';
  import Badge from './components/ui/badge/Badge.svelte';

  // Svelte 5 Runes for Fine-Grained Reactive State
  let drones = $state<DroneTelemetry[]>([]);
  let stats = $state<FleetStats | null>(null);
  let geofences = $state<NoFlyZone[]>([]);
  let selectedDroneId = $state<string | null>('DRN-801');
  let wsConnected = $state<boolean>(false);
  let isLoading = $state<boolean>(true);
  let errorMessage = $state<string | null>(null);
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
      errorMessage = null;
      const [geoRes, droneRes, statRes] = await Promise.all([
        fetch(`${API_BASE}/api/v1/geofences`),
        fetch(`${API_BASE}/api/v1/drones`),
        fetch(`${API_BASE}/api/v1/telemetry/stats`),
      ]);
      if (geoRes.ok) geofences = await geoRes.json();
      if (droneRes.ok) drones = await droneRes.json();
      if (statRes.ok) stats = await statRes.json();
    } catch (err: any) {
      errorMessage = 'Backend connection offline. Attempting automatic reconnection to telemetry engine.';
      console.warn('Initial data load warning:', err);
    } finally {
      isLoading = false;
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
        errorMessage = null;
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

<div class="min-h-screen bg-background text-foreground flex flex-col antialiased">
  <!-- Top Command Navigation Bar -->
  <header class="border-b border-border bg-card/80 backdrop-blur sticky top-0 z-50 px-4 py-2.5">
    <div class="max-w-7xl mx-auto flex items-center justify-between">
      
      <!-- Brand & System Identity -->
      <div class="flex items-center gap-3">
        <div class="size-8 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center text-primary font-bold shadow-sm">
          <!-- Crosshair Radar Icon -->
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><line x1="22" x2="18" y1="12" y2="12"/><line x1="6" x2="2" y1="12" y2="12"/><line x1="12" x2="12" y1="6" y2="2"/><line x1="12" x2="12" y1="22" y2="18"/></svg>
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h1 class="text-sm font-semibold tracking-wider font-mono text-foreground">SKYPULSE</h1>
            <Badge variant="outline" class="text-[10px] font-mono font-medium">
              Svelte 5 + FastAPI
            </Badge>
          </div>
          <p class="text-[10px] font-mono text-muted-foreground">Autonomous Fleet and Drone Telemetry Radar</p>
        </div>
      </div>

      <!-- Live Stream Status Indicators -->
      <div class="flex items-center gap-3 text-xs font-mono">
        <!-- WebSocket Status Indicator -->
        <div class="flex items-center gap-2 px-2.5 py-1 rounded-md bg-secondary border border-border">
          <span class="size-2 rounded-full {wsConnected ? 'bg-emerald-500' : 'bg-destructive'}"></span>
          <span class="{wsConnected ? 'text-emerald-600 dark:text-emerald-400 font-medium' : 'text-destructive font-medium'}">
            {wsConnected ? 'STREAMING 20Hz' : 'DISCONNECTED'}
          </span>
        </div>

        <!-- Airspace Sector -->
        <div class="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-secondary border border-border text-muted-foreground">
          <span class="text-muted-foreground">SECTOR:</span>
          <span class="text-foreground font-medium">JAKARTA TMA (FIR)</span>
        </div>

        <!-- UTC Clock -->
        <div class="hidden md:block font-mono text-foreground font-semibold px-2.5 py-1 bg-secondary rounded-md border border-border">
          {currentTime}
        </div>

        <!-- Working Theme Switcher -->
        <ThemeToggle />
      </div>
    </div>
  </header>

  <!-- Error Reconnect Banner (R-27 Error State) -->
  {#if errorMessage}
    <div class="bg-destructive/15 border-b border-destructive/25 text-destructive text-xs font-mono px-4 py-2 text-center" role="alert">
      {errorMessage}
    </div>
  {/if}

  <!-- Main Cockpit Viewport -->
  <main class="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 space-y-5">
    
    {#if isLoading && drones.length === 0}
      <!-- Loading Skeleton (R-27 Loading State) -->
      <div class="space-y-4">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          {#each Array(4) as _}
            <div class="h-24 rounded-xl bg-muted/60 animate-pulse border border-border"></div>
          {/each}
        </div>
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
          <div class="lg:col-span-2 h-[500px] rounded-xl bg-muted/60 animate-pulse border border-border"></div>
          <div class="lg:col-span-1 h-[500px] rounded-xl bg-muted/60 animate-pulse border border-border"></div>
        </div>
      </div>
    {:else}
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
    {/if}

  </main>

  <!-- Cockpit Footer -->
  <footer class="border-t border-border py-4 text-center text-xs font-mono text-muted-foreground">
    SkyPulse v1.1.0: Autonomous Flight Control & Telemetry System
  </footer>
</div>
