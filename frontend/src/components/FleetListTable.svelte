<script lang="ts">
  import type { DroneTelemetry } from '../types';
  import Card from './ui/card/Card.svelte';
  import CardHeader from './ui/card/CardHeader.svelte';
  import CardTitle from './ui/card/CardTitle.svelte';
  import CardDescription from './ui/card/CardDescription.svelte';
  import Badge from './ui/badge/Badge.svelte';
  import Button from './ui/button/Button.svelte';
  import TabsList from './ui/tabs/TabsList.svelte';
  import TabsTrigger from './ui/tabs/TabsTrigger.svelte';

  let { 
    drones, 
    selectedDroneId, 
    onSelectDrone 
  }: {
    drones: DroneTelemetry[];
    selectedDroneId: string | null;
    onSelectDrone: (id: string) => void;
  } = $props();

  let filterTab = $state<'ALL' | 'AIRBORNE' | 'RTH' | 'WARNINGS'>('ALL');
  let searchQuery = $state<string>('');

  // $derived filtered list
  let filteredDrones = $derived(
    drones.filter((d) => {
      // Tab filter
      if (filterTab === 'AIRBORNE' && d.flight_mode !== 'EN_ROUTE' && d.flight_mode !== 'HOVER') return false;
      if (filterTab === 'RTH' && d.flight_mode !== 'RETURNING_HOME') return false;
      if (filterTab === 'WARNINGS' && !d.geofence_warning && d.battery_pct >= 25) return false;

      // Text query
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        return d.callsign.toLowerCase().includes(q) || d.drone_id.toLowerCase().includes(q) || d.model.toLowerCase().includes(q);
      }
      return true;
    })
  );
</script>

<Card class="overflow-hidden">
  <CardHeader class="p-4 border-b border-border flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
    <div>
      <div class="flex items-center gap-2">
        <CardTitle class="text-sm font-semibold">
          Fleet Telemetry Directory
        </CardTitle>
        <Badge variant="secondary" class="font-mono text-xs">
          {drones.length} Units Active
        </Badge>
      </div>
      <CardDescription class="text-xs mt-0.5">
        Live telemetry status of autonomous logistics assets in Greater Jakarta
      </CardDescription>
    </div>

    <!-- Filter Tabs & Search Bar -->
    <div class="flex flex-wrap items-center gap-2">
      <!-- Search input -->
      <div class="relative">
        <input 
          type="text"
          placeholder="Filter callsign or ID..."
          bind:value={searchQuery}
          class="h-8 px-2.5 text-xs font-mono rounded-md border border-input bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring w-44"
        />
        {#if searchQuery}
          <button 
            type="button"
            onclick={() => searchQuery = ''}
            class="absolute right-2 top-2 text-muted-foreground hover:text-foreground text-xs"
            aria-label="Clear filter search"
          >
            ×
          </button>
        {/if}
      </div>

      <!-- Segmented Tabs -->
      <TabsList>
        <TabsTrigger value="ALL" active={filterTab === 'ALL'} onclick={() => filterTab = 'ALL'}>
          All
        </TabsTrigger>
        <TabsTrigger value="AIRBORNE" active={filterTab === 'AIRBORNE'} onclick={() => filterTab = 'AIRBORNE'}>
          Airborne
        </TabsTrigger>
        <TabsTrigger value="RTH" active={filterTab === 'RTH'} onclick={() => filterTab = 'RTH'}>
          RTH
        </TabsTrigger>
        <TabsTrigger value="WARNINGS" active={filterTab === 'WARNINGS'} onclick={() => filterTab = 'WARNINGS'}>
          Alerts
        </TabsTrigger>
      </TabsList>
    </div>
  </CardHeader>

  <!-- Table Body -->
  <div class="overflow-x-auto">
    <table class="w-full text-left font-mono text-xs">
      <thead>
        <tr class="border-b border-border text-[11px] text-muted-foreground bg-muted/40">
          <th class="py-2.5 px-4 font-medium">CALLSIGN / ID</th>
          <th class="py-2.5 px-4 font-medium">STATUS</th>
          <th class="py-2.5 px-4 font-medium">BATTERY</th>
          <th class="py-2.5 px-4 font-medium">ALTITUDE</th>
          <th class="py-2.5 px-4 font-medium">GROUND SPEED</th>
          <th class="py-2.5 px-4 font-medium">HEADING</th>
          <th class="py-2.5 px-4 font-medium">NEAREST GEOFENCE</th>
          <th class="py-2.5 px-4 font-medium text-right">ACTION</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-border">
        {#if filteredDrones.length === 0}
          <tr>
            <td colspan="8" class="py-8 text-center text-muted-foreground text-xs font-mono">
              No drones match the selected filter criteria.
            </td>
          </tr>
        {:else}
          {#each filteredDrones as drone}
            {@const isSelected = drone.drone_id === selectedDroneId}
            <tr 
              tabindex="0"
              role="button"
              class="transition-colors cursor-pointer focus:outline-none focus:bg-muted {
                isSelected ? 'bg-primary/10 text-primary font-semibold' : 
                drone.geofence_warning ? 'bg-destructive/10 hover:bg-destructive/15' : 
                'hover:bg-muted/50 text-foreground'
              }"
              onclick={() => onSelectDrone(drone.drone_id)}
              onkeydown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  onSelectDrone(drone.drone_id);
                }
              }}
            >
              <!-- Callsign -->
              <td class="py-3 px-4 whitespace-nowrap">
                <div class="flex items-center gap-2">
                  <span class="size-2 rounded-full {drone.geofence_warning ? 'bg-destructive animate-pulse' : isSelected ? 'bg-primary' : 'bg-emerald-500'}"></span>
                  <span class="font-medium">{drone.callsign}</span>
                  <span class="text-[11px] text-muted-foreground">({drone.drone_id})</span>
                </div>
              </td>

              <!-- Status -->
              <td class="py-3 px-4 whitespace-nowrap">
                <Badge 
                  variant={
                    drone.flight_mode === 'RETURNING_HOME' ? 'warning' :
                    drone.flight_mode === 'HOVER' ? 'secondary' :
                    drone.flight_mode === 'COLLISION_AVOIDANCE' ? 'destructive' :
                    'success'
                  }
                  class="font-mono text-[10px]"
                >
                  {drone.flight_mode}
                </Badge>
              </td>

              <!-- Battery -->
              <td class="py-3 px-4 whitespace-nowrap">
                <div class="flex items-center gap-2">
                  <div class="w-12 bg-secondary h-1.5 rounded-full overflow-hidden" role="progressbar" aria-valuenow={drone.battery_pct} aria-valuemin={0} aria-valuemax={100}>
                    <div 
                      class="h-full rounded-full {drone.battery_pct < 25 ? 'bg-destructive' : 'bg-primary'}"
                      style="width: {drone.battery_pct}%;"
                    ></div>
                  </div>
                  <span class="{drone.battery_pct < 25 ? 'text-destructive font-bold' : ''}">{drone.battery_pct}%</span>
                </div>
              </td>

              <!-- Altitude -->
              <td class="py-3 px-4 whitespace-nowrap">
                {Math.round(drone.coords.alt_m)} m
              </td>

              <!-- Speed -->
              <td class="py-3 px-4 whitespace-nowrap">
                {drone.speed_mps} m/s
              </td>

              <!-- Heading -->
              <td class="py-3 px-4 whitespace-nowrap text-primary font-medium">
                {drone.heading_deg}°
              </td>

              <!-- Geofence -->
              <td class="py-3 px-4 whitespace-nowrap">
                {#if drone.geofence_warning}
                  <span class="text-destructive font-semibold flex items-center gap-1">
                    [!] {drone.nearest_no_fly_zone ? `${drone.nearest_no_fly_zone.slice(0, 18)}...` : 'Restricted'}
                  </span>
                {:else}
                  <span class="text-muted-foreground">
                    {drone.nearest_no_fly_zone ? `${drone.nearest_no_fly_zone.slice(0, 18)}...` : 'Safe Corridor'}
                  </span>
                {/if}
              </td>

              <!-- Action button -->
              <td class="py-3 px-4 whitespace-nowrap text-right">
                <Button 
                  variant={isSelected ? 'default' : 'outline'}
                  size="sm"
                  class="h-7 text-[11px] font-mono px-2.5"
                  onclick={(e: MouseEvent) => {
                    e.stopPropagation();
                    onSelectDrone(drone.drone_id);
                  }}
                >
                  {isSelected ? 'TRACKING' : 'INSPECT'}
                </Button>
              </td>
            </tr>
          {/each}
        {/if}
      </tbody>
    </table>
  </div>
</Card>
