<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import axios from 'axios'
import { showToast } from './useAdminToast.js'
import { getAssetUrl } from '../../utils/assets'

const activeTab = ref('list')
const activeKind = ref('AVATAR')
const RARETE_MAP = {
  COMMUN:     'bg-base-300 text-base-content/60 border border-base-300',
  RARE:       'bg-info/15 text-info border border-info/30',
  EPIC:       'bg-secondary/15 text-secondary border border-secondary/30',
  LEGENDARY:  'bg-warning/15 text-warning border border-warning/30',
}
const rareteClass = r => RARETE_MAP[r] ?? 'bg-base-300 text-base-content/60 border border-base-300'
const cosmetics        = ref([])
const loadingCosmetics = ref(false)
const expandedCosmetic = ref(null)
const search           = ref('')
const filterType       = ref('')
const sortKey          = ref('name')
const sortDir          = ref('asc')
const filteredCosmetics = computed(() => {
  return cosmetics.value.filter(c => {
    const matchesSearch = !search.value.trim() || 
      c.name.toLowerCase().includes(search.value.trim().toLowerCase()) || 
      c.description.toLowerCase().includes(search.value.trim().toLowerCase())
    
    const matchesType = !filterType.value || c.type === filterType.value
    return matchesSearch && matchesType
  })
})
const assignModalOpen = ref(false)
const targetCosmetic  = ref(null)
const assignQuery     = ref('')
const assignResults   = ref([])
const assignSearching = ref(false)
const assigning       = ref(false)
let assignDebounceTimer = null
const explorerOpen     = ref(false)
const explorerStep     = ref('root')
const explorerCategory = ref(null)
const explorerSubtype  = ref(null)
const explorerIcons    = ref([])
const loadingIcons     = ref(false)
const createDefaults = { type: 'AVATAR', name: '', description: '', rarete: 'COMMUN', exclu: false, icon_id: null, icon_url: '' }
const createForm = reactive({ ...createDefaults })
const creating   = ref(false)
const editTarget = ref(null)
const editForm   = reactive({ type: '', name: '', description: '', rarete: 'COMMUN', exclu: false, icon_id: null, icon_url: '' })
const editing    = ref(false)

async function fetchCosmetics() {
  loadingCosmetics.value = true
  try {
    const res = await axios.get('/api/admin/cosmetic/list')
    cosmetics.value = res.data?.cosmetics ?? res.data?.data ?? []
  } catch {
    showToast('Impossible de charger les cosmétiques', 'error')
  } finally {
    loadingCosmetics.value = false
  }
}
function toggleCosmetic(id) {
  expandedCosmetic.value = expandedCosmetic.value === id ? null : id
}
async function deleteCosmetic(id, name) {
  if (!confirm(`Supprimer le cosmétique "${name}" ? Action irréversible.`)) return
  try {
    await axios.post(`/api/admin/cosmetic/${id}/delete`)
    showToast(`Cosmétique "${name}" supprimé`)
    if (expandedCosmetic.value === id) expandedCosmetic.value = null
    await fetchCosmetics()
  } catch (e) {
    showToast(e.response?.data?.message ?? 'Erreur suppression', 'error')
  }
}
function setSort(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = 'asc'
  }
  cosmetics.value.sort((a, b) => {
    let modifier = sortDir.value === 'asc' ? 1 : -1
    if (a[sortKey.value] < b[sortKey.value]) return -1 * modifier
    if (a[sortKey.value] > b[sortKey.value]) return 1 * modifier
    return 0
  })
}
function openAssignModal(c) {
  targetCosmetic.value = c
  assignQuery.value = ''
  assignResults.value = []
  assignModalOpen.value = true
}
function onAssignQueryInput() {
  clearTimeout(assignDebounceTimer)
  const q = assignQuery.value.trim()
  if (!q) { assignResults.value = []; return }
  assignDebounceTimer = setTimeout(() => searchAssignUsers(q), 250)
}
async function searchAssignUsers(q) {
  assignSearching.value = true
  try {
    const res = await axios.get('/api/admin/user/list', { params: { search: q, limit: 8 } })
    assignResults.value = res.data?.users ?? []
  } catch {
    assignResults.value = []
  } finally {
    assignSearching.value = false
  }
}
async function toggleUserCosmetic(user, assign) {
  if (!targetCosmetic.value) return
  assigning.value = true
  try {
    // Appel de la fonction d'assignation/retrait existante
    await axios.post(`/api/admin/cosmetic/${targetCosmetic.value.id}/assign`, { 
      user_id: user.id,
      assign: assign 
    })
    showToast(`Cosmétique ${assign ? 'attribué à' : 'retiré de'} ${user.username}`)
    await fetchCosmetics()
    // Met à jour l'objet cible localement pour le feedback immédiat dans la modale si besoin
  } catch (e) {
    showToast(e.response?.data?.message ?? 'Erreur lors de l\'attribution', 'error')
  } finally {
    assigning.value = false
  }
}
async function openExplorer() {
  explorerOpen.value = true
  explorerStep.value = 'root'
  explorerCategory.value = null
  explorerSubtype.value = null
  explorerIcons.value = []
}
function selectCategory(cat) {
  explorerCategory.value = cat
  if (cat === 'BADGE') {
    explorerSubtype.value = 'BADGE'
    loadIconsForExplorer('BADGE')
  } else {
    explorerStep.value = 'cosmetic_sub'
  }
}
function selectCosmeticSubtype(sub) {
  explorerSubtype.value = sub
  loadIconsForExplorer(sub)
}
async function loadIconsForExplorer(type) {
  loadingIcons.value = true
  try {
    const res = await axios.get(`/api/admin/icon/list/${type}`)
    explorerIcons.value = res.data?.icons ?? []
    explorerStep.value = 'grid'
  } catch {
    showToast('Erreur lors du chargement des icônes', 'error')
    explorerIcons.value = []
  } finally {
    loadingIcons.value = false
  }
}
function explorerBack() {
  if (explorerStep.value === 'grid') {
    if (explorerCategory.value === 'BADGE') {
      explorerStep.value = 'root'
      explorerCategory.value = null
    } else {
      explorerStep.value = 'cosmetic_sub'
      explorerSubtype.value = null
    }
  } else if (explorerStep.value === 'cosmetic_sub') {
    explorerStep.value = 'root'
    explorerCategory.value = null
  }
}
function pickIcon(icon) {
  createForm.icon_id = icon.id
  createForm.icon_url = icon.filepath
  editForm.icon_id = icon.id
  editForm.icon_url = icon.filepath
  explorerOpen.value = false
}
function openCreate(kind) {
  activeKind.value = kind
  Object.assign(createForm, { ...createDefaults, type: kind })
  activeTab.value = 'create'
}
async function submitCreate() {
  if (!createForm.name || !createForm.description || !createForm.rarete) {
    showToast('Tous le nom, la description et la rareté sont requis', 'error'); return
  }
  if (!createForm.icon_id) {
    showToast('Veuillez sélectionner une icône depuis l\'explorateur', 'error'); return
  }
  creating.value = true
  try {
    await axios.post('/api/admin/cosmetic/create', {
      type: createForm.type,
      name: createForm.name,
      description: createForm.description,
      rarete: createForm.rarete,
      exclu: createForm.exclu,
      icon_id: createForm.icon_id
    })
    await fetchCosmetics()
    showToast(`${createForm.type === 'AVATAR' ? 'Avatar' : 'Bannière'} "${createForm.name}" créé(e) !`)
    Object.assign(createForm, { ...createDefaults, type: activeKind.value })
    activeTab.value = 'list'
  } catch (e) {
    showToast(e.response?.data?.message ?? 'Erreur création', 'error')
  } finally {
    creating.value = false
  }
}
function openEdit(c) {
  editTarget.value   = c.id
  activeTab.value    = 'edit'
  Object.assign(editForm, {
    type:        c.type        ?? 'AVATAR',
    name:        c.name        ?? '',
    description: c.description ?? '',
    rarete:      c.rarete      ?? 'COMMUN',
    exclu:       c.exclu       ?? false,
    icon_id:     c.icon_id     ?? null,
    icon_url:    c.icon_url    ?? '',
  })
}
async function submitEdit() {
  if (!editForm.name || !editForm.description || !editForm.rarete) {
    showToast('Tous les champs obligatoires sont requis', 'error'); return
  }
  editing.value = true
  try {
    const payload = {
      new_type: editForm.type,
      new_name: editForm.name,
      new_description: editForm.description,
      new_rarete: editForm.rarete,
      new_exclu: editForm.exclu
    }
    if (editForm.icon_id) {
      payload.new_icon_id = editForm.icon_id
    }
    await axios.post(`/api/admin/cosmetic/${editTarget.value}/modify`, payload)
    showToast('Cosmétique modifié !')
    activeTab.value  = 'list'
    editTarget.value = null
    await fetchCosmetics()
  } catch (e) {
    showToast(e.response?.data?.message ?? 'Erreur modification', 'error')
  } finally {
    editing.value = false
  }
}

onMounted(() => { fetchCosmetics() })
</script>

<template>
  <!-- Titre -->
  <div class="flex items-end justify-between mb-6">
    <div>
      <p class="font-code text-[10px] tracking-[0.18em] uppercase text-base-content/40 mb-1">Admin › Cosmétiques</p>
      <h1 class="font-titre font-bold text-2xl text-base-content leading-none">Cosmétiques</h1>
    </div>
    <span class="font-code text-sm text-base-content/50 border border-secondary px-2 py-1">{{ cosmetics.length }} COSMÉTIQUE{{ cosmetics.length > 1 ? 'S' : '' }}</span>
  </div>
  <div class="flex gap-0 border-b border-base-300 mb-6">
    <button
      v-for="tab in [
        { id: 'list',   label: 'Liste' },
        { id: 'create', label: 'Créer' },
        { id: 'edit',   label: 'Modifier', locked: !editTarget },
      ]"
      :key="tab.id"
      :disabled="tab.locked"
      @click="!tab.locked && (activeTab = tab.id)"
      :class="[
        'px-5 py-2.5 font-code text-xs tracking-wide transition-colors duration-150 border-b-2 -mb-px',
        activeTab === tab.id
          ? 'border-primary text-base-content'
          : tab.locked
            ? 'border-transparent text-base-content/20 cursor-not-allowed'
            : 'border-transparent text-base-content/45 hover:text-base-content/75 hover:border-base-content/20'
      ]"
    >{{ tab.label }}</button>
  </div>
  <div v-if="activeTab === 'list'" class="flex flex-col gap-4">
    <div class="flex items-center justify-between gap-2 flex-wrap">
      <button @click="openCreate('AVATAR')" class="bg-primary text-base-100 hover:bg-primary/80 px-4 py-2 font-code text-xs font-bold transition-colors shadow-sm">
        <span>+ Créer un nouveau cosmétique</span>
      </button>
    </div>
    <div class="flex items-center gap-2 flex-wrap mb-2">
      <div class="relative flex-1 min-w-48">
        <span class="absolute left-3 top-1/2 -translate-y-1/2 font-code text-base-content/30 text-xs select-none">⌕</span>
        <input
          v-model="search"
          type="text"
          placeholder="Rechercher un cosmétique..."
          class="w-full bg-base-100 border border-base-300 focus:border-primary outline-none pl-7 pr-3 py-2 font-code text-xs text-base-content placeholder:text-base-content/25 transition-colors"
        />
      </div>
      <select
        v-model="filterType"
        class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-xs text-base-content transition-colors"
      >
        <option value="">Tous les types</option>
        <option value="AVATAR">Avatar</option>
        <option value="BANNER">Bannière</option>
      </select>
    </div>
    <div class="border border-base-300 overflow-hidden flex flex-col" style="max-height: calc(100vh - 220px);">
      <div class="grid grid-cols-[1fr_2.5fr_1.5fr_1.5fr_1fr_120px] bg-base-200 border-b border-base-300 shrink-0">
        <div class="px-4 py-2.5 font-code text-[10px] uppercase tracking-widest text-base-content/40">Aperçu</div>
        <button v-for="col in [{ key: 'name', label: 'Nom' }, { key: 'type', label: 'Type' }, { key: 'rarete', label: 'Rareté' }, { key: 'exclu', label: 'Exclusif' }]" :key="col.key" @click="setSort(col.key)" class="flex items-center gap-1 px-4 py-2.5 font-code text-[10px] uppercase tracking-widest text-base-content/40 hover:text-base-content text-left">
          {{ col.label }} <span v-if="sortKey === col.key" class="text-primary">{{ sortDir === 'asc' ? '↑' : '↓' }}</span>
        </button>
        <div class="px-4 py-2.5 font-code text-[10px] uppercase tracking-widest text-base-content/40 text-right">Actions</div>
      </div>
      <div class="flex-1 overflow-y-auto">
        <div v-if="loadingCosmetics" class="flex justify-center py-16"><span class="loading loading-spinner text-primary"></span></div>
        <div v-else-if="!filteredCosmetics.length" class="flex justify-center py-10"><span class="font-code text-xs text-base-content/25">Aucun cosmétique trouvé</span></div>
        <div v-else class="flex flex-col">
          <template v-for="c in filteredCosmetics" :key="c.id">
            <div @click="toggleCosmetic(c.id)" :class="['grid grid-cols-[1fr_2.5fr_1.5fr_1.5fr_1fr_120px] items-center border-b border-base-300/50 cursor-pointer transition-colors duration-100', expandedCosmetic === c.id ? 'bg-primary/8 border-l-2 border-l-primary' : 'hover:bg-base-300/30']">
              <div class="px-4 py-2">
                <div class="w-8 h-8 bg-base-100 border border-base-300 flex items-center justify-center overflow-hidden">
                  <img v-if="c.icon_url" :src="getAssetUrl(c.icon_url)" class="w-full h-full object-contain" @error="$event.target.style.display='none'" />
                  <span v-else class="text-xs opacity-20">🎨</span>
                </div>
              </div>
              <div class="px-4 py-3 font-code text-xs font-medium truncate">#{{ c.id }} - {{ c.name }}</div>
              <div class="px-4 py-3 font-code text-xs text-base-content/70 uppercase">{{ c.type }}</div>
              <div class="px-4 py-3 font-code text-xs"><span :class="['px-2 py-0.5 text-[10px]', rareteClass(c.rarete)]">{{ c.rarete }}</span></div>
              <div class="px-4 py-3 font-code text-xs">{{ c.exclu ? 'Oui' : 'Non' }}</div>
              <div class="px-4 py-3 flex justify-end gap-1.5" @click.stop>
                <button class="font-text text-xs text-info hover:text-info/70 px-1" @click="openEdit(c)" title="Modifier">Modifier</button>
                <button class="font-text text-xs text-error hover:text-error/70 px-1" @click="deleteCosmetic(c.id, c.name)" title="Supprimer">Supprimer</button>
              </div>
            </div>
            <div v-if="expandedCosmetic === c.id" class="border-b border-base-300 bg-base-300/50 p-6">
              <div class="grid grid-cols-1 md:grid-cols-3 gap-6 items-start">
                <div class="flex flex-col gap-4">
                  <div class="flex items-center gap-4">
                    <div class="w-16 h-16 bg-base-100 border border-base-300 flex items-center justify-center overflow-hidden shrink-0">
                      <img v-if="c.icon_url" :src="getAssetUrl(c.icon_url)" class="max-w-full max-h-full object-contain" @error="$event.target.style.display='none'" />
                      <span v-else class="text-xl opacity-20">🎨</span>
                    </div>
                    <div>
                      <p class="font-code text-xs text-base-content/40">#{{ c.id }}</p>
                      <h3 class="font-titre font-bold text-base text-base-content">{{ c.name }}</h3>
                      <span :class="['inline-block mt-1 px-2 py-0.5 text-[10px] font-code uppercase', rareteClass(c.rarete)]">{{ c.rarete }}</span>
                    </div>
                  </div>
                  <dl class="grid grid-cols-2 gap-2 text-xs font-code bg-base-100/40 p-3 border border-base-300">
                    <dt class="text-base-content/40">Type</dt><dd class="text-base-content font-medium uppercase text-right">{{ c.type }}</dd>
                    <dt class="text-base-content/40">Exclusif</dt><dd class="text-base-content font-medium text-right">{{ c.exclu ? 'Oui' : 'Non' }}</dd>
                  </dl>
                </div>
                <div class="flex flex-col gap-4">
                  <p class="font-code text-[10px] tracking-widest uppercase text-primary/70">Statistiques</p>
                  <div class="grid grid-cols-2 gap-3">
                    <div class="bg-base-100/60 border border-base-300 p-3 text-center">
                      <p class="font-titre font-bold text-primary text-xl leading-none">{{ c.user_count ?? 0 }}</p>
                      <p class="font-code text-[9px] uppercase tracking-widest text-base-content/40 mt-1">Possédé{{ c.user_count > 1 ? 's' : '' }}</p>
                    </div>
                    <div class="bg-base-100/60 border border-base-300 p-3 text-center">
                      <p class="font-titre font-bold text-success text-xl leading-none">{{ c.active_user_count ?? 0 }}</p>
                      <p class="font-code text-[9px] uppercase tracking-widest text-base-content/40 mt-1">Actif{{ c.active_user_count > 1 ? 's' : '' }}</p>
                    </div>
                  </div>
                  <div>
                    <p class="font-code text-[10px] tracking-widest uppercase text-base-content/40 mb-1">Description</p>
                    <p class="text-xs text-base-content/70 bg-base-200/60 border border-base-300 p-3 leading-relaxed">{{ c.description || 'Aucune description.' }}</p>
                  </div>
                </div>
                <div class="flex flex-col justify-between h-full bg-base-100/30 p-4 border border-base-300">
                  <div>
                    <p class="font-code text-[10px] tracking-widest uppercase text-primary/70 mb-2">Gestion des attributions</p>
                    <p class="text-xs text-base-content/60 mb-4">Gérez les attributions manuelles de ce cosmétique auprès des utilisateurs.</p>
                  </div>
                  <button
                    @click="openAssignModal(c)"
                    class="w-full py-2.5 bg-primary text-base-100 hover:bg-primary/80 font-code text-xs font-bold transition-colors shadow-sm text-center"
                  >
                    Gérer les attributions...
                  </button>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
  <div v-if="activeTab === 'create'" class="w-full">
    <div class="grid grid-cols-1 xl:grid-cols-2 gap-8 items-start">
      <div class="border border-base-300 bg-base-200/40 p-6">
        <p class="font-code text-[10px] tracking-widest uppercase text-base-content/35 mb-1">Nouveau cosmétique</p>
        <h2 class="font-titre font-bold text-lg text-base-content mb-6">Créer un cosmétique</h2>
        <div class="grid grid-cols-2 gap-2 mb-6">
          <button type="button" @click="createForm.type = 'AVATAR'" :class="['py-2 font-code text-xs border transition-colors', createForm.type === 'AVATAR' ? 'bg-primary text-base-100 border-primary font-bold' : 'bg-base-100 text-base-content/70 border-base-300 hover:text-base-content']">Avatar</button>
          <button type="button" @click="createForm.type = 'BANNER'" :class="['py-2 font-code text-xs border transition-colors', createForm.type === 'BANNER' ? 'bg-primary text-base-100 border-primary font-bold' : 'bg-base-100 text-base-content/70 border-base-300 hover:text-base-content']">Bannière</button>
        </div>
        <div class="flex flex-col gap-4">
          <div class="flex flex-col gap-1">
            <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Nom *</label>
            <input v-model="createForm.name" type="text" placeholder="Nom du cosmétique..." class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors" />
          </div>
          <div class="flex flex-col gap-1">
            <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Rareté *</label>
            <select v-model="createForm.rarete" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors">
              <option value="COMMUN">COMMUN</option>
              <option value="RARE">RARE</option>
              <option value="EPIC">ÉPIQUE</option>
              <option value="LEGENDARY">LÉGENDAIRE</option>
            </select>
          </div>
          <div class="border border-base-300/60 bg-base-100/30 p-2.5">
            <label class="flex items-center gap-2 cursor-pointer select-none">
              <input v-model="createForm.exclu" type="checkbox" class="checkbox checkbox-xs checkbox-primary rounded-none" />
              <span class="font-code text-xs text-base-content font-medium">Cosmétique exclusif</span>
            </label>
          </div>
          <div class="flex flex-col gap-1">
            <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Description *</label>
            <textarea v-model="createForm.description" rows="3" placeholder="Description..." class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content resize-none transition-colors"></textarea>
          </div>
        </div>
        <div class="flex gap-3 mt-6">
          <button @click="submitCreate" :disabled="creating || !createForm.name || !createForm.icon_id" class="px-5 py-2 font-code text-xs tracking-wide bg-primary text-base-100 hover:bg-primary/80 transition-colors disabled:opacity-30 flex items-center gap-2">
            <span v-if="creating" class="loading loading-xs"></span>
            <span>Créer le cosmétique</span>
          </button>
          <button @click="activeTab = 'list'" class="px-5 py-2 font-code text-xs tracking-wide border border-base-300 text-base-content/50 hover:text-base-content transition-colors">Annuler</button>
        </div>
      </div>
      <div class="border border-primary/30 bg-base-100/80 p-6 shadow-xl">
        <div class="flex items-center justify-between border-b border-base-300 pb-3 mb-4">
          <span class="font-code text-[10px] tracking-widest uppercase text-primary font-bold">Explorateur d'icônes</span>
          <button v-if="explorerStep !== 'root'" @click="explorerBack" class="font-code text-xs text-primary">← Revenir en arrière</button>
        </div>
        <div v-if="explorerStep === 'root'" class="grid grid-cols-2 gap-4 py-8">
          <div @click="selectCategory('COSMETIC')" class="border border-base-300 bg-base-200/50 p-6 flex flex-col items-center justify-center cursor-pointer hover:border-primary transition-all">
            <span class="text-3xl mb-2">📁</span>
            <span class="font-code text-xs font-bold text-base-content">Cosmétiques</span>
          </div>
          <div @click="selectCategory('BADGE')" class="border border-base-300 bg-base-200/50 p-6 flex flex-col items-center justify-center cursor-pointer hover:border-primary transition-all">
            <span class="text-3xl mb-2">📁</span>
            <span class="font-code text-xs font-bold text-base-content">Badges</span>
          </div>
        </div>
        <div v-else-if="explorerStep === 'cosmetic_sub'" class="grid grid-cols-2 gap-4 py-8">
          <div @click="selectCosmeticSubtype('AVATAR')" class="border border-base-300 bg-base-200/50 p-6 flex flex-col items-center justify-center cursor-pointer hover:border-primary transition-all">
            <span class="text-3xl mb-2">📁</span>
            <span class="font-code text-xs font-bold text-base-content">Avatars</span>
          </div>
          <div @click="selectCosmeticSubtype('BANNER')" class="border border-base-300 bg-base-200/50 p-6 flex flex-col items-center justify-center cursor-pointer hover:border-primary transition-all">
            <span class="text-3xl mb-2">📁</span>
            <span class="font-code text-xs font-bold text-base-content">Bannières</span>
          </div>
        </div>
        <div v-else-if="explorerStep === 'grid'">
          <div v-if="loadingIcons" class="flex justify-center py-12"><span class="loading loading-spinner text-primary"></span></div>
          <div v-else-if="!explorerIcons.length" class="text-center py-12 font-code text-xs text-base-content/40">Aucune icône dans ce dossier.</div>
          <div v-else class="grid grid-cols-3 sm:grid-cols-4 gap-3 max-h-80 overflow-y-auto p-1">
            <div
              v-for="ic in explorerIcons"
              :key="ic.id"
              @click="pickIcon(ic)"
              :class="['border p-2 flex flex-col items-center cursor-pointer transition-all bg-base-200/40', createForm.icon_id === ic.id ? 'border-primary bg-primary/10' : 'border-base-300 hover:border-base-content/40']"
            >
              <div class="w-12 h-12 flex items-center justify-center bg-base-100 border border-base-300 mb-1 overflow-hidden">
                <img :src="getAssetUrl(ic.filepath)" class="max-w-full max-h-full object-contain" @error="$event.target.style.display='none'" />
              </div>
              <span class="font-code text-[9px] text-base-content/60 truncate w-full text-center">{{ ic.filename }}</span>
            </div>
          </div>
        </div>
        <div class="mt-6 pt-4 border-t border-base-300 flex items-center justify-between">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 border border-base-300 bg-base-200 flex items-center justify-center overflow-hidden">
              <img v-if="createForm.icon_url" :src="getAssetUrl(createForm.icon_url)" class="max-w-full max-h-full object-contain" @error="$event.target.style.display='none'" />
            </div>
            <span class="font-code text-xs text-base-content/70">{{ createForm.icon_id ? `Icône #${createForm.icon_id} sélectionnée` : 'Aucune icône sélectionnée' }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div v-if="activeTab === 'edit' && editTarget" class="w-full">
    <div class="grid grid-cols-1 xl:grid-cols-2 gap-8 items-start">
      <div class="border border-base-300 bg-base-200/40 p-6">
        <p class="font-code text-[10px] tracking-widest uppercase text-base-content/35 mb-1">Cosmétique #{{ editTarget }}</p>
        <h2 class="font-titre font-bold text-lg text-base-content mb-6">Modifier le cosmétique</h2>
        <div class="grid grid-cols-2 gap-2 mb-6">
          <button type="button" @click="editForm.type = 'AVATAR'" :class="['py-2 font-code text-xs border transition-colors', editForm.type === 'AVATAR' ? 'bg-primary text-base-100 border-primary font-bold' : 'bg-base-100 text-base-content/70 border-base-300 hover:text-base-content']">👤 Avatar</button>
          <button type="button" @click="editForm.type = 'BANNER'" :class="['py-2 font-code text-xs border transition-colors', editForm.type === 'BANNER' ? 'bg-primary text-base-100 border-primary font-bold' : 'bg-base-100 text-base-content/70 border-base-300 hover:text-base-content']">🖼️ Bannière</button>
        </div>
        <div class="flex flex-col gap-4">
          <div class="flex flex-col gap-1">
            <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Nom *</label>
            <input v-model="editForm.name" type="text" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors" />
          </div>
          <div class="flex flex-col gap-1">
            <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Rareté *</label>
            <select v-model="editForm.rarete" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors">
              <option value="COMMUN">COMMUN</option>
              <option value="RARE">RARE</option>
              <option value="EPIC">ÉPIQUE</option>
              <option value="LEGENDARY">LÉGENDAIRE</option>
            </select>
          </div>
          <div class="border border-base-300/60 bg-base-100/30 p-2.5">
            <label class="flex items-center gap-2 cursor-pointer select-none">
              <input v-model="editForm.exclu" type="checkbox" class="checkbox checkbox-xs checkbox-primary rounded-none" />
              <span class="font-code text-xs text-base-content font-medium">Cosmétique exclusif</span>
            </label>
          </div>
          <div class="flex flex-col gap-1">
            <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Description *</label>
            <textarea v-model="editForm.description" rows="3" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content resize-none transition-colors"></textarea>
          </div>
        </div>
        <div class="flex gap-3 mt-6">
          <button @click="submitEdit" :disabled="editing" class="px-5 py-2 font-code text-xs tracking-wide bg-primary text-base-100 hover:bg-primary/80 transition-colors disabled:opacity-30 flex items-center gap-2">
            <span v-if="editing" class="loading loading-xs"></span>
            <span>Sauvegarder</span>
          </button>
          <button @click="activeTab = 'list'; editTarget = null" class="px-5 py-2 font-code text-xs tracking-wide border border-base-300 text-base-content/50 hover:text-base-content transition-colors">Annuler</button>
        </div>
      </div>
      <div class="border border-primary/30 bg-base-100/80 p-6 shadow-xl">
        <div class="flex items-center justify-between border-b border-base-300 pb-3 mb-4">
          <span class="font-code text-[10px] tracking-widest uppercase text-primary font-bold">Explorateur d'icônes</span>
          <button v-if="explorerStep !== 'root'" @click="explorerBack" class="font-code text-xs text-primary">← Revenir en arrière</button>
        </div>
        <div v-if="explorerStep === 'root'" class="grid grid-cols-2 gap-4 py-8">
          <div @click="selectCategory('COSMETIC')" class="border border-base-300 bg-base-200/50 p-6 flex flex-col items-center justify-center cursor-pointer hover:border-primary transition-all">
            <span class="text-3xl mb-2">📁</span>
            <span class="font-code text-xs font-bold text-base-content">Cosmétiques</span>
          </div>
          <div @click="selectCategory('BADGE')" class="border border-base-300 bg-base-200/50 p-6 flex flex-col items-center justify-center cursor-pointer hover:border-primary transition-all">
            <span class="text-3xl mb-2">📁</span>
            <span class="font-code text-xs font-bold text-base-content">Badges</span>
          </div>
        </div>
        <div v-else-if="explorerStep === 'cosmetic_sub'" class="grid grid-cols-2 gap-4 py-8">
          <div @click="selectCosmeticSubtype('AVATAR')" class="border border-base-300 bg-base-200/50 p-6 flex flex-col items-center justify-center cursor-pointer hover:border-primary transition-all">
            <span class="text-3xl mb-2">📁</span>
            <span class="font-code text-xs font-bold text-base-content">Avatars</span>
          </div>
          <div @click="selectCosmeticSubtype('BANNER')" class="border border-base-300 bg-base-200/50 p-6 flex flex-col items-center justify-center cursor-pointer hover:border-primary transition-all">
            <span class="text-3xl mb-2">📁</span>
            <span class="font-code text-xs font-bold text-base-content">Bannières</span>
          </div>
        </div>
        <div v-else-if="explorerStep === 'grid'">
          <div v-if="loadingIcons" class="flex justify-center py-12"><span class="loading loading-spinner text-primary"></span></div>
          <div v-else-if="!explorerIcons.length" class="text-center py-12 font-code text-xs text-base-content/40">Aucune icône dans ce dossier.</div>
          <div v-else class="grid grid-cols-3 sm:grid-cols-4 gap-3 max-h-80 overflow-y-auto p-1">
            <div
              v-for="ic in explorerIcons"
              :key="ic.id"
              @click="pickIcon(ic)"
              :class="['border p-2 flex flex-col items-center cursor-pointer transition-all bg-base-200/40', editForm.icon_id === ic.id ? 'border-primary bg-primary/10' : 'border-base-300 hover:border-base-content/40']"
            >
              <div class="w-12 h-12 flex items-center justify-center bg-base-100 border border-base-300 mb-1 overflow-hidden">
                <img :src="getAssetUrl(ic.filepath)" class="max-w-full max-h-full object-contain" @error="$event.target.style.display='none'" />
              </div>
              <span class="font-code text-[9px] text-base-content/60 truncate w-full text-center">{{ ic.filename }}</span>
            </div>
          </div>
        </div>
        <div class="mt-6 pt-4 border-t border-base-300 flex items-center justify-between">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 border border-base-300 bg-base-200 flex items-center justify-center overflow-hidden">
              <img v-if="editForm.icon_url" :src="getAssetUrl(editForm.icon_url)" class="max-w-full max-h-full object-contain" @error="$event.target.style.display='none'" />
            </div>
            <span class="font-code text-xs text-base-content/70">{{ editForm.icon_id ? `Icône #${editForm.icon_id} sélectionnée` : 'Icône actuelle conservée' }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
  <Teleport to="body">
    <div v-if="assignModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4" @click.self="assignModalOpen = false">
      <div class="w-full max-w-lg bg-base-200 border border-base-300 flex flex-col shadow-2xl p-6">
        <div class="flex items-center justify-between border-b border-base-300 pb-3 mb-4">
          <div>
            <p class="font-code text-[10px] uppercase text-base-content/40">Attribution manuelle</p>
            <h3 class="font-titre font-bold text-base text-base-content">{{ targetCosmetic?.name }}</h3>
          </div>
          <button @click="assignModalOpen = false" class="font-code text-xs text-error hover:text-error/70">Fermer</button>
        </div>
        <div class="flex flex-col gap-4">
          <div class="relative">
            <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40 block mb-1">Rechercher un utilisateur</label>
            <input
              v-model="assignQuery"
              @input="onAssignQueryInput"
              type="text"
              placeholder="Nom d'utilisateur..."
              class="w-full bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-xs text-base-content"
            />
            <div v-if="assignResults.length > 0" class="absolute z-10 top-full left-0 right-0 mt-1 bg-base-100 border border-base-300 shadow-lg max-h-48 overflow-y-auto">
              <div
                v-for="u in assignResults"
                :key="u.id"
                class="px-3 py-2 font-code text-xs text-base-content hover:bg-primary/10 transition-colors flex items-center justify-between gap-2 border-b border-base-300/40 last:border-0"
              >
                <div>
                  <span class="font-bold">{{ u.username }}</span>
                  <span class="text-[10px] text-base-content/40 ml-2">#{{ u.id }}</span>
                </div>
                <div class="flex gap-2">
                  <button
                    @click="toggleUserCosmetic(u, true)"
                    :disabled="assigning"
                    class="px-2.5 py-1 bg-primary text-base-100 hover:bg-primary/80 text-[10px] font-bold"
                  >
                    Attribuer
                  </button>
                  <button
                    @click="toggleUserCosmetic(u, false)"
                    :disabled="assigning"
                    class="px-2.5 py-1 bg-error/20 text-error hover:bg-error/30 text-[10px] font-bold"
                  >
                    Retirer
                  </button>
                </div>
              </div>
            </div>
            <div v-else-if="assignQuery.trim() && !assignSearching" class="mt-1 p-2 bg-base-100 border border-base-300 text-center font-code text-xs text-base-content/40">
              Aucun utilisateur trouvé.
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>