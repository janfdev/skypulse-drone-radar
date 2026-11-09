<script lang="ts">
  import type { Snippet } from 'svelte';
  let { class: className = '', children, ...restProps }: { class?: string; children?: Snippet; [key: string]: any } = $props();
</script>

<p class="text-xs text-slate-500 dark:text-slate-400 {className}" {...restProps}>
  {#if children}
    {@render children()}
  {/if}
</p>
