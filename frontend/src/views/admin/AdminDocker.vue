<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import { showToast } from './useAdminToast.js'
import PopUpConfirm from '../../components/PopUpConfirm.vue'

const props = defineProps({
  initialTab: {
    type: String,
    default: 'image',
  },
})
const images         = ref([])
const totalImages    = ref(0)
const loadingImages  = ref(false)
const expandedImage  = ref(null)
const imageDetail    = ref(null)
const instances            = ref([])
const loadingInstances     = ref(false)
const userSuggestions      = ref([])
const challengeSuggestions = ref([])
const launchingInst        = ref(false)
const instanceForm         = reactive({ user_id: '', challenge_id: '' })
const isLaunchModalOpen    = ref(false)
const userSearchInput       = ref('')
const userDropdownOpen      = ref(false)
const challengeSearchInput  = ref('')
const challengeDropdownOpen = ref(false)
const search         = ref('')
const sortKey        = ref('name')
const sortDir        = ref('asc')
const currentPage    = ref(1)
const itemsPerPage   = 25
const createDefaults = { 
  image_name: '', image_tag: 'latest', internal_port: 80, memory_limit: '256m' 
}
const createForm   = reactive({ ...createDefaults })
const createZipFile = ref(null)
const creating     = ref(false)
const editTarget = ref(null)
const editForm   = reactive({ 
  image_name: '', image_tag: '', internal_port: 80, memory_limit: '256m' 
})
const editing    = ref(false)
const tabGroup = computed(() => TAB_GROUPS[props.initialTab] ?? TAB_GROUPS.image)
const activeTab = ref('image_list')
const filteredImagesTable = computed(() => {
  if (!search.value.trim()) return images.value
  const term = search.value.trim().toLowerCase()
  return images.value.filter(img => img.name.toLowerCase().includes(term) || img.image_tag.toLowerCase().includes(term))
})
const TAB_GROUPS = {
  image: [
    { id: 'image_list', label: 'Liste' },
    { id: 'image_create', label: 'Créer' },
    { id: 'image_edit', label: 'Modifier', locked: () => !editTarget.value },
  ],
  instance: [
    { id: 'instance_list', label: 'Liste' },
  ]
}
const breadcrumbSubCategory = computed(() => {
  if (activeTab.value.startsWith('image_')) return 'Images'
  if (activeTab.value.startsWith('instance_')) return 'Instances'
  return 'Docker'
})
const confirmModal = reactive({
  isOpen: false,
  title: '',
  message: '',
  loading: false,
  onConfirm: null
})

function defaultTabForGroup(groupKey) {
  if (groupKey === 'instance') return 'instance_list'
  return 'image_list'
}
function onTabChange(tab) {
  activeTab.value = tab
  if (tab === 'image_list') fetchImages()
  if (tab === 'instance_list') fetchInstances()
  if (tab === 'image_create') {
    Object.assign(createForm, { ...createDefaults })
    createZipFile.value = null
  }
}
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
async function fetchImages() {
  loadingImages.value = true
  try {
    const res = await axios.get('/api/admin/docker/image/list')
    const list = res.data?.images ?? res.data?.data ?? []
    images.value = list
    totalImages.value = list.length
  } catch {
    showToast('Impossible de charger les images Docker', 'error')
  } finally {
    loadingImages.value = false
  }
}
async function fetchInstances() {
  loadingInstances.value = true
  try {
    const res = await axios.get('/api/admin/docker/instance/list')
    instances.value = res.data?.instances ?? res.data?.data ?? []
  } catch {
    showToast('Impossible de charger les instances Docker', 'error')
  } finally {
    loadingInstances.value = false
  }
}
function selectUserForLaunch(u) {
  instanceForm.user_id = u.id
  userSearchInput.value = u.username
  userDropdownOpen.value = false
}
function selectChallengeForLaunch(c) {
  instanceForm.challenge_id = c.id
  challengeSearchInput.value = c.name
  challengeDropdownOpen.value = false
}
function openLaunchModal() {
  instanceForm.user_id = ''
  instanceForm.challenge_id = ''
  userSearchInput.value = ''
  challengeSearchInput.value = ''
  userSuggestions.value = []
  challengeSuggestions.value = []
  isLaunchModalOpen.value = true
}
async function submitLaunchInstance() {
  if (!instanceForm.user_id || !instanceForm.challenge_id) return
  launchingInst.value = true
  try {
    const payload = {
      user_id: Number(instanceForm.user_id),
      challenge_id: Number(instanceForm.challenge_id)
    }
    const res = await axios.post('/api/admin/docker/instance/launch', payload)
    showToast(res.data?.message || 'Instance lancée avec succès !')
    isLaunchModalOpen.value = false
    await fetchInstances()
  } catch (e) {
    showToast(e.response?.data?.message ?? "Erreur lors du lancement de l'instance", 'error')
  } finally {
    launchingInst.value = false
  }
}
function stopAdminInstance(userId, challengeId, containerName) {
  triggerConfirm(
    'Stopper l\'instance',
    `Voulez-vous vraiment stopper l'instance "${containerName}" ?`,
    async () => {
      try {
        const payload = { user_id: userId, challenge_id: challengeId }
        const res = await axios.post('/api/admin/docker/instance/stop', payload)
        showToast(res.data?.message || 'Instance stoppée avec succès')
        await fetchInstances()
      } catch (e) {
        showToast(e.response?.data?.message ?? "Erreur lors de l'arrêt de l'instance", 'error')
        throw e
      }
    }
  )
}
async function toggleImage(id) {
  if (expandedImage.value === id) {
    expandedImage.value = null
    imageDetail.value = null
    return
  }
  expandedImage.value = id
  imageDetail.value = null
  try {
    const res = await axios.get(`/api/admin/docker/image/${id}/info`)
    imageDetail.value = res.data?.image ?? res.data?.data ?? res.data
  } catch {
    imageDetail.value = images.value.find(i => i.id === id) || null
  }
}
function deleteImage(id, name) {
  triggerConfirm(
    'Supprimer l\'image Docker',
    `Voulez-vous vraiment supprimer l'image "${name}" ?`,
    async () => {
      try {
        await axios.post(`/api/admin/docker/image/${id}/delete`)
        showToast(`Image "${name}" supprimée`)
        if (expandedImage.value === id) { expandedImage.value = null; imageDetail.value = null }
        await fetchImages()
      } catch (e) {
        showToast(e.response?.data?.message ?? 'Erreur suppression image', 'error')
        throw e
      }
    }
  )
}
function setSort(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = 'asc'
  }
  images.value.sort((a, b) => {
    let modifier = sortDir.value === 'asc' ? 1 : -1
    if (a[sortKey.value] < b[sortKey.value]) return -1 * modifier
    if (a[sortKey.value] > b[sortKey.value]) return 1 * modifier
    return 0
  })
}
function clearFilters() {
  search.value = ''
  currentPage.value = 1
}
function onZipFileChange(e) {
  const file = e.target.files[0]
  if (file) {
    createZipFile.value = file
  }
}
function handleFileDrop(e) {
  const file = e.dataTransfer.files[0]
  if (file && file.name.endsWith('.zip')) {
    createZipFile.value = file
  } else {
    showToast('Veuillez déposer un fichier au format .zip', 'error')
  }
}
async function submitCreate() {
  if (!createForm.image_name.trim()) {
    showToast('Le nom de l\'image est obligatoire', 'error')
    return
  }
  if (!createZipFile.value) {
    showToast('Le fichier ZIP de configuration est obligatoire', 'error')
    return
  }
  creating.value = true
  try {
    const formData = new FormData()
    formData.append('name', createForm.image_name.trim())
    formData.append('tag', createForm.image_tag.trim() || 'latest')
    formData.append('internal_port', Number(createForm.internal_port))
    formData.append('memory_limit', createForm.memory_limit.trim() || '256m')
    formData.append('file', createZipFile.value)
    const res = await axios.post('/api/admin/docker/image/create', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    showToast(res.data?.message || `Image Docker "${createForm.image_name}" créée !`)
    Object.assign(createForm, { ...createDefaults })
    createZipFile.value = null
    activeTab.value = 'image_list'
    await fetchImages()
  } catch (e) {
    showToast(e.response?.data?.message ?? 'Erreur création image', 'error')
  } finally {
    creating.value = false
  }
}
async function openEdit(img) {
  editTarget.value = img.id
  activeTab.value = 'image_edit'
  Object.assign(editForm, {
    image_name: img.name,
    image_tag: img.image_tag,
    internal_port: img.internal_port,
    memory_limit: img.memory_limit
  })
}
async function submitEdit() {
  editing.value = true
  try {
    const payload = {
      new_image_name: editForm.image_name.trim(),
      new_image_tag: editForm.image_tag.trim(),
      new_internal_port: Number(editForm.internal_port),
      new_memory_limit: editForm.memory_limit.trim()
    }
    await axios.post(`/api/admin/docker/image/${editTarget.value}/modify`, payload)
    showToast('Image Docker modifiée !')
    activeTab.value = 'image_list'
    editTarget.value = null
    await fetchImages()
  } catch (e) {
    showToast(e.response?.data?.message ?? 'Erreur modification image', 'error')
  } finally {
    editing.value = false
  }
}

watch(userSearchInput, async (newVal) => {
  if (!newVal || newVal.trim().length === 0) {
    userSuggestions.value = []
    return
  }
  try {
    const res = await axios.get('/api/admin/user/list', {
      params: { search: newVal.trim(), limit: 10 }
    })
    userSuggestions.value = res.data?.users ?? []
    userDropdownOpen.value = true
  } catch {
    userSuggestions.value = []
  }
})
watch(challengeSearchInput, async (newVal) => {
  if (!newVal || newVal.trim().length === 0) {
    challengeSuggestions.value = []
    challengeDropdownOpen.value = false
    return
  }
  try {
    const res = await axios.get('/api/admin/challenge/list', {
      params: { search: newVal.trim(), limit: 10 }
    })
    challengeSuggestions.value = res.data?.challenges ?? res.data?.data ?? []
    challengeDropdownOpen.value = true
  } catch (e) {
    console.error("Erreur recherche challenges :", e)
    challengeSuggestions.value = []
  }
})
watch(
  () => props.initialTab,
  async (groupKey) => {
    activeTab.value = defaultTabForGroup(groupKey)
    if (groupKey === 'image' || !groupKey) {
      await fetchImages()
    } else if (groupKey === 'instance') {
      await fetchInstances()
    }
  },
  { immediate: true }
)

onMounted(() => {
  if (props.initialTab === 'instance') {
    fetchInstances()
  } else {
    fetchImages()
  }
})
</script>

<template>
  <div class="flex flex-col h-full">
    <div class="flex items-center justify-between mb-6">
      <div>
        <p class="font-code text-[10px] tracking-[0.18em] uppercase text-base-content/40 mb-1">Admin > Docker > {{ breadcrumbSubCategory }}</p>
        <h1 class="font-titre font-bold text-2xl text-base-content leading-none">Docker {{ props.initialTab === 'instance' ? 'Instances' : 'Images' }}</h1>
      </div>
      <span v-if="activeTab.includes('image')" class="font-code text-sm text-base-content/50 border border-secondary px-2 py-1">{{ images.length }} IMAGE{{ images.length > 1 ? 'S' : '' }}</span>
      <span v-if="activeTab.includes('instance')" class="font-code text-sm text-base-content/50 border border-secondary px-2 py-1">{{ instances.length }} INSTANCE{{ instances.length > 1 ? 'S' : '' }}</span>
    </div>
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
    <div v-if="activeTab === 'image_list'" class="flex flex-col gap-4">
      <div class="flex justify-start">
        <button
          @click="activeTab = 'image_create'"
          class="flex items-center gap-2 bg-primary text-base-100 hover:bg-primary/80 px-4 py-2 font-code text-xs font-bold tracking-wider transition-colors shadow-sm"
        >
          <span>+ Créer une nouvelle image Docker</span>
        </button>
      </div>
      <div class="flex items-center gap-2 flex-wrap mb-2">
        <div class="relative flex-1 min-w-48">
          <span class="absolute left-3 top-1/2 -translate-y-1/2 font-code text-base-content/30 text-xs select-none">⌕</span>
          <input
            v-model="search"
            type="text"
            placeholder="Rechercher une image..."
            class="w-full bg-base-100 border border-base-300 focus:border-primary outline-none pl-7 pr-3 py-2 font-code text-xs text-base-content placeholder:text-base-content/25 transition-colors"
          />
        </div>
      </div>
      <div class="border border-base-300 overflow-hidden flex flex-col" style="max-height: calc(100vh - 220px);">
        <div class="grid grid-cols-[2fr_1.5fr_1fr_1fr_120px] bg-base-200 border-b border-base-300 shrink-0">
          <button
            v-for="col in [
              { key: 'name',          label: 'Nom de l\'image' },
              { key: 'image_tag',     label: 'Tag'             },
              { key: 'internal_port', label: 'Port Interne'    },
              { key: 'memory_limit',  label: 'Mémoire Limite'  },
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
          <div v-if="loadingImages" class="flex justify-center py-16">
            <span class="loading loading-spinner loading-md text-primary"></span>
          </div>
          <div v-else-if="!filteredImagesTable.length" class="flex flex-col items-center justify-center py-10 gap-1">
            <span class="font-code text-xs text-base-content/25">Aucune image Docker trouvée</span>
          </div>
          <div v-else class="flex flex-col">
            <template v-for="img in filteredImagesTable" :key="img.id">
              <div
                @click="toggleImage(img.id)"
                :class="[
                  'grid grid-cols-[2fr_1.5fr_1fr_1fr_120px] items-center border-b border-base-300/50 cursor-pointer transition-colors duration-100',
                  expandedImage === img.id ? 'bg-primary/8 border-l-2 border-l-primary' : 'hover:bg-base-300/30'
                ]"
              >
                <div class="px-4 py-3 flex items-center gap-2 min-w-0">
                  <span class="font-code text-[10px] text-base-content/30 shrink-0">#{{ img.id }}</span>
                  <span class="font-code text-xs text-base-content font-medium truncate">{{ img.name }}</span>
                </div>
                <div class="px-4 py-3 flex items-center">
                  <span class="font-code text-xs text-secondary bg-secondary/15 px-2 py-0.5 border border-secondary/30">{{ img.image_tag }}</span>
                </div>
                <div class="px-4 py-3 flex items-center">
                  <span class="font-code text-xs text-base-content/70">{{ img.internal_port }}</span>
                </div>
                <div class="px-4 py-3 flex items-center">
                  <span class="font-code font-bold text-primary text-xs">{{ img.memory_limit }}</span>
                </div>
                <div class="px-4 py-3 flex items-center justify-end gap-1.5" @click.stop>
                  <button class="font-text text-xs text-info hover:text-info/70 px-1" @click="openEdit(img)" title="Modifier">Modifier</button>
                  <button class="font-text text-xs text-error hover:text-error/70 px-1" @click="deleteImage(img.id, img.name)" title="Supprimer">Supprimer</button>
                </div>
              </div>
              <div v-if="expandedImage === img.id" class="border-b border-base-300 bg-base-300/50 p-5">
                <p class="font-stitre text-[12px] tracking-widest uppercase text-primary/70 mb-3">Détails de l'image Docker</p>
                <dl class="grid grid-cols-[auto_1fr] gap-x-6 gap-y-2 text-sm font-text max-w-lg">
                  <dt class="text-base-content/40">ID Interne</dt>
                  <dd class="text-base-content font-mono">{{ img.id }}</dd>
                  <dt class="text-base-content/40">Nom complet</dt>
                  <dd class="text-base-content font-mono">{{ img.name }}:{{ img.image_tag }}</dd>
                  <dt class="text-base-content/40">Port Conteneur</dt>
                  <dd class="text-base-content font-mono">{{ img.internal_port }}</dd>
                  <dt class="text-base-content/40">Allocation RAM max</dt>
                  <dd class="text-base-content font-mono">{{ img.memory_limit }}</dd>
                </dl>
              </div>
            </template>
          </div>
        </div>
        <div class="border-t border-base-300 px-4 py-2 bg-base-200/50 flex items-center justify-between shrink-0">
          <span class="font-code text-[10px] text-base-content/30">{{ filteredImagesTable.length }} / {{ images.length }} IMAGE{{ filteredImagesTable.length > 1 ? 'S' : '' }}</span>
          <span
            v-if="search"
            class="font-code text-[10px] text-primary/60 cursor-pointer hover:text-primary transition-colors"
            @click="clearFilters"
          >Effacer les filtres</span>
        </div>
      </div>
    </div>
    <div v-if="activeTab === 'image_create'" class="w-full">
      <div class="border border-base-300 bg-base-200/40 p-6 max-w-4xl">
        <p class="font-code text-[10px] tracking-widest uppercase text-base-content/35 mb-1">Nouvelle image</p>
        <h2 class="font-titre font-bold text-lg text-base-content mb-6">Enregistrer et builder une image Docker</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 items-start">
          <div class="flex flex-col gap-4">
            <div class="flex flex-col gap-1">
              <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Nom de l'image *</label>
              <input v-model="createForm.image_name" type="text" placeholder="guardihack/challenge-web" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content placeholder:text-base-content/20 transition-colors" />
            </div>
            <div class="flex flex-col gap-1">
              <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Tag</label>
              <input v-model="createForm.image_tag" type="text" placeholder="latest" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content placeholder:text-base-content/20 transition-colors" />
            </div>
            <div class="flex flex-col gap-1">
              <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Port interne *</label>
              <input v-model.number="createForm.internal_port" type="number" min="1" placeholder="80" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors" />
            </div>
            <div class="flex flex-col gap-1">
              <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Limite de mémoire (ex: 256m, 1g)</label>
              <input v-model="createForm.memory_limit" type="text" placeholder="256m" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors" />
            </div>
          </div>
          <div class="flex flex-col gap-1 h-full">
            <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Configuration Docker (ZIP) *</label>
            <div
              @dragover.prevent
              @drop.prevent="handleFileDrop"
              class="border-2 border-dashed border-base-300 hover:border-primary bg-base-100/50 p-6 flex flex-col items-center justify-center text-center cursor-pointer transition-colors h-full min-h-[220px] relative rounded-md"
              @click="$refs.zipFileInput.click()"
            >
              <input
                ref="zipFileInput"
                type="file"
                accept=".zip"
                class="hidden"
                @change="onZipFileChange"
              />
              <div v-if="!createZipFile" class="flex flex-col items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-primary/60" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p class="font-code text-xs text-base-content/70">Glissez-déposez votre archive ZIP ici ou <span class="text-primary underline">parcourez</span></p>
                <span class="text-[10px] font-code text-base-content/40">Contient le Dockerfile et les fichiers nécessaires</span>
              </div>
              <div v-else class="flex flex-col items-center gap-2" @click.stop>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p class="font-code text-xs font-bold text-success truncate max-w-xs">{{ createZipFile.name }}</p>
                <span class="text-[10px] font-code text-base-content/60">{{ createZipFile.size }} Ko</span>
                <button @click.prevent="createZipFile = null" class="mt-2 text-xs text-error hover:underline font-code">Supprimer / Changer de fichier</button>
              </div>
            </div>
          </div>
        </div>
        <div class="flex gap-3 mt-8 pt-4 border-t border-base-300">
          <button @click="submitCreate" :disabled="creating || !createForm.image_name || !createZipFile" class="px-5 py-2 font-code text-xs tracking-wide bg-primary text-base-100 hover:bg-primary/80 transition-colors disabled:opacity-30 flex items-center gap-2">
            <span v-if="creating" class="loading loading-xs"></span>
            <span>Créer l'image</span>
          </button>
          <button @click="activeTab = 'image_list'" class="px-5 py-2 font-code text-xs tracking-wide border border-base-300 text-base-content/50 hover:text-base-content hover:border-base-content/30 transition-colors">Annuler</button>
        </div>
      </div>
    </div>
    <div v-if="activeTab === 'image_edit' && editTarget" class="w-full">
      <div class="border border-base-300 bg-base-200/40 p-6 max-w-xl">
        <p class="font-code text-[10px] tracking-widest uppercase text-base-content/35 mb-1">Image #{{ editTarget }}</p>
        <h2 class="font-titre font-bold text-lg text-base-content mb-6">Modifier l'image Docker</h2>
        <div class="flex flex-col gap-4">
          <div class="flex flex-col gap-1">
            <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Nom de l'image</label>
            <input v-model="editForm.image_name" type="text" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors" />
          </div>
          <div class="flex flex-col gap-1">
            <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Tag</label>
            <input v-model="editForm.image_tag" type="text" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors" />
          </div>
          <div class="flex flex-col gap-1">
            <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Port interne</label>
            <input v-model.number="editForm.internal_port" type="number" min="1" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors" />
          </div>
          <div class="flex flex-col gap-1">
            <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Limite de mémoire</label>
            <input v-model="editForm.memory_limit" type="text" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors" />
          </div>
        </div>
        <div class="flex gap-3 mt-6">
          <button @click="submitEdit" :disabled="editing" class="px-5 py-2 font-code text-xs tracking-wide bg-warning text-base-100 hover:bg-warning/80 transition-colors disabled:opacity-30">
            <span v-if="editing" class="loading loading-xs"></span>
            <span v-else>Sauvegarder</span>
          </button>
          <button @click="activeTab = 'image_list'; editTarget = null" class="px-5 py-2 font-code text-xs tracking-wide border border-base-300 text-base-content/50 hover:text-base-content hover:border-base-content/30 transition-colors">Annuler</button>
        </div>
      </div>
    </div>
    <div v-if="activeTab === 'instance_list'" class="flex flex-col gap-4">
      <div class="flex justify-start">
        <button
          @click="openLaunchModal"
          class="flex items-center gap-2 bg-primary text-base-100 hover:bg-primary/80 px-4 py-2 font-code text-xs font-bold tracking-wider transition-colors shadow-sm"
        >
          <span>+ Lancer une instance manuellement</span>
        </button>
      </div>
      <div class="border border-base-300 overflow-hidden flex flex-col" style="max-height: calc(100vh - 220px);">
        <div class="grid grid-cols-[1.5fr_1fr_2fr_2fr_120px] bg-base-200 border-b border-base-300 shrink-0">
          <div class="px-4 py-2.5 font-code text-[10px] uppercase tracking-widest text-base-content/40">Utilisateur</div>
          <div class="px-4 py-2.5 font-code text-[10px] uppercase tracking-widest text-base-content/40">Challenge</div>
          <div class="px-4 py-2.5 font-code text-[10px] uppercase tracking-widest text-base-content/40">Nom du conteneur</div>
          <div class="px-4 py-2.5 font-code text-[10px] uppercase tracking-widest text-base-content/40">Création / Expiration</div>
          <div class="px-4 py-2.5 font-code text-[10px] uppercase tracking-widest text-base-content/40 text-right">Actions</div>
        </div>
        <div class="flex-1 overflow-y-auto">
          <div v-if="loadingInstances" class="flex justify-center py-16">
            <span class="loading loading-spinner loading-md text-primary"></span>
          </div>
          <div v-else-if="!instances.length" class="flex flex-col items-center justify-center py-10 gap-1">
            <span class="font-code text-xs text-base-content/25">Aucune instance active trouvée</span>
          </div>
          <div v-else class="flex flex-col">
            <div
              v-for="inst in instances" :key="inst.id || inst.container_name"
              class="grid grid-cols-[1.5fr_1fr_2fr_2fr_120px] items-center border-b border-base-300/50 hover:bg-base-300/30 transition-colors duration-100"
            >
              <div class="px-4 py-3 flex items-center font-code text-xs text-base-content font-medium">
                {{ inst.username }}
              </div>
              <div class="px-4 py-3 flex items-center font-code text-xs text-base-content/70">
                {{ inst.challenge_name }}
              </div>
              <div class="px-4 py-3 flex items-center min-w-0">
                <span class="font-code text-xs text-primary truncate" :title="inst.container_name">
                  {{ inst.container_name }}
                </span>
              </div>
              <div class="px-4 py-3 flex flex-col justify-center font-code text-[11px] gap-0.5">
                <span class="text-base-content/60" title="Date de création">Création : {{ inst.created_at ?? '—' }}</span>
                <span class="text-warning font-semibold" title="Date d'expiration">Expire : {{ inst.expires_at ?? '—' }}</span>
              </div>
              <div class="px-4 py-3 flex items-center justify-end gap-1.5" @click.stop>
                <a :href="inst.url" target="_blank" class="font-text text-xs text-info hover:text-info/70 px-1" title="Accéder">Accéder</a>
                <button class="font-text text-xs text-error hover:text-error/70 px-1" @click="stopAdminInstance(inst.user_id, inst.challenge_id, inst.container_name)" title="Stopper">Stopper</button>
              </div>
            </div>
          </div>
        </div>
        <div class="border-t border-base-300 px-4 py-2 bg-base-200/50 flex items-center justify-between shrink-0">
          <span class="font-code text-[10px] text-base-content/30">{{ instances.length }} INSTANCE{{ instances.length > 1 ? 'S' : '' }} ACTIVE{{ instances.length > 1 ? 'S' : '' }}</span>
        </div>
      </div>
    </div>
  </div>
  <dialog :class="['modal', { 'modal-open': isLaunchModalOpen }]">
    <div class="modal-box bg-base-100 border border-base-300 rounded-none shadow-2xl p-6 max-w-lg">
      <div class="flex items-center justify-between border-b border-base-300 pb-3 mb-4">
        <div>
          <p class="font-code text-[10px] tracking-widest uppercase text-base-content/35 mb-0.5">Lancer une instance</p>
          <h3 class="font-titre font-bold text-base text-primary uppercase tracking-wider">Démarrer un conteneur</h3>
        </div>
        <button @click="isLaunchModalOpen = false" class="btn btn-sm btn-ghost font-code">✕</button>
      </div>
      <div class="flex flex-col gap-4 font-text text-xs">
        <div class="flex flex-col gap-1 relative">
          <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Utilisateur *</label>
          <input
            v-model="userSearchInput"
            @focus="userDropdownOpen = true"
            @blur="setTimeout(() => userDropdownOpen = false, 200)"
            type="text"
            placeholder="Taper un nom d'utilisateur..."
            class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-xs text-base-content transition-colors"
          />
          <div v-if="userDropdownOpen && userSuggestions.length" class="absolute z-20 top-full left-0 right-0 mt-1 bg-base-100 border border-base-300 shadow-xl max-h-48 overflow-y-auto">
            <div
              v-for="u in userSuggestions" :key="u.id"
              @mousedown.prevent="selectUserForLaunch(u)"
              class="px-3 py-2 font-code text-xs text-base-content hover:bg-primary/15 cursor-pointer flex justify-between items-center"
            >
              <span>{{ u.username }}</span>
              <span class="text-[10px] text-base-content/40">#{{ u.id }}</span>
            </div>
          </div>
        </div>
        <div class="flex flex-col gap-1 relative">
          <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Challenge *</label>
          <input
            v-model="challengeSearchInput"
            @focus="challengeDropdownOpen = true"
            @blur="setTimeout(() => challengeDropdownOpen = false, 200)"
            type="text"
            placeholder="Taper un nom de challenge..."
            class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-xs text-base-content transition-colors"
          />
          <div v-if="challengeDropdownOpen && challengeSuggestions.length" class="absolute z-20 top-full left-0 right-0 mt-1 bg-base-100 border border-base-300 shadow-xl max-h-48 overflow-y-auto">
            <div
              v-for="c in challengeSuggestions" :key="c.id"
              @mousedown.prevent="selectChallengeForLaunch(c)"
              class="px-3 py-2 font-code text-xs text-base-content hover:bg-primary/15 cursor-pointer flex justify-between items-center"
            >
              <span>{{ c.name }}</span>
              <span class="text-[10px] text-base-content/40">#{{ c.id }}</span>
            </div>
          </div>
        </div>
      </div>
      <div class="modal-action mt-6 pt-4 border-t border-base-300 flex justify-end gap-2">
        <button @click="isLaunchModalOpen = false" class="btn btn-sm btn-ghost font-code text-xs">Annuler</button>
        <button
          @click="submitLaunchInstance"
          :disabled="launchingInst || !instanceForm.user_id || !instanceForm.challenge_id"
          class="btn btn-primary btn-sm font-titre font-bold tracking-wider relative flex items-center justify-center min-w-[120px]"
        >
          <span v-if="launchingInst" class="loading loading-spinner loading-xs absolute"></span>
          <span :class="{ 'opacity-0': launchingInst }">LANCER</span>
        </button>
      </div>
    </div>
    <form method="dialog" class="modal-backdrop">
      <button @click="isLaunchModalOpen = false">fermer</button>
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