<script setup>
import { ref, computed } from 'vue'

const searchQuery = ref('')
const activeFilter = ref('ALL')

// Données des groupes avec membres
const groups = ref([
  {
    id: 1,
    name: 'Red Team',
    image: 'https://api.dicebear.com/7.x/bottts/svg?seed=redteam',
    color: 'text-error',
    members: [
      { id: 1, username: 'Vex_Root', level: 42, points: 2500, avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Vex_Root' },
      { id: 2, username: '0xGhost', level: 38, points: 2100, avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=0xGhost' },
      { id: 3, username: 'CyberSlayer', level: 35, points: 1850, avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=CyberSlayer' },
      { id: 4, username: 'Alice_In_Pwn', level: 30, points: 1600, avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Alice_In_Pwn' },
      { id: 5, username: 'Bob_The_Hacker', level: 28, points: 1400, avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Bob_The_Hacker' }
    ]
  },
  {
    id: 2,
    name: 'Blue Squad',
    image: 'https://api.dicebear.com/7.x/bottts/svg?seed=blueteam',
    color: 'text-info',
    members: [
      { id: 6, username: 'NullPointer', level: 25, points: 1250, avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=NullPointer' },
      { id: 7, username: 'Root_Me', level: 22, points: 1100, avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Root_Me' },
      { id: 8, username: 'ScriptKiddie', level: 18, points: 950, avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=ScriptKiddie' },
      { id: 9, username: 'Flag_Hunter', level: 15, points: 800, avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Flag_Hunter' },
      { id: 10, username: 'BufferOver', level: 14, points: 750, avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=BufferOver' }
    ]
  },
  {
    id: 3,
    name: 'Green Hackers',
    image: 'https://api.dicebear.com/7.x/bottts/svg?seed=greenteam',
    color: 'text-success',
    members: [
      { id: 11, username: 'Cracker', level: 28, points: 1350, avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Cracker' },
      { id: 12, username: 'Phisher', level: 26, points: 1200, avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Phisher' },
      { id: 13, username: 'Exploit_Dev', level: 31, points: 1700, avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Exploit_Dev' },
      { id: 14, username: 'Memory_Leak', level: 24, points: 1000, avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Memory_Leak' },
      { id: 15, username: 'Shellcode', level: 29, points: 1450, avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Shellcode' }
    ]
  },
  {
    id: 4,
    name: 'Purple Crew',
    image: 'https://api.dicebear.com/7.x/bottts/svg?seed=purpleteam',
    color: 'text-secondary',
    members: [
      { id: 16, username: 'Fuzzer', level: 32, points: 1800, avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Fuzzer' },
      { id: 17, username: 'Patched', level: 20, points: 850, avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Patched' },
      { id: 18, username: 'Scanner', level: 27, points: 1300, avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Scanner' },
      { id: 19, username: 'Stealthy', level: 33, points: 1950, avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Stealthy' },
      { id: 20, username: 'Reverse_', level: 30, points: 1600, avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Reverse_' }
    ]
  }
])

const filteredGroups = computed(() => {
  return groups.value.filter(group => 
    group.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})
</script>

<template>
  <div class="w-full animate-fade-in pb-20 px-4 max-w-[1600px] mx-auto font-sans">

    <div class="mb-10">
      <h1 class="block w-full text-center text-3xl font-cyber font-bold bg-primary text-base-100 py-3 uppercase tracking-widest shadow-sm">
        Groupes
      </h1>
    </div>

    <!-- RECHERCHE -->
    <div class="mb-10 flex justify-center">
      <input 
        v-model="searchQuery" 
        type="text" 
        placeholder="Chercher un groupe..." 
        class="input input-bordered input-lg w-full max-w-md font-mono"
      />
    </div>

    <!-- GRILLE DE GROUPES -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-8">
      <div v-for="group in filteredGroups" :key="group.id" class="card bg-base-200/50 border border-base-300 hover:border-primary/50 transition-all hover:shadow-lg">
        
        <!-- En-tête du groupe -->
        <div class="relative h-32 bg-gradient-to-r from-primary/20 to-secondary/20 border-b border-base-300 overflow-hidden">
          <img :src="group.image" :alt="group.name" class="w-full h-full object-cover opacity-30" />
          <div class="absolute inset-0 flex items-center justify-center">
            <div class="text-center">
              <div class="text-5xl font-cyber font-black" :class="group.color">{{ group.name[0] }}</div>
              <h2 class="text-2xl font-cyber font-bold mt-2">{{ group.name }}</h2>
            </div>
          </div>
        </div>

        <!-- Contenu du groupe -->
        <div class="card-body">
          
          <!-- Membres -->
          <div class="space-y-3">
            <h3 class="font-bold text-sm uppercase tracking-widest opacity-60">Membres ({{ group.members.length }}/5)</h3>
            
            <div class="space-y-2">
              <div v-for="member in group.members" :key="member.id" class="flex items-center justify-between p-2 bg-base-100/50 rounded hover:bg-base-100 transition-colors">
                <div class="flex items-center gap-3 flex-1">
                  <img :src="member.avatar" :alt="member.username" class="w-8 h-8 rounded-full" />
                  <div class="min-w-0 flex-1">
                    <p class="font-mono text-sm font-bold truncate">{{ member.username }}</p>
                    <p class="text-xs text-base-content/60">LVL {{ member.level }}</p>
                  </div>
                </div>
                <div class="text-right">
                  <p class="font-mono text-sm font-bold text-primary">{{ member.points }}</p>
                  <p class="text-xs text-base-content/60">pts</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Stats du groupe -->
          <div class="grid grid-cols-3 gap-2 mt-4 pt-4 border-t border-base-300">
            <div class="text-center">
              <p class="font-bold text-lg text-primary">{{ group.members.reduce((sum, m) => sum + m.points, 0) }}</p>
              <p class="text-xs opacity-60">Total Pts</p>
            </div>
            <div class="text-center">
              <p class="font-bold text-lg text-secondary">{{ Math.round(group.members.reduce((sum, m) => sum + m.level, 0) / group.members.length) }}</p>
              <p class="text-xs opacity-60">LVL Moy</p>
            </div>
            <div class="text-center">
              <p class="font-bold text-lg text-accent">{{ group.members.length }}</p>
              <p class="text-xs opacity-60">Membres</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Aucun résultat -->
    <div v-if="filteredGroups.length === 0" class="flex flex-col items-center justify-center min-h-[40vh]">
      <div class="text-6xl mb-4">🔍</div>
      <p class="text-base-content/60 font-mono">Aucun groupe trouvé</p>
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
</style>
