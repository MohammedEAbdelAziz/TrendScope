<script lang="ts">
  import "./layout.css";

  let { children } = $props();
</script>

<svelte:head>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link
    rel="preconnect"
    href="https://fonts.gstatic.com"
    crossorigin="anonymous"
  />
  <!-- Inter for English -->
  <link
    href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
    rel="stylesheet"
  />
  <!-- IBM Plex Sans Arabic for Arabic - professional, highly readable -->
  <link
    href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&display=swap"
    rel="stylesheet"
  />
  <link rel="icon" href="/favicon.png" />
</svelte:head>

<div class="dark font-sans">
  {@render children()}
</div>

<style>
  :global(body) {
    font-family: "Inter", sans-serif;
  }

  /* Arabic font for RTL content */
  :global([dir="rtl"]) {
    font-family: "IBM Plex Sans Arabic", "Inter", sans-serif;
  }
</style>
