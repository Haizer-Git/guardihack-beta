<template>
  <div class="w-full animate-fade-in pb-20 px-4 max-w-[1800px] mx-auto">

    <PageTitle text="Joueurs" />

    <div v-if="error" class="alert alert-error shadow-lg mb-6 max-w-2xl mx-auto">
      <span>{{ error }}</span>
    </div>

    <div class="flex flex-col sm:flex-row gap-4 mb-6 w-full">
      <div class="form-control w-full sm:w-64 flex-shrink-0">
        <select v-model="selectedAffiliation" class="select select-bordered w-full bg-base-200 focus:border-primary">
          <option value="">Tous les Campus</option>
          <option value="PARIS">PARIS</option>
          <option value="LYON">LYON</option>
          <option value="BORDEAUX">BORDEAUX</option>
        </select>
      </div>
      <div class="form-control w-full flex-grow">
        <input v-model="searchQuery" type="text" placeholder="Rechercher par nom..."
          class="input input-bordered w-full focus:border-primary" />
      </div>
    </div>

    <div class="overflow-x-auto w-full relative min-h-[400px]">

      <div v-if="loading" class="absolute inset-0 flex justify-center items-start pt-20 bg-base-100/50 z-10">
        <span class="loading loading-spinner loading-lg text-primary"></span>
      </div>

      <table class="table table-zebra w-full">
        <thead>
          <tr class="bg-transparent text-base-content/70 text-sm border-b border-base-content">
            <th class="w-1/2 font-text pb-4">Utilisateur</th>
            <th class="font-text pb-4">Affiliation</th>
            <th class="font-text pb-4">Niveau</th>
            <th class="font-text pb-4">Classe</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in filteredUsers" :key="user.username" class="border-none hover:bg-base-200/50">

            <td class="py-4">
              <div class="flex items-center gap-4">
                <!-- On utilise directement user.avatar renvoyé par l'API -->
                <div class="avatar" v-if="user.avatar">
                  <div class="w-8 h-8 rounded bg-transparent">
                    <img :src="getAssetUrl(user.avatar)" class="max-w-full max-h-full object-contain" :alt="user.username" />
                  </div>
                </div>
                <div class="avatar placeholder" v-else>
                  <div class="bg-neutral text-neutral-content w-8 h-8 rounded flex items-center justify-center">
                    <span class="text-xs font-text font-bold">{{ user.username ? user.username.charAt(0).toUpperCase() :
                      '?'
                      }}</span>
                  </div>
                </div>
                <router-link :to="`/profile/${user.username}`"
                  class="font-code font-bold text-base hover:text-primary duration-200">
                  {{ user.username }}
                </router-link>
              </div>
            </td>

            <td class="py-4 text-base-content/80">
              <span v-if="user.affiliation" class="badge-sm font-text">
                {{ user.affiliation }}
              </span>
              <span v-else class="text-sm opacity-40 italic font-text">N/A</span>
            </td>

            <td class="py-4">
              <span class="text-sm font-code opacity-80">
                {{ user.niveau || 'N/A' }}
              </span>
            </td>
            <td class="py-4">
              <span class="text-sm font-code opacity-80">
                {{ user.classe || 'N/A' }}
              </span>
            </td>
          </tr>

          <tr v-if="!loading && filteredUsers.length === 0">
            <td colspan="3" class="text-center py-16 text-base-content/50 font-medium font-text text-lg">
              Aucun utilisateur trouvé.
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="flex justify-center mt-8" v-if="totalPages > 1 || currentPage > 1">
      <div class="join shadow-sm">
        <button class="join-item btn btn-sm bg-base-200 hover:bg-primary hover:text-base-100 border-base-300"
          :disabled="currentPage === 1" @click="changePage(currentPage - 1)">
          «
        </button>

        <button v-for="page in totalPages" :key="page" class="join-item btn btn-sm border-base-300"
          :class="{ 'bg-primary text-base-100 pointer-events-none': currentPage === page, 'bg-base-200 hover:bg-base-300': currentPage !== page }"
          @click="changePage(page)">
          {{ page }}
        </button>

        <button class="join-item btn btn-sm bg-base-200 hover:bg-primary hover:text-base-100 border-base-300"
          :disabled="currentPage === totalPages" @click="changePage(currentPage + 1)">
          »
        </button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import axios from 'axios'
import PageTitle from '../../components/PageTitle.vue'
import { getAssetUrl } from '../../utils/assets.js'

// --- ÉTATS ---
const users = ref([])
const loading = ref(true)
const error = ref(null)

const searchQuery = ref('')
const selectedAffiliation = ref('')

const currentPage = ref(1)
const totalPages = ref(1)
const itemsPerPage = 20 // Doit correspondre à la limite de ton API

// --- APPEL API ---
const fetchUsers = async (page = 1) => {
  try {
    loading.value = true
    error.value = null
    const offset = (page - 1) * itemsPerPage

    let params = { offset: offset }

    // On combine les deux critères s'ils sont actifs tous les deux
    if (selectedAffiliation.value) {
      params.affiliation = selectedAffiliation.value
    }
    if (searchQuery.value) {
      params.username = searchQuery.value
    }

    const response = await axios.get('/api/user/list/search', { params })

    if (response.data?.status === 'success') {
      users.value = response.data.users || []
      if (response.data.total_users !== undefined) {
        totalPages.value = Math.ceil(response.data.total_users / itemsPerPage) || 1
      }
      currentPage.value = page
    }
  } catch (err) {
    console.error('Erreur API Users:', err)
    error.value = "Impossible de charger la liste des utilisateurs."
  } finally {
    loading.value = false
  }
}

// --- FILTRAGE LOCAL ---
const filteredUsers = computed(() => {
  return users.value
})

const changePage = (newPage) => {
  if (newPage > 0 && newPage <= totalPages.value) {
    fetchUsers(newPage)
  }
}

// --- EFFETS SECONDAIRES ---
watch(searchQuery, () => {
  currentPage.value = 1
  fetchUsers(1)
})

watch(selectedAffiliation, () => {
  currentPage.value = 1
  fetchUsers(1)
})

watch(currentPage, () => {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  })
})

// Chargement initial (plus besoin de fetchAllAvatars)
onMounted(() => {
  fetchUsers(1)
})
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.4s ease-out forwards;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>