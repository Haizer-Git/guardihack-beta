<template>
  <div class="flex flex-col items-center w-full min-h-screen">
    
    <!-- ========================================= -->
    <!-- PHASE 1 : BOOT SEQUENCE FULL SCREEN       -->
    <!-- ========================================= -->
    <div 
      v-if="isBooting" 
      class="fixed inset-0 z-[9999] bg-black overflow-hidden font-code text-sm md:text-base select-none"
    >
      <!-- 1A. Le texte du terminal (Affiché pendant le boot, s'efface à la fin) -->
      <div 
        v-if="!showRootGrantedBox" 
        class="absolute top-0 left-0 w-full md:w-3/4 p-2 z-10 pointer-events-none"
      >
        <p v-for="(line, index) in displayedLines" :key="index" class="mb-0.5 text-white leading-snug">
          {{ line.text }}
          <!-- Affichage du statut en VERT uniquement -->
          <span v-if="line.status" class="text-success font-bold ml-2">[{{ line.status }}]</span>
        </p>
        <!-- Curseur clignotant vert -->
        <div class="mt-1">
          <span class="inline-block w-2.5 h-5 bg-white animate-pulse align-middle"></span>
        </div>
      </div>

      <!-- 1B. BOÎTE CENTRALE "ROOT ACCESS GRANTED" (Apparaît quand le boot est fini) -->
      <div 
        v-else 
        class="absolute inset-0 z-20 flex items-center justify-center p-4 animate-fade-in"
      >
        <div class="bg-black/90 border-2 border-base-content p-4 md:p-4 text-center max-w-xl">
          
          <h1 class="text-3xl md:text-xl font-black text-success">
            [ POOL ACCESS GRANTED ]
          </h1>
          
          <div class="w-full bg-success/10 h-1 my-4">
            <div class="bg-success h-full w-full animate-pulse"></div>
          </div>

          <p class="text-base-content text-sm md:text-sm">
            Bienvenue sur GuardiHack-Pool !
          </p>
        </div>
      </div>

      <!-- 1C. La vague binaire VERTICALE en SVG (Toujours visible) -->
      <svg class="absolute top-0 right-0 w-full h-full pointer-events-none z-0">
        <defs>
          <!-- Le motif binaire qui remplit la vague -->
          <pattern id="binary-pattern-vertical" patternUnits="userSpaceOnUse" width="120" height="120">
            <text x="0" y="15" fill="#00FF41" font-family="monospace" font-size="13" font-weight="bold">01001011 01100101</text>
            <text x="0" y="30" fill="#00FF41" font-family="monospace" font-size="13" font-weight="bold">11010010 10101011</text>
            <text x="0" y="45" fill="#00FF41" font-family="monospace" font-size="13" font-weight="bold">00110101 11000101</text>
            <text x="0" y="60" fill="#00FF41" font-family="monospace" font-size="13" font-weight="bold">10101010 00110011</text>
            <text x="0" y="75" fill="#00FF41" font-family="monospace" font-size="13" font-weight="bold">11110000 00001111</text>
            <text x="0" y="90" fill="#00FF41" font-family="monospace" font-size="13" font-weight="bold">01101100 10010011</text>
            <text x="0" y="105" fill="#00FF41" font-family="monospace" font-size="13" font-weight="bold">00001010 11110101</text>
            <text x="0" y="120" fill="#00FF41" font-family="monospace" font-size="13" font-weight="bold">11001100 00110011</text>
          </pattern>
        </defs>
        <!-- Le chemin de la vague verticale mis à jour en JS -->
        <path ref="wavePath" fill="url(#binary-pattern-vertical)"></path>
      </svg>
    </div>

    <!-- ========================================= -->
    <!-- PHASE 2 : ACCUEIL POOL (APRÈS BOOT)       -->
    <!-- ========================================= -->
    <div v-else class="animate-fade-in flex flex-col items-center gap-10 w-full pt-10">
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
      <div class="text-center space-y-4">
        <h2 class="text-6xl md:text-8xl font-black font-titre text-secondary tracking-widest drop-shadow-[0_0_15px_rgba(0,245,255,0.5)]">
          P O O L _
        </h2>
        <p class="text-primary font-code tracking-[0.3em] uppercase opacity-80">
          Sélectionnez votre module
        </p>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-4xl px-4 mt-8">
        <button class="group relative px-6 py-8 bg-base-200 border-2 border-primary/40 hover:border-primary transition-all duration-300 hover:-translate-y-2 hover:shadow-[0_0_25px_rgba(0,255,65,0.3)]">
          <span class="block text-2xl font-titre text-secondary mb-2">> COURS</span>
        </button>
        <button class="group relative px-6 py-8 bg-base-200 border-2 border-secondary/40 hover:border-secondary transition-all duration-300 hover:-translate-y-2 hover:shadow-[0_0_25px_rgba(0,245,255,0.3)]">
          <span class="block text-2xl font-titre text-secondary mb-2">> JEOPARDY</span>
        </button>
        <button class="group relative px-6 py-8 bg-base-200 border-2 border-accent/40 hover:border-accent transition-all duration-300 hover:-translate-y-2 hover:shadow-[0_0_25px_rgba(255,0,60,0.3)]">
          <span class="block text-2xl font-titre text-accent mb-2">> MACHINE</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const isBooting = ref(true)
const showRootGrantedBox = ref(false)
const displayedLines = ref([])
const wavePath = ref(null)

// --- GESTION DE LA VAGUE VERTICALE (CÔTÉ DROIT) ---
let width = window.innerWidth
let height = window.innerHeight
const WAVEHEIGHT = 50
// 50
const FREQUENCY = 100
// 120
const SPEED = 5
// 5

let ys = []
let tick = 0
let animationFrameId = null

const createWave = () => {
  ys = []
  for (let i = 0; i <= height; i += 2) {
    ys.push(i)
  }
}

const animateWave = () => {
  if (!wavePath.value) return

  let points = ys.map(y => {
    let x = (width - 180) + WAVEHEIGHT * Math.sin((y + tick) / FREQUENCY)
    return [x, y]
  })

  let path =
    "M " + points.map(p => p[0] + "," + p[1]).join(" L ") +
    " L " + width + "," + height +
    " L " + width + ",0 Z"

  wavePath.value.setAttribute("d", path)
  tick += SPEED
  animationFrameId = requestAnimationFrame(animateWave)
}

const handleResize = () => {
  width = window.innerWidth
  height = window.innerHeight
  createWave()
}

// --- SCRIPT DE BOOT ULTRARAPIDE ---
const bootScript = [
  { text: "GuardiHack OS v1.2026 (core 6.1.0-sec) boot sequence initiated", status: null, delay: 50 },
  { text: "Initializing hardware kernel modules...", status: "OK", delay: 30 },
  { text: "Mounting core virtual file systems...", status: "OK", delay: 30 },
  { text: "Compiling exploit database signatures...", status: "OK", delay: 30 },
  { text: "Loading User Profile data...", status: "OK", delay: 80 },
  { text: "Synchronizing Badges & Achievements...", status: "OK", delay: 40 },
  { text: "Fetching User Cosmetics & Avatars...", status: "OK", delay: 30 },
  { text: "Calibrating Level & XP Progression...", status: "OK", delay: 30 },
    { text: "Loading Jeopardy Modules...", status: "OK", delay: 40 },
    { text: "Booting Machine Instances...", status: "OK", delay: 50 },
    { text: "Initializing Network Stack...", status: "OK", delay: 30 },
  { text: "Establishing secure uplink to GuardiHack mainframe...", status: "OK", delay: 50 },
  { text: "Validating session tokens...", status: "OK", delay: 30 },
  { text: "Spawning isolated Docker containers...", status: "OK", delay: 40 },
  { text: "Engaging hypervisor for CTF instances...", status: "OK", delay: 40 },
  { text: "Initializing sandbox environment...", status: "OK", delay: 40 },
  { text: "Verifying flag submission endpoints...", status: "OK", delay: 35 },
  
  // Transition Piscine
  { text: "..........................................", status: null, delay: 35 },
  { text: ">>> INITIATING 'GUARDIHACKPOOL' IMMERSION PROTOCOL <<<", status: null, delay: 100 },
  { text: "Allocating deep-water memory blocks...", status: "OK", delay: 40 },
  { text: "Flooding isolated environments...", status: "OK", delay: 50 },
  { text: "Diving sequence initiated...", status: "OK", delay: 30 },
  { text: "Submerging virtual systems...", status: "OK", delay: 45 },
  
  // Intrusion
  { text: "WARNING: Unrecognized signature detected.", status: null, delay: 80 },
  { text: "Tracing origin IP address...", status: "OK", delay: 40 },
  { text: "Deploying countermeasures...", status: "OK", delay: 30 },
  { text: "Establishing reverse shell listeners...", status: "OK", delay: 30 },
  { text: "Analyzing threat level...", status: "OK", delay: 30 },
  { text: "Injecting payload into sub-routines...", status: "OK", delay: 30 },
  { text: "Bypassing firewall...", status: "OK", delay: 40 },
  { text: "Decrypting modules (COURS, JEOPARDY, MACHINE)...", status: "OK", delay: 45 }
]

onMounted(() => {
  createWave()
  animateWave()
  window.addEventListener("resize", handleResize)

  let accumulatedDelay = 0;
  
  bootScript.forEach((item, index) => {
    accumulatedDelay += item.delay;

    setTimeout(() => {
      displayedLines.value.push(item);
      
      // Quand la dernière ligne de commande s'affiche
      if (index === bootScript.length - 1) {
        setTimeout(() => {
          showRootGrantedBox.value = true;
          
          // 2. On laisse le message central affiché 1,8 seconde avant de quitter le boot screen
          setTimeout(() => {
            isBooting.value = false;
          }, 1800);
        }, 300);
      }
    }, accumulatedDelay);
  });
})

onBeforeUnmount(() => {
  window.removeEventListener("resize", handleResize)
  if (animationFrameId) cancelAnimationFrame(animationFrameId)
})
</script>