<script lang="ts">
  import type { Snippet } from 'svelte';
  let { class: className = '', children, ...restProps }: { class?: string; children?: Snippet; [key: string]: any } = $props();
</script>

<div class="inline-flex h-9 items-center justify-center rounded-lg bg-slate-100 dark:bg-slate-900/80 p-1 text-slate-500 dark:text-slate-400 border border-slate-200 dark:border-slate-800 {className}" {...restProps}>
  {#if children}
    {@render children()}
  {/if}
</div>
