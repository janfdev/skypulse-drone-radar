<script lang="ts">
  import type { FleetStats } from '../types';
  import Card from './ui/card/Card.svelte';
  import CardHeader from './ui/card/CardHeader.svelte';
  import CardTitle from './ui/card/CardTitle.svelte';
  import CardContent from './ui/card/CardContent.svelte';
  import Badge from './ui/badge/Badge.svelte';

  let { stats }: { stats: FleetStats | null } = $props();
</script>

<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
  <!-- Card 1: Active Drones -->
  <Card class="transition-shadow hover:shadow-md">
    <CardHeader class="p-4 pb-2 flex flex-row items-center justify-between space-y-0">
      <CardTitle class="text-xs font-mono uppercase tracking-wider text-slate-600 dark:text-slate-400">
        Airborne Units
      </CardTitle>
      <Badge variant="success" class="text-[10px] font-mono px-1.5 py-0">
        ONLINE
      </Badge>
    </CardHeader>
    <CardContent class="p-4 pt-1">
      <div class="flex items-baseline gap-2">
        <span class="text-2xl font-bold font-mono tracking-tight text-slate-900 dark:text-slate-100">
          {stats?.active_airborne ?? 0}
        </span>
        <span class="text-xs font-mono text-slate-500">
          / {stats?.total_drones ?? 0} active
        </span>
      </div>
      <p class="text-[11px] font-mono text-emerald-600 dark:text-emerald-400 mt-1">
        100% telemetry link lock
      </p>
    </CardContent>
  </Card>

  <!-- Card 2: Alerts & Geofences -->
  <Card class="transition-shadow hover:shadow-md">
    <CardHeader class="p-4 pb-2 flex flex-row items-center justify-between space-y-0">
      <CardTitle class="text-xs font-mono uppercase tracking-wider text-slate-600 dark:text-slate-400">
        Airspace Alerts
      </CardTitle>
      {#if (stats?.alerts_count ?? 0) > 0}
        <Badge variant="destructive" class="text-[10px] font-mono px-1.5 py-0">
          RESTRICTED
        </Badge>
      {:else}
        <Badge variant="outline" class="text-[10px] font-mono px-1.5 py-0 text-emerald-600 dark:text-emerald-400">
          CLEAR
        </Badge>
      {/if}
    </CardHeader>
    <CardContent class="p-4 pt-1">
      <div class="flex items-baseline gap-2">
        <span class="text-2xl font-bold font-mono tracking-tight {(stats?.alerts_count ?? 0) > 0 ? 'text-destructive' : 'text-slate-900 dark:text-slate-100'}">
          {stats?.alerts_count ?? 0}
        </span>
        <span class="text-xs font-mono text-slate-500">
          zones flagged
        </span>
      </div>
      <p class="text-[11px] font-mono text-slate-500 dark:text-slate-400 mt-1">
        {(stats?.alerts_count ?? 0) > 0 ? 'Collision avoidance ready' : 'No boundary intrusions'}
      </p>
    </CardContent>
  </Card>

  <!-- Card 3: Avg Fleet Battery -->
  <Card class="transition-shadow hover:shadow-md">
    <CardHeader class="p-4 pb-2 flex flex-row items-center justify-between space-y-0">
      <CardTitle class="text-xs font-mono uppercase tracking-wider text-slate-600 dark:text-slate-400">
        Battery State
      </CardTitle>
      <span class="text-[11px] font-mono text-cyan-600 dark:text-cyan-400">LiPo HV</span>
    </CardHeader>
    <CardContent class="p-4 pt-1">
      <div class="flex items-baseline gap-2">
        <span class="text-2xl font-bold font-mono tracking-tight text-slate-900 dark:text-slate-100">
          {stats?.avg_battery_pct ?? 0}%
        </span>
        <span class="text-xs font-mono text-slate-500">
          avg SoC
        </span>
      </div>
      <!-- Progress Bar -->
      <div class="mt-2 w-full bg-slate-200 dark:bg-slate-800 h-1.5 rounded-full overflow-hidden" role="progressbar" aria-valuenow={stats?.avg_battery_pct ?? 0} aria-valuemin={0} aria-valuemax={100}>
        <div 
          class="h-full rounded-full transition-all duration-300 {(stats?.avg_battery_pct ?? 0) < 30 ? 'bg-destructive' : (stats?.avg_battery_pct ?? 0) < 50 ? 'bg-amber-500' : 'bg-primary'}"
          style="width: {stats?.avg_battery_pct ?? 0}%;"
        ></div>
      </div>
    </CardContent>
  </Card>

  <!-- Card 4: Avg Speed -->
  <Card class="transition-shadow hover:shadow-md">
    <CardHeader class="p-4 pb-2 flex flex-row items-center justify-between space-y-0">
      <CardTitle class="text-xs font-mono uppercase tracking-wider text-slate-600 dark:text-slate-400">
        Ground Speed
      </CardTitle>
      <span class="text-[11px] font-mono text-slate-500">GPS SPD</span>
    </CardHeader>
    <CardContent class="p-4 pt-1">
      <div class="flex items-baseline gap-2">
        <span class="text-2xl font-bold font-mono tracking-tight text-slate-900 dark:text-slate-100">
          {stats?.avg_speed_mps ?? 0}
        </span>
        <span class="text-xs font-mono text-slate-500">
          m/s (~{Math.round((stats?.avg_speed_mps ?? 0) * 3.6)} km/h)
        </span>
      </div>
      <p class="text-[11px] font-mono text-slate-500 dark:text-slate-400 mt-1">
        Air corridor traffic: nominal
      </p>
    </CardContent>
  </Card>
</div>
