<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <div class="w-full animate-fade-in pb-20">
    
    <!-- HERO SECTION -->
    <section class="min-h-[80vh] flex flex-col items-center justify-center relative overflow-hidden px-4">
      <!-- Fond avec gradient animé -->
      <div class="absolute inset-0 bg-gradient-to-b from-primary/10 via-transparent to-secondary/5 pointer-events-none"></div>
      
      <div class="max-w-5xl space-y-8 text-center relative z-10">
        <div class="space-y-4">
          <h1 class="text-6xl md:text-8xl font-black font-cyber text-transparent bg-clip-text bg-gradient-to-r from-primary via-secondary to-primary drop-shadow-sm uppercase tracking-tighter animate-pulse-slow">
            GuardiHack CTF
          </h1>
          <p class="text-xl md:text-3xl text-base-content/80 font-mono tracking-widest">
            Hack the Planet. Secure the Future.
          </p>
        </div>

        <!-- CTA Buttons -->
        <div class="flex flex-col sm:flex-row justify-center gap-6 pt-8">
          <router-link to="/tracks" class="btn btn-primary btn-lg font-cyber px-10 text-lg shadow-[0_0_20px_rgba(var(--p),0.4)] hover:shadow-[0_0_30px_rgba(var(--p),0.6)] transition-all hover:scale-105">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Play Now
          </router-link>
          <router-link to="/scoreboard" class="btn btn-outline btn-secondary btn-lg font-cyber px-10 text-lg hover:scale-105 transition-transform">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            Leaderboard
          </router-link>
          <router-link to="/rules" class="btn btn-ghost btn-lg font-cyber px-10 text-lg border-base-content/20 hover:border-primary/50 transition-all">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C6.5 6.253 2 10.998 2 17s4.5 10.747 10 10.747c5.5 0 10-4.998 10-10.747S17.5 6.253 12 6.253z" />
            </svg>
            Règles
          </router-link>
        </div>
      </div>
    </section>

    <!-- STATS SECTION -->
    <section class="py-20 bg-base-200/40 border-y border-base-300">
      <div class="max-w-6xl mx-auto px-4">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          
          <div class="flex flex-col items-center p-8 bg-base-200/50 rounded-xl border border-primary/20 hover:border-primary/50 transition-all hover:shadow-lg hover:shadow-primary/20">
            <div class="text-5xl font-black text-primary mb-3">42</div>
            <div class="text-sm uppercase tracking-widest opacity-60 text-center">Challenges</div>
            <div class="text-xs font-mono text-primary/60 mt-2">À travers 4 catégories</div>
          </div>

          <div class="flex flex-col items-center p-8 bg-base-200/50 rounded-xl border border-secondary/20 hover:border-secondary/50 transition-all hover:shadow-lg hover:shadow-secondary/20">
            <div class="text-5xl font-black text-secondary mb-3">1,337</div>
            <div class="text-sm uppercase tracking-widest opacity-60 text-center">Participants</div>
            <div class="text-xs font-mono text-secondary/60 mt-2">Chercheurs de sécurité</div>
          </div>

          <div class="flex flex-col items-center p-8 bg-base-200/50 rounded-xl border border-accent/20 hover:border-accent/50 transition-all hover:shadow-lg hover:shadow-accent/20">
            <div class="text-5xl font-black text-accent mb-3">12</div>
            <div class="text-sm uppercase tracking-widest opacity-60 text-center">Équipes</div>
            <div class="text-xs font-mono text-accent/60 mt-2">En compétition</div>
          </div>

          <div class="flex flex-col items-center p-8 bg-base-200/50 rounded-xl border border-success/20 hover:border-success/50 transition-all hover:shadow-lg hover:shadow-success/20">
            <div class="text-5xl font-black text-success mb-3">24h</div>
            <div class="text-sm uppercase tracking-widest opacity-60 text-center">Durée</div>
            <div class="text-xs font-mono text-success/60 mt-2">Temps restant</div>
          </div>
        </div>
      </div>
    </section>

    <!-- CATEGORIES SECTION -->
    <section class="py-20 max-w-6xl mx-auto px-4">
      <h2 class="text-4xl font-cyber font-bold text-center mb-12 uppercase tracking-widest">
        <span class="text-transparent bg-clip-text bg-gradient-to-r from-primary to-secondary">Parcours d'Apprentissage</span>
      </h2>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        
        <div class="card bg-base-200/50 border border-base-300 hover:border-primary/50 transition-all hover:shadow-lg group cursor-pointer">
          <div class="card-body">
            <h3 class="card-title text-xl font-cyber text-primary group-hover:text-secondary transition-colors">
              T01 - Fondamentaux Réseau
            </h3>
            <p class="text-sm text-base-content/70">
              Maîtrisez TCP/IP, DNS et les protocoles réseau essentiels pour tout hacker.
            </p>
            <div class="flex gap-2 mt-4">
              <span class="badge badge-outline">Débutant</span>
              <span class="badge badge-outline">Réseau</span>
            </div>
          </div>
        </div>

        <div class="card bg-base-200/50 border border-base-300 hover:border-primary/50 transition-all hover:shadow-lg group cursor-pointer">
          <div class="card-body">
            <h3 class="card-title text-xl font-cyber text-primary group-hover:text-secondary transition-colors">
              T02 - Fondamentaux Système
            </h3>
            <p class="text-sm text-base-content/70">
              Linux, shell scripting et gestion du système d'exploitation.
            </p>
            <div class="flex gap-2 mt-4">
              <span class="badge badge-outline">Débutant</span>
              <span class="badge badge-outline">Linux</span>
            </div>
          </div>
        </div>

        <div class="card bg-base-200/50 border border-base-300 hover:border-secondary/50 transition-all hover:shadow-lg group cursor-pointer opacity-60">
          <div class="card-body">
            <h3 class="card-title text-xl font-cyber text-secondary group-hover:text-primary transition-colors">
              T03 - Fondamentaux Développement
            </h3>
            <p class="text-sm text-base-content/70">
              Programmation sécurisée et analyse de code malveillant.
            </p>
            <div class="flex gap-2 mt-4">
              <span class="badge badge-outline">Intermédiaire</span>
              <span class="badge badge-outline">Code</span>
            </div>
          </div>
          <div class="absolute inset-0 flex items-center justify-center bg-base-100/20 rounded-2xl backdrop-blur-sm">
            <span class="badge badge-primary">Bientôt</span>
          </div>
        </div>

        <div class="card bg-base-200/50 border border-base-300 hover:border-secondary/50 transition-all hover:shadow-lg group cursor-pointer opacity-60">
          <div class="card-body">
            <h3 class="card-title text-xl font-cyber text-secondary group-hover:text-primary transition-colors">
              T04 - Fondamentaux Sécurité
            </h3>
            <p class="text-sm text-base-content/70">
              Cryptographie et principes de sécurité moderne.
            </p>
            <div class="flex gap-2 mt-4">
              <span class="badge badge-outline">Intermédiaire</span>
              <span class="badge badge-outline">Crypto</span>
            </div>
          </div>
          <div class="absolute inset-0 flex items-center justify-center bg-base-100/20 rounded-2xl backdrop-blur-sm">
            <span class="badge badge-primary">Bientôt</span>
          </div>
        </div>
      </div>
    </section>

    <!-- INFO SECTION -->
    <section class="py-20 bg-base-200/40 border-t border-base-300">
      <div class="max-w-6xl mx-auto px-4">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          
          <div class="flex flex-col gap-4">
            <div class="text-3xl text-primary">🎯</div>
            <h3 class="font-cyber text-lg font-bold">Format Mixte</h3>
            <p class="text-sm text-base-content/70">
              Routes théoriques, défis Jeopardy et machines pratiques pour une apprentissage complet.
            </p>
          </div>

          <div class="flex flex-col gap-4">
            <div class="text-3xl text-secondary">🏆</div>
            <h3 class="font-cyber text-lg font-bold">Classement en Direct</h3>
            <p class="text-sm text-base-content/70">
              Seguez votre progression en temps réel contre vos adversaires.
            </p>
          </div>

          <div class="flex flex-col gap-4">
            <div class="text-3xl text-accent">🔐</div>
            <h3 class="font-cyber text-lg font-bold">Compétition Saine</h3>
            <p class="text-sm text-base-content/70">
              Respectez les règles, aidez la communauté et développez vos compétences.
            </p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.6s ease-out forwards;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse-slow {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.95; }
}

.animate-pulse-slow {
  animation: pulse-slow 3s ease-in-out infinite;
}
</style>