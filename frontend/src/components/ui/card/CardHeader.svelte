<script lang="ts">
  import type { Snippet } from 'svelte';
  let { class: className = '', children, ...restProps }: { class?: string; children?: Snippet; [key: string]: any } = $props();
</script>

<div class="flex flex-col space-y-1.5 p-5 {className}" {...restProps}>
  {#if children}
    {@render children()}
  {/if}
</div>
