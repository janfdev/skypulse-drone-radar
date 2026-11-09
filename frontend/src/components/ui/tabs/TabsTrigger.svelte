<script lang="ts">
  import type { Snippet } from 'svelte';
  
  let { 
    value, 
    active = false, 
    class: className = '', 
    onclick, 
    children, 
    ...restProps 
  }: { 
    value: string; 
    active?: boolean; 
    class?: string; 
    onclick?: () => void; 
    children?: Snippet; 
    [key: string]: any 
  } = $props();
</script>

<button
  type="button"
  role="tab"
  aria-selected={active}
  class="inline-flex items-center justify-center whitespace-nowrap rounded-md px-3 py-1 text-xs font-medium ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 {active ? 'bg-white dark:bg-slate-800 text-slate-950 dark:text-slate-100 shadow-sm font-semibold' : 'hover:text-slate-900 dark:hover:text-slate-200'} {className}"
  {onclick}
  {...restProps}
>
  {#if children}
    {@render children()}
  {/if}
</button>
