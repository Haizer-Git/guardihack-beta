<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const days = ref([
  {
    id: 1,
    tag: "T01",
    title: "Fondamentaux Réseau",
    description: "Maîtrisez les bases du réseau : TCP/IP, DNS, HTTP et reconnaissance active.",
    isLocked: false,
    isCollapsed: false,
    date: "2026-04-21",
    tracks: [
      { id: "r1", type: "ROUTE", name: "Route Théorique", description: "Questions guidées sur TCP/IP, DNS et protocoles réseaux.", points: "1-5 pts", progress: 100, isLocked: false },
      { id: "j1", type: "JEOPARDY", name: "Jeopardy Réseau", description: "Défis pratiques : paquets TCP, analyse réseau, ICMP.", points: "Var. pts", progress: 45, isLocked: false },
      { id: "m1", type: "MACHINE", name: "Machine : NetMaster", description: "Configuration réseau complète et troubleshooting.", points: "Write-up", progress: 0, isLocked: false }
    ]
  },
  {
    id: 2,
    tag: "T02",
    title: "Fondamentaux Système",
    description: "Comprenez les systèmes d'exploitation, le shell et les fichiers.",
    isLocked: false,
    isCollapsed: false,
    date: "2026-04-22",
    tracks: [
      { id: "r2", type: "ROUTE", name: "Bases Système", description: "Cours interactif : Linux, processus, permissions et gestion de fichiers.", points: "1-5 pts", progress: 0, isLocked: false },
      { id: "j2", type: "JEOPARDY", name: "CTF Système", description: "Défis bash, scripts shell et exploitation de fichiers.", points: "Var. pts", progress: 0, isLocked: false },
      { id: "m2", type: "MACHINE", name: "Machine : SysAdmin", description: "Administration Linux et escalade de privilèges.", points: "Write-up", progress: 0, isLocked: false }
    ]
  },
  {
    id: 3,
    tag: "T03",
    title: "Fondamentaux Développement",
    description: "Apprenez les bases de la programmation et des vulnérabilités liées au code.",
    isLocked: true,
    isCollapsed: true,
    date: "2026-04-23",
    tracks: [
      { id: "r3", type: "ROUTE", name: "Concepts Dev", description: "Variables, boucles, fonctions et bonnes pratiques.", points: "1-5 pts", progress: 0, isLocked: false },
      { id: "j3", type: "JEOPARDY", name: "Code Challenges", description: "Reverse engineering, fuzzing et code analysis.", points: "Var. pts", progress: 0, isLocked: false },
      { id: "m3", type: "MACHINE", name: "Machine : CodeLab", description: "Développement sécurisé et exploitation de failles.", points: "Write-up", progress: 0, isLocked: false }
    ]
  },
  {
    id: 4,
    tag: "T04",
    title: "Fondamentaux Sécurité",
    description: "Maîtrisez les principes de sécurité : chiffrement, authentification et cryptographie.",
    isLocked: true,
    isCollapsed: true,
    date: "2026-04-24",
    tracks: [
      { id: "r4", type: "ROUTE", name: "Crypto Basics", description: "Chiffrement symétrique, asymétrique et fonctions de hash.", points: "1-5 pts", progress: 0, isLocked: false },
      { id: "j4", type: "JEOPARDY", name: "Crypto Challenges", description: "Casse de chiffrage, RSA, AES et analyse cryptanalytique.", points: "Var. pts", progress: 0, isLocked: false },
      { id: "m4", type: "MACHINE", name: "Machine : CryptoVault", description: "Sécurisation complète et pentesting.", points: "Write-up", progress: 0, isLocked: false }
    ]
  }
])

const toggleDay = (day) => {
  day.isCollapsed = !day.isCollapsed
}

// Fonction de navigation intelligente
const goToTrack = (track) => {
  if (track.isLocked) return 

  if (track.type === 'ROUTE') {
    router.push({ name: 'route-detail', params: { id: track.id } })
  } else {
    router.push({ name: 'challenge-list', params: { id: track.id } })
  }
}

const getTypeColor = (type) => {
  switch (type) {
    case 'ROUTE': return 'text-info border-info/30 bg-info/10'
    case 'JEOPARDY': return 'text-warning border-warning/30 bg-warning/10'
    case 'MACHINE': return 'text-secondary border-secondary/30 bg-secondary/10'
    default: return 'text-ghost'
  }
}
</script>

<template>
  <div class="w-full animate-fade-in pb-20 px-4 max-w-[1600px] mx-auto font-sans">

    <div class="mb-10">
      <h1 class="block w-full text-center text-3xl font-cyber font-bold bg-primary text-base-100 py-3 uppercase tracking-widest shadow-sm">
        Tracks
      </h1>
    </div>

    <div class="space-y-8">
      <div v-for="day in days" :key="day.id" class="w-full">

        <div @click="toggleDay(day)"
          class="flex items-center justify-between p-6 bg-base-200/50 border-l-4 border-primary cursor-pointer hover:bg-primary/5 transition-all rounded-r-lg group">
          <div class="flex items-center gap-6">
            <span class="text-3xl font-cyber font-black text-primary transition-transform group-hover:scale-110">{{
              day.tag }}</span>
            <div>
              <h2 class="text-xl font-bold uppercase tracking-widest flex items-center gap-3">
                {{ day.title }}
                <span v-if="day.isLocked"
                  class="badge badge-error badge-sm font-mono opacity-70 text-[10px]">ENCRYPTED</span>
              </h2>
              <p class="text-xs font-mono opacity-50">{{ day.date }} — {{ day.description }}</p>
            </div>
          </div>
          <button class="btn btn-circle btn-ghost transition-transform duration-500"
            :class="{ 'rotate-180': !day.isCollapsed }">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24"
              stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>
        </div>

        <transition name="expand">
          <div v-show="!day.isCollapsed" class="overflow-hidden">
            <div class="relative mt-6 p-2">

              <div class="grid grid-cols-1 lg:grid-cols-3 gap-8"
                :class="{ 'filter blur-lg pointer-events-none select-none': day.isLocked }">
                
                <div v-for="track in day.tracks" :key="track.id"
                  class="card bg-base-200/40 border border-white/5 p-8 flex flex-col min-h-[350px] hover:border-primary/30 transition-colors">

                  <div class="flex justify-between mb-6">
                    <span :class="['px-3 py-1 rounded border text-[10px] font-black uppercase', getTypeColor(track.type)]">
                        {{ track.type }}
                    </span>
                    <span v-if="track.progress === 100"
                      class="text-success text-[10px] font-bold uppercase flex items-center gap-2">
                      <span class="w-2 h-2 bg-success rounded-full animate-pulse"></span> Ready
                    </span>
                  </div>

                  <h3 class="text-xl font-cyber font-bold mb-4">{{ track.name }}</h3>
                  <p class="text-sm opacity-50 mb-8 flex-grow leading-relaxed">{{ track.description }}</p>

                  <div class="mt-auto space-y-4">
                    <div class="space-y-2">
                      <div class="flex justify-between text-[10px] font-mono opacity-50 uppercase tracking-tighter">
                        <span>Progression</span>
                        <span>{{ track.progress }}%</span>
                      </div>
                      <div class="h-1 bg-base-300 rounded-full overflow-hidden">
                        <div class="h-full bg-primary transition-all duration-1000"
                          :style="{ width: track.progress + '%' }"></div>
                      </div>
                    </div>

                    <button 
                        @click="goToTrack(track)" 
                        class="btn btn-primary btn-sm w-full font-cyber tracking-widest rounded-none hover:shadow-[0_0_15px_rgba(var(--p),0.4)]"
                    >
                      {{ track.progress === 100 ? 'Revoir' : (track.progress > 0 ? 'Continuer' : 'Commencer') }}
                    </button>
                  </div>
                </div>
              </div>

              <div v-if="day.isLocked" class="absolute inset-0 z-40 flex items-center justify-center">
                <div
                  class="bg-base-300/40 backdrop-blur-2xl border border-primary/20 p-12 flex flex-col items-center shadow-2xl rounded-2xl">
                  <div class="mb-6 text-primary animate-pulse">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-20 w-20" fill="none" viewBox="0 0 24 24"
                      stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1"
                        d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    </svg>
                  </div>
                  <h4 class="text-5xl font-cyber font-black tracking-[0.4em] text-white ml-[0.4em]">DATALOCK</h4>
                  <p class="font-mono text-xs mt-6 opacity-80 tracking-[0.2em] text-primary uppercase text-center">Secteur {{
                    day.tag }} sous protection cryptographique</p>
                </div>
              </div>

            </div>
          </div>
        </transition>

      </div>
    </div>
  </div>
</template>

<style scoped>

.animate-fade-in {
  animation: fadeIn 0.4s ease-out forwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ACCORDION ANIMATION */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  max-height: 1500px;
}

.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
}

/* Glassmorphism fort pour le flou */
.backdrop-blur-2xl {
  backdrop-filter: blur(40px);
  -webkit-backdrop-filter: blur(40px);
}
</style>