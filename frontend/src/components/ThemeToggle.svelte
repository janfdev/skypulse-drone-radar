<script lang="ts">
  import { onMount } from 'svelte';
  import Button from './ui/button/Button.svelte';

  let theme = $state<'dark' | 'light'>('dark');

  function updateTheme(newTheme: 'dark' | 'light') {
    theme = newTheme;
    const root = document.documentElement;
    if (newTheme === 'dark') {
      root.classList.add('dark');
      root.style.colorScheme = 'dark';
    } else {
      root.classList.remove('dark');
      root.style.colorScheme = 'light';
    }
    localStorage.setItem('skypulse-theme', newTheme);
  }

  function toggle() {
    updateTheme(theme === 'dark' ? 'light' : 'dark');
  }

  onMount(() => {
    const saved = localStorage.getItem('skypulse-theme') as 'dark' | 'light' | null;
    if (saved) {
      updateTheme(saved);
    } else {
      updateTheme('dark');
    }
  });
</script>

<Button 
  variant="outline" 
  size="icon" 
  onclick={toggle} 
  aria-label="Toggle visual theme between Light and Dark mode"
  class="relative h-9 w-9 text-slate-700 dark:text-slate-300"
>
  {#if theme === 'dark'}
    <!-- Sun icon for switching to light -->
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <circle cx="12" cy="12" r="4"/>
      <path d="M12 2v2"/>
      <path d="M12 20v2"/>
      <path d="m4.93 4.93 1.41 1.41"/>
      <path d="m17.66 17.66 1.41 1.41"/>
      <path d="M2 12h2"/>
      <path d="M20 12h2"/>
      <path d="m6.34 17.66-1.41 1.41"/>
      <path d="m19.07 4.93-1.41 1.41"/>
    </svg>
  {:else}
    <!-- Moon icon for switching to dark -->
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>
    </svg>
  {/if}
</Button>
