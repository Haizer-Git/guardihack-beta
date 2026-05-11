<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import ChallengeCard from '../components/ChallengeCard.vue'

const router = useRouter()
const STORAGE_KEY = 'guardiahack_categories_state'

// --- DONNÉES ---
// On garde la structure groupée pour permettre le "collapse" par catégorie
const categoriesData = ref([
  {
    name: 'WEB', isCollapsed: false,
    challenges: [
      { id: 1, title: 'SQLi Bypasser', difficulty: 'Facile', points: 100, solved: true, solves: 142 },
      { id: 2, title: 'XSS to Admin', difficulty: 'Moyen', points: 300, solved: false, solves: 89 },
      { id: 3, title: 'SSTI Nightmare', difficulty: 'Difficile', points: 500, solved: false, solves: 12 },
      { id: 9, title: 'CSRF Token', difficulty: 'Facile', points: 150, solved: false, solves: 45 },
      { id: 10, title: 'GraphQL Leak', difficulty: 'Moyen', points: 400, solved: false, solves: 3 },
      { id: 11, title: 'Web Chal 6', difficulty: 'Facile', points: 100, solved: false, solves: 20 },
      { id: 12, title: 'Web Chal 7', difficulty: 'Facile', points: 100, solved: false, solves: 15 },
      { id: 13, title: 'Web Chal 8', difficulty: 'Facile', points: 100, solved: false, solves: 10 },
      { id: 14, title: 'Web Chal 9', difficulty: 'Facile', points: 100, solved: false, solves: 5 },
    ]
  },
  {
    name: 'PWN', isCollapsed: false,
    challenges: [
      { id: 4, title: 'Buffer Overflow 101', difficulty: 'Facile', points: 100, solved: true, solves: 60 },
      { id: 5, title: 'ROP Chain', difficulty: 'Moyen', points: 300, solved: true, solves: 25 },
      { id: 6, title: 'Heap Exploitation', difficulty: 'Insane', points: 1000, solved: false, solves: 1 },
    ]
  },
  {
    name: 'REVERSE', isCollapsed: false,
    challenges: [
      { id: 15, title: 'CrackMe 1', difficulty: 'Facile', points: 100, solved: false, solves: 30 },
    ]
  }
])

const activeFilter = ref('ALL')
const filterList = computed(() => ['ALL', ...categoriesData.value.map(c => c.name)])

// --- LOGIQUE DE FILTRAGE ---
const filteredCategories = computed(() => {
  if (activeFilter.value === 'ALL') return categoriesData.value
  return categoriesData.value.filter(cat => cat.name === activeFilter.value)
})

// --- PERSISTANCE ---
onMounted(() => {
  const savedState = localStorage.getItem(STORAGE_KEY)
  if (savedState) {
    const parsed = JSON.parse(savedState)
    categoriesData.value.forEach(cat => {
      if (parsed[cat.name] !== undefined) cat.isCollapsed = parsed[cat.name]
    })
  }
})

const toggleCategory = (cat) => {
  cat.isCollapsed = !cat.isCollapsed
  const stateToSave = {}
  categoriesData.value.forEach(c => stateToSave[c.name] = c.isCollapsed)
  localStorage.setItem(STORAGE_KEY, JSON.stringify(stateToSave))
}

const getProgress = (challenges) => {
  if (!challenges.length) return 0
  return Math.round((challenges.filter(c => c.solved).length / challenges.length) * 100)
}

const goToChallenge = (id) => {
  router.push(`/challenges/${id}`)
}
</script>

<template>
  <div class="w-full animate-fade-in pb-20 px-6">
    
    <div class="mb-10">
      <h1 class="block w-full text-center text-3xl font-cyber font-bold bg-primary text-base-100 py-3 uppercase tracking-widest shadow-sm">
        Challenges
      </h1>
    </div>

    <div class="flex flex-col md:flex-row justify-between items-center gap-4 bg-base-200/50 backdrop-blur-md p-4 rounded-xl border border-base-300 mb-10">
      <span class="text-sm font-cyber opacity-60 uppercase tracking-widest">Filtrer par catégorie :</span>
      <div class="flex flex-wrap gap-2 justify-center">
        <button 
          v-for="filter in filterList" :key="filter"
          @click="activeFilter = filter"
          :class="['btn btn-sm font-mono px-6', activeFilter === filter ? 'btn-primary' : 'btn-ghost border border-base-content/10']"
        >
          {{ filter }}
        </button>
      </div>
    </div>

    <div class="space-y-12">
      <div v-for="cat in filteredCategories" :key="cat.name" class="w-full">
        
        <div class="flex flex-col sm:flex-row justify-between items-center py-4 border-b border-primary/40 gap-4 cursor-pointer hover:bg-primary/5 transition-all px-4 rounded-t-lg bg-base-200/30"
             @click="toggleCategory(cat)">
          
          <div class="flex items-center gap-4">
            <h2 class="text-2xl font-cyber text-primary tracking-widest">{{ cat.name }}</h2>
            <div class="badge badge-outline opacity-50 font-mono">{{ cat.challenges.length }}</div>
          </div>
          
          <div class="flex items-center gap-6">
            <div class="flex items-center gap-3">
              <progress class="progress progress-primary w-32 md:w-48 bg-base-300" :value="getProgress(cat.challenges)" max="100"></progress>
              <span class="font-mono text-sm opacity-80 w-10 text-right">{{ getProgress(cat.challenges) }}%</span>
            </div>
            <button class="btn btn-sm btn-ghost btn-circle transition-transform duration-300" :class="{ 'rotate-180': cat.isCollapsed }">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" /></svg>
            </button>
          </div>
        </div>

        <transition name="expand">
          <div v-show="!cat.isCollapsed" class="overflow-hidden">
            <div class="grid grid-cols-1 xl:grid-cols-4 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-7 2xl:grid-cols-8 gap-4 py-8">
              <ChallengeCard 
                v-for="chal in cat.challenges" 
                :key="chal.id" 
                :challenge="chal" 
                @open="goToChallenge"
              />
            </div>
          </div>
        </transition>

      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-fade-in { animation: fadeIn 0.4s ease-out forwards; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

/* ANIMATION EXPAND (Conserve l'effet fluide) */
.expand-enter-active, .expand-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  max-height: 2000px; /* Augmenté pour les très grandes listes */
}
.expand-enter-from, .expand-leave-to {
  max-height: 0;
  opacity: 0;
  transform: translateY(-10px);
}

/* Custom Grid pour gérer le 8 colonnes proprement */
@media (min-width: 1920px) {
  .grid-cols-8 {
    grid-template-columns: repeat(8, minmax(0, 1fr));
  }
}
</style>