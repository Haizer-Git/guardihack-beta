<script setup>
import { ref } from 'vue'

const settings = ref({
  username: 'GUARDIAROOT',
  email: 'guardiaroot@guardiahack.ctf',
  password: '',
  confirmPassword: '',
  theme: 'dark',
  notifications: {
    email: true,
    browser: true,
    achievements: true
  },
  privacy: {
    showProfile: true,
    showStats: true,
    showAchievements: true
  }
})

const showSuccessMessage = ref(false)

const saveSettings = () => {
  // Simulation de sauvegarde
  showSuccessMessage.value = true
  setTimeout(() => {
    showSuccessMessage.value = false
  }, 3000)
}

const changePassword = () => {
  if (settings.value.password !== settings.value.confirmPassword) {
    alert('Les mots de passe ne correspondent pas')
    return
  }
  alert('Mot de passe changé avec succès!')
  settings.value.password = ''
  settings.value.confirmPassword = ''
}
</script>

<template>
  <div class="w-full animate-fade-in pb-20 px-4 max-w-4xl mx-auto">

    <div class="mb-10">
      <h1 class="block w-full text-center text-3xl font-cyber font-bold bg-primary text-base-100 py-3 uppercase tracking-widest shadow-sm">
        Paramètres de Profil
      </h1>
    </div>

    <!-- Message de succès -->
    <transition name="fade">
      <div v-if="showSuccessMessage" class="alert alert-success mb-6 shadow-lg">
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        <span>Paramètres sauvegardés avec succès!</span>
      </div>
    </transition>

    <div class="grid gap-8">
      
      <!-- INFORMATIONS DE COMPTE -->
      <div class="card bg-base-200/50 border border-base-300">
        <div class="card-body">
          <h2 class="card-title text-xl font-cyber uppercase">Informations du Compte</h2>
          
          <div class="divider"></div>
          
          <div class="space-y-4">
            <div>
              <label class="label">
                <span class="label-text font-bold">Nom d'utilisateur</span>
              </label>
              <input v-model="settings.username" type="text" class="input input-bordered w-full" disabled />
            </div>

            <div>
              <label class="label">
                <span class="label-text font-bold">Email</span>
              </label>
              <input v-model="settings.email" type="email" class="input input-bordered w-full" />
            </div>
          </div>

          <div class="divider my-2"></div>

          <h3 class="font-bold uppercase tracking-widest text-sm">Changer le mot de passe</h3>
          
          <div class="space-y-4">
            <div>
              <label class="label">
                <span class="label-text">Nouveau mot de passe</span>
              </label>
              <input v-model="settings.password" type="password" class="input input-bordered w-full" />
            </div>

            <div>
              <label class="label">
                <span class="label-text">Confirmer le mot de passe</span>
              </label>
              <input v-model="settings.confirmPassword" type="password" class="input input-bordered w-full" />
            </div>

            <button @click="changePassword" class="btn btn-warning btn-sm">
              Changer le mot de passe
            </button>
          </div>
        </div>
      </div>

      <!-- NOTIFICATIONS -->
      <div class="card bg-base-200/50 border border-base-300">
        <div class="card-body">
          <h2 class="card-title text-xl font-cyber uppercase">Notifications</h2>
          
          <div class="divider"></div>

          <div class="space-y-4">
            <div class="flex items-center justify-between p-4 bg-base-100/50 rounded">
              <div>
                <p class="font-bold">Notifications Email</p>
                <p class="text-sm opacity-60">Recevoir des emails sur les mises à jour</p>
              </div>
              <input v-model="settings.notifications.email" type="checkbox" class="checkbox" />
            </div>

            <div class="flex items-center justify-between p-4 bg-base-100/50 rounded">
              <div>
                <p class="font-bold">Notifications du Navigateur</p>
                <p class="text-sm opacity-60">Afficher les notifications du système</p>
              </div>
              <input v-model="settings.notifications.browser" type="checkbox" class="checkbox" />
            </div>

            <div class="flex items-center justify-between p-4 bg-base-100/50 rounded">
              <div>
                <p class="font-bold">Accomplissements</p>
                <p class="text-sm opacity-60">Notifier pour les nouveaux accomplissements</p>
              </div>
              <input v-model="settings.notifications.achievements" type="checkbox" class="checkbox" />
            </div>
          </div>
        </div>
      </div>

      <!-- CONFIDENTIALITÉ -->
      <div class="card bg-base-200/50 border border-base-300">
        <div class="card-body">
          <h2 class="card-title text-xl font-cyber uppercase">Confidentialité</h2>
          
          <div class="divider"></div>

          <div class="space-y-4">
            <div class="flex items-center justify-between p-4 bg-base-100/50 rounded">
              <div>
                <p class="font-bold">Afficher le Profil</p>
                <p class="text-sm opacity-60">Rendre votre profil visible aux autres</p>
              </div>
              <input v-model="settings.privacy.showProfile" type="checkbox" class="checkbox" />
            </div>

            <div class="flex items-center justify-between p-4 bg-base-100/50 rounded">
              <div>
                <p class="font-bold">Afficher les Statistiques</p>
                <p class="text-sm opacity-60">Montrer votre score et votre niveau</p>
              </div>
              <input v-model="settings.privacy.showStats" type="checkbox" class="checkbox" />
            </div>

            <div class="flex items-center justify-between p-4 bg-base-100/50 rounded">
              <div>
                <p class="font-bold">Afficher les Accomplissements</p>
                <p class="text-sm opacity-60">Partager vos badges et réalisations</p>
              </div>
              <input v-model="settings.privacy.showAchievements" type="checkbox" class="checkbox" />
            </div>
          </div>
        </div>
      </div>

      <!-- ACTIONS -->
      <div class="flex gap-4">
        <button @click="saveSettings" class="btn btn-primary btn-lg font-cyber flex-1">
          💾 Sauvegarder les modifications
        </button>
        <router-link to="/profile" class="btn btn-ghost btn-lg font-cyber">
          ← Retour
        </router-link>
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

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
