<script lang="ts">
  import type { Snippet } from 'svelte';
  
  let { 
    variant = 'default', 
    class: className = '', 
    children, 
    ...restProps 
  }: { 
    variant?: 'default' | 'secondary' | 'destructive' | 'outline' | 'warning' | 'success'; 
    class?: string; 
    children?: Snippet; 
    [key: string]: any 
  } = $props();

  const variantClasses = {
    default: 'bg-primary text-primary-foreground hover:bg-primary/80 border-transparent',
    secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80 border-transparent',
    destructive: 'bg-destructive/15 text-destructive border-destructive/30 dark:bg-destructive/20',
    outline: 'text-foreground border-border',
    warning: 'bg-amber-500/15 text-amber-700 dark:text-amber-400 border-amber-500/30',
    success: 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 border-emerald-500/30',
  };
</script>

<div class="inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 {variantClasses[variant] || variantClasses.default} {className}" {...restProps}>
  {#if children}
    {@render children()}
  {/if}
</div>
