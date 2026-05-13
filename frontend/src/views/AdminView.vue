<script setup>
import { ref } from 'vue'

const adminStats = ref({
  totalUsers: 1337,
  totalTeams: 12,
  totalChallenges: 42,
  totalSubmissions: 5432,
  ctfStatus: 'En cours',
  uptime: '99.8%'
})

const recentViolations = ref([
  { id: 1, user: 'SpamBot', violation: 'Brute force', severity: 'high', time: '2026-05-13 14:32', action: 'pending' },
  { id: 2, user: 'Cheater123', violation: 'Flag partage', severity: 'critical', time: '2026-05-13 13:15', action: 'banned' },
  { id: 3, user: 'NoobHacker', violation: 'Langage abusif', severity: 'medium', time: '2026-05-13 11:00', action: 'warning' }
])

const activeTab = ref('overview')
</script>

<template>
  <div class="w-full animate-fade-in pb-20 px-4 max-w-7xl mx-auto">

    <div class="mb-10">
      <h1 class="block w-full text-center text-3xl font-cyber font-bold bg-error text-base-100 py-3 uppercase tracking-widest shadow-sm">
        🛡️ Panneau Admin
      </h1>
    </div>

    <!-- TABS DE NAVIGATION -->
    <div class="tabs tabs-bordered mb-8 bg-base-200/50 p-2 rounded">
      <button 
        @click="activeTab = 'overview'"
        :class="['tab font-cyber font-bold', activeTab === 'overview' ? 'tab-active' : '']"
      >
        Aperçu
      </button>
      <button 
        @click="activeTab = 'users'"
        :class="['tab font-cyber font-bold', activeTab === 'users' ? 'tab-active' : '']"
      >
        Utilisateurs
      </button>
      <button 
        @click="activeTab = 'violations'"
        :class="['tab font-cyber font-bold', activeTab === 'violations' ? 'tab-active' : '']"
      >
        Violations
      </button>
      <button 
        @click="activeTab = 'settings'"
        :class="['tab font-cyber font-bold', activeTab === 'settings' ? 'tab-active' : '']"
      >
        Configuration
      </button>
    </div>

    <!-- CONTENU DES TABS -->
    
    <!-- OVERVIEW -->
    <div v-show="activeTab === 'overview'" class="space-y-8">
      
      <!-- STAT CARDS -->
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div class="card bg-base-200/50 border border-primary/30">
          <div class="card-body p-4 text-center">
            <p class="text-2xl font-bold text-primary">{{ adminStats.totalUsers }}</p>
            <p class="text-xs opacity-60 uppercase tracking-widest">Utilisateurs</p>
          </div>
        </div>
        <div class="card bg-base-200/50 border border-secondary/30">
          <div class="card-body p-4 text-center">
            <p class="text-2xl font-bold text-secondary">{{ adminStats.totalTeams }}</p>
            <p class="text-xs opacity-60 uppercase tracking-widest">Équipes</p>
          </div>
        </div>
        <div class="card bg-base-200/50 border border-accent/30">
          <div class="card-body p-4 text-center">
            <p class="text-2xl font-bold text-accent">{{ adminStats.totalChallenges }}</p>
            <p class="text-xs opacity-60 uppercase tracking-widest">Challenges</p>
          </div>
        </div>
        <div class="card bg-base-200/50 border border-warning/30">
          <div class="card-body p-4 text-center">
            <p class="text-2xl font-bold text-warning">{{ adminStats.totalSubmissions }}</p>
            <p class="text-xs opacity-60 uppercase tracking-widest">Submissions</p>
          </div>
        </div>
        <div class="card bg-base-200/50 border border-success/30">
          <div class="card-body p-4 text-center">
            <p class="text-2xl font-bold text-success">{{ adminStats.uptime }}</p>
            <p class="text-xs opacity-60 uppercase tracking-widest">Uptime</p>
          </div>
        </div>
        <div class="card bg-base-200/50 border border-info/30">
          <div class="card-body p-4 text-center">
            <p class="text-2xl font-bold text-info">{{ adminStats.ctfStatus }}</p>
            <p class="text-xs opacity-60 uppercase tracking-widest">Statut</p>
          </div>
        </div>
      </div>

      <!-- ACTIONS RAPIDES -->
      <div class="card bg-base-200/50 border border-base-300">
        <div class="card-body">
          <h2 class="card-title font-cyber">Actions Rapides</h2>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <button class="btn btn-outline btn-sm">📋 Générer Rapport</button>
            <button class="btn btn-outline btn-sm">🔄 Redémarrer Serveurs</button>
            <button class="btn btn-outline btn-sm">📊 Exporter Stats</button>
            <button class="btn btn-outline btn-sm">🔔 Broadcast Message</button>
          </div>
        </div>
      </div>

      <!-- ACTIVITÉ RÉCENTE -->
      <div class="card bg-base-200/50 border border-base-300">
        <div class="card-body">
          <h2 class="card-title font-cyber">Activité Récente</h2>
          <div class="space-y-2 max-h-64 overflow-y-auto">
            <div class="p-3 bg-base-100/50 rounded text-sm font-mono">
              <span class="text-primary">[14:32]</span> Utilisateur 'Vex_Root' a résolu 'SQLi Bypasser'
            </div>
            <div class="p-3 bg-base-100/50 rounded text-sm font-mono">
              <span class="text-info">[14:15]</span> Équipe 'Red Team' a pris la 1ère place
            </div>
            <div class="p-3 bg-base-100/50 rounded text-sm font-mono">
              <span class="text-warning">[13:45]</span> Alerte: Brute force détecté sur port 22
            </div>
            <div class="p-3 bg-base-100/50 rounded text-sm font-mono">
              <span class="text-success">[13:20]</span> Serveur MySQL redémarré avec succès
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- USERS -->
    <div v-show="activeTab === 'users'" class="space-y-6">
      <div class="card bg-base-200/50 border border-base-300">
        <div class="card-body">
          <h2 class="card-title font-cyber mb-6">Gestion des Utilisateurs</h2>
          <input type="text" placeholder="Rechercher un utilisateur..." class="input input-bordered w-full mb-6" />
          <div class="overflow-x-auto">
            <table class="table">
              <thead>
                <tr>
                  <th>Utilisateur</th>
                  <th>Email</th>
                  <th>Équipe</th>
                  <th>Points</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>Vex_Root</strong></td>
                  <td>vex@guardiahack.ctf</td>
                  <td>Red Team</td>
                  <td>2500</td>
                  <td><button class="btn btn-ghost btn-xs">Détails</button></td>
                </tr>
                <tr>
                  <td><strong>0xGhost</strong></td>
                  <td>ghost@guardiahack.ctf</td>
                  <td>Red Team</td>
                  <td>2100</td>
                  <td><button class="btn btn-ghost btn-xs">Détails</button></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- VIOLATIONS -->
    <div v-show="activeTab === 'violations'" class="space-y-6">
      <div class="card bg-base-200/50 border border-base-300">
        <div class="card-body">
          <h2 class="card-title font-cyber mb-6 text-error">Violations Détectées</h2>
          <div class="space-y-3">
            <div v-for="violation in recentViolations" :key="violation.id" class="p-4 bg-base-100/50 rounded border-l-4" :class="violation.severity === 'critical' ? 'border-error' : violation.severity === 'high' ? 'border-warning' : 'border-info'">
              <div class="flex justify-between items-start">
                <div>
                  <p class="font-bold">{{ violation.user }}</p>
                  <p class="text-sm opacity-70">{{ violation.violation }} • {{ violation.time }}</p>
                </div>
                <div class="flex gap-2">
                  <span class="badge" :class="violation.severity === 'critical' ? 'badge-error' : violation.severity === 'high' ? 'badge-warning' : 'badge-info'">
                    {{ violation.severity }}
                  </span>
                  <span v-if="violation.action === 'pending'" class="badge badge-warning">En attente</span>
                  <span v-else-if="violation.action === 'banned'" class="badge badge-error">Banni</span>
                  <span v-else class="badge badge-info">Avertissement</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- SETTINGS -->
    <div v-show="activeTab === 'settings'" class="space-y-6">
      <div class="card bg-base-200/50 border border-base-300">
        <div class="card-body">
          <h2 class="card-title font-cyber">Configuration du CTF</h2>
          <div class="space-y-4 divider-y">
            <div>
              <label class="label">
                <span class="label-text font-bold">Nom du CTF</span>
              </label>
              <input type="text" value="GuardiHack CTF 2026" class="input input-bordered w-full" />
            </div>
            <div>
              <label class="label">
                <span class="label-text font-bold">Statut</span>
              </label>
              <select class="select select-bordered w-full">
                <option>En cours</option>
                <option>Pause</option>
                <option>Terminé</option>
              </select>
            </div>
            <div>
              <label class="label">
                <span class="label-text font-bold">Limite de soumissions par jour</span>
              </label>
              <input type="number" value="100" class="input input-bordered w-full" />
            </div>
          </div>
          <button class="btn btn-primary mt-6 font-cyber">💾 Sauvegarder</button>
        </div>
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
</style>
