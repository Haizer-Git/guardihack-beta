<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import { showToast } from './useAdminToast.js'
import PopUpConfirm from '../../components/PopUpConfirm.vue'
import { getAssetUrl } from '../../utils/assets'

const props = defineProps({
  initialTab: {
    type: String,
    default: 'icon_list',
  },
})

// ════════════════════════════════════════════════════════
// 1. DÉCLARATION DES VARIABLES & ÉTATS
// ════════════════════════════════════════════════════════
const icons          = ref([])
const loadingIcons   = ref(false)

// Filtres et Tri
const search         = ref('')
const sortKey        = ref('filename')
const sortDir        = ref('asc')

// Formulaires / Modale d'upload
const isModalOpen    = ref(false)
const uploadType     = ref('BADGE')
const selectedFiles  = ref([])
const uploading      = ref(false)

// ════════════════════════════════════════════════════════
// 2. COMPUTED PROPERTIES
// ════════════════════════════════════════════════════════
const tabGroup = computed(() => TAB_GROUPS[props.initialTab] ?? TAB_GROUPS.icon)
const activeTab = ref('icon_list')

const filteredIconsTable = computed(() => {
  if (!search.value.trim()) return icons.value
  const term = search.value.trim().toLowerCase()
  return icons.value.filter(ic => ic.filename.toLowerCase().includes(term) || ic.filetype.toLowerCase().includes(term))
})

// ════════════════════════════════════════════════════════
// 3. CONFIGURATION DES ONGLETS & HELPERS UI
// ════════════════════════════════════════════════════════
const TAB_GROUPS = {
  icon: [
    { id: 'icon_list', label: 'Liste' },
  ]
}

function defaultTabForGroup(groupKey) {
  return 'icon_list'
}

function onTabChange(tab) {
  activeTab.value = tab
  if (tab === 'icon_list') fetchIcons()
}

const breadcrumbSubCategory = computed(() => {
  return 'Photothèque'
})

// ════════════════════════════════════════════════════════
// 4. GESTION DES POPUPS DE CONFIRMATION
// ════════════════════════════════════════════════════════
const confirmModal = reactive({
  isOpen: false,
  title: '',
  message: '',
  loading: false,
  onConfirm: null
})

function triggerConfirm(title, message, callback) {
  confirmModal.title = title
  confirmModal.message = message
  confirmModal.loading = false
  confirmModal.onConfirm = callback
  confirmModal.isOpen = true
}

async function handleConfirmDialog() {
  if (confirmModal.onConfirm) {
    confirmModal.loading = true
    try {
      await confirmModal.onConfirm()
      closeConfirmDialog()
    } catch (e) {
      // Erreur gérée
    } finally {
      confirmModal.loading = false
    }
  } else {
    closeConfirmDialog()
  }
}

function closeConfirmDialog() {
  confirmModal.isOpen = false
  confirmModal.loading = false
  confirmModal.onConfirm = null
}

// ════════════════════════════════════════════════════════
// 5. FONCTIONS API (Icônes)
// ════════════════════════════════════════════════════════
async function fetchIcons() {
  loadingIcons.value = true
  try {
    const res = await axios.get('/api/admin/icon/list')
    icons.value = res.data?.icons ?? res.data?.data ?? []
  } catch {
    showToast('Impossible de charger les icônes', 'error')
    icons.value = []
  } finally {
    loadingIcons.value = false
  }
}

function deleteIcon(id, filename) {
  triggerConfirm(
    'Supprimer l\'icône',
    `Voulez-vous vraiment supprimer l'icône "${filename}" ?`,
    async () => {
      try {
        const res = await axios.post(`/api/admin/icon/${id}/delete`)
        showToast(res.data?.message || `Icône "${filename}" supprimée`)
        await fetchIcons()
      } catch (e) {
        showToast(e.response?.data?.message ?? 'Erreur lors de la suppression', 'error')
        throw e
      }
    }
  )
}

function handleFileSelection(e) {
  selectedFiles.value = Array.from(e.target.files)
}

async function handleUpload() {
  if (selectedFiles.value.length === 0) return

  const formData = new FormData()
  selectedFiles.value.forEach(file => {
    formData.append('files', file)
  })

  uploading.value = true
  try {
    const res = await axios.post(`/api/admin/icon/upload/${uploadType.value}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    showToast(res.data?.message || 'Icônes uploadées avec succès !')
    isModalOpen.value = false
    selectedFiles.value = []
    await fetchIcons()
  } catch (e) {
    showToast(e.response?.data?.message ?? 'Erreur lors de l\'upload', 'error')
  } finally {
    uploading.value = false
  }
}

function setSort(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = 'asc'
  }
  icons.value.sort((a, b) => {
    let modifier = sortDir.value === 'asc' ? 1 : -1
    if (a[sortKey.value] < b[sortKey.value]) return -1 * modifier
    if (a[sortKey.value] > b[sortKey.value]) return 1 * modifier
    return 0
  })
}

function clearFilters() {
  search.value = ''
}

watch(
  () => props.initialTab,
  async (groupKey) => {
    activeTab.value = defaultTabForGroup(groupKey)
    await fetchIcons()
  },
  { immediate: true }
)

onMounted(() => {
  fetchIcons()
})
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- Titre Principal -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <p class="font-code text-[10px] tracking-[0.18em] uppercase text-base-content/40 mb-1">Admin > {{ breadcrumbSubCategory }}</p>
        <h1 class="font-titre font-bold text-2xl text-base-content leading-none">Photothèque</h1>
      </div>
      <span class="font-code text-sm text-base-content/50 border border-secondary px-2 py-1">{{ icons.length }} ICÔNE{{ icons.length > 1 ? 'S' : '' }}</span>
    </div>

    <!-- Barre d'onglets -->
    <div class="flex gap-0 border-b border-primary mb-6">
      <button
        v-for="tab in tabGroup"
        :key="tab.id"
        :disabled="tab.locked?.() ?? false"
        @click="!(tab.locked?.() ?? false) && onTabChange(tab.id)"
        :class="[
          'px-5 py-2.5 font-text text-sm tracking-wide border border-primary transition-colors duration-150 -mb-px',
          activeTab === tab.id
            ? 'border-primary text-base-content'
            : (tab.locked?.() ?? false)
              ? 'border-transparent text-base-content/20 cursor-not-allowed'
              : 'border-transparent text-base-content/45 hover:text-base-content/75 hover:border-primary/20'
        ]"
      >{{ tab.label }}</button>
    </div>

    <!-- ── TAB : LISTE DES ICÔNES ── -->
    <div v-if="activeTab === 'icon_list'" class="flex flex-col gap-4">
      <div class="flex items-center gap-2">
        <button
          @click="isModalOpen = true"
          class="flex items-center gap-2 bg-primary text-base-100 hover:bg-primary/80 px-4 py-2 font-code text-xs font-bold tracking-wider transition-colors shadow-sm"
        >
          <span>+ Ajouter de nouvelles icônes</span>
        </button>
      </div>

      <!-- Filtres et recherche -->
      <div class="flex items-center gap-2 flex-wrap mb-2">
        <div class="relative flex-1 min-w-48">
          <span class="absolute left-3 top-1/2 -translate-y-1/2 font-code text-base-content/30 text-xs select-none">⌕</span>
          <input
            v-model="search"
            type="text"
            placeholder="Rechercher une icône..."
            class="w-full bg-base-100 border border-base-300 focus:border-primary outline-none pl-7 pr-3 py-2 font-code text-xs text-base-content placeholder:text-base-content/25 transition-colors"
          />
        </div>
      </div>

      <!-- Tableau -->
      <div class="border border-base-300 overflow-hidden flex flex-col" style="max-height: calc(100vh - 220px);">
        <div class="grid grid-cols-[1fr_2fr_1.5fr_1.5fr_120px] bg-base-200 border-b border-base-300 shrink-0">
          <div class="px-4 py-2.5 font-code text-[10px] uppercase tracking-widest text-base-content/40">Aperçu</div>
          <button
            v-for="col in [
              { key: 'filename', label: 'Nom du fichier' },
              { key: 'filetype', label: 'Type'           },
              { key: 'uploaded_at', label: 'Date d\'ajout' },
            ]"
            :key="col.key"
            @click="setSort(col.key)"
            class="flex items-center gap-1 px-4 py-2.5 font-code text-[10px] uppercase tracking-widest text-base-content/40 hover:text-base-content/70 transition-colors text-left"
          >
            {{ col.label }}
            <span v-if="sortKey === col.key" class="text-primary ml-0.5">{{ sortDir === 'asc' ? '↑' : '↓' }}</span>
          </button>
          <div class="px-4 py-2.5 font-code text-[10px] uppercase tracking-widest text-base-content/40 text-right">Actions</div>
        </div>

        <div class="flex-1 overflow-y-auto">
          <div v-if="loadingIcons" class="flex justify-center py-16">
            <span class="loading loading-spinner loading-md text-primary"></span>
          </div>
          <div v-else-if="!filteredIconsTable.length" class="flex flex-col items-center justify-center py-10 gap-1">
            <span class="font-code text-xs text-base-content/25">Aucune icône trouvée</span>
          </div>
          <div v-else class="flex flex-col">
            <div
              v-for="icon in filteredIconsTable" :key="icon.id"
              class="grid grid-cols-[1fr_2fr_1.5fr_1.5fr_120px] items-center border-b border-base-300/50 hover:bg-base-300/30 transition-colors duration-100"
            >
              <!-- Aperçu -->
              <div class="px-4 py-2 flex items-center">
                <div class="w-10 h-10 bg-base-100 border border-base-300 flex items-center justify-center overflow-hidden">
                    <img :src="getAssetUrl(icon.filepath)" :alt="icon.filename" class="w-full h-full object-contain" @error="$event.target.style.display='none'" />
                </div>
              </div>
              <!-- Nom du fichier -->
              <div class="px-4 py-3 flex items-center gap-2 min-w-0">
                <span class="font-code text-[10px] text-base-content/30 shrink-0">#{{ icon.id }}</span>
                <span class="font-code text-xs text-base-content font-medium truncate" :title="icon.filename">{{ icon.filename }}</span>
              </div>
              <!-- Type -->
              <div class="px-4 py-3 flex items-center">
                <span class="font-code text-xs text-secondary bg-secondary/15 px-2 py-0.5 border border-secondary/30 uppercase">{{ icon.filetype }}</span>
              </div>
              <!-- Date d'ajout -->
              <div class="px-4 py-3 flex items-center">
                <span class="font-code text-[11px] text-base-content/60">{{ icon.uploaded_at ?? '—' }}</span>
              </div>
              <!-- Actions -->
              <div class="px-4 py-3 flex items-center justify-end gap-1.5">
                <button class="font-text text-xs text-error hover:text-error/70 px-1" @click="deleteIcon(icon.id, icon.filename)" title="Supprimer">Supprimer</button>
              </div>
            </div>
          </div>
        </div>

        <div class="border-t border-base-300 px-4 py-2 bg-base-200/50 flex items-center justify-between shrink-0">
          <span class="font-code text-[10px] text-base-content/30">{{ filteredIconsTable.length }} / {{ icons.length }} ICÔNE{{ filteredIconsTable.length > 1 ? 'S' : '' }}</span>
          <span
            v-if="search"
            class="font-code text-[10px] text-primary/60 cursor-pointer hover:text-primary transition-colors"
            @click="clearFilters"
          >Effacer les filtres</span>
        </div>
      </div>
    </div>

  </div>

  <!-- MODALE D'UPLOAD MULTIPLE -->
  <dialog :class="['modal', { 'modal-open': isModalOpen }]">
    <div class="modal-box bg-base-100 border border-base-300 rounded-none shadow-2xl p-6 max-w-lg">
      <div class="flex items-center justify-between border-b border-base-300 pb-3 mb-4">
        <div>
          <p class="font-code text-[10px] tracking-widest uppercase text-base-content/35 mb-0.5">Photothèque</p>
          <h3 class="font-titre font-bold text-base text-primary uppercase tracking-wider">Uploader des icônes</h3>
        </div>
        <button @click="isModalOpen = false" class="btn btn-sm btn-ghost font-code">✕</button>
      </div>

      <div class="flex flex-col gap-4 font-text text-xs">
        <div class="flex flex-col gap-1">
          <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Type de ressource *</label>
          <select v-model="uploadType" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-xs text-base-content transition-colors">
            <option value="BADGE">Badge</option>
            <option value="AVATAR">Avatar</option>
            <option value="BANNER">Bannière</option>
          </select>
        </div>

        <div class="flex flex-col gap-1">
          <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Fichiers (PNG, JPG, SVG...) *</label>
          <input
            type="file"
            multiple
            @change="handleFileSelection"
            accept=".png, .jpg, .jpeg, .gif, .svg"
            class="file-input file-input-bordered file-input-sm rounded-none w-full bg-base-100 font-code text-xs"
          />
        </div>
      </div>

      <div class="modal-action mt-6 pt-4 border-t border-base-300 flex justify-end gap-2">
        <button @click="isModalOpen = false" class="btn btn-sm btn-ghost font-code text-xs">Annuler</button>
        <button
          @click="handleUpload"
          :disabled="uploading || selectedFiles.length === 0"
          class="btn btn-primary btn-sm font-titre font-bold tracking-wider relative flex items-center justify-center min-w-[120px]"
        >
          <span v-if="uploading" class="loading loading-spinner loading-xs absolute"></span>
          <span :class="{ 'opacity-0': uploading }">UPLOADER</span>
        </button>
      </div>
    </div>
    <form method="dialog" class="modal-backdrop">
      <button @click="isModalOpen = false">fermer</button>
    </form>
  </dialog>

  <PopUpConfirm
    :is-open="confirmModal.isOpen"
    :title="confirmModal.title"
    :message="confirmModal.message"
    :loading="confirmModal.loading"
    @confirm="handleConfirmDialog"
    @cancel="closeConfirmDialog"
  />
</template>