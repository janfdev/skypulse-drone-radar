<script lang="ts">
  import type { DroneTelemetry } from '../types';

  let { 
    drones, 
    selectedDroneId, 
    onSelectDrone 
  }: {
    drones: DroneTelemetry[];
    selectedDroneId: string | null;
    onSelectDrone: (id: string) => void;
  } = $props();
</script>

<div class="rounded-2xl border border-slate-800 bg-slate-900/50 backdrop-blur overflow-hidden">
  <div class="px-4 py-3 border-b border-slate-800 flex items-center justify-between">
    <div class="flex items-center gap-2">
      <span class="text-xs font-mono font-bold text-slate-200">ACTIVE FLEET TELEMETRY DIRECTORY</span>
      <span class="text-[11px] font-mono text-cyan-400 bg-cyan-950/80 px-2 py-0.5 rounded border border-cyan-800/80">
        {drones.length} UNITS
      </span>
    </div>
    <span class="text-[10px] font-mono text-slate-500">SORTED BY CALLSIGN</span>
  </div>

  <div class="overflow-x-auto">
    <table class="w-full text-left font-mono text-xs">
      <thead>
        <tr class="border-b border-slate-800/80 text-[11px] text-slate-400 bg-slate-950/40">
          <th class="py-2.5 px-3">CALLSIGN / ID</th>
          <th class="py-2.5 px-3">STATUS</th>
          <th class="py-2.5 px-3">BATTERY</th>
          <th class="py-2.5 px-3">ALTITUDE</th>
          <th class="py-2.5 px-3">SPEED</th>
          <th class="py-2.5 px-3">HEADING</th>
          <th class="py-2.5 px-3">NEAREST GEOFENCE</th>
          <th class="py-2.5 px-3 text-right">ACTION</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-slate-800/50">
        {#each drones as drone}
          {@const isSelected = drone.drone_id === selectedDroneId}
          <tr 
            class="transition-colors cursor-pointer {
              isSelected ? 'bg-cyan-950/30 text-cyan-100 font-bold' : 
              drone.geofence_warning ? 'bg-red-950/20 hover:bg-red-950/30' : 
              'hover:bg-slate-800/30 text-slate-300'
            }"
            onclick={() => onSelectDrone(drone.drone_id)}
          >
            <!-- Drone Callsign -->
            <td class="py-2.5 px-3 whitespace-nowrap">
              <div class="flex items-center gap-2">
                <span class="size-1.5 rounded-full {drone.geofence_warning ? 'bg-red-500 animate-ping' : isSelected ? 'bg-cyan-400' : 'bg-emerald-400'}"></span>
                <span>{drone.callsign}</span>
                <span class="text-[10px] text-slate-500">({drone.drone_id})</span>
              </div>
            </td>

            <!-- Mode -->
            <td class="py-2.5 px-3 whitespace-nowrap">
              <span class="px-2 py-0.5 rounded text-[10px] font-bold {
                drone.flight_mode === 'RETURNING_HOME' ? 'bg-amber-950 text-amber-400 border border-amber-800' :
                drone.flight_mode === 'HOVER' ? 'bg-purple-950 text-purple-400 border border-purple-800' :
                drone.flight_mode === 'COLLISION_AVOIDANCE' ? 'bg-red-950 text-red-400 border border-red-800' :
                'bg-emerald-950 text-emerald-400 border border-emerald-800'
              }">
                {drone.flight_mode}
              </span>
            </td>

            <!-- Battery -->
            <td class="py-2.5 px-3 whitespace-nowrap">
              <div class="flex items-center gap-2">
                <div class="w-12 bg-slate-800 h-1.5 rounded-full overflow-hidden">
                  <div 
                    class="h-full rounded-full {drone.battery_pct < 25 ? 'bg-red-500' : 'bg-cyan-400'}"
                    style="width: {drone.battery_pct}%;"
                  ></div>
                </div>
                <span class="{drone.battery_pct < 25 ? 'text-red-400 font-bold' : ''}">{drone.battery_pct}%</span>
              </div>
            </td>

            <!-- Altitude -->
            <td class="py-2.5 px-3 whitespace-nowrap">
              {Math.round(drone.coords.alt_m)} m
            </td>

            <!-- Speed -->
            <td class="py-2.5 px-3 whitespace-nowrap">
              {drone.speed_mps} m/s
            </td>

            <!-- Heading -->
            <td class="py-2.5 px-3 whitespace-nowrap text-cyan-400">
              {drone.heading_deg}°
            </td>

            <!-- Geofence -->
            <td class="py-2.5 px-3 whitespace-nowrap">
              {#if drone.geofence_warning}
                <span class="text-red-400 font-bold flex items-center gap-1">
                  ⚠️ {drone.nearest_no_fly_zone?.slice(0, 18)}...
                </span>
              {:else}
                <span class="text-slate-500">
                  {drone.nearest_no_fly_zone ? `${drone.nearest_no_fly_zone.slice(0, 16)}...` : 'Safe Corridor'}
                </span>
              {/if}
            </td>

            <!-- Action -->
            <td class="py-2.5 px-3 whitespace-nowrap text-right">
              <button 
                class="px-2 py-1 rounded text-[10px] {isSelected ? 'bg-cyan-500 text-slate-950 font-bold' : 'bg-slate-800 hover:bg-slate-700 text-slate-300'}"
                onclick={(e) => {
                  e.stopPropagation();
                  onSelectDrone(drone.drone_id);
                }}
              >
                {isSelected ? 'TRACKING' : 'INSPECT'}
              </button>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</div>
