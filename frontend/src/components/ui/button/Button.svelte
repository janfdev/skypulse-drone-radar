<script lang="ts">
  import type { Snippet } from 'svelte';

  let { 
    variant = 'default', 
    size = 'default', 
    class: className = '', 
    disabled = false,
    children, 
    ...restProps 
  }: { 
    variant?: 'default' | 'secondary' | 'destructive' | 'outline' | 'ghost' | 'link'; 
    size?: 'default' | 'sm' | 'lg' | 'icon'; 
    class?: string; 
    disabled?: boolean;
    children?: Snippet; 
    [key: string]: any 
  } = $props();

  const variantClasses = {
    default: 'bg-primary text-primary-foreground shadow hover:opacity-90',
    secondary: 'bg-secondary text-secondary-foreground shadow-sm hover:bg-secondary/80',
    destructive: 'bg-destructive text-destructive-foreground shadow-sm hover:opacity-90',
    outline: 'border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground',
    ghost: 'hover:bg-accent hover:text-accent-foreground',
    link: 'text-primary underline-offset-4 hover:underline',
  };

  const sizeClasses = {
    default: 'h-9 px-4 py-2 min-h-[44px] sm:min-h-[36px]',
    sm: 'h-8 rounded-md px-3 text-xs min-h-[44px] sm:min-h-[32px]',
    lg: 'h-10 rounded-md px-8 min-h-[44px] sm:min-h-[40px]',
    icon: 'h-9 w-9 min-h-[44px] min-w-[44px] sm:min-h-[36px] sm:min-w-[36px]',
  };
</script>

<button 
  class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 select-none {variantClasses[variant] || variantClasses.default} {sizeClasses[size] || sizeClasses.default} {className}" 
  {disabled}
  {...restProps}
>
  {#if children}
    {@render children()}
  {/if}
</button>
