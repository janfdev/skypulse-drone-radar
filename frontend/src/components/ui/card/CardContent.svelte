<script lang="ts">
  import type { Snippet } from 'svelte';
  let { class: className = '', children, ...restProps }: { class?: string; children?: Snippet; [key: string]: any } = $props();
</script>

<div class="p-5 pt-0 {className}" {...restProps}>
  {#if children}
    {@render children()}
  {/if}
</div>
