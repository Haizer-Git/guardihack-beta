<template>
  <PageTitle text="Notifications" />

  <div class="text-base-content antialiased md:p-8">
    <div class="max-w-6xl mx-auto flex flex-col md:flex-row gap-6 items-start">

      <!-- Menu de filtres (à gauche) -->
      <div class="w-full md:w-64 bg-base-300 border-[2px] border-base-200 p-4 shrink-0 rounded-sm">
        <h2 class="font-titre font-bold text-xs uppercase tracking-wider text-base-content/50 px-3 py-1 mb-2">
          Filtres
        </h2>

        <nav class="flex flex-col gap-1 font-text text-sm">
            <button @click="activeFilter = 'unread'"
            class="flex items-center justify-between px-3 py-2.5 rounded-sm transition-colors text-left font-bold cursor-pointer"
            :class="activeFilter === 'unread' ? 'bg-primary text-primary-content' : 'hover:bg-base-200 text-base-content/80'">
            <span class="flex items-center gap-2">Non lues</span>
            <span class="badge badge-sm badge-error" :class="activeFilter === 'unread' ? 'text-white' : ''">
              {{ counts.unread }}
            </span>
          </button>

          <div class="border-t border-base-200 my-1"></div>

          <button @click="activeFilter = 'all'"
            class="flex items-center justify-between px-3 py-2.5 rounded-sm transition-colors text-left font-bold cursor-pointer"
            :class="activeFilter === 'all' ? 'bg-primary text-primary-content' : 'hover:bg-base-200 text-base-content/80'">
            <span class="flex items-center gap-2">Toutes</span>
            <span class="badge badge-sm" :class="activeFilter === 'all' ? 'badge-ghost' : 'bg-base-200 border-none'">
              {{ counts.all }}
            </span>
          </button>

          <button @click="activeFilter = 'global'"
            class="flex items-center justify-between px-3 py-2.5 rounded-sm transition-colors text-left font-bold cursor-pointer"
            :class="activeFilter === 'global' ? 'bg-primary text-primary-content' : 'hover:bg-base-200 text-base-content/80'">
            <span class="flex items-center gap-2">Globales</span>
            <span class="badge badge-sm" :class="activeFilter === 'global' ? 'badge-ghost' : 'bg-base-200 border-none'">
              {{ counts.global }}
            </span>
          </button>

          <button @click="activeFilter = 'personal'"
            class="flex items-center justify-between px-3 py-2.5 rounded-sm transition-colors text-left font-bold cursor-pointer"
            :class="activeFilter === 'personal' ? 'bg-primary text-primary-content' : 'hover:bg-base-200 text-base-content/80'">
            <span class="flex items-center gap-2">Personnelles</span>
            <span class="badge badge-sm" :class="activeFilter === 'personal' ? 'badge-ghost' : 'bg-base-200 border-none'">
              {{ counts.personal }}
            </span>
          </button>


        </nav>
      </div>

      <!-- Liste des notifications (à droite) -->
      <div class="flex-1 w-full space-y-4">

        <div v-if="isLoading" class="flex justify-center p-10 bg-base-300 border border-base-200">
          <span class="loading loading-spinner text-primary"></span>
        </div>

        <div v-else-if="filteredNotifications.length === 0" class="bg-base-300 border border-base-200 p-10 text-center text-base-content/50 font-text">
          Aucune notification dans cette catégorie.
        </div>

        <div v-else v-for="notif in filteredNotifications" :key="notif.id + notif.type"
          class="relative flex flex-col md:flex-row gap-4 p-5 md:items-center border-[2px] transition-all duration-200"
          :class="notif.is_read ? 'bg-base-100 border-base-300 opacity-70' : 'bg-base-300 border-primary/20 shadow-lg hover:border-primary'">          

          <!-- Contenu -->
          <div class="flex-1 space-y-1">
            <div class="flex flex-col md:flex-row md:items-center gap-2">
              <h3 class="font-titre font-bold uppercase tracking-wide" :class="notif.is_read ? 'text-base-content/80' : 'text-primary'">
                {{ notif.title || 'Notification Système' }}
              </h3>
              <span class="badge badge-sm rounded-sm font-code text-[10px]" :class="notif.type === 'global' ? 'badge-secondary' : 'badge-accent'">
                {{ notif.type === 'global' ? 'Globale' : 'Personnelle' }}
              </span>
            </div>
            <p class="font-text text-sm text-base-content/80 leading-relaxed">{{ notif.message }}</p>
            <p class="font-code text-xs text-base-content/40">{{ formatDate(notif.created_at) }}</p>
          </div>

          <!-- Actions -->
          <div class="flex-shrink-0 flex md:flex-col gap-2 justify-end mt-2 md:mt-0">
            <button @click="toggleReadStatus(notif)" class="btn btn-sm btn-outline rounded-sm font-titre text-xs uppercase tracking-wider w-full md:w-auto border-base-content/20 hover:bg-base-content/10">
              {{ notif.is_read ? 'Marquer comme non lu' : 'Marquer comme lu' }}
            </button>
          </div>

        </div>

      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import PageTitle from '../../components/PageTitle.vue'

const notifications = ref([])
const isLoading = ref(true)
const activeFilter = ref('all') // 'all', 'personal', 'global', 'unread'

// Calcul dynamique des compteurs pour le menu
const counts = computed(() => ({
  all: notifications.value.length,
  personal: notifications.value.filter(n => n.type === 'personal').length,
  global: notifications.value.filter(n => n.type === 'global').length,
  unread: notifications.value.filter(n => !n.is_read).length
}))

// Filtrage de la liste selon l'onglet actif
const filteredNotifications = computed(() => {
  if (activeFilter.value === 'personal') {
    return notifications.value.filter(n => n.type === 'personal')
  }
  if (activeFilter.value === 'global') {
    return notifications.value.filter(n => n.type === 'global')
  }
  if (activeFilter.value === 'unread') {
    return notifications.value.filter(n => !n.is_read)
  }
  return notifications.value
})

async function fetchNotifications() {
  isLoading.value = true
  try {
    const { data } = await axios.get('/api/user/notification/all')
    if (data.status === 'success') {
      notifications.value = data.notifications
    }
  } catch (error) {
    console.error('Erreur lors du chargement des notifications :', error)
  } finally {
    isLoading.value = false
  }
}

async function toggleReadStatus(notif) {
  const isGlobal = notif.type === 'global'
  const action = notif.is_read ? 'unread' : 'read'
  const baseUrl = isGlobal ? '/api/user/notification/global' : '/api/user/notification'
  const url = `${baseUrl}/${notif.id}/${action}`

  try {
    notif.is_read = !notif.is_read
    await axios.post(url)
  } catch (error) {
    notif.is_read = !notif.is_read
    console.error('Erreur de mise à jour du statut :', error)
  }
}

function formatDate(dateString) {
  if (!dateString) return 'Date inconnue'
  const date = new Date(dateString)
  return date.toLocaleString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).replace(':', 'h')
}

onMounted(() => {
  fetchNotifications()
})
</script>