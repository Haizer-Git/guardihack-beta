<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import { showToast } from './useAdminToast.js'

const activeTab = ref('list')

// ─── HELPERS UI ───────────────────────────────────────────────────────────────
// Doit rester synchronisé avec AUTHORIZED_BADGE_TYPES dans badge_service.py
const TYPE_MAP = {
  CHALLENGE:    'bg-info/15 text-info border border-info/30',
  ACHIEVEMENT:  'bg-primary/15 text-primary border border-primary/30',
  SPECIAL:      'bg-secondary/15 text-secondary border border-secondary/30',
  ADMIN:        'bg-warning/15 text-warning border border-warning/30',
}
const typeClass = t => TYPE_MAP[t] ?? 'bg-base-300 text-base-content/60 border border-base-300'

// Doit rester synchronisé avec AUTHORIZED_REQUIREMENTS dans badge_service.py
const REQUIREMENT_TYPES = [
  { value: 'CHALLENGE_ID',          label: 'Challenge précis' },
  { value: 'SOLVE_COUNT',           label: 'Nombre de challenges résolus' },
  { value: 'SCORE',                 label: 'Score total' },
  { value: 'CATEGORY_SOLVE_COUNT',  label: 'Résolutions dans une catégorie' },
  { value: 'CONNECTION_STREAK',     label: 'Série de connexions' },
  { value: 'CONNECTION_DATE',       label: 'Date de connexion' },
]

import { getAssetUrl } from '../../utils/assets'

// ════════════════════════════════════════════════════════
// BADGES
// ════════════════════════════════════════════════════════
const badges        = ref([])
const loadingBadges  = ref(false)
const expandedBadge  = ref(null)

async function fetchBadges() {
  loadingBadges.value = true
  try {
    const res = await axios.get('/api/admin/badge/list')
    badges.value = res.data?.badges ?? res.data?.data ?? []
  } catch {
    showToast('Impossible de charger les badges', 'error')
  } finally {
    loadingBadges.value = false
  }
}

function toggleBadge(id) {
  expandedBadge.value = expandedBadge.value === id ? null : id
}

async function deleteBadge(id, name) {
  if (!confirm(`Supprimer le badge "${name}" ? Action irréversible.`)) return
  try {
    await axios.post(`/api/admin/badge/${id}/delete`)
    showToast(`Badge "${name}" supprimé`)
    if (expandedBadge.value === id) expandedBadge.value = null
    await fetchBadges()
  } catch (e) {
    showToast(e.response?.data?.message ?? 'Erreur suppression', 'error')
  }
}

// ── Création ──────────────────────────────────────────────────────────────────
const createDefaults = { type: 'SPECIAL', name: '', description: '', requirement_type: '', requirement_value: 1, requirement_text: '' }
const createForm = reactive({ ...createDefaults })
const creating   = ref(false)
const createIconFile  = ref(null)
const createFileInput = ref(null)

function onCreateFileChange(e) {
  createIconFile.value = e.target.files[0] ?? null
}

async function submitCreate() {
  if (!createForm.name || !createForm.description || !createForm.requirement_type || !createForm.requirement_text || !createForm.requirement_value || createForm.requirement_value < 1) {
    showToast('Tous les champs marqués * sont requis', 'error'); return
  }
  if (!createIconFile.value) {
    showToast('Une icône est requise', 'error'); return
  }
  creating.value = true
  try {
    // 1) Création du badge en JSON (le backend attend request.get_json(), pas de multipart ici)
    await axios.post('/api/admin/badge/create', {
      type: createForm.type,
      name: createForm.name,
      description: createForm.description,
      requirement_type: createForm.requirement_type,
      requirement_value: createForm.requirement_value,
      requirement_text: createForm.requirement_text
    })

    await fetchBadges()
    const created = badges.value.find(b => b.name === createForm.name)
    if (!created) {
      showToast('Badge créé mais introuvable pour l\'upload de l\'icône', 'error')
      return
    }
    const createdId = created.id

    try {
      const iconData = new FormData()
      iconData.append('file', createIconFile.value)
      await axios.put(`/api/admin/badge/${createdId}/icon`, iconData, { headers: { 'Content-Type': 'multipart/form-data' } })
    } catch (iconError) {
      await axios.post(`/api/admin/badge/${createdId}/delete`)
      await fetchBadges()
      showToast(iconError.response?.data?.message ?? 'Image refusée (nom de fichier déjà utilisé ?) — badge annulé, réessaie avec une autre image.', 'error')
      return
    }

    await fetchBadges()

    showToast(`Badge "${createForm.name}" créé !`)
    Object.assign(createForm, { ...createDefaults })
    createIconFile.value = null
    if (createFileInput.value) createFileInput.value.value = ''
    activeTab.value = 'list'
  } catch (e) {
    showToast(e.response?.data?.message ?? 'Erreur création', 'error')
  } finally {
    creating.value = false
  }
}

// ── Modification ───────────────────────────────────────────────────────────────
const editTarget = ref(null)
const editForm   = reactive({ type: '', name: '', description: '', icon_url: '', requirement_type: '', requirement_value: 0, requirement_text: '' })
const editing    = ref(false)
const editIconFile  = ref(null)
const editFileInput = ref(null)

function onEditFileChange(e) {
  editIconFile.value = e.target.files[0] ?? null
}

function openEdit(b) {
  editTarget.value    = b.id
  activeTab.value     = 'edit'
  editIconFile.value  = null
  if (editFileInput.value) editFileInput.value.value = ''
  Object.assign(editForm, {
    type:              b.type              ?? 'SPECIAL',
    name:              b.name              ?? '',
    description:       b.description       ?? '',
    icon_url:          b.icon_url          ?? '',
    requirement_type:  b.requirement_type  ?? '',
    requirement_value: b.requirement_value ?? 0,
    requirement_text:  b.requirement_text  ?? '',
  })
}

async function submitEdit() {
  if (!editForm.name || !editForm.description || !editForm.requirement_type || !editForm.requirement_text || !editForm.requirement_value || editForm.requirement_value < 1) {
    showToast('Tous les champs marqués * sont requis', 'error'); return
  }
  editing.value = true
  try {
    // La route /modify attend du JSON (request.get_json() côté backend) avec les clés
    // new_name / new_description / new_type / new_requirement_type / new_requirement_value / new_requirement_text
    await axios.post(`/api/admin/badge/${editTarget.value}/modify`, {
      new_name: editForm.name,
      new_description: editForm.description,
      new_type: editForm.type,
      new_requirement_type: editForm.requirement_type,
      new_requirement_value: editForm.requirement_value,
      new_requirement_text: editForm.requirement_text
    })

    // L'icône a sa propre route dédiée (multipart), distincte de /modify
    if (editIconFile.value) {
      const iconData = new FormData()
      iconData.append('file', editIconFile.value)
      await axios.put(`/api/admin/badge/${editTarget.value}/icon`, iconData, { headers: { 'Content-Type': 'multipart/form-data' } })
    }

    showToast('Badge modifié !')
    activeTab.value  = 'list'
    editTarget.value = null
    await fetchBadges()
  } catch (e) {
    showToast(e.response?.data?.message ?? 'Erreur modification', 'error')
  } finally {
    editing.value = false
  }
}

// ── Attribution manuelle ────────────────────────────────────────────────────────
// Recherche par nom d'utilisateur (autocomplete) au lieu d'un ID brut.
// Utilise la route existante /api/admin/user/list?search=... (filtre "contient",
// donc taper "Pa" remonte aussi bien "Pauline" que "Sparta" — c'est voulu, ça
// couvre plus large que le simple "commence par").
const assignQuery     = ref('')
const assignResults   = ref([])
const assignSelected  = ref(null) // { id, username }
const assignSearching = ref(false)
const assigning       = ref(false)
let assignDebounceTimer = null

function onAssignQueryInput() {
  assignSelected.value = null
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

function selectAssignUser(u) {
  assignSelected.value = u
  assignQuery.value = u.username
  assignResults.value = []
}

async function assignToUser(badgeId, badgeName) {
  if (!assignSelected.value) { showToast('Sélectionne un utilisateur dans la liste', 'error'); return }
  assigning.value = true
  try {
    await axios.post(`/api/admin/badge/${badgeId}/assign`, { user_id: assignSelected.value.id })
    showToast(`Badge "${badgeName}" attribué à ${assignSelected.value.username}`)
    assignQuery.value = ''
    assignSelected.value = null
    assignResults.value = []
  } catch (e) {
    showToast(e.response?.data?.message ?? 'Erreur attribution', 'error')
  } finally {
    assigning.value = false
  }
}

onMounted(() => { fetchBadges() })
</script>

<template>
  <!-- Titre -->
  <div class="flex items-end justify-between mb-6">
    <div>
      <p class="font-code text-[10px] tracking-[0.18em] uppercase text-base-content/40 mb-1">Admin › Badges</p>
      <h1 class="font-titre font-bold text-2xl text-base-content leading-none">Badges</h1>
    </div>
    <span class="font-code text-xs text-base-content/30 border border-base-300 px-2 py-1">{{ badges.length }} badges</span>
  </div>

  <!-- Onglets -->
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

  <!-- ── TAB : LISTE ── -->
  <div v-if="activeTab === 'list'">
    <div v-if="loadingBadges" class="flex justify-center py-20">
      <span class="loading loading-spinner loading-md text-primary"></span>
    </div>
    <div v-else-if="!badges.length" class="flex flex-col items-center justify-center py-20 gap-3">
      <span class="font-code text-sm text-base-content/30">Aucun badge.</span>
      <button @click="activeTab = 'create'" class="font-code text-xs text-primary underline underline-offset-2 hover:no-underline">Créer le premier →</button>
    </div>
    <div v-else class="flex flex-col gap-1.5">
      <div v-for="b in badges" :key="b.id" class="border border-base-300 bg-base-200/50 overflow-hidden">

        <!-- En-tête -->
        <div class="flex items-center gap-3 px-4 py-3 cursor-pointer select-none hover:bg-base-300/40 transition-colors duration-150" @click="toggleBadge(b.id)">
          <div class="w-8 h-8 shrink-0 bg-base-100 border border-base-300 overflow-hidden flex items-center justify-center">
            <img v-if="b.icon_url" :src="getAssetUrl(b.icon_url)" class="w-full h-full object-contain" @error="$event.target.style.display='none'" />
            <span v-else class="text-xs opacity-20">🏅</span>
          </div>
          <span :class="['font-code text-[10px] px-2 py-0.5 leading-none', typeClass(b.type)]">{{ b.type }}</span>
          <span class="font-titre font-semibold text-base-content text-sm flex-1 truncate">{{ b.name }}</span>
          <span class="font-code text-[11px] text-base-content/35 shrink-0 hidden sm:block">{{ b.requirement_text || '—' }}</span>
          <button class="font-code text-xs text-info hover:text-info/70 transition-colors px-1 shrink-0" @click.stop="openEdit(b)" title="Modifier">✏️</button>
          <button class="font-code text-xs text-error hover:text-error/70 transition-colors px-1 shrink-0" @click.stop="deleteBadge(b.id, b.name)" title="Supprimer">🗑️</button>
          <svg :class="['w-3.5 h-3.5 text-base-content/30 transition-transform duration-300 shrink-0', expandedBadge === b.id ? 'rotate-180' : '']" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
        </div>

        <!-- Accordéon -->
        <transition
          enter-active-class="transition-[max-height,opacity] duration-350 ease-out overflow-hidden"
          enter-from-class="max-h-0 opacity-0"
          enter-to-class="max-h-[500px] opacity-100"
          leave-active-class="transition-[max-height,opacity] duration-250 ease-in overflow-hidden"
          leave-from-class="max-h-[500px] opacity-100"
          leave-to-class="max-h-0 opacity-0"
        >
          <div v-if="expandedBadge === b.id" class="border-t border-base-300 bg-base-100/20 p-5 grid grid-cols-1 lg:grid-cols-2 gap-6">

            <!-- Infos -->
            <div>
              <p class="font-code text-[10px] tracking-widest uppercase text-primary/70 mb-3">Informations</p>
              <dl class="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1.5 text-xs font-code">
                <dt class="text-base-content/40">ID</dt>
                <dd class="text-base-content">#{{ b.id }}</dd>
                <dt class="text-base-content/40">Type</dt>
                <dd><span :class="['px-1.5 py-0.5 text-[10px]', typeClass(b.type)]">{{ b.type }}</span></dd>
                <dt class="text-base-content/40">Condition</dt>
                <dd class="text-base-content">{{ b.requirement_type || '—' }}</dd>
                <dt class="text-base-content/40">Texte condition</dt>
                <dd class="text-base-content">{{ b.requirement_text || '—' }}</dd>
                <dt class="text-base-content/40">Icône</dt>
                <dd class="text-base-content break-all">{{ b.icon_url || '—' }}</dd>
              </dl>
              <div class="mt-4">
                <p class="font-code text-[10px] tracking-widest uppercase text-base-content/30 mb-2">Description</p>
                <p class="text-xs text-base-content/70 bg-base-200/60 border border-base-300 px-3 py-2.5 leading-relaxed">{{ b.description || 'Aucune description.' }}</p>
              </div>
            </div>

            <!-- Attribution manuelle -->
            <div>
              <p class="font-code text-[10px] tracking-widest uppercase text-primary/70 mb-3">Attribuer manuellement</p>
              <div class="flex flex-col gap-2">
                <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Nom d'utilisateur</label>
                <div class="flex gap-2">
                  <div class="relative flex-1">
                    <input
                      v-model="assignQuery"
                      @input="onAssignQueryInput"
                      @focus="onAssignQueryInput"
                      type="text"
                      autocomplete="off"
                      placeholder="Pa..."
                      class="w-full bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content placeholder:text-base-content/20 transition-colors"
                    />
                    <div v-if="assignQuery && !assignSelected && (assignSearching || assignResults.length)" class="absolute z-10 top-full left-0 right-0 mt-1 bg-base-100 border border-base-300 shadow-lg max-h-48 overflow-y-auto">
                      <div v-if="assignSearching" class="px-3 py-2 font-code text-xs text-base-content/40">Recherche...</div>
                      <template v-else-if="assignResults.length">
                        <button
                          v-for="u in assignResults"
                          :key="u.id"
                          @click="selectAssignUser(u)"
                          type="button"
                          class="w-full text-left px-3 py-2 font-code text-xs text-base-content hover:bg-primary/10 transition-colors flex items-center justify-between gap-2"
                        >
                          <span class="truncate">{{ u.username }}</span>
                          <span class="text-base-content/30 shrink-0">#{{ u.id }}</span>
                        </button>
                      </template>
                      <div v-else class="px-3 py-2 font-code text-xs text-base-content/30">Aucun résultat.</div>
                    </div>
                  </div>
                  <button @click="assignToUser(b.id, b.name)" :disabled="assigning || !assignSelected" class="px-4 py-2 font-code text-xs tracking-wide bg-primary text-base-100 hover:bg-primary/80 transition-colors disabled:opacity-30 shrink-0">
                    <span v-if="assigning" class="loading loading-xs"></span>
                    <span v-else>Attribuer</span>
                  </button>
                </div>
                <p class="font-code text-[10px] text-base-content/25 mt-1">Tape un nom d'utilisateur, choisis-le dans la liste, puis clique sur "Attribuer".</p>
              </div>
            </div>

          </div>
        </transition>
      </div>
    </div>
  </div>

  <!-- ── TAB : CRÉER ── -->
  <div v-if="activeTab === 'create'" class="max-w-2xl">
    <div class="border border-base-300 bg-base-200/40 p-6">
      <p class="font-code text-[10px] tracking-widest uppercase text-base-content/35 mb-1">Nouveau badge</p>
      <h2 class="font-titre font-bold text-lg text-base-content mb-6">Créer un badge</h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">

        <div class="sm:col-span-2 flex flex-col gap-1">
          <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Nom *</label>
          <input v-model="createForm.name" type="text" placeholder="Premier sang" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content placeholder:text-base-content/20 transition-colors" />
        </div>

        <div class="flex flex-col gap-1">
          <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Type</label>
          <select v-model="createForm.type" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors">
            <option value="CHALLENGE">CHALLENGE</option>
            <option value="ACHIEVEMENT">ACHIEVEMENT</option>
            <option value="SPECIAL">SPECIAL</option>
            <option value="ADMIN">ADMIN</option>
          </select>
        </div>

        <div class="flex flex-col gap-1">
          <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Icône *</label>
          <input ref="createFileInput" type="file" accept="image/*" @change="onCreateFileChange" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-xs text-base-content file:mr-3 file:px-2 file:py-1 file:border-0 file:bg-primary/15 file:text-primary file:font-code file:text-xs transition-colors" />
        </div>

        <div class="flex flex-col gap-1">
          <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Type de condition *</label>
          <select v-model="createForm.requirement_type" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors">
            <option value="" disabled>Choisir un type...</option>
            <option value="CHALLENGE_ID">CHALLENGE_ID — Challenge spécifique</option>
            <option value="SOLVE_COUNT">SOLVE_COUNT — Nombre de challenges résolus</option>
            <option value="SCORE">SCORE — Score total atteint</option>
            <option value="CATEGORY_SOLVE_COUNT">CATEGORY_SOLVE_COUNT — Challenges résolus dans une catégorie</option>
          </select>
        </div>

        <div class="flex flex-col gap-1">
          <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Valeur de la condition</label>
          <input v-model.number="createForm.requirement_value" type="number" min="1" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors" />
          <p class="font-code text-[10px] text-base-content/25 mt-1">
            <template v-if="createForm.requirement_type === 'CHALLENGE_ID'">ID du challenge requis.</template>
            <template v-else-if="createForm.requirement_type === 'SOLVE_COUNT'">Nombre de challenges à résoudre.</template>
            <template v-else-if="createForm.requirement_type === 'SCORE'">Score total à atteindre.</template>
            <template v-else-if="createForm.requirement_type === 'CATEGORY_SOLVE_COUNT'">Nombre de challenges dans la catégorie.</template>
          </p>
        </div>

        <div class="sm:col-span-2 flex flex-col gap-1">
          <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Texte de la condition *</label>
          <input v-model="createForm.requirement_text" type="text" placeholder="Ex: Être le premier à valider un challenge" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content placeholder:text-base-content/20 transition-colors" />
        </div>

        <div class="sm:col-span-2 flex flex-col gap-1">
          <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Description *</label>
          <textarea v-model="createForm.description" rows="3" placeholder="Description du badge..." class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content placeholder:text-base-content/20 transition-colors resize-none"></textarea>
        </div>

      </div>
      <button @click="submitCreate" :disabled="creating" class="mt-5 w-full py-2.5 font-code text-xs tracking-wide bg-primary text-base-100 hover:bg-primary/80 transition-colors disabled:opacity-30">
        <span v-if="creating" class="loading loading-xs"></span>
        <span v-else>Créer le badge</span>
      </button>
    </div>
  </div>

  <!-- ── TAB : MODIFIER ── -->
  <div v-if="activeTab === 'edit' && editTarget" class="max-w-2xl">
    <div class="border border-base-300 bg-base-200/40 p-6">
      <p class="font-code text-[10px] tracking-widest uppercase text-base-content/35 mb-1">Badge #{{ editTarget }}</p>
      <h2 class="font-titre font-bold text-lg text-base-content mb-6">Modifier le badge</h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">

        <div class="sm:col-span-2 flex flex-col gap-1">
          <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Nom *</label>
          <input v-model="editForm.name" type="text" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors" />
        </div>

        <div class="flex flex-col gap-1">
          <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Type</label>
          <select v-model="editForm.type" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors">
            <option value="CHALLENGE">CHALLENGE</option>
            <option value="ACHIEVEMENT">ACHIEVEMENT</option>
            <option value="SPECIAL">SPECIAL</option>
            <option value="ADMIN">ADMIN</option>
          </select>
        </div>

        <div class="sm:col-span-2 flex flex-col gap-1">
          <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Icône actuelle</label>
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 shrink-0 bg-base-100 border border-base-300 overflow-hidden flex items-center justify-center">
              <img v-if="editForm.icon_url" :src="getAssetUrl(editForm.icon_url)" class="w-full h-full object-contain" @error="$event.target.style.display='none'" />
              <span v-else class="text-xs opacity-20">🏅</span>
            </div>
            <input ref="editFileInput" type="file" accept="image/*" @change="onEditFileChange" class="flex-1 bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-xs text-base-content file:mr-3 file:px-2 file:py-1 file:border-0 file:bg-primary/15 file:text-primary file:font-code file:text-xs transition-colors" />
          </div>
          <p class="font-code text-[10px] text-base-content/25 mt-1">Laisse vide pour conserver l'icône actuelle.</p>
        </div>

        <div class="flex flex-col gap-1">
          <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Type de condition *</label>
          <select v-model="editForm.requirement_type" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors">
            <option value="" disabled>Choisir un type...</option>
            <option value="CHALLENGE_ID">CHALLENGE_ID — Challenge spécifique</option>
            <option value="SOLVE_COUNT">SOLVE_COUNT — Nombre de challenges résolus</option>
            <option value="SCORE">SCORE — Score total atteint</option>
            <option value="CATEGORY_SOLVE_COUNT">CATEGORY_SOLVE_COUNT — Challenges résolus dans une catégorie</option>
          </select>
        </div>

        <div class="flex flex-col gap-1">
          <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Valeur de la condition</label>
          <input v-model.number="editForm.requirement_value" type="number" min="1" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors" />
          <p class="font-code text-[10px] text-base-content/25 mt-1">
            <template v-if="editForm.requirement_type === 'CHALLENGE_ID'">ID du challenge requis.</template>
            <template v-else-if="editForm.requirement_type === 'SOLVE_COUNT'">Nombre de challenges à résoudre.</template>
            <template v-else-if="editForm.requirement_type === 'SCORE'">Score total à atteindre.</template>
            <template v-else-if="editForm.requirement_type === 'CATEGORY_SOLVE_COUNT'">Nombre de challenges dans la catégorie.</template>
          </p>
        </div>

        <div class="sm:col-span-2 flex flex-col gap-1">
          <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Texte de la condition *</label>
          <input v-model="editForm.requirement_text" type="text" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors" />
        </div>

        <div class="sm:col-span-2 flex flex-col gap-1">
          <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Description *</label>
          <textarea v-model="editForm.description" rows="3" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors resize-none"></textarea>
        </div>

      </div>
      <div class="flex gap-3 mt-5">
        <button @click="submitEdit" :disabled="editing" class="flex-1 py-2.5 font-code text-xs tracking-wide bg-primary text-base-100 hover:bg-primary/80 transition-colors disabled:opacity-30">
          <span v-if="editing" class="loading loading-xs"></span>
          <span v-else>Sauvegarder</span>
        </button>
        <button @click="activeTab = 'list'; editTarget = null" class="px-5 py-2.5 font-code text-xs tracking-wide border border-base-300 text-base-content/60 hover:text-base-content hover:border-base-content/30 transition-colors">Annuler</button>
      </div>
    </div>
  </div>
</template>