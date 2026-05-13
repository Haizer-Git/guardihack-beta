<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const machineId = route.params.id

const machine = ref({
  id: machineId,
  name: 'NetMaster',
  difficulty: 'Moyen',
  category: 'NETWORK',
  points: 250,
  solved: false,
  solves: 23,
  description: 'Exploitez les failles réseau pour obtenir l\'accès root. Configuration défaillante, protocols non sécurisés.',
  ip: '10.10.10.45',
  os: 'Linux Ubuntu 20.04',
  services: [
    { port: 22, service: 'SSH', version: 'OpenSSH 7.4' },
    { port: 80, service: 'HTTP', version: 'Apache 2.4.6' },
    { port: 443, service: 'HTTPS', version: 'Apache 2.4.6' },
    { port: 3306, service: 'MySQL', version: '5.7.20' }
  ],
  hints: [
    { id: 1, title: 'Énumération', content: 'Commencez par scanner l\'adresse IP pour découvrir les ports ouverts.', revealed: false },
    { id: 2, title: 'HTTP', content: 'Explorez le service HTTP sur le port 80. Il y a une page d\'administration...', revealed: false },
    { id: 3, title: 'Base de Données', content: 'Les identifiants MySQL sont faibles. Essayez root:root', revealed: false }
  ],
  writeupRequired: true,
  timeLimit: '∞',
  status: 'En cours...'
})

const myProgress = ref({
  stepsCompleted: 1,
  totalSteps: 4,
  lastAttempt: '2026-05-13 14:30'
})

const showHint = (hintId) => {
  const hint = machine.value.hints.find(h => h.id === hintId)
  if (hint) {
    hint.revealed = !hint.revealed
  }
}
</script>

<template>
  <div class="w-full animate-fade-in pb-20 px-4 max-w-6xl mx-auto">

    <!-- ENTÊTE -->
    <div class="mb-10">
      <router-link to="/tracks" class="btn btn-sm btn-ghost font-mono gap-1 mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        Retour
      </router-link>
      
      <div class="card bg-gradient-to-r from-primary/20 to-secondary/20 border border-primary/50 mb-8">
        <div class="card-body">
          <div class="flex justify-between items-start gap-8">
            <div>
              <h1 class="text-4xl font-cyber font-bold">{{ machine.name }}</h1>
              <p class="text-base-content/70 font-mono mt-2">
                {{ machine.category }} • {{ machine.difficulty }} • {{ machine.points }} pts
              </p>
            </div>
            <div class="text-right">
              <p class="text-sm opacity-60">Résolutions</p>
              <p class="text-3xl font-bold text-primary">{{ machine.solves }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">

      <!-- COLONNE PRINCIPAL -->
      <div class="lg:col-span-2 space-y-8">

        <!-- DESCRIPTION -->
        <div class="card bg-base-200/50 border border-base-300">
          <div class="card-body">
            <h2 class="card-title font-cyber">Description</h2>
            <p class="leading-relaxed">{{ machine.description }}</p>
          </div>
        </div>

        <!-- INFORMATIONS MACHINE -->
        <div class="card bg-base-200/50 border border-base-300">
          <div class="card-body">
            <h2 class="card-title font-cyber">Informations Techniques</h2>
            <div class="overflow-x-auto">
              <table class="table table-sm">
                <tr>
                  <td class="font-bold">Adresse IP</td>
                  <td class="font-mono">{{ machine.ip }}</td>
                </tr>
                <tr>
                  <td class="font-bold">Système d'exploitation</td>
                  <td>{{ machine.os }}</td>
                </tr>
              </table>
            </div>
          </div>
        </div>

        <!-- SERVICES DÉTECTÉS -->
        <div class="card bg-base-200/50 border border-base-300">
          <div class="card-body">
            <h2 class="card-title font-cyber">Services Détectés</h2>
            <div class="space-y-2">
              <div v-for="service in machine.services" :key="service.port" class="p-3 bg-base-100/50 rounded border border-base-300">
                <p class="font-bold">{{ service.service }} (Port {{ service.port }})</p>
                <p class="text-sm opacity-60">{{ service.version }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- INDICES -->
        <div class="card bg-base-200/50 border border-base-300">
          <div class="card-body">
            <h2 class="card-title font-cyber">Indices 💡</h2>
            <div class="space-y-3">
              <div v-for="hint in machine.hints" :key="hint.id" class="collapse collapse-arrow border border-base-300">
                <input type="checkbox" @click="showHint(hint.id)" />
                <div class="collapse-title font-bold">
                  <span class="badge badge-sm badge-outline mr-2">{{ hint.id }}</span>
                  {{ hint.title }}
                </div>
                <div v-if="hint.revealed" class="collapse-content">
                  <p class="pt-4 text-sm bg-warning/10 p-3 rounded">{{ hint.content }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>

      <!-- SIDEBAR -->
      <div class="space-y-6">

        <!-- STATUT -->
        <div class="card bg-base-200/50 border border-base-300">
          <div class="card-body">
            <h3 class="card-title text-sm font-cyber">Statut</h3>
            <div class="space-y-3">
              <div>
                <p class="text-xs opacity-60 uppercase tracking-widest">Progression</p>
                <progress class="progress progress-primary w-full" :value="myProgress.stepsCompleted" :max="myProgress.totalSteps"></progress>
                <p class="text-xs text-center mt-1 opacity-60">{{ myProgress.stepsCompleted }}/{{ myProgress.totalSteps }} étapes</p>
              </div>
              <p class="text-xs font-mono opacity-60">Dernier essai: {{ myProgress.lastAttempt }}</p>
            </div>
          </div>
        </div>

        <!-- START BUTTON -->
        <button class="btn btn-primary w-full btn-lg font-cyber">
          🚀 Accéder à la Machine
        </button>

        <!-- REQUIREMENTS -->
        <div class="card bg-base-200/50 border border-base-300">
          <div class="card-body">
            <h3 class="card-title text-sm font-cyber">Conditions</h3>
            <ul class="list-disc list-inside text-xs space-y-1 opacity-70">
              <li>VPN connecté</li>
              <li>Outils de pentesting installés</li>
              <li>Rapport/Write-up {{ machine.writeupRequired ? 'requis' : 'optionnel' }}</li>
              <li>Délai: {{ machine.timeLimit }}</li>
            </ul>
          </div>
        </div>

        <!-- SUBMISSION -->
        <div class="card bg-base-200/50 border border-primary/50">
          <div class="card-body">
            <h3 class="card-title text-sm font-cyber text-primary">Soumettre le Flag</h3>
            <input type="text" placeholder="Entrez le flag..." class="input input-bordered input-sm w-full mb-2" />
            <button class="btn btn-primary btn-sm w-full">✓ Valider</button>
          </div>
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
