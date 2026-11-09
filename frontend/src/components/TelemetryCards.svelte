<script lang="ts">
  import type { FleetStats } from '../types';

  let { stats }: { stats: FleetStats | null } = $props();
</script>

<div class="grid grid-cols-2 md:grid-cols-4 gap-3">
  <!-- Card 1: Active Drones -->
  <div class="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 backdrop-blur flex flex-col justify-between">
    <div class="flex items-center justify-between text-xs font-mono text-slate-400">
      <span>AIRBORNE FLEET</span>
      <span class="flex h-2 w-2 relative">
        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
        <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
      </span>
    </div>
    <div class="mt-2 flex items-baseline gap-2">
      <span class="text-2xl font-bold font-mono text-slate-100">{stats?.active_airborne ?? 0}</span>
      <span class="text-xs font-mono text-slate-500">/ {stats?.total_drones ?? 0} ACTIVE</span>
    </div>
    <div class="mt-1 text-[11px] font-mono text-emerald-400">
      100% TELEMETRY LOCK
    </div>
  </div>

  <!-- Card 2: Alerts & Geofences -->
  <div class="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 backdrop-blur flex flex-col justify-between">
    <div class="flex items-center justify-between text-xs font-mono text-slate-400">
      <span>GEOFENCE ALERTS</span>
      {#if (stats?.alerts_count ?? 0) > 0}
        <span class="px-1.5 py-0.5 rounded text-[10px] bg-red-950/80 text-red-400 border border-red-800 font-bold animate-pulse">
          WARNING
        </span>
      {:else}
        <span class="px-1.5 py-0.5 rounded text-[10px] bg-emerald-950/80 text-emerald-400 border border-emerald-800">
          CLEAR
        </span>
      {/if}
    </div>
    <div class="mt-2 flex items-baseline gap-2">
      <span class="text-2xl font-bold font-mono {(stats?.alerts_count ?? 0) > 0 ? 'text-red-400' : 'text-slate-100'}">
        {stats?.alerts_count ?? 0}
      </span>
      <span class="text-xs font-mono text-slate-500">ZONES FLAGGED</span>
    </div>
    <div class="mt-1 text-[11px] font-mono text-slate-400">
      {(stats?.alerts_count ?? 0) > 0 ? 'COLLISION AVOIDANCE ARMED' : 'NO ACTIVE INTRUSIONS'}
    </div>
  </div>

  <!-- Card 3: Avg Fleet Battery -->
  <div class="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 backdrop-blur flex flex-col justify-between">
    <div class="flex items-center justify-between text-xs font-mono text-slate-400">
      <span>FLEET ENERGY</span>
      <span class="text-[11px] font-mono text-cyan-400">LiPo HV</span>
    </div>
    <div class="mt-2 flex items-baseline gap-2">
      <span class="text-2xl font-bold font-mono text-slate-100">{stats?.avg_battery_pct ?? 0}%</span>
      <span class="text-xs font-mono text-slate-500">AVG SOC</span>
    </div>
    <!-- Battery Bar -->
    <div class="mt-2 w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
      <div 
        class="h-full rounded-full transition-all duration-500 {(stats?.avg_battery_pct ?? 0) < 30 ? 'bg-red-500' : (stats?.avg_battery_pct ?? 0) < 50 ? 'bg-amber-400' : 'bg-cyan-400'}"
        style="width: {stats?.avg_battery_pct ?? 0}%;"
      ></div>
    </div>
  </div>

  <!-- Card 4: Avg Speed -->
  <div class="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 backdrop-blur flex flex-col justify-between">
    <div class="flex items-center justify-between text-xs font-mono text-slate-400">
      <span>CRUISING VELOCITY</span>
      <span class="text-[11px] font-mono text-slate-500">GPS SPD</span>
    </div>
    <div class="mt-2 flex items-baseline gap-2">
      <span class="text-2xl font-bold font-mono text-slate-100">{stats?.avg_speed_mps ?? 0}</span>
      <span class="text-xs font-mono text-slate-500">M/S (~{Math.round((stats?.avg_speed_mps ?? 0) * 3.6)} KM/H)</span>
    </div>
    <div class="mt-1 text-[11px] font-mono text-slate-400">
      AIRSPACE DENSITY: NOMINAL
    </div>
  </div>
</div>
