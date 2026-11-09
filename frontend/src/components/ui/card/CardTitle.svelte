<script lang="ts">
  import type { Snippet } from 'svelte';
  let { class: className = '', children, ...restProps }: { class?: string; children?: Snippet; [key: string]: any } = $props();
</script>

<h3 class="font-semibold leading-none tracking-tight text-slate-900 dark:text-slate-100 {className}" {...restProps}>
  {#if children}
    {@render children()}
  {/if}
</h3>
