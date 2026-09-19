<template>
  <!-- Le data-theme force l'application de ton thème DaisyUI exclusif à la Pool -->
  <div data-theme="pool-theme" class="min-h-screen bg-base-300 text-base-content font-text">
    
    <!-- Tu pourras créer et importer une PoolNavbar.vue plus tard ici -->
    <header class="p-4 bg-base-200 border-b border-primary text-center">
      <h1 class="text-primary font-titre text-2xl">GUARDIHACK POOL</h1>
    </header>

    <!-- C'est ici que les différentes pages (cours, jeopardy, etc.) vont s'injecter -->
    <main class="p-4 md:p-8">
      <router-view></router-view>
    </main>

  </div>
</template>

<script setup>
// Tu pourras importer tes composants spécifiques à la pool ici
</script>