<script lang="ts">
  import type { DroneTelemetry, NoFlyZone } from '../types';
  import Card from './ui/card/Card.svelte';
  import CardHeader from './ui/card/CardHeader.svelte';
  import CardTitle from './ui/card/CardTitle.svelte';
  import CardDescription from './ui/card/CardDescription.svelte';
  import Badge from './ui/badge/Badge.svelte';

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

  // Radar Center (Central Jakarta): lat: -6.195, lng: 106.815
  const CENTER_LAT = -6.195;
  const CENTER_LNG = 106.815;
  let rangeKm = $state<number>(30);

  // $derived scale factor based on selected range
  let radarSpanDeg = $derived((rangeKm / 30) * 0.22);

  // Convert GPS Coordinates to SVG Viewport (bounds 0..600, safe content 50..550)
  function gpsToSvg(lat: number, lng: number): { x: number; y: number } {
    const x = 300 + ((lng - CENTER_LNG) / radarSpanDeg) * 225;
    const y = 300 - ((lat - CENTER_LAT) / radarSpanDeg) * 225;
    return { x: Math.max(55, Math.min(535, x)), y: Math.max(55, Math.min(535, y)) };
  }
</script>

<Card class="overflow-hidden">
  <CardHeader class="p-4 border-b border-[var(--border)] flex flex-row items-center justify-between">
    <div>
      <div class="flex items-center gap-2">
        <CardTitle class="text-sm font-semibold">
          Tactical Airspace Radar
        </CardTitle>
        <Badge variant="outline" class="text-[10px] font-mono px-1.5 py-0">
          PPI SCOPE
        </Badge>
      </div>
      <CardDescription class="text-xs mt-0.5">
        Plan Position Indicator with 20Hz real-time telemetry sweep
      </CardDescription>
    </div>

    <!-- Range Selector Controls -->
    <div class="flex items-center gap-1 bg-secondary rounded-lg p-1 border border-border">
      <button 
        type="button"
        onclick={() => rangeKm = 15}
        class="px-2 py-0.5 text-xs font-mono rounded transition-colors {rangeKm === 15 ? 'bg-background text-foreground shadow-sm font-bold' : 'text-muted-foreground hover:text-foreground'}"
      >
        15 KM
      </button>
      <button 
        type="button"
        onclick={() => rangeKm = 30}
        class="px-2 py-0.5 text-xs font-mono rounded transition-colors {rangeKm === 30 ? 'bg-background text-foreground shadow-sm font-bold' : 'text-muted-foreground hover:text-foreground'}"
      >
        30 KM
      </button>
      <button 
        type="button"
        onclick={() => rangeKm = 50}
        class="px-2 py-0.5 text-xs font-mono rounded transition-colors {rangeKm === 50 ? 'bg-background text-foreground shadow-sm font-bold' : 'text-muted-foreground hover:text-foreground'}"
      >
        50 KM
      </button>
    </div>
  </CardHeader>

  <!-- Canvas Container with proper themed background -->
  <div class="p-4">
    <div class="relative w-full aspect-square max-w-[580px] mx-auto rounded-xl border border-[var(--border)] bg-[var(--radar-bg)] overflow-hidden shadow-inner flex items-center justify-center select-none">
      
      <!-- Sweeping Radar Line -->
      <div class="absolute inset-0 pointer-events-none flex items-center justify-center">
        <div class="w-[470px] h-[470px] rounded-full border border-primary/20 relative">
          <div class="absolute inset-0 rounded-full radar-sweep" style="background: conic-gradient(from 0deg, rgba(2, 132, 199, 0.25) 0deg, rgba(2, 132, 199, 0) 60deg);"></div>
        </div>
      </div>

      <svg viewBox="0 0 600 600" class="w-full h-full relative z-10" aria-label="Tactical polar radar scope">
        <defs>
          <filter id="radarGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="2.5" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        <!-- Range Rings -->
        <circle cx="300" cy="300" r="235" fill="none" stroke="currentColor" class="text-slate-300 dark:text-slate-800" stroke-width="1.5" stroke-dasharray="4 4" />
        <circle cx="300" cy="300" r="160" fill="none" stroke="currentColor" class="text-slate-300 dark:text-slate-800" stroke-width="1.5" />
        <circle cx="300" cy="300" r="85" fill="none" stroke="currentColor" class="text-slate-300 dark:text-slate-800" stroke-width="1.5" stroke-dasharray="2 2" />
        <circle cx="300" cy="300" r="18" fill="none" stroke="currentColor" class="text-primary/60" stroke-width="1.2" />

        <!-- Crosshairs & Cardinal Headings -->
        <line x1="300" y1="45" x2="300" y2="555" stroke="currentColor" class="text-slate-300 dark:text-slate-800" stroke-width="1" />
        <line x1="45" y1="300" x2="555" y2="300" stroke="currentColor" class="text-slate-300 dark:text-slate-800" stroke-width="1" />
        
        <text x="300" y="32" text-anchor="middle" class="fill-slate-500 dark:fill-slate-400" font-size="11" font-weight="bold" font-family="monospace">000° N</text>
        <text x="300" y="582" text-anchor="middle" class="fill-slate-500 dark:fill-slate-400" font-size="11" font-weight="bold" font-family="monospace">180° S</text>
        <text x="25" y="304" text-anchor="middle" class="fill-slate-500 dark:fill-slate-400" font-size="11" font-weight="bold" font-family="monospace">270° W</text>
        <text x="575" y="304" text-anchor="middle" class="fill-slate-500 dark:fill-slate-400" font-size="11" font-weight="bold" font-family="monospace">090° E</text>

        <!-- Range Distance Annotations -->
        <text x="306" y="195" class="fill-slate-700 dark:fill-slate-400 font-semibold" font-size="10" font-family="monospace">{Math.round(rangeKm * 0.33)} KM</text>
        <text x="306" y="120" class="fill-slate-700 dark:fill-slate-400 font-semibold" font-size="10" font-family="monospace">{Math.round(rangeKm * 0.67)} KM</text>
        <text x="306" y="45" class="fill-slate-700 dark:fill-slate-400 font-semibold" font-size="10" font-family="monospace">{rangeKm} KM</text>

        <!-- No-Fly Exclusion Zones -->
        {#each geofences as nfz}
          {@const pt = gpsToSvg(nfz.center_lat, nfz.center_lng)}
          {@const radiusPx = (nfz.radius_meters / 1000) * (235 / rangeKm)}
          <g class="cursor-help">
            <circle 
              cx={pt.x} 
              cy={pt.y} 
              r={Math.max(6, radiusPx)} 
              fill="rgba(220, 38, 38, 0.12)" 
              stroke="#ef4444" 
              stroke-width="1.5" 
              stroke-dasharray="3 3"
            />
            <text 
              x={pt.x} 
              y={pt.y + 3} 
              text-anchor="middle" 
              fill="#ef4444" 
              font-size="8.5" 
              font-family="monospace" 
              font-weight="bold"
            >
              {nfz.id}
            </text>
          </g>
        {/each}

        <!-- Active Drones in Flight -->
        {#each drones as drone}
          {@const pt = gpsToSvg(drone.coords.lat, drone.coords.lng)}
          {@const isSelected = drone.drone_id === selectedDroneId}
          {@const isWarning = drone.geofence_warning || drone.battery_pct < 25}

          <!-- Keyboard accessible target -->
          <g 
            role="button"
            tabindex="0"
            aria-label="Inspect drone {drone.callsign} ({drone.drone_id})"
            class="cursor-pointer transition-all duration-200 focus:outline-none"
            onclick={() => onSelectDrone(drone.drone_id)}
            onkeydown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                onSelectDrone(drone.drone_id);
              }
            }}
          >
            <!-- Selection Reticle -->
            {#if isSelected}
              <circle 
                cx={pt.x} 
                cy={pt.y} 
                r="16" 
                fill="none" 
                stroke="currentColor" 
                class="text-primary animate-spin"
                stroke-width="2" 
                stroke-dasharray="3 3"
                style="transform-origin: {pt.x}px {pt.y}px;"
              />
            {/if}

            <!-- Warning Ring -->
            {#if isWarning}
              <circle 
                cx={pt.x} 
                cy={pt.y} 
                r="12" 
                fill="none" 
                stroke="#ef4444" 
                stroke-width="1.5" 
                class="opacity-75"
              />
            {/if}

            <!-- Heading Vector Pointer -->
            <g transform="translate({pt.x}, {pt.y}) rotate({drone.heading_deg})">
              <polygon 
                points="0,-7 5,5 0,2 -5,5" 
                fill={isWarning ? '#ef4444' : isSelected ? '#0284c7' : '#0ea5e9'} 
                filter="url(#radarGlow)"
              />
            </g>

            <!-- Callsign Tag -->
            <text 
              x={pt.x + 8} 
              y={pt.y + 3} 
              class="{isSelected ? 'fill-primary font-bold' : 'fill-slate-900 dark:fill-slate-100 font-semibold'}" 
              font-size="10" 
              font-family="monospace"
            >
              {drone.callsign}
            </text>

            <!-- Small Status -->
            <text 
              x={pt.x + 8} 
              y={pt.y + 13} 
              class="{isWarning ? 'fill-destructive font-bold' : 'fill-slate-600 dark:fill-slate-400 font-medium'}" 
              font-size="8.5" 
              font-family="monospace"
            >
              {Math.round(drone.coords.alt_m)}m · {drone.flight_mode}
            </text>
          </g>
        {/each}
      </svg>

      <!-- Scope HUD Tag -->
      <div class="absolute bottom-3 left-3 text-[10px] font-mono text-muted-foreground bg-background/90 px-2 py-0.5 rounded border border-border backdrop-blur-sm pointer-events-none">
        SWEEP: 20Hz · COVERAGE: {rangeKm} KM
      </div>
    </div>
  </div>
</Card>
