<script lang="ts">
  import type { DroneTelemetry } from '../types';
  import Card from './ui/card/Card.svelte';
  import CardHeader from './ui/card/CardHeader.svelte';
  import CardTitle from './ui/card/CardTitle.svelte';
  import CardDescription from './ui/card/CardDescription.svelte';
  import CardContent from './ui/card/CardContent.svelte';
  import Badge from './ui/badge/Badge.svelte';
  import Button from './ui/button/Button.svelte';

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

<Card class="h-full flex flex-col justify-between">
  {#if drone}
    <div class="space-y-4">
      <!-- Target Inspector Header -->
      <CardHeader class="p-4 border-b border-[var(--border)]">
        <div class="flex items-start justify-between">
          <div>
            <div class="flex items-center gap-2">
              <Badge variant="outline" class="font-mono text-primary font-bold">
                {drone.drone_id}
              </Badge>
              <CardTitle class="text-base font-semibold">
                {drone.callsign}
              </CardTitle>
            </div>
            <CardDescription class="text-xs font-mono mt-1">
              {drone.model}
            </CardDescription>
          </div>

          <!-- Flight Status Badge -->
          <Badge 
            variant={
              drone.flight_mode === 'RETURNING_HOME' ? 'warning' :
              drone.flight_mode === 'HOVER' ? 'secondary' :
              drone.flight_mode === 'COLLISION_AVOIDANCE' ? 'destructive' :
              'success'
            }
            class="font-mono text-[11px] font-bold"
          >
            {drone.flight_mode}
          </Badge>
        </div>
      </CardHeader>

      <CardContent class="p-4 pt-0 space-y-4">
        <!-- 2x2 Flight Telemetry Grid -->
        <div class="grid grid-cols-2 gap-2.5 text-xs font-mono">
          <div class="p-2.5 rounded-lg bg-secondary/50 border border-[var(--border)]">
            <span class="text-muted-foreground block text-[10px] uppercase font-mono tracking-wider">Altitude AGL</span>
            <span class="text-base font-bold text-foreground mt-0.5 block">{Math.round(drone.coords.alt_m)} m</span>
            <span class="text-[10px] text-muted-foreground">~{Math.round(drone.coords.alt_m * 3.28)} ft</span>
          </div>

          <div class="p-2.5 rounded-lg bg-secondary/50 border border-[var(--border)]">
            <span class="text-muted-foreground block text-[10px] uppercase font-mono tracking-wider">Ground Speed</span>
            <span class="text-base font-bold text-foreground mt-0.5 block">{drone.speed_mps} m/s</span>
            <span class="text-[10px] text-muted-foreground">~{Math.round(drone.speed_mps * 3.6)} km/h</span>
          </div>

          <div class="p-2.5 rounded-lg bg-secondary/50 border border-[var(--border)]">
            <span class="text-muted-foreground block text-[10px] uppercase font-mono tracking-wider">Heading Azimuth</span>
            <span class="text-base font-bold text-primary mt-0.5 block">{drone.heading_deg}°</span>
            <span class="text-[10px] text-muted-foreground">Magnetic True</span>
          </div>

          <div class="p-2.5 rounded-lg bg-secondary/50 border border-[var(--border)]">
            <span class="text-muted-foreground block text-[10px] uppercase font-mono tracking-wider">Signal Link</span>
            <span class="text-base font-bold text-foreground mt-0.5 block">{drone.signal_rssi_dbm} dBm</span>
            <span class="text-[10px] text-emerald-600 dark:text-emerald-400">99.8% quality</span>
          </div>
        </div>

        <!-- Battery Gauge -->
        <div class="p-3 rounded-lg bg-secondary/50 border border-[var(--border)]">
          <div class="flex items-center justify-between text-xs font-mono mb-1.5">
            <span class="text-muted-foreground uppercase text-[10px] tracking-wider">Propulsion Battery</span>
            <span class="font-bold {drone.battery_pct < 25 ? 'text-destructive' : 'text-foreground'}">
              {drone.battery_pct}%
            </span>
          </div>
          <div class="w-full bg-slate-200 dark:bg-slate-800 h-2 rounded-full overflow-hidden" role="progressbar" aria-valuenow={drone.battery_pct} aria-valuemin={0} aria-valuemax={100}>
            <div 
              class="h-full rounded-full transition-all duration-300 {drone.battery_pct < 25 ? 'bg-destructive' : drone.battery_pct < 50 ? 'bg-amber-500' : 'bg-primary'}"
              style="width: {drone.battery_pct}%;"
            ></div>
          </div>
        </div>

        <!-- Airspace Proximity Alert -->
        <div class="p-3 rounded-lg border {drone.geofence_warning ? 'bg-destructive/10 border-destructive/30' : 'bg-secondary/50 border-[var(--border)]'}">
          <div class="flex items-center justify-between text-xs font-mono">
            <span class="font-semibold uppercase text-[10px] tracking-wider {drone.geofence_warning ? 'text-destructive' : 'text-muted-foreground'}">
              Airspace Proximity
            </span>
            {#if drone.geofence_warning}
              <Badge variant="destructive" class="text-[10px] font-mono px-1.5 py-0">
                PROXIMITY ALERT
              </Badge>
            {:else}
              <Badge variant="outline" class="text-[10px] font-mono px-1.5 py-0 text-emerald-600 dark:text-emerald-400">
                CLEAR
              </Badge>
            {/if}
          </div>
          <p class="mt-1 text-xs font-mono text-foreground font-medium">
            {drone.nearest_no_fly_zone ?? 'No active restriction nearby'}
          </p>
          {#if drone.distance_to_nfz_m}
            <p class="text-[11px] font-mono text-muted-foreground mt-0.5">
              Distance: <span class="font-semibold text-foreground">{Math.round(drone.distance_to_nfz_m)} m</span> to boundary
            </p>
          {/if}
        </div>

        <!-- Coordinates GPS -->
        <div class="text-[11px] font-mono text-muted-foreground flex justify-between px-1">
          <span>LAT: {drone.coords.lat.toFixed(5)}</span>
          <span>LNG: {drone.coords.lng.toFixed(5)}</span>
        </div>
      </CardContent>
    </div>

    <!-- Mission Command Action Strip: Prioritized Shadcn Hierarchy -->
    <div class="p-4 border-t border-[var(--border)] space-y-2">
      <div class="flex items-center justify-between">
        <span class="text-xs font-mono font-semibold uppercase tracking-wider text-muted-foreground">
          Tactical Command Strip
        </span>
        {#if loadingCmd}
          <span class="text-[10px] font-mono text-primary animate-pulse">
            TRANSMITTING...
          </span>
        {/if}
      </div>

      <div class="grid grid-cols-2 gap-2">
        <!-- Emergency Action: High-Priority Destructive -->
        <Button 
          variant="outline" 
          size="sm"
          onclick={() => handleCmd('RTH')}
          disabled={loadingCmd !== null}
          class="font-mono text-xs w-full justify-center border-red-300 text-red-700 bg-red-50 hover:bg-red-100 dark:bg-destructive dark:text-destructive-foreground dark:border-transparent dark:hover:opacity-90 font-semibold"
        >
          <svg class="size-3.5 mr-1.5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
          RTH (Home)
        </Button>

        <!-- Standard Operational Action: Default Primary -->
        <Button 
          variant="default" 
          size="sm"
          onclick={() => handleCmd('RESUME')}
          disabled={loadingCmd !== null}
          class="font-mono text-xs w-full justify-center font-semibold"
        >
          <svg class="size-3.5 mr-1.5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polygon points="6 3 20 12 6 21 6 3"/></svg>
          Resume
        </Button>

        <!-- Secondary Action: Hover -->
        <Button 
          variant="outline" 
          size="sm"
          onclick={() => handleCmd('HOLD')}
          disabled={loadingCmd !== null}
          class="font-mono text-xs w-full justify-center border-purple-200 text-purple-700 bg-purple-50 hover:bg-purple-100 dark:border-border dark:bg-secondary dark:text-secondary-foreground"
        >
          <svg class="size-3.5 mr-1.5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect width="4" height="16" x="6" y="4"/><rect width="4" height="16" x="14" y="4"/></svg>
          Hold Hover
        </Button>

        <!-- Secondary Action: Collision Avoidance Divert -->
        <Button 
          variant="outline" 
          size="sm"
          onclick={() => handleCmd('DIVERT')}
          disabled={loadingCmd !== null}
          class="font-mono text-xs w-full justify-center border-sky-200 text-sky-700 bg-sky-50 hover:bg-sky-100 dark:border-border dark:bg-accent dark:text-accent-foreground"
        >
          <svg class="size-3.5 mr-1.5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m18 8 4 4-4 4"/><path d="M2 12h20"/></svg>
          Divert +90°
        </Button>
      </div>
    </div>
  {:else}
    <!-- Empty State (R-27 compliant) -->
    <div class="h-64 flex flex-col items-center justify-center p-6 text-center">
      <div class="size-12 rounded-full bg-secondary flex items-center justify-center text-muted-foreground mb-3">
        <svg class="size-6" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="m4.93 4.93 4.24 4.24"/><path d="m14.83 9.17 4.24-4.24"/><path d="m14.83 14.83 4.24 4.24"/><path d="m9.17 14.83-4.24 4.24"/></svg>
      </div>
      <CardTitle class="text-sm font-semibold mb-1">No Unit Selected</CardTitle>
      <CardDescription class="text-xs max-w-[220px]">
        Select an airborne drone on the tactical radar or from the fleet directory below to inspect live kinematics.
      </CardDescription>
    </div>
  {/if}
</Card>
