<script setup>
</script>

<template>
  <div class="flex flex-col items-center justify-center w-full min-h-[70vh] text-center animate-fade-in">
    <div class="max-w-4xl space-y-8 bg-base-200/50 backdrop-blur-md p-12 rounded-3xl border border-base-content/10 shadow-2xl">
      <h1 class="text-6xl md:text-8xl font-black font-cyber text-transparent bg-clip-text bg-gradient-to-r from-primary to-secondary drop-shadow-sm uppercase tracking-tighter">
        GuardiHack CTF
      </h1>
      <p class="text-xl md:text-2xl text-base-content/80 font-mono">
        Hack the planet. Secure the future.
      </p>
      <div class="flex justify-center gap-6 pt-8">
        <router-link to="/challenges" class="btn btn-primary btn-lg font-cyber px-10 text-lg shadow-[0_0_20px_rgba(var(--p),0.4)] hover:scale-105 transition-transform">
          Play Now
        </router-link>
        <router-link to="/scoreboard" class="btn btn-outline btn-secondary btn-lg font-cyber px-10 text-lg hover:scale-105 transition-transform">
          Leaderboard
        </router-link>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 pt-12 mt-12 border-t border-base-content/10">
        <div class="flex flex-col items-center">
          <div class="text-4xl font-black text-primary mb-2">42</div>
          <div class="text-sm uppercase tracking-widest opacity-60">Challenges</div>
        </div>
        <div class="flex flex-col items-center">
          <div class="text-4xl font-black text-secondary mb-2">1,337</div>
          <div class="text-sm uppercase tracking-widest opacity-60">Hackers</div>
        </div>
        <div class="flex flex-col items-center">
          <div class="text-4xl font-black text-accent mb-2">24h</div>
          <div class="text-sm uppercase tracking-widest opacity-60">Time Left</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-fade-in { animation: fadeIn 0.5s ease-out forwards; }
@keyframes fadeIn { from { opacity: 0; transform: scale(0.95); } to { opacity: 1; transform: scale(1); } }
</style>