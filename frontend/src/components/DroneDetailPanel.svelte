<script lang="ts">
  import type { DroneTelemetry } from '../types';

  let { 
    drone, 
    onSendCommand 
  }: { 
    drone: DroneTelemetry | null;
    onSendCommand: (droneId: string, command: string) => Promise<void>;
  } = $props();

  let loadingCmd = $state<string | null>(null);

  async function handleCmd(cmd: string) {
    if (!drone) return;
    loadingCmd = cmd;
    try {
      await onSendCommand(drone.drone_id, cmd);
    } finally {
      loadingCmd = null;
    }
  }
</script>

<div class="h-full rounded-2xl bg-slate-900/50 border border-slate-800 p-4 flex flex-col justify-between backdrop-blur">
  {#if drone}
    <div class="space-y-4">
      <!-- Header -->
      <div class="flex items-start justify-between border-b border-slate-800 pb-3">
        <div>
          <div class="flex items-center gap-2">
            <span class="text-xs font-mono font-bold text-cyan-400 bg-cyan-950/60 border border-cyan-800 px-2 py-0.5 rounded">
              {drone.drone_id}
            </span>
            <span class="text-sm font-bold text-slate-100">{drone.callsign}</span>
          </div>
          <div class="text-[11px] font-mono text-slate-400 mt-1">{drone.model}</div>
        </div>

        <!-- Flight Mode Badge -->
        <span class="px-2.5 py-1 rounded-full text-[11px] font-mono font-bold {
          drone.flight_mode === 'RETURNING_HOME' ? 'bg-amber-950 text-amber-400 border border-amber-800' :
          drone.flight_mode === 'HOVER' ? 'bg-purple-950 text-purple-400 border border-purple-800' :
          drone.flight_mode === 'COLLISION_AVOIDANCE' ? 'bg-red-950 text-red-400 border border-red-800' :
          'bg-emerald-950 text-emerald-400 border border-emerald-800'
        }">
          {drone.flight_mode}
        </span>
      </div>

      <!-- Tactical Metrics Grid -->
      <div class="grid grid-cols-2 gap-2 text-xs font-mono">
        <div class="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/80">
          <div class="text-slate-500">ALTITUDE AGL</div>
          <div class="text-base font-bold text-slate-200 mt-0.5">{Math.round(drone.coords.alt_m)} m</div>
          <div class="text-[10px] text-slate-500">~{Math.round(drone.coords.alt_m * 3.28)} ft</div>
        </div>

        <div class="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/80">
          <div class="text-slate-500">GROUND SPEED</div>
          <div class="text-base font-bold text-slate-200 mt-0.5">{drone.speed_mps} m/s</div>
          <div class="text-[10px] text-slate-500">~{Math.round(drone.speed_mps * 3.6)} km/h</div>
        </div>

        <div class="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/80">
          <div class="text-slate-500">HEADING AZIMUTH</div>
          <div class="text-base font-bold text-cyan-400 mt-0.5">{drone.heading_deg}°</div>
          <div class="text-[10px] text-slate-500">MAG TRUE</div>
        </div>

        <div class="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/80">
          <div class="text-slate-500">SIGNAL LINK (RSSI)</div>
          <div class="text-base font-bold text-slate-200 mt-0.5">{drone.signal_rssi_dbm} dBm</div>
          <div class="text-[10px] text-emerald-400">99.8% LINK QTY</div>
        </div>
      </div>

      <!-- Battery SoC Section -->
      <div class="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80">
        <div class="flex items-center justify-between text-xs font-mono mb-1.5">
          <span class="text-slate-400">PROPULSION BATTERY</span>
          <span class="font-bold {drone.battery_pct < 25 ? 'text-red-400' : 'text-slate-200'}">
            {drone.battery_pct}%
          </span>
        </div>
        <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
          <div 
            class="h-full rounded-full transition-all duration-300 {
              drone.battery_pct < 20 ? 'bg-red-500' :
              drone.battery_pct < 45 ? 'bg-amber-400' :
              'bg-emerald-400'
            }"
            style="width: {drone.battery_pct}%;"
          ></div>
        </div>
      </div>

      <!-- Geofence & Proximity Monitor -->
      <div class="p-3 rounded-lg border {drone.geofence_warning ? 'bg-red-950/30 border-red-800/80' : 'bg-slate-950/60 border-slate-800/80'}">
        <div class="flex items-center justify-between text-xs font-mono">
          <span class="{drone.geofence_warning ? 'text-red-400 font-bold' : 'text-slate-400'}">
            AIRSPACE PROXIMITY
          </span>
          {#if drone.geofence_warning}
            <span class="text-[10px] bg-red-900/60 text-red-300 px-1.5 py-0.5 rounded border border-red-700 animate-pulse">
              RESTRICTED
            </span>
          {:else}
            <span class="text-[10px] text-emerald-400">SAFE CORRIDOR</span>
          {/if}
        </div>
        <div class="mt-1.5 text-xs font-mono text-slate-300">
          {drone.nearest_no_fly_zone ?? 'No active restriction nearby'}
        </div>
        {#if drone.distance_to_nfz_m}
          <div class="text-[11px] font-mono text-slate-500 mt-0.5">
            Range: <span class="text-slate-300 font-bold">{Math.round(drone.distance_to_nfz_m)} m</span> to perimeter
          </div>
        {/if}
      </div>

      <!-- GPS Coordinates -->
      <div class="text-[10px] font-mono text-slate-500 flex justify-between px-1">
        <span>LAT: {drone.coords.lat.toFixed(5)}</span>
        <span>LNG: {drone.coords.lng.toFixed(5)}</span>
      </div>
    </div>

    <!-- Mission Control Action Buttons -->
    <div class="pt-4 border-t border-slate-800 space-y-2">
      <div class="text-[11px] font-mono text-slate-400 uppercase tracking-wider">
        Tactical Command Strip
      </div>
      <div class="grid grid-cols-2 gap-2">
        <button 
          onclick={() => handleCmd('RTH')}
          disabled={loadingCmd !== null}
          class="px-3 py-2 rounded-lg bg-amber-950/60 hover:bg-amber-900/80 border border-amber-800 text-amber-200 text-xs font-mono font-bold transition flex items-center justify-center gap-1.5 disabled:opacity-50"
        >
          <span>🏠</span> RTH (HOME)
        </button>

        <button 
          onclick={() => handleCmd('HOLD')}
          disabled={loadingCmd !== null}
          class="px-3 py-2 rounded-lg bg-purple-950/60 hover:bg-purple-900/80 border border-purple-800 text-purple-200 text-xs font-mono font-bold transition flex items-center justify-center gap-1.5 disabled:opacity-50"
        >
          <span>⏸️</span> HOLD HOVER
        </button>

        <button 
          onclick={() => handleCmd('RESUME')}
          disabled={loadingCmd !== null}
          class="px-3 py-2 rounded-lg bg-emerald-950/60 hover:bg-emerald-900/80 border border-emerald-800 text-emerald-200 text-xs font-mono font-bold transition flex items-center justify-center gap-1.5 disabled:opacity-50"
        >
          <span>▶️</span> RESUME
        </button>

        <button 
          onclick={() => handleCmd('DIVERT')}
          disabled={loadingCmd !== null}
          class="px-3 py-2 rounded-lg bg-cyan-950/60 hover:bg-cyan-900/80 border border-cyan-800 text-cyan-200 text-xs font-mono font-bold transition flex items-center justify-center gap-1.5 disabled:opacity-50"
        >
          <span>⚠️</span> DIVERT +90°
        </button>
      </div>
    </div>
  {:else}
    <div class="h-full flex flex-col items-center justify-center text-center text-slate-500 font-mono text-xs">
      <span class="text-2xl mb-2">🎯</span>
      <span>SELECT A DRONE ON THE RADAR OR FLEET TABLE</span>
    </div>
  {/if}
</div>
