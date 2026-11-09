<script lang="ts">
  import type { Snippet } from 'svelte';
  let { 
    class: className = '', 
    children, 
    ...restProps 
  }: { 
    class?: string; 
    children?: Snippet; 
    [key: string]: any 
  } = $props();
</script>

<div class="rounded-xl border border-[var(--border)] bg-[var(--card)] text-[var(--card-foreground)] shadow-sm {className}" {...restProps}>
  {#if children}
    {@render children()}
  {/if}
</div>
