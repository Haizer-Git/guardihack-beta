<script setup>
import { ref } from 'vue'

const userProfile = ref({
  username: 'GUARDIAROOT',
  level: 42,
  email: 'guardiaroot@guardiahack.ctf',
  joinDate: '2026-01-15',
  totalPoints: 2500,
  challengesSolved: 28,
  bestRank: 1,
  currentRank: 1,
  avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=GUARDIAROOT',
  bio: 'Cybersecurity enthusiast and CTF champion. Always learning, always hacking.',
  group: 'Red Team',
  achievements: [
    { id: 1, name: 'First Blood', description: 'Resoudre le premier challenge', unlocked: true, icon: '🩸' },
    { id: 2, name: 'Hacker Pro', description: '50 challenges résolus', unlocked: true, icon: '👾' },
    { id: 3, name: 'Top 10', description: 'Être classé dans le top 10', unlocked: true, icon: '🏆' },
    { id: 4, name: 'Master', description: '100 challenges résolus', unlocked: false, icon: '👑' },
    { id: 5, name: 'Legendary', description: 'Score ultime de 10000', unlocked: false, icon: '⚡' },
    { id: 6, name: 'Night Owl', description: 'Resoudre 5 challenges après minuit', unlocked: false, icon: '🌙' }
  ]
})

const stats = [
  { label: 'Challenges Résolus', value: userProfile.value.challengesSolved, icon: '✅' },
  { label: 'Points Totaux', value: userProfile.value.totalPoints, icon: '⭐' },
  { label: 'Classement', value: userProfile.value.currentRank, icon: '🏅' },
  { label: 'Niveau', value: userProfile.value.level, icon: '📈' }
]

const recentSolves = ref([
  { id: 1, title: 'SQLi Bypasser', category: 'WEB', points: 100, solvedAt: '2026-05-13 14:32' },
  { id: 2, title: 'XSS to Admin', category: 'WEB', points: 300, solvedAt: '2026-05-12 11:15' },
  { id: 3, title: 'Buffer Overflow 101', category: 'PWN', points: 100, solvedAt: '2026-05-11 09:45' }
])
</script>

<template>
  <div class="w-full animate-fade-in pb-20 px-4 max-w-6xl mx-auto">
    
    <!-- PROFIL HEADER -->
    <div class="card bg-gradient-to-r from-primary/20 to-secondary/20 border border-primary/50 mb-10 overflow-hidden">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8 p-8">
        
        <!-- Avatar et Info Principale -->
        <div class="flex flex-col items-center md:items-start gap-4">
          <img :src="userProfile.avatar" :alt="userProfile.username" class="w-32 h-32 rounded-lg border-4 border-primary shadow-lg" />
          <div>
            <h1 class="text-3xl font-cyber font-bold">{{ userProfile.username }}</h1>
            <p class="text-primary font-mono uppercase tracking-widest">LVL {{ userProfile.level }}</p>
            <p class="text-sm opacity-70 mt-2">{{ userProfile.bio }}</p>
          </div>
        </div>

        <!-- Stats principales -->
        <div class="grid grid-cols-2 gap-4">
          <div v-for="stat in stats" :key="stat.label" class="flex flex-col items-center p-4 bg-base-200/50 rounded border border-base-300">
            <span class="text-2xl mb-1">{{ stat.icon }}</span>
            <p class="font-bold text-lg">{{ stat.value }}</p>
            <p class="text-xs text-center opacity-60">{{ stat.label }}</p>
          </div>
        </div>

        <!-- Groupe et Actions -->
        <div class="flex flex-col justify-between">
          <div class="space-y-4">
            <div class="p-4 bg-base-200/50 rounded border border-base-300">
              <p class="text-xs opacity-60 uppercase tracking-widest mb-1">Groupe</p>
              <p class="font-bold">{{ userProfile.group }}</p>
            </div>
            <div class="p-4 bg-base-200/50 rounded border border-base-300">
              <p class="text-xs opacity-60 uppercase tracking-widest mb-1">Membre depuis</p>
              <p class="font-mono text-sm">{{ userProfile.joinDate }}</p>
            </div>
          </div>
          <router-link to="/profile/settings" class="btn btn-primary btn-sm w-full font-cyber">
            ⚙️ Paramètres
          </router-link>
        </div>
      </div>
    </div>

    <!-- ACCOMPLISSEMENTS -->
    <section class="mb-10">
      <h2 class="text-2xl font-cyber font-bold mb-6 uppercase tracking-widest">Accomplissements</h2>
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div v-for="achievement in userProfile.achievements" :key="achievement.id" 
          :class="['p-4 rounded-lg text-center border-2 transition-all', 
            achievement.unlocked ? 'bg-base-200/50 border-primary/50 hover:shadow-lg hover:shadow-primary/20' : 'bg-base-300/30 border-base-300/30 opacity-50']">
          <div class="text-4xl mb-2">{{ achievement.icon }}</div>
          <p class="font-bold text-sm">{{ achievement.name }}</p>
          <p class="text-xs opacity-60">{{ achievement.description }}</p>
        </div>
      </div>
    </section>

    <!-- RÉSOLUTIONS RÉCENTES -->
    <section>
      <h2 class="text-2xl font-cyber font-bold mb-6 uppercase tracking-widest">Challenges Récents</h2>
      <div class="space-y-3">
        <div v-for="solve in recentSolves" :key="solve.id" class="card bg-base-200/50 border border-base-300 hover:border-primary/50 transition-all">
          <div class="card-body p-4">
            <div class="flex justify-between items-center">
              <div class="flex-1">
                <h3 class="font-bold">{{ solve.title }}</h3>
                <p class="text-sm opacity-60">{{ solve.category }} • {{ solve.solvedAt }}</p>
              </div>
              <div class="text-right">
                <p class="font-bold text-primary">+{{ solve.points }}</p>
                <p class="text-xs opacity-60">points</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
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
