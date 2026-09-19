<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import { showToast } from './useAdminToast.js'
import PopUpConfirm from '../../components/PopUpConfirm.vue'

const props = defineProps({
  initialTab: {
    type: String,
    default: 'announcement',
  },
})
const globalNotifications  = ref([])
const loadingGlobal        = ref(false)
const expandedGlobal       = ref(null)
const globalDetail         = ref(null)
const globalReads          = ref([])
const loadingReads         = ref(false)
const allUsers             = ref([])
const allPresets           = ref([])
const loadingTargets       = ref(false)
const search         = ref('')
const sortKey        = ref('created_at')
const sortDir        = ref('desc')
const currentPage    = ref(1)
const creationType   = ref('global')
const getCurrentLocalDateTime = () => {
  const now = new Date()
  const offset = now.getTimezoneOffset()
  const localDate = new Date(now.getTime() - (offset*60*1000))
  return localDate.toISOString().slice(0, 16)
}
const globalFormDefaults = { title: '', message: '', isPermanent: false, end_date: '' }
const globalForm = reactive({ ...globalFormDefaults })
const creatingGlobal = ref(false)
const targetedFormDefaults = { user_id: '', preset_id: '', title: '', message: '', target_type: 'user' }
const targetedForm = reactive({ ...targetedFormDefaults })
const creatingTargeted = ref(false)
const userSearchInput = ref('')
const userDropdownOpen = ref(false)
const userSuggestions = ref([])
const tabGroup = computed(() => TAB_GROUPS[props.initialTab] ?? TAB_GROUPS.announcement)
const activeTab = ref('announcement_list')
const filteredGlobalTable = computed(() => {
  if (!search.value.trim()) return globalNotifications.value
  const term = search.value.trim().toLowerCase()
  return globalNotifications.value.filter(n => 
    n.title.toLowerCase().includes(term) || n.message.toLowerCase().includes(term)
  )
})
const TAB_GROUPS = {
  announcement: [
    { id: 'announcement_list', label: 'Liste' },
    { id: 'announcement_create', label: 'Créer' },
  ]
}
const breadcrumbSubCategory = computed(() => {
  if (activeTab.value.includes('announcement')) return 'Communication'
  return 'Communication'
})
const confirmModal = reactive({
  isOpen: false,
  title: '',
  message: '',
  loading: false,
  onConfirm: null
})

function defaultTabForGroup(groupKey) {
  return 'announcement_list'
}
function onTabChange(tab) {
  activeTab.value = tab
  if (tab === 'announcement_list') fetchGlobalNotifications()
  if (tab === 'announcement_create') {
    loadPresetsAndUsers()
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
async function fetchGlobalNotifications() {
  loadingGlobal.value = true
  try {
    const res = await axios.get('/api/admin/notification/global/list')
    globalNotifications.value = res.data?.notifications ?? res.data?.data ?? []
  } catch {
    globalNotifications.value = []
  } finally {
    loadingGlobal.value = false
  }
}
async function loadPresetsAndUsers() {
  try {
    const [pr, ur] = await Promise.all([
      axios.get('/api/admin/preset/list'),
      axios.get('/api/admin/user/list', { params: { limit: 100 } })
    ])
    allPresets.value = pr.data?.presets ?? pr.data?.data ?? []
    allUsers.value = ur.data?.users ?? []
  } catch {
    showToast('Erreur lors du chargement des cibles', 'error')
  }
}
function selectUserForTarget(u) {
  targetedForm.user_id = u.id
  userSearchInput.value = u.username
  userDropdownOpen.value = false
}
async function toggleGlobalNotification(id) {
  if (expandedGlobal.value === id) {
    expandedGlobal.value = null
    globalDetail.value = null
    globalReads.value = []
    return
  }
  expandedGlobal.value = id
  globalDetail.value = globalNotifications.value.find(n => n.id === id) || null
  loadingReads.value = true
  try {
    const res = await axios.get(`/api/admin/notification/global/${id}/reads`)
    globalReads.value = res.data?.reads ?? res.data?.data ?? []
  } catch {
    globalReads.value = []
  } finally {
    loadingReads.value = false
  }
}
async function deleteGlobalNotification(id, title) {
  triggerConfirm(
    'Supprimer l\'annonce globale',
    `Voulez-vous vraiment supprimer l'annonce "${title}" ? Les suivis de lecture associés seront également supprimés.`,
    async () => {
      try {
        await axios.post(`/api/admin/notification/global/${id}/delete`)
        showToast(`Annonce "${title}" supprimée`)
        if (expandedGlobal.value === id) {
          expandedGlobal.value = null
          globalDetail.value = null
        }
        await fetchGlobalNotifications()
      } catch (e) {
        showToast(e.response?.data?.message ?? 'Erreur lors de la suppression', 'error')
        throw e
      }
    }
  )
}
async function submitCreateGlobal() {
  if (!globalForm.title.trim() || !globalForm.message.trim()) {
    showToast('Le titre et le message sont requis', 'error')
    return
  }
  if (!globalForm.isPermanent && !globalForm.end_date) {
    showToast('Veuillez définir une date de fin, ou cochez "Diffusion permanente".', 'error')
    return
  }
  creatingGlobal.value = true
  try {
    const now = new Date()
    const pad = (n) => String(n).padStart(2, '0')
    const currentDebut = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`
    const payload = {
      title: globalForm.title.trim(),
      message: globalForm.message.trim(),
      debut: currentDebut,
      end: globalForm.isPermanent ? null : globalForm.end_date.replace('T', ' ') + ':00'
    }
    await axios.post('/api/admin/notification/global/create', payload)
    showToast('Annonce globale diffusée avec succès !')
    Object.assign(globalForm, { ...globalFormDefaults })
    activeTab.value = 'announcement_list'
    await fetchGlobalNotifications()
  } catch (e) {
    showToast(e.response?.data?.message ?? 'Erreur lors de la diffusion de l\'annonce', 'error')
  } finally {
    creatingGlobal.value = false
  }
}
async function submitCreateTargeted() {
  if (!targetedForm.title.trim() || !targetedForm.message.trim()) {
    showToast('Le titre et le message sont requis', 'error')
    return
  }
  if (targetedForm.target_type === 'user' && !targetedForm.user_id) {
    showToast('Veuillez sélectionner un utilisateur cible', 'error')
    return
  }
  if (targetedForm.target_type === 'preset' && !targetedForm.preset_id) {
    showToast('Veuillez sélectionner un preset / groupe cible', 'error')
    return
  }
  creatingTargeted.value = true
  try {
    let endpoint = ''
    let payload = {
      title: targetedForm.title.trim(),
      message: targetedForm.message.trim()
    }
    if (targetedForm.target_type === 'user') {
      payload.user_id = Number(targetedForm.user_id)
      endpoint = '/api/admin/notification/create'
    } else {
      payload.preset_id = Number(targetedForm.preset_id)
      endpoint = '/api/admin/notification/preset/send'
    }
    const res = await axios.post(endpoint, payload)
    showToast(res.data?.message || 'Notification ciblée envoyée avec succès !')
    Object.assign(targetedForm, { ...targetedFormDefaults })
    userSearchInput.value = ''
    activeTab.value = 'announcement_list'
  } catch (e) {
    showToast(e.response?.data?.message ?? 'Erreur lors de l\'envoi de la notification', 'error')
  } finally {
    creatingTargeted.value = false
  }
}
function setSort(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = 'asc'
  }
  globalNotifications.value.sort((a, b) => {
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
watch(
  () => props.initialTab,
  async (groupKey) => {
    activeTab.value = defaultTabForGroup(groupKey)
    await fetchGlobalNotifications()
  },
  { immediate: true }
)

onMounted(() => {
  fetchGlobalNotifications()
})
</script>

<template>
  <div class="flex flex-col h-full">
    <div class="flex items-center justify-between mb-6">
      <div>
        <p class="font-code text-[10px] tracking-[0.18em] uppercase text-base-content/40 mb-1">Admin > {{ breadcrumbSubCategory }}</p>
        <h1 class="font-titre font-bold text-2xl text-base-content leading-none">Communication</h1>
      </div>
      <span v-if="activeTab === 'announcement_list'" class="font-code text-sm text-base-content/50 border border-secondary px-2 py-1">{{ globalNotifications.length }} ANNONCE{{ globalNotifications.length > 1 ? 'S' : '' }}</span>
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
    <div v-if="activeTab === 'announcement_list'" class="flex flex-col gap-4">
      <div class="flex items-center gap-2">
        <button
          @click="activeTab = 'announcement_create'"
          class="flex items-center gap-2 bg-primary text-base-100 hover:bg-primary/80 px-4 py-2 font-code text-xs font-bold tracking-wider transition-colors shadow-sm"
        >
          <span>+ Créer une nouvelle annonce</span>
        </button>
      </div>
      <div class="flex items-center gap-2 flex-wrap mb-2">
        <div class="relative flex-1 min-w-48">
          <span class="absolute left-3 top-1/2 -translate-y-1/2 font-code text-base-content/30 text-xs select-none">⌕</span>
          <input
            v-model="search"
            type="text"
            placeholder="Rechercher une annonce..."
            class="w-full bg-base-100 border border-base-300 focus:border-primary outline-none pl-7 pr-3 py-2 font-code text-xs text-base-content placeholder:text-base-content/25 transition-colors"
          />
        </div>
      </div>
      <div class="border border-base-300 overflow-hidden flex flex-col" style="max-height: calc(100vh - 220px);">
        <div class="grid grid-cols-[2fr_2.5fr_1fr_1.2fr_1.2fr_1.2fr_120px] bg-base-200 border-b border-base-300 shrink-0">
          <button
            v-for="col in [
              { key: 'title',      label: 'Titre'     },
              { key: 'message',    label: 'Message'   },
              { key: 'type',       label: 'Type'      },
              { key: 'debut',      label: 'Début'     },
              { key: 'end',        label: 'Fin'       },
              { key: 'created_at', label: 'Envoi'     },
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
          <div v-if="loadingGlobal" class="flex justify-center py-16">
            <span class="loading loading-spinner loading-md text-primary"></span>
          </div>
          <div v-else-if="!filteredGlobalTable.length" class="flex flex-col items-center justify-center py-10 gap-1">
            <span class="font-code text-xs text-base-content/25">Aucune annonce globale trouvée</span>
          </div>
          <div v-else class="flex flex-col">
            <template v-for="notif in filteredGlobalTable" :key="notif.id">
              <div
                @click="toggleGlobalNotification(notif.id)"
                :class="[
                  'grid grid-cols-[2fr_2.5fr_1fr_1.2fr_1.2fr_1.2fr_120px] items-center border-b border-base-300/50 cursor-pointer transition-colors duration-100',
                  expandedGlobal === notif.id ? 'bg-primary/8 border-l-2 border-l-primary' : 'hover:bg-base-300/30'
                ]"
              >
                <div class="px-4 py-3 flex items-center gap-2 min-w-0">
                  <span class="font-code text-[10px] text-base-content/30 shrink-0">#{{ notif.id }}</span>
                  <span class="font-code text-xs text-base-content font-medium truncate">{{ notif.title }}</span>
                </div>
                <div class="px-4 py-3 flex items-center min-w-0">
                  <span class="font-code text-xs text-base-content/70 truncate">{{ notif.message }}</span>
                </div>
                <!-- Type (Temporaire / Permanent) -->
                <div class="px-4 py-3 flex items-center">
                  <span :class="['font-text text-[10px] px-2 py-0.5 leading-none border', notif.end ? 'bg-warning/15 text-warning border-warning/30' : 'bg-info/15 text-info border-info/30']">
                    {{ notif.end ? 'Temporaire' : 'Permanent' }}
                  </span>
                </div>
                <div class="px-4 py-3 flex items-center">
                  <span class="font-code text-[11px] text-base-content/60">{{ notif.debut ?? '—' }}</span>
                </div>
                <div class="px-4 py-3 flex items-center">
                  <span class="font-code text-[11px] text-base-content/60">{{ notif.end ?? '-' }}</span>
                </div>
                <div class="px-4 py-3 flex items-center">
                  <span class="font-code text-[11px] text-base-content/60">{{ notif.created_at ?? '—' }}</span>
                </div>
                <div class="px-4 py-3 flex items-center justify-end gap-1.5" @click.stop>
                  <button class="font-text text-xs text-error hover:text-error/70 px-1" @click="deleteGlobalNotification(notif.id, notif.title)" title="Supprimer">Supprimer</button>
                </div>
              </div>
              <div v-if="expandedGlobal === notif.id" class="border-b border-base-300 bg-base-300/50 p-5">
                <p class="font-stitre text-[12px] tracking-widest uppercase text-primary/70 mb-3">Suivi de lecture des utilisateurs</p>
                <div v-if="loadingReads" class="flex justify-center py-6">
                  <span class="loading loading-dots loading-sm text-primary"></span>
                </div>
                <div v-else-if="!globalReads.length" class="font-code text-xs text-base-content/40">Aucun utilisateur n'a encore lu cette annonce.</div>
                <div v-else class="max-h-48 overflow-y-auto flex flex-col gap-1">
                  <div v-for="r in globalReads" :key="r.user_id" class="flex items-center justify-between px-3 py-1.5 bg-base-100 border border-base-300 font-code text-xs">
                    <span class="text-base-content font-medium">{{ r.username }}</span>
                    <span class="text-base-content/40 text-[10px]">Lu le : {{ r.read_at ?? '—' }}</span>
                  </div>
                </div>
              </div>
            </template>
          </div>
        </div>
        <div class="border-t border-base-300 px-4 py-2 bg-base-200/50 flex items-center justify-between shrink-0">
          <span class="font-code text-[10px] text-base-content/30">{{ filteredGlobalTable.length }} / {{ globalNotifications.length }} ANNONCE{{ filteredGlobalTable.length > 1 ? 'S' : '' }}</span>
          <span
            v-if="search"
            class="font-code text-[10px] text-primary/60 cursor-pointer hover:text-primary transition-colors"
            @click="clearFilters"
          >Effacer les filtres</span>
        </div>
      </div>
    </div>
    <div v-if="activeTab === 'announcement_create'" class="w-full">
      <div class="grid grid-cols-1 xl:grid-cols-2 gap-8 items-start">
        <div class="border border-base-300 bg-base-200/40 p-6">
          <p class="font-code text-[10px] tracking-widest uppercase text-base-content/35 mb-1">Nouveau message</p>
          <h2 class="font-titre font-bold text-lg text-base-content mb-6">Créer une nouvelle annonce</h2>
          <div class="flex flex-col gap-4">
            <div class="flex flex-col gap-1">
              <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Portée de l'annonce</label>
              <div class="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  @click="creationType = 'global'"
                  :class="[
                    'py-2 font-code text-xs border transition-colors',
                    creationType === 'global' ? 'bg-primary text-base-100 border-primary font-bold' : 'bg-base-100 text-base-content/70 border-base-300 hover:text-base-content'
                  ]"
                >
                  Annonce Globale
                </button>
                <button
                  type="button"
                  @click="creationType = 'targeted'"
                  :class="[
                    'py-2 font-code text-xs border transition-colors',
                    creationType === 'targeted' ? 'bg-primary text-base-100 border-primary font-bold' : 'bg-base-100 text-base-content/70 border-base-300 hover:text-base-content'
                  ]"
                >
                  Notification Ciblée
                </button>
              </div>
            </div>
            <template v-if="creationType === 'targeted'">
              <div class="flex flex-col gap-1">
                <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Type de destinataire</label>
                <select v-model="targetedForm.target_type" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors">
                  <option value="user">Utilisateur unique</option>
                  <option value="preset">Groupe / Preset (Ex: Campus)</option>
                </select>
              </div>
              <div v-if="targetedForm.target_type === 'user'" class="flex flex-col gap-1 relative">
                <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Utilisateur cible *</label>
                <input
                  v-model="userSearchInput"
                  @focus="userDropdownOpen = true"
                  @blur="setTimeout(() => userDropdownOpen = false, 200)"
                  type="text"
                  placeholder="Taper un nom d'utilisateur..."
                  class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors"
                />
                <div v-if="userDropdownOpen && userSuggestions.length" class="absolute z-20 top-full left-0 right-0 mt-1 bg-base-100 border border-base-300 shadow-xl max-h-48 overflow-y-auto">
                  <div
                    v-for="u in userSuggestions" :key="u.id"
                    @mousedown.prevent="selectUserForTarget(u)"
                    class="px-3 py-2 font-code text-xs text-base-content hover:bg-primary/15 cursor-pointer flex justify-between items-center"
                  >
                    <span>{{ u.username }}</span>
                    <span class="text-[10px] text-base-content/40">#{{ u.id }}</span>
                  </div>
                </div>
              </div>
              <div v-if="targetedForm.target_type === 'preset'" class="flex flex-col gap-1">
                <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Preset / Groupe cible *</label>
                <select v-model="targetedForm.preset_id" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors">
                  <option value="">— Choisir un preset —</option>
                  <option v-for="p in allPresets" :key="p.id" :value="p.id">{{ p.name }} ({{ p.affiliation }})</option>
                </select>
              </div>
            </template>
            <template v-if="creationType === 'global'">
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div class="flex flex-col gap-1">
                  <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Début de diffusion</label>
                  <input 
                    type="datetime-local" 
                    :value="getCurrentLocalDateTime()" 
                    disabled 
                    title="Pour programmer une annonce, passer par l'onglet Programmation"
                    class="bg-base-100/50 border border-base-300/60 opacity-70 outline-none px-3 py-2 font-code text-sm text-base-content cursor-not-allowed" 
                  />
                </div>
                <div class="flex flex-col gap-1">
                  <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Fin de diffusion</label>
                  <input 
                    v-model="globalForm.end_date" 
                    type="datetime-local" 
                    :disabled="globalForm.isPermanent"
                    :class="{'opacity-40 cursor-not-allowed bg-base-100/50': globalForm.isPermanent}"
                    class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors" 
                  />
                </div>
              </div>
              <div class="border border-base-300/60 bg-base-100/30 p-2.5">
                <label class="flex items-center gap-2 cursor-pointer select-none">
                  <input v-model="globalForm.isPermanent" type="checkbox" class="checkbox checkbox-xs checkbox-primary rounded-none" />
                  <span class="font-code text-xs text-base-content font-medium">Diffusion permanente (pas de date de fin)</span>
                </label>
              </div>
            </template>
            <div class="flex flex-col gap-1">
              <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Titre *</label>
              <input 
                :value="creationType === 'global' ? globalForm.title : targetedForm.title"
                @input="e => creationType === 'global' ? globalForm.title = e.target.value : targetedForm.title = e.target.value"
                type="text" 
                placeholder="Titre de l'annonce..." 
                class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content placeholder:text-base-content/20 transition-colors" 
              />
            </div>
            <div class="flex flex-col gap-1">
              <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Message *</label>
              <textarea 
                :value="creationType === 'global' ? globalForm.message : targetedForm.message"
                @input="e => creationType === 'global' ? globalForm.message = e.target.value : targetedForm.message = e.target.value"
                rows="5" 
                placeholder="Contenu du message..." 
                class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content placeholder:text-base-content/20 transition-colors resize-none"
              ></textarea>
            </div>
          </div>
          <div class="flex gap-3 mt-6">
            <button 
                v-if="creationType === 'global'"
                @click="submitCreateGlobal" 
                :disabled="creatingGlobal || !globalForm.title || !globalForm.message || (!globalForm.isPermanent && !globalForm.end_date)" 
                class="px-5 py-2 font-code text-xs tracking-wide bg-primary text-base-100 hover:bg-primary/80 transition-colors disabled:opacity-30 flex items-center gap-2"
                >
                <span v-if="creatingGlobal" class="loading loading-xs"></span>
                <span>Diffuser l'annonce globale</span>
            </button>
            <button 
              v-else
              @click="submitCreateTargeted" 
              :disabled="creatingTargeted || !targetedForm.title || !targetedForm.message" 
              class="px-5 py-2 font-code text-xs tracking-wide bg-primary text-base-100 hover:bg-primary/80 transition-colors disabled:opacity-30 flex items-center gap-2"
            >
              <span v-if="creatingTargeted" class="loading loading-xs"></span>
              <span>Envoyer la notification ciblée</span>
            </button>
            <button @click="activeTab = 'announcement_list'" class="px-5 py-2 font-code text-xs tracking-wide border border-base-300 text-base-content/50 hover:text-base-content hover:border-base-content/30 transition-colors">Annuler</button>
          </div>
        </div>
        <div class="sticky top-6 border border-primary/30 bg-base-100/80 p-6 shadow-2xl backdrop-blur-md">
          <div class="flex items-center justify-between border-b border-base-300 pb-3 mb-6">
            <span class="font-code text-[10px] tracking-widest uppercase text-primary font-bold">
              Prévisualisation ({{ creationType === 'global' ? 'Annonce Globale' : 'Notification Personnelle' }})
            </span>
          </div>
          <div class="space-y-4">
            <div class="p-4 bg-base-200 border border-base-300 flex items-start gap-3">
              <span class="badge badge-sm mt-0.5" :class="creationType === 'global' ? 'badge-primary' : 'badge-success'">
                {{ creationType === 'global' ? '📢' : '🔔' }}
              </span>
              <div class="flex flex-col gap-1 flex-1">
                <span class="font-bold text-xs text-base-content">
                  {{ (creationType === 'global' ? globalForm.title : targetedForm.title) || 'Titre du message' }}
                </span>
                <span class="text-xs opacity-75 whitespace-normal break-words leading-tight">
                  {{ (creationType === 'global' ? globalForm.message : targetedForm.message) || 'Le contenu de votre message apparaîtra ici en temps réel...' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <PopUpConfirm
    :is-open="confirmModal.isOpen"
    :title="confirmModal.title"
    :message="confirmModal.message"
    :loading="confirmModal.loading"
    @confirm="handleConfirmDialog"
    @cancel="closeConfirmDialog"
  />
</template>