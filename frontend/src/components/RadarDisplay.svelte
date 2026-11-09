<script lang="ts">
  import type { DroneTelemetry, NoFlyZone } from '../types';

  // Svelte 5 Props using $props rune
  let { 
    drones = [], 
    geofences = [], 
    selectedDroneId = null,
    onSelectDrone
  }: {
    drones: DroneTelemetry[];
    geofences: NoFlyZone[];
    selectedDroneId: string | null;
    onSelectDrone: (id: string) => void;
  } = $props();

  // Radar Center (Monas / Central Jakarta): lat: -6.185, lng: 106.82
  const CENTER_LAT = -6.195;
  const CENTER_LNG = 106.815;
  const RADAR_SPAN_DEG = 0.22; // ~24 km radius

  // Convert GPS Coordinates to SVG Viewport (0..600)
  function gpsToSvg(lat: number, lng: number): { x: number; y: number } {
    const x = 300 + ((lng - CENTER_LNG) / RADAR_SPAN_DEG) * 260;
    const y = 300 - ((lat - CENTER_LAT) / RADAR_SPAN_DEG) * 260;
    return { x: Math.max(20, Math.min(580, x)), y: Math.max(20, Math.min(580, y)) };
  }
</script>

<div class="relative w-full aspect-square max-w-[640px] mx-auto rounded-2xl border border-slate-800 bg-[#070b14] overflow-hidden shadow-2xl flex items-center justify-center select-none radar-grid">
  
  <!-- Sweeping Radar Line -->
  <div class="absolute inset-0 pointer-events-none flex items-center justify-center">
    <div class="w-[560px] h-[560px] rounded-full border border-cyan-500/20 relative">
      <div class="absolute inset-0 rounded-full radar-sweep" style="background: conic-gradient(from 0deg, rgba(0, 242, 254, 0.25) 0deg, rgba(0, 242, 254, 0) 60deg);"></div>
    </div>
  </div>

  <svg viewBox="0 0 600 600" class="w-full h-full relative z-10">
    <defs>
      <!-- Glow filter -->
      <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur stdDeviation="3" result="blur" />
        <feComposite in="SourceGraphic" in2="blur" operator="over" />
      </filter>
      <filter id="alertGlow" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur stdDeviation="4" result="blur" />
        <feComposite in="SourceGraphic" in2="blur" operator="over" />
      </filter>
    </defs>

    <!-- Radar Range Rings -->
    <circle cx="300" cy="300" r="260" fill="none" stroke="#1e293b" stroke-width="1.5" stroke-dasharray="4 4" />
    <circle cx="300" cy="300" r="180" fill="none" stroke="#1e293b" stroke-width="1.5" />
    <circle cx="300" cy="300" r="100" fill="none" stroke="#1e293b" stroke-width="1.5" stroke-dasharray="2 2" />
    <circle cx="300" cy="300" r="20" fill="none" stroke="#00f2fe" stroke-opacity="0.4" stroke-width="1" />

    <!-- Crosshairs & Cardinal Labels -->
    <line x1="300" y1="40" x2="300" y2="560" stroke="#1e293b" stroke-width="1" />
    <line x1="40" y1="300" x2="560" y2="300" stroke="#1e293b" stroke-width="1" />
    <text x="300" y="32" text-anchor="middle" fill="#64748b" font-size="11" font-weight="bold" font-family="monospace">000° N</text>
    <text x="300" y="582" text-anchor="middle" fill="#64748b" font-size="11" font-weight="bold" font-family="monospace">180° S</text>
    <text x="25" y="304" text-anchor="middle" fill="#64748b" font-size="11" font-weight="bold" font-family="monospace">270° W</text>
    <text x="575" y="304" text-anchor="middle" fill="#64748b" font-size="11" font-weight="bold" font-family="monospace">090° E</text>

    <!-- Range Annotations -->
    <text x="306" y="205" fill="#475569" font-size="10" font-family="monospace">10 KM</text>
    <text x="306" y="125" fill="#475569" font-size="10" font-family="monospace">20 KM</text>
    <text x="306" y="48" fill="#475569" font-size="10" font-family="monospace">30 KM</text>

    <!-- No-Fly Zones (Restricted Airspaces) -->
    {#each geofences as nfz}
      {@const pt = gpsToSvg(nfz.center_lat, nfz.center_lng)}
      {@const radiusPx = (nfz.radius_meters / 1000) * (260 / 30)}
      <g class="cursor-help">
        <circle 
          cx={pt.x} 
          cy={pt.y} 
          r={radiusPx} 
          fill="rgba(239, 68, 68, 0.12)" 
          stroke="#ef4444" 
          stroke-width="1.5" 
          stroke-dasharray="3 3"
        />
        <text 
          x={pt.x} 
          y={pt.y + 3} 
          text-anchor="middle" 
          fill="#f87171" 
          font-size="9" 
          font-family="monospace" 
          font-weight="bold"
        >
          {nfz.id}
        </text>
      </g>
    {/each}

    <!-- Active Drones -->
    {#each drones as drone}
      {@const pt = gpsToSvg(drone.coords.lat, drone.coords.lng)}
      {@const isSelected = drone.drone_id === selectedDroneId}
      {@const isWarning = drone.geofence_warning || drone.battery_pct < 25}

      <!-- Drone Target Element with Click Handler -->
      <!-- svelte-ignore a11y_click_events_have_key_events -->
      <!-- svelte-ignore a11y_no_static_element_interactions -->
      <g 
        class="cursor-pointer transition-all duration-300"
        onclick={() => onSelectDrone(drone.drone_id)}
      >
        <!-- Selection ring -->
        {#if isSelected}
          <circle 
            cx={pt.x} 
            cy={pt.y} 
            r="18" 
            fill="none" 
            stroke="#00f2fe" 
            stroke-width="2" 
            stroke-dasharray="2 2"
            class="animate-spin"
            style="transform-origin: {pt.x}px {pt.y}px;"
          />
        {/if}

        <!-- Warning Pulsing Halo -->
        {#if isWarning}
          <circle 
            cx={pt.x} 
            cy={pt.y} 
            r="14" 
            fill="none" 
            stroke="#ef4444" 
            stroke-width="1.5" 
            class="animate-ping opacity-75"
          />
        {/if}

        <!-- Drone Symbol Oriented by Heading -->
        <g transform="translate({pt.x}, {pt.y}) rotate({drone.heading_deg})">
          <!-- Direction Arrow -->
          <polygon 
            points="0,-8 6,6 0,3 -6,6" 
            fill={isWarning ? '#ef4444' : isSelected ? '#00f2fe' : '#38bdf8'} 
            filter="url(#glow)"
          />
        </g>

        <!-- Drone Callsign Label -->
        <text 
          x={pt.x + 10} 
          y={pt.y + 4} 
          fill={isSelected ? '#00f2fe' : '#e2e8f0'} 
          font-size="10" 
          font-weight={isSelected ? 'bold' : 'normal'}
          font-family="monospace"
        >
          {drone.callsign}
        </text>

        <!-- Small Altitude & Mode -->
        <text 
          x={pt.x + 10} 
          y={pt.y + 15} 
          fill={isWarning ? '#f87171' : '#64748b'} 
          font-size="8" 
          font-family="monospace"
        >
          {Math.round(drone.coords.alt_m)}m · {drone.flight_mode}
        </text>
      </g>
    {/each}
  </svg>

  <!-- Live Status Overlay -->
  <div class="absolute bottom-3 left-3 text-[10px] font-mono text-slate-400 bg-slate-900/80 px-2.5 py-1 rounded-md border border-slate-800 backdrop-blur-sm pointer-events-none">
    RADAR RANGE: 30 KM · MODE: HIGH-FREQ 20Hz
  </div>
</div>
