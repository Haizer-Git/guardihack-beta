<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import { showToast } from './useAdminToast.js'
import { getAssetUrl } from '../../utils/assets'

const props = defineProps({
  initialTab: {
    type: String,
    default: 'user',
  },
})
const users          = ref([])
const totalUsers     = ref(0)
const loadingUsers   = ref(false)
const search         = ref('')
const filterRole     = ref('')
const filterCity     = ref('')
const filterConnected = ref(true)
const filterStatus    = ref('')
const sortKey        = ref('id')
const sortDir        = ref('desc')
const currentPage    = ref(1)
const itemsPerPage   = 25
const tabGroup = computed(() => TAB_GROUPS[props.initialTab] ?? TAB_GROUPS.user)
const activeTab = ref('users_list')
const filteredUsers = computed(() => users.value)
const availableCities = computed(() => {
  const set = new Set(users.value.map(u => u.affiliation).filter(Boolean))
  return [...set].sort()
})
const TAB_GROUPS = {
  user: [
    { id: 'users_list', label: 'Liste' },
  ],
  preset: [
    { id: 'users_presets_list', label: 'Liste' },
    { id: 'users_presets_create', label: 'Créer' },
  ],
  token: [
    { id: 'users_tokens_list', label: 'Liste' },
    { id: 'users_tokens_create', label: 'Créer' },
    { id: 'users_tokens_auto', label: 'Automatisation' },
  ],
}
const USER_TYPE_MAP = {
  ADMIN: 'bg-error/15 text-error border-error/30',
  PEDAGOGIE: 'bg-warning/15 text-warning border-warning/30',
  USER: 'bg-info/15 text-info border border-info/30',
  INVITE: 'bg-secondary/15 text-secondary border border-secondary/30',
  EXTERNE: 'bg-base-300 text-base-content/70 border-base-300'
}
const userTypeClass = (type) => {
  const upper = (type || '').toUpperCase()
  return USER_TYPE_MAP[upper] ?? 'bg-base-300 text-base-content/70 border-base-300'
}
const breadcrumbSubCategory = computed(() => {
  if (activeTab.value.startsWith('users_') && !activeTab.value.startsWith('users_presets') && !activeTab.value.startsWith('users_tokens')) return 'Utilisateurs'
  if (activeTab.value.startsWith('users_presets')) return 'Presets'
  if (activeTab.value.startsWith('users_tokens')) return 'Tokens'
  return ''
})
const totalPages = computed(() => {
  return Math.ceil(totalUsers.value / itemsPerPage) || 1
})
const selectedUser     = ref(null)
const loadingUserInfo  = ref(false)
const detailedUserInfo = ref(null)
const statusModalOpen  = ref(false)
const targetUserForStatus = ref(null)
const statusForm       = reactive({ new_status: 'ACTIVE', reason: '', ended_at: '' })
const updatingStatus   = ref(false)
const userBadgesModalOpen = ref(false)
const userCosmeticsModalOpen = ref(false)
const userStatusHistoryModalOpen = ref(false)
const userSubmissionsModalOpen = ref(false)
const exportingUserBadges = ref(false)
const exportingUserCosmetics = ref(false)
const exportingUserStatusHistory = ref(false)
const exportingUserSubmissions = ref(false)
const userAchievementsModalOpen = ref(false)
const exportingUserAchievements = ref(false)
const autoTokenPreset = ref('')
const selectedCsvFile = ref(null)
const autoSendEmail = ref(true)
const uploadingAutoTokens = ref(false)
const allPresets          = ref([])
const allTokens           = ref([])
const loadingPresets      = ref(false)
const newPresetForm       = reactive({ name: '', type: 'USER', affiliation: 'PARIS'})
const creatingPreset      = ref(false)
const expandedPreset      = ref(null)
const expandedTokenPreset = ref(null)
const presetUsersPanelOpen = ref(false)
const selectedPresetObj    = ref(null)
const presetUsersList      = ref([])
const loadingPresetUsers   = ref(false)
const exportingPresetUsers = ref(false)
const presetTokensModalOpen = ref(false)
const selectedPresetForTokens = ref(null)
const modalTokensList        = ref([])
const loadingModalTokens     = ref(false)
const exportingModalTokens   = ref(false)
const tokensGroupedByPreset = computed(() => {
  const map = {}
  allTokens.value.forEach(token => {
    const pId = token.preset_id
    if (!map[pId]) {
      const presetInfo = allPresets.value.find(p => p.id === pId) || { name: `Preset #${pId}` }
      map[pId] = { presetId: pId, presetName: presetInfo.name, tokens: [] }
    }
    map[pId].tokens.push(token)
  })
  return Object.values(map)
})
const newTokenPreset      = ref('')
const newTokenMaxUses     = ref(1)
const newTokenExpiresAt   = ref('')
const creatingToken       = ref(false)
const enableEmail       = ref(false)
const enableName        = ref(false)
const enableClasse     = ref(false)
const enableExpiration  = ref(false)
const newTokenMail      = ref('')
const newTokenFirstName = ref('')
const newTokenLastName  = ref('')
const newTokenClasse    = ref('')
const newTokenNiveau    = ref('')
const selectedPresetData = computed(() => {
  if (!newTokenPreset.value) return null
  return allPresets.value.find(p => p.id === Number(newTokenPreset.value)) || null
})

function defaultTabForGroup(groupKey) {
  if (groupKey === 'preset') return 'users_presets_list'
  if (groupKey === 'token') return 'users_tokens_list'
  return 'users_list'
}
function onTabChange(tab) {
  activeTab.value = tab
  if (tab === 'users_list') fetchUsers()
  if (tab.startsWith('users_presets_')) loadPresetsAndTokens()
  if (tab.startsWith('users_tokens_')) loadPresetsAndTokens()
}
async function fetchUsers() {
  loadingUsers.value = true
  try {
    const offset = (currentPage.value - 1) * itemsPerPage
    const params = {
      offset: offset,
      limit: itemsPerPage,
      sort_by: sortKey.value,
      sort_dir: sortDir.value
    }
    if (search.value.trim()) params.search = search.value.trim()
    if (filterRole.value) params.role = filterRole.value
    if (filterCity.value) params.affiliation = filterCity.value
    if (filterStatus.value) params.status = filterStatus.value
    if (filterConnected.value) params.connected = true
    const res = await axios.get('/api/admin/user/list', { params })
    totalUsers.value = res.data?.total_users ?? 0
    users.value = res.data?.users ?? []
  } catch {
    showToast('Impossible de charger les utilisateurs', 'error')
  } finally {
    loadingUsers.value = false
  }
}
function setSort(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = 'asc'
  }
}
function clearFilters() {
  search.value          = ''
  filterRole.value      = ''
  filterCity.value      = ''
  filterStatus.value    = ''
  filterConnected.value = false
  currentPage.value     = 1
}
function nextPage() {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}
function prevPage() {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}
function goToPage(page) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}
async function openUser(user) {
  if (selectedUser.value?.id === user.id) {
    closePanel()
    return
  }
  selectedUser.value = user
  detailedUserInfo.value = null
  loadingUserInfo.value = true
  try {
    const res = await axios.get(`/api/admin/user/${user.id}/info`)
    detailedUserInfo.value = res.data?.user ?? null
  } catch {
    showToast('Erreur lors du chargement des informations détaillées', 'error')
  } finally {
    loadingUserInfo.value = false
  }
}
function closePanel() {
  selectedUser.value = null
  detailedUserInfo.value = null
}
function openStatusModal(user) {
  targetUserForStatus.value = user
  statusForm.new_status = user.status ?? 'ACTIVE'
  statusForm.reason = ''
  statusForm.ended_at = ''
  statusModalOpen.value = true
}
async function submitStatusUpdate() {
  if (!targetUserForStatus.value) return
  if (['BANNED', 'LOCKED'].includes(statusForm.new_status) && !statusForm.reason.trim()) {
    showToast('Une raison est requise pour le bannissement ou le verrouillage', 'error')
    return
  }
  updatingStatus.value = true
  try {
    const payload = {
      new_status: statusForm.new_status,
      reason: statusForm.reason.trim() || null,
      ended_at: statusForm.ended_at ? statusForm.ended_at.replace('T', ' ') + ':00' : null
    }
    const res = await axios.post(`/api/admin/user/${targetUserForStatus.value.id}/status/update`, payload)
    showToast(res.data?.message || 'Statut mis à jour avec succès')
    statusModalOpen.value = false
    await fetchUsers()
    if (selectedUser.value?.id === targetUserForStatus.value.id) {
      openUser(targetUserForStatus.value)
    }
  } catch (e) {
    showToast(e.response?.data?.message ?? 'Erreur lors de la mise à jour du statut', 'error')
  } finally {
    updatingStatus.value = false
  }
}
function exportToCsv(filename, headers, rowsData) {
  if (!rowsData.length) return
  const escape = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`
  const rows = rowsData.map(r => r.map(escape).join(','))
  const csv = [headers.join(','), ...rows].join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  
  const now = new Date()
  const pad = (n) => String(n).padStart(2, '0')
  const dateStr = `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}_${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`
  
  const a = document.createElement('a')
  a.href = url
  a.download = `${filename}_${dateStr}.csv`
  a.click()
  URL.revokeObjectURL(url)
}
function downloadUserBadgesCsv() {
  exportingUserBadges.value = true
  try {
    const badges = detailedUserInfo.value?.inventory?.badges ?? []
    const headers = ['Nom du badge']
    const rows = badges.map(b => [b])
    exportToCsv(`utilisateur_${selectedUser.value?.username}_badges`, headers, rows)
  } finally {
    exportingUserBadges.value = false
  }
}
function downloadUserCosmeticsCsv() {
  exportingUserCosmetics.value = true
  try {
    const cosmetics = detailedUserInfo.value?.inventory?.cosmetics ?? []
    const headers = ['Nom du cosmétique']
    const rows = cosmetics.map(c => [c])
    exportToCsv(`utilisateur_${selectedUser.value?.username}_cosmetiques`, headers, rows)
  } finally {
    exportingUserCosmetics.value = false
  }
}
function downloadUserStatusHistoryCsv() {
  exportingUserStatusHistory.value = true
  try {
    const history = detailedUserInfo.value?.status_history ?? []
    const headers = ['Statut', 'Raison', 'Date de changement', 'Date de fin']
    const rows = history.map(h => [h.status, h.reason ?? '—', h.created_at ?? h.changed_at, h.ended_at ?? 'En cours'])
    exportToCsv(`utilisateur_${selectedUser.value?.username}_historique_statuts`, headers, rows)
  } finally {
    exportingUserStatusHistory.value = false
  }
}
function downloadUserSubmissionsCsv() {
  exportingUserSubmissions.value = true
  try {
    const submissions = detailedUserInfo.value?.challenges_history ?? []
    const headers = ['Nom du challenge', 'Résultat', 'Date de soumission']
    const rows = submissions.map(s => [s.challenge_name, s.is_correct ? 'Correct' : 'Incorrect', s.submitted_at])
    exportToCsv(`utilisateur_${selectedUser.value?.username}_soumissions`, headers, rows)
  } finally {
    exportingUserSubmissions.value = false
  }
}
function downloadUserAchievementsCsv() {
  exportingUserAchievements.value = true
  try {
    const achievements = detailedUserInfo.value?.achievements ?? []
    const headers = ['Nom du succès']
    const rows = achievements.map(a => [a])
    exportToCsv(`utilisateur_${selectedUser.value?.username}_succes`, headers, rows)
  } finally {
    exportingUserAchievements.value = false
  }
}
function handleCsvFileSelect(event) {
  const file = event.target.files[0]
  selectedCsvFile.value = file || null
}
async function submitAutoCreateTokens() {
  if (!autoTokenPreset.value || !selectedCsvFile.value) {
    showToast('Veuillez sélectionner un preset et un fichier CSV', 'error')
    return
  }
  uploadingAutoTokens.value = true
  const formData = new FormData()
  formData.append('file', selectedCsvFile.value)
  try {
    const res = await axios.post(`/api/admin/token/create/auto/${autoTokenPreset.value}/${autoSendEmail.value}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    const data = res.data?.message || {}
    showToast(`Succès : ${data.success || 'Tokens importés'}`)
    if (data.errors && data.errors.length > 0) {
      showToast(`${data.errors.length} erreur(s) détectée(s), voir console`, 'warning')
    }
    autoTokenPreset.value = ''
    selectedCsvFile.value = ''
    autoSendEmail.value = true
    allTokens.value = []
    await loadPresetsAndTokens()
    activeTab.value = 'users_tokens_list'
  } catch (e) {
    showToast(e.response?.data?.message ?? 'Erreur lors de l\'import automatisé', 'error')
  } finally {
    uploadingAutoTokens.value = false
  }
}
async function loadPresetsAndTokens() {
  if (allPresets.value.length && allTokens.value.length) return
  loadingPresets.value = true
  try {
    const [pr, tr] = await Promise.all([axios.get('/api/admin/preset/list'), axios.get('/api/admin/token/list')])
    allPresets.value = pr.data?.presets ?? pr.data?.data ?? []
    allTokens.value  = tr.data?.tokens  ?? tr.data?.data  ?? []
  } catch {} finally { loadingPresets.value = false }
}
function toggleTokenPreset(presetId) {
  expandedTokenPreset.value = expandedTokenPreset.value === presetId ? null : presetId
}
function togglePreset(id) {
  expandedPreset.value = expandedPreset.value === id ? null : id
}
async function fetchPresetUsers(preset) {
  selectedPresetObj.value = preset
  presetUsersPanelOpen.value = true
  loadingPresetUsers.value = true
  presetUsersList.value = []
  try {
    const res = await axios.get(`/api/admin/preset/${preset.id}/users`)
    presetUsersList.value = res.data?.users ?? []
  } catch {
    showToast('Impossible de charger les utilisateurs de ce preset', 'error')
  } finally {
    loadingPresetUsers.value = false
  }
}
async function downloadPresetUsersCsv() {
  if (!presetUsersList.value.length || !selectedPresetObj.value) return
  exportingPresetUsers.value = true
  try {
    const headers = ['ID', 'Nom', 'Prénom', 'Username', 'Email', 'Classe', 'Niveau', 'Affiliation']
    const escape = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`
    const rows = presetUsersList.value.map(u => [
      u.id, u.last_name, u.first_name, u.username, u.mail, u.classe, u.niveau, u.affiliation
    ].map(escape).join(','))
    const csv = [headers.join(','), ...rows].join('\n')
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const now = new Date()
    const pad = (n) => String(n).padStart(2, '0')
    const dateStr = `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}_${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`
    const safeName = (selectedPresetObj.value.name || 'preset').trim().replace(/\s+/g, '-').replace(/[^a-zA-Z0-9_-]/g, '')
    const a = document.createElement('a')
    a.href = url
    a.download = `${safeName}_utilisateurs_${dateStr}.csv`
    a.click()
    URL.revokeObjectURL(url)
  } catch {
    showToast("Impossible d'exporter les utilisateurs", 'error')
  } finally {
    exportingPresetUsers.value = false
  }
}
async function createPreset() {
  if (!newPresetForm.name.trim() || !newPresetForm.affiliation.trim()) {
    showToast('Le nom et l\'affiliation sont requis', 'error')
    return
  }
  creatingPreset.value = true
  try {
    await axios.post('/api/admin/preset/create', { 
      name: newPresetForm.name.trim(), 
      type: newPresetForm.type,
      affiliation: newPresetForm.affiliation
    })
    showToast('Preset créé !')
    Object.assign(newPresetForm, { name: '', type: 'USER', affiliation: 'PARIS' })
    allPresets.value = []
    await loadPresetsAndTokens()
    activeTab.value = 'users_presets_list'
  } catch (e) { 
    showToast(e.response?.data?.message ?? 'Erreur lors de la création', 'error') 
  } finally { 
    creatingPreset.value = false 
  }
}
async function deletePreset(presetId) {
  try {
    await axios.post(`/api/admin/preset/${presetId}/delete`)
    showToast('Preset supprimé')
    allPresets.value = []
    await loadPresetsAndTokens()
  } catch (e) { showToast(e.response?.data?.message ?? 'Erreur', 'error') }
}
function openPresetTokensModal(group) {
  selectedPresetForTokens.value = group
  modalTokensList.value = group.tokens
  presetTokensModalOpen.value = true
}
async function downloadModalTokensCsv() {
  if (!modalTokensList.value.length || !selectedPresetForTokens.value) return
  exportingModalTokens.value = true
  try {
    const headers = ['Token', 'Email', 'Prénom', 'Nom', 'Utilisations', 'Max Utilisations', 'Expiration', 'Actif']
    const escape = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`
    const rows = modalTokensList.value.map(t => [
      t.token, t.mail ?? '—', t.first_name ?? '—', t.last_name ?? '—', t.uses, t.max_uses ?? 'Illimité', t.expires_at ?? 'Jamais', t.is_active === 'ACTIVE' ? 'Oui' : 'Non'
    ].map(escape).join(','))
    const csv = [headers.join(','), ...rows].join('\n')
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const now = new Date()
    const pad = (n) => String(n).padStart(2, '0')
    const dateStr = `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}_${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`
    const safeName = (selectedPresetForTokens.value.presetName || 'tokens').trim().replace(/\s+/g, '-').replace(/[^a-zA-Z0-9_-]/g, '')
    const a = document.createElement('a')
    a.href = url
    a.download = `${safeName}_tokens_${dateStr}.csv`
    a.click()
    URL.revokeObjectURL(url)
  } catch {
    showToast("Impossible d'exporter les tokens", 'error')
  } finally {
    exportingModalTokens.value = false
  }
}
async function createToken() {
  if (!newTokenPreset.value) return
  creatingToken.value = true
  try {
    const payload = { preset_id: Number(newTokenPreset.value) }
    if (newTokenMaxUses.value) payload.max_uses = Number(newTokenMaxUses.value)
    if (enableEmail.value && newTokenMail.value.trim()) payload.mail = newTokenMail.value.trim()
    if (enableName.value) {
      if (newTokenFirstName.value.trim()) payload.first_name = newTokenFirstName.value.trim()
      if (newTokenLastName.value.trim()) payload.last_name = newTokenLastName.value.trim()
    }
    if (enableClasse.value) {
      if (newTokenClasse.value.trim()) payload.classe = newTokenClasse.value.trim()
      if (newTokenNiveau.value.trim()) payload.niveau = newTokenNiveau.value.trim()
    }
    if (enableExpiration.value && newTokenExpiresAt.value) payload.expires_at = newTokenExpiresAt.value
    await axios.post('/api/admin/token/create', payload)
    showToast('Token créé avec succès !')
    newTokenPreset.value = ''
    newTokenMaxUses.value = 1
    newTokenExpiresAt.value = ''
    enableEmail.value = false
    enableName.value = false
    enableClasse.value = false
    enableExpiration.value = false
    newTokenMail.value = ''
    newTokenFirstName.value = ''
    newTokenLastName.value = ''
    newTokenClasse.value = ''
    newTokenNiveau.value = ''
    allTokens.value = []
    await loadPresetsAndTokens()
    activeTab.value = 'users_tokens_list'
  } catch (e) { 
    showToast(e.response?.data?.message ?? 'Erreur lors de la création du token', 'error') 
  } finally { 
    creatingToken.value = false 
  }
}
async function deleteToken(tokenId) {
  try {
    await axios.post(`/api/admin/token/${tokenId}/delete`)
    showToast('Token supprimé')
    allTokens.value = []
    await loadPresetsAndTokens()
  } catch (e) { showToast(e.response?.data?.message ?? 'Erreur', 'error') }
}
async function notifyToken(tokenId) {
  try {
    await axios.post(`/api/admin/token/${tokenId}/notify`)
    showToast('Notification envoyée')
  } catch (e) {
    showToast(e.response?.data?.message ?? 'Erreur lors de l\'envoi de la notification', 'error')
  }
}

watch(
  [search, filterRole, filterCity, sortKey, sortDir, currentPage, filterStatus, filterConnected],
  () => {
    fetchUsers()
  }
)
watch([search, filterRole, filterCity, filterStatus, filterConnected], () => {
  currentPage.value = 1
})
watch(
  () => props.initialTab,
  async (groupKey) => {
    activeTab.value = defaultTabForGroup(groupKey)
    if (groupKey === 'user') {
      await fetchUsers()
    } else if (groupKey === 'preset') {
      await loadPresetsAndTokens()
    } else if (groupKey === 'token') {
      await loadPresetsAndTokens()
    }
  },
  { immediate: true }
)

onMounted(() => {
  fetchUsers()
  loadPresetsAndTokens()
})
</script>

<template>
  <div class="flex flex-col h-full">
    <div class="flex items-center justify-between mb-6">
      <div>
        <p class="font-code text-[10px] tracking-[0.18em] uppercase text-base-content/40 mb-1">Admin > Utilisateurs > {{ breadcrumbSubCategory }}</p>
        <h1 class="font-titre font-bold text-2xl text-base-content leading-none">Utilisateurs</h1>
      </div>
      <span v-if="activeTab === 'users_list'" class="font-code text-sm text-base-content/50 border border-secondary px-2 py-1">{{ totalUsers }} UTILISATEUR{{ totalUsers > 1 ? 'S' : '' }}</span>
    </div>
    <div class="flex gap-0 border-b border-primary mb-6">
      <button
        v-for="tab in tabGroup"
        :key="tab.id"
        @click="onTabChange(tab.id)"
        :class="[
          'px-5 py-2.5 font-text text-sm tracking-wide border border-primary transition-colors duration-150 -mb-px',
          activeTab === tab.id
            ? 'border-primary text-base-content'
            : 'border-transparent text-base-content/45 hover:text-base-content/75 hover:border-primary/20'
        ]"
      >{{ tab.label }}</button>
    </div>
    <div class="flex gap-6 flex-1 min-h-0">
      <div v-if="activeTab === 'users_list'" class="flex flex-col min-w-0 w-full">
        <div class="flex flex-col gap-3 mb-4">
          <div class="flex items-center gap-2 flex-wrap">
            <div class="relative flex-1 min-w-48">
              <span class="absolute left-3 top-1/2 -translate-y-1/2 font-code text-base-content/30 text-xs select-none">⌕</span>
              <input
                v-model="search"
                type="text"
                placeholder="Rechercher un utilisateur..."
                class="w-full bg-base-100 border border-base-300 focus:border-primary outline-none pl-7 pr-3 py-2 font-code text-xs text-base-content placeholder:text-base-content/25 transition-colors"
              />
            </div>
            <select
              v-model="filterRole"
              class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-xs text-base-content transition-colors"
            >
              <option value="">Tous les rôles</option>
              <option value="admin">Admin</option>
              <option value="user">User</option>
              <option value="pedagogie">Pédagogie</option>
              <option value="invite">Invité</option>
              <option value="externe">Externe</option>
            </select>
            <select
              v-model="filterCity"
              class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-xs text-base-content transition-colors"
            >
              <option value="">Toutes les villes</option>
              <option v-for="city in availableCities" :key="city" :value="city">{{ city }}</option>
            </select>
            <select
              v-model="filterStatus"
              class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-xs text-base-content transition-colors"
            >
              <option value="">Tous les statuts</option>
              <option value="ACTIVE">Actif</option>
              <option value="PENDING">En attente</option>
              <option value="LOCKED">Verrouillé</option>
              <option value="BANNED">Suspendu</option>
            </select>
            <label class="flex items-center gap-2 px-3 py-2 bg-base-100 border border-base-300 cursor-pointer select-none">
              <input v-model="filterConnected" type="checkbox" class="checkbox checkbox-xs checkbox-primary rounded-none" />
              <span class="font-code text-xs text-base-content">Connecté</span>
            </label>
          </div>
        </div>
        <div class="border border-base-300 overflow-hidden flex flex-col" style="max-height: calc(100vh - 220px);">
          <div class="flex-1 overflow-y-auto">
            <div class="grid grid-cols-[1.5fr_1.5fr_1.5fr_2.5fr_1fr_1fr_1.2fr_1.2fr_1fr_100px] bg-base-200 border-b border-base-300 sticky top-0 z-10 font-code text-[10px] uppercase tracking-widest text-base-content/40">
              <div class="px-3 py-2.5">ID / Pseudo</div>
              <div class="px-3 py-2.5">Prénom</div>
              <div class="px-3 py-2.5">Nom</div>
              <div class="px-3 py-2.5">Email</div>
              <div class="px-3 py-2.5">Niveau/Classe</div>
              <div class="px-3 py-2.5">Type</div>
              <div class="px-3 py-2.5">Statut</div>
              <div class="px-3 py-2.5">Connecté</div>
              <div class="px-3 py-2.5 text-right">Actions</div>
            </div>
            <div v-if="loadingUsers" class="flex justify-center py-16">
              <span class="loading loading-spinner loading-md text-primary"></span>
            </div>
            <div v-else-if="!filteredUsers.length" class="flex flex-col items-center justify-center py-16 gap-2">
              <span class="font-code text-4xl opacity-10">👤</span>
              <span class="font-code text-xs text-base-content/25">Aucun utilisateur trouvé</span>
            </div>
            <div v-else>
              <template v-for="user in filteredUsers" :key="user.id">
                <div
                  @click="openUser(user)"
                  :class="[
                    'grid grid-cols-[1.5fr_1.5fr_1.5fr_2.5fr_1fr_1fr_1.2fr_1.2fr_1fr_100px] items-center border-b border-base-300/50 cursor-pointer transition-colors duration-100 font-code text-xs',
                    selectedUser?.id === user.id
                      ? 'bg-primary/8 border-l-2 border-l-primary'
                      : 'hover:bg-base-300/30'
                  ]"
                >
                  <div class="px-3 py-3 flex items-center gap-2 min-w-0">
                    <span class="text-base-content/30 shrink-0">#{{ user.id }}</span>
                    <span class="text-base-content font-medium truncate">{{ user.username }}</span>
                  </div>
                  <div class="px-3 py-3 truncate text-base-content/80">{{ user.first_name }}</div>
                  <div class="px-3 py-3 truncate text-base-content/80">{{ user.last_name }}</div>
                  <div class="px-3 py-3 truncate text-base-content/60">{{ user.mail }}</div>
                  <div class="px-3 py-3 text-base-content/70">{{ user.niveau }}/{{ user.classe }}</div>
                  <div class="px-3 py-3">
                    <div class="px-3 py-3">
                      <span :class="['px-1.5 py-0.5 text-[10px] border leading-none', userTypeClass(user.type)]">{{ user.type }}</span>
                    </div>
                  </div>
                  <div class="px-3 py-3">
                    <span :class="['px-1.5 py-0.5 text-[10px] font-bold', user.status === 'ACTIVE' ? 'text-success' : 'text-warning']">{{ user.status }}</span>
                  </div>
                  <div class="px-3 py-3">
                    <span :class="['w-2.5 h-2.5 rounded-full inline-block', user.connected ? 'bg-success' : 'bg-error/40']" :title="user.connected ? 'Connecté' : 'Déconnecté'"></span>
                  </div>
                  <div class="px-3 py-3 flex items-center justify-end gap-2" @click.stop>
                    <button @click="openStatusModal(user)" class="font-text text-xs text-info hover:text-info/70 px-1 shrink-0">Modifier le statut</button>
                  </div>
                </div>
                <div v-if="selectedUser?.id === user.id" class="border-b border-base-300 bg-base-300/50 p-6">
                  <div class="flex items-center justify-between mb-4 border-b border-base-300 pb-3">
                    <h3 class="font-titre font-bold text-base text-base-content">Détails de l'utilisateur — {{ selectedUser.username }}</h3>
                  </div>
                  <div v-if="loadingUserInfo" class="flex justify-center py-10">
                    <span class="loading loading-dots loading-sm text-primary"></span>
                  </div>
                  <div v-else-if="!detailedUserInfo" class="text-center py-6 font-code text-xs text-base-content/25">Impossible de charger les détails</div>
                  <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 font-code text-xs">
                    <div class="bg-base-100/40 border border-base-300 p-4 flex flex-col gap-2">
                      <p class="text-[10px] uppercase tracking-widest text-primary font-bold mb-1">Informations générales</p>
                      <div class="flex justify-between"><span class="text-base-content/40">Création :</span> <span class="text-base-content">{{ detailedUserInfo.created_at }}</span></div>
                      <div class="flex justify-between"><span class="text-base-content/40">Preset :</span> <span class="text-base-content">{{ detailedUserInfo.user_preset }}</span></div>
                      <div class="flex justify-between"><span class="text-base-content/40">Dernière connexion :</span> <span class="text-base-content">{{ detailedUserInfo.last_connection }}</span></div>
                    </div>
                    <div class="bg-base-100/40 border border-base-300 p-4 flex flex-col justify-between gap-3">
                      <div>
                        <p class="text-[10px] uppercase tracking-widest text-primary font-bold mb-1">Inventaire</p>
                        <p class="text-base-content/60 text-[11px]">Badges et cosmétiques de l'utilisateur.</p>
                      </div>
                      <div class="flex gap-2">
                        <button @click="userBadgesModalOpen = true" class="flex-1 py-2 px-3 bg-base-200 border border-base-300 hover:border-primary text-center font-code text-xs transition-colors">
                          Badges ({{ detailedUserInfo.inventory.badges.length }})
                        </button>
                        <button @click="userCosmeticsModalOpen = true" class="flex-1 py-2 px-3 bg-base-200 border border-base-300 hover:border-primary text-center font-code text-xs transition-colors">
                          Cosmétiques ({{ detailedUserInfo.inventory.cosmetics.length }})
                        </button>
                      </div>
                    </div>
                    <div class="bg-base-100/40 border border-base-300 p-4 flex flex-col justify-between gap-3">
                      <div>
                        <p class="text-[10px] uppercase tracking-widest text-primary font-bold mb-1">Succès validés</p>
                        <p class="text-base-content/60 text-[11px]">Liste des succès débloqués par l'utilisateur.</p>
                      </div>
                      <button @click="userAchievementsModalOpen = true" class="w-full py-2 px-3 bg-base-200 border border-base-300 hover:border-primary text-center font-code text-xs transition-colors">
                        Voir les succès validés ({{ detailedUserInfo.achievement_count }})
                      </button>
                    </div>
                    <div class="bg-base-100/40 border border-base-300 p-4 flex flex-col gap-2">
                      <p class="text-[10px] uppercase tracking-widest text-primary font-bold mb-1">Statistiques de soumissions</p>
                      <div class="flex justify-between"><span class="text-base-content/40">Total soumissions :</span> <span class="font-bold text-base-content">{{ detailedUserInfo.challenges_count.total }}</span></div>
                      <div class="flex justify-between"><span class="text-base-content/40">Challenges uniques :</span> <span class="font-bold text-base-content">{{ detailedUserInfo.challenges_count.unique }}</span></div>
                      <div class="flex justify-between"><span class="text-base-content/40">Challenges validés :</span> <span class="font-bold text-success">{{ detailedUserInfo.challenges_count.validated }}</span></div>
                    </div>
                    <div class="bg-base-100/40 border border-base-300 p-4 flex flex-col justify-between gap-3">
                      <div>
                        <p class="text-[10px] uppercase tracking-widest text-primary font-bold mb-1">Historique des statuts</p>
                        <p class="text-base-content/60 text-[11px]">Historique des modifications de statut du compte.</p>
                      </div>
                      <button @click="userStatusHistoryModalOpen = true" class="w-full py-2 px-3 bg-base-200 border border-base-300 hover:border-primary text-center font-code text-xs transition-colors">
                        Voir l'historique des statuts ({{ detailedUserInfo.status_history.length }})
                      </button>
                    </div>
                    <div class="bg-base-100/40 border border-base-300 p-4 flex flex-col justify-between gap-3 lg:col-span-3">
                      <div>
                        <p class="text-[10px] uppercase tracking-widest text-primary font-bold mb-1">Historique des soumissions de flags</p>
                        <p class="text-base-content/60 text-[11px]">Historique des soumissions de l'utilisateur.</p>
                      </div>
                      <button @click="userSubmissionsModalOpen = true" class="w-full py-2 px-3 bg-base-200 border border-base-300 hover:border-primary text-center font-code text-xs transition-colors">
                        Voir toutes les soumissions ({{ detailedUserInfo.challenges_history.length }})
                      </button>
                    </div>
                  </div>
                </div>
              </template>
            </div>
          </div>
          <div class="border-t border-base-300 px-4 py-3 bg-base-200/50 flex items-center justify-between shrink-0 font-code text-xs">
            <div class="flex items-center gap-4">
              <span class="text-base-content/50">
                Affichage de <span class="text-base-content font-bold">{{ users.length ? (currentPage - 1) * itemsPerPage + 1 : 0 }}</span> à <span class="text-base-content font-bold">{{ (currentPage - 1) * itemsPerPage + users.length }}</span> sur <span class="text-base-content font-bold">{{ totalUsers }}</span> utilisateur{{ totalUsers > 1 ? 's' : '' }}.
              </span>
              <span
                v-if="search || filterRole || filterCity || filterStatus || filterConnected"
                class="text-primary/60 cursor-pointer hover:text-primary transition-colors"
                @click="clearFilters"
              >Effacer les filtres ×</span>
            </div>
            <div class="flex items-center gap-2">
              <button
                @click="prevPage"
                :disabled="currentPage === 1 || loadingUsers"
                class="px-3 py-1 bg-base-100 border border-base-300 hover:border-primary disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              >
                Précédent
              </button>
              <span class="text-base-content/70 px-2">
                Page {{ currentPage }} / {{ totalPages }}
              </span>
              <button
                @click="nextPage"
                :disabled="currentPage >= totalPages || loadingUsers"
                class="px-3 py-1 bg-base-100 border border-base-300 hover:border-primary disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              >
                Suivant
              </button>
            </div>
          </div>
        </div>
      </div>
      <div v-if="activeTab === 'users_presets_list'" class="flex flex-col gap-4 w-full">
        <div class="flex justify-start">
          <button
            @click="activeTab = 'users_presets_create'"
            class="flex items-center gap-2 bg-primary text-base-100 hover:bg-primary/80 px-4 py-2 font-code text-xs font-bold tracking-wider transition-colors shadow-sm"
          >
            <span>+ Créer un nouveau preset</span>
          </button>
        </div>
        <div v-if="loadingPresets" class="flex justify-center py-20">
          <span class="loading loading-spinner loading-md text-primary"></span>
        </div>
        <div v-else-if="!allPresets.length" class="flex flex-col items-center justify-center py-10 gap-1">
          <span class="font-text text-sm text-base-content/40">Aucun preset trouvé.</span>
        </div>
        <div v-else class="flex flex-col gap-1.5">
          <div v-for="preset in allPresets" :key="preset.id" class="border border-base-200/50 overflow-hidden">
            <div
              @click="togglePreset(preset.id)"
              class="flex items-center gap-3 px-4 py-3 cursor-pointer select-none hover:bg-base-300/40 transition-colors duration-150"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-base-content/50 transition-transform duration-200 shrink-0" :class="{ 'rotate-90': expandedPreset === preset.id }" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
              <span class="font-text text-[10px] px-2 py-0.5 leading-none bg-base-300 text-base-content/70 border border-base-300 shrink-0">
                {{ preset.users_count ?? 0 }} UTILISATEUR{{ (preset.users_count ?? 0) > 1 ? 'S' : '' }}
              </span>
              <span class="font-text font-semibold text-base-content text-sm flex-1 truncate">{{ preset.name }}</span>
              <button 
                class="font-text text-xs px-1 shrink-0 transition-colors"
                :class="preset.users_count > 0 ? 'text-base-content/20 cursor-not-allowed' : 'text-error hover:text-error/70'"
                @click.stop="preset.users_count === 0 && deletePreset(preset.id)" 
                :title="preset.users_count > 0 ? 'Impossible de supprimer : des utilisateurs sont liés à ce preset' : 'Supprimer'"
              >
                Supprimer
              </button>
            </div>
            <div v-if="expandedPreset === preset.id" class="bg-base-200/20 border-t border-base-200/50 p-4 animate-fade-in flex flex-col gap-4">
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4 font-code text-xs">
                <div class="bg-base-100 p-3 border border-base-300">
                  <span class="text-base-content/40 block text-[10px] uppercase">Type</span>
                  <span class="font-bold text-base-content">{{ preset.type }}</span>
                </div>
                <div class="bg-base-100 p-3 border border-base-300">
                  <span class="text-base-content/40 block text-[10px] uppercase">Affiliation</span>
                  <span class="font-bold text-base-content">{{ preset.affiliation }}</span>
                </div>
              </div>
              <div class="flex justify-start">
                <button
                  @click.stop="fetchPresetUsers(preset)"
                  class="px-4 py-2 font-code text-xs border border-base-300 hover:border-primary/40 text-base-content/70 hover:text-base-content bg-base-100 transition-colors"
                >
                  Afficher les utilisateurs liés ({{ preset.users_count ?? 0 }})
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-if="activeTab === 'users_presets_create'" class="w-full">
        <div class="grid grid-cols-1 xl:grid-cols-2 gap-8 items-start">
          <div class="border border-base-300 bg-base-200/40 p-6">
            <p class="font-code text-[10px] tracking-widest uppercase text-base-content/35 mb-1">Nouveau preset</p>
            <h2 class="font-titre font-bold text-lg text-base-content mb-6">Créer un preset</h2>
            
            <div class="flex flex-col gap-4">
              <div>
                <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40 block mb-1">Nom du preset *</label>
                <input v-model="newPresetForm.name" type="text" placeholder="Ex: Paris GCS3" class="w-full bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-xs text-base-content" />
              </div>
              <div>
                <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40 block mb-1">Type</label>
                <select v-model="newPresetForm.type" class="w-full bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-xs text-base-content">
                  <option value="USER">USER</option>
                  <option value="ADMIN">ADMIN</option>
                  <option value="PEDAGOGIE">PEDAGOGIE</option>
                  <option value="INVITE">INVITE</option>
                  <option value="EXTERNE">EXTERNE</option>
                </select>
              </div>
              <div>
                <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40 block mb-1">Affiliation</label>
                <select v-model="newPresetForm.affiliation" class="w-full bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-xs text-base-content">
                  <option value="PARIS">PARIS</option>
                  <option value="LYON">LYON</option>
                  <option value="BORDEAUX">BORDEAUX</option>
                </select>
              </div>
              <div class="flex gap-3 mt-4">
                <button @click="createPreset" :disabled="creatingPreset || !newPresetForm.name.trim() || !newPresetForm.affiliation.trim()" class="px-5 py-2 bg-primary text-base-100 font-code text-xs hover:bg-primary/80 transition-colors disabled:opacity-30">
                  <span v-if="creatingPreset" class="loading loading-xs"></span>
                  <span v-else>Créer le preset</span>
                </button>
                <button @click="activeTab = 'users_presets_list'" class="px-5 py-2 border border-base-300 font-code text-xs text-base-content/70 hover:text-base-content hover:bg-base-200 transition-colors">Annuler</button>
              </div>
            </div>
          </div>
          <div class="sticky top-6 border border-primary/30 bg-base-100/90 p-6 shadow-2xl backdrop-blur-md">
            <div class="flex items-center justify-between border-b border-base-300 pb-3 mb-6">
              <span class="font-code text-[10px] tracking-widest uppercase text-primary font-bold">Aperçu page d'inscription</span>
            </div>
            <div class="text-center">
              <div class="mb-6">
                <h1 class="text-2xl font-bold tracking-tight text-base-content m-0 font-titre">GUARDIHACK</h1>
                <p class="text-xs font-medium text-base-content/60 mt-0.5">Inscription</p>
                <p class="text-[10px] font-mono tracking-widest text-base-content/40 uppercase mt-2">
                  {{ newPresetForm.type || 'COMPTE' }} <br> {{ newPresetForm.affiliation || 'AFFILIATION' }}
                </p>
              </div>
              <div class="flex flex-col gap-4 text-left pointer-events-none opacity-90">
                <div class="grid grid-cols-2 gap-3">
                  <div class="flex flex-col gap-1">
                    <label class="text-[11px] text-base-content/70 font-medium">Prénom</label>
                    <div class="w-full bg-base-200 border border-base-content/10 px-3 py-2 text-xs text-base-content/40 rounded-sm">Prénom</div>
                  </div>
                  <div class="flex flex-col gap-1">
                    <label class="text-[11px] text-base-content/70 font-medium">Nom</label>
                    <div class="w-full bg-base-200 border border-base-content/10 px-3 py-2 text-xs text-base-content/40 rounded-sm">Nom</div>
                  </div>
                </div>
                <div class="flex flex-col gap-1">
                  <label class="text-[11px] text-base-content/70 font-medium">Email</label>
                  <div class="w-full bg-base-200 border border-base-content/10 px-3 py-2 text-xs text-base-content/40 rounded-sm">nom.prenom@guardiaschool.fr</div>
                </div>
                <div class="flex flex-col gap-1">
                  <label class="text-[11px] text-base-content/70 font-medium">Username</label>
                  <div class="w-full bg-base-200 border border-base-content/10 px-3 py-2 text-xs text-base-content/40 rounded-sm">ex: Haizer</div>
                </div>
                <div class="flex flex-col gap-1">
                  <label class="text-[11px] text-base-content/70 font-medium">Passphrase</label>
                  <div class="w-full bg-base-200 border border-base-content/10 px-3 py-2 text-xs text-base-content/40 rounded-sm">••••••</div>
                </div>
                <div class="w-full mt-2 bg-neutral text-neutral-content text-xs font-medium py-2.5 px-4 rounded-sm tracking-wide text-center font-mono">
                  Créer mon compte
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-if="activeTab === 'users_tokens_list'" class="flex flex-col gap-4 w-full">
        <div class="flex justify-start">
          <button
            @click="activeTab = 'users_tokens_create'"
            class="flex items-center gap-2 bg-primary text-base-100 hover:bg-primary/80 px-4 py-2 font-code text-xs font-bold tracking-wider transition-colors shadow-sm"
          >
            <span>+ Créer un nouveau token</span>
          </button>
        </div>
        <div v-if="loadingPresets" class="flex justify-center py-20">
          <span class="loading loading-spinner loading-md text-primary"></span>
        </div>
        <div v-else-if="!tokensGroupedByPreset.length" class="flex flex-col items-center justify-center py-10 gap-1">
          <span class="font-text text-sm text-base-content/40">Aucun token généré pour le moment.</span>
        </div>
        <div v-else class="flex flex-col gap-1.5">
          <div v-for="group in tokensGroupedByPreset" :key="group.presetId" class="border border-base-200/50 overflow-hidden">
            <div
              @click="toggleTokenPreset(group.presetId)"
              class="flex items-center gap-3 px-4 py-3 cursor-pointer select-none hover:bg-base-300/40 transition-colors duration-150"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-base-content/50 transition-transform duration-200 shrink-0" :class="{ 'rotate-90': expandedTokenPreset === group.presetId }" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
              <span class="font-text text-[10px] px-2 py-0.5 leading-none bg-base-300 text-base-content/70 border border-base-300 shrink-0">
                {{ group.tokens.length }} TOKEN{{ group.tokens.length > 1 ? 'S' : '' }}
              </span>
              <span class="font-text font-semibold text-base-content text-sm flex-1 truncate">{{ group.presetName }}</span>
            </div>
            <div v-if="expandedTokenPreset === group.presetId" class="bg-base-200/20 border-t border-base-200/50 p-4 animate-fade-in flex flex-col gap-4">
              <div class="grid grid-cols-2 md:grid-cols-2 gap-4 font-code text-xs">
                <div class="bg-base-100 p-3 border border-base-300 flex flex-col gap-1">
                  <span class="text-base-content/40 uppercase text-[10px]">Tokens utilisés / Total</span>
                  <span class="font-bold text-primary text-base">
                    {{ group.tokens.filter(t => t.uses > 0 || t.is_active !== 'ACTIVE').length }} / {{ group.tokens.length }}
                  </span>
                </div>
                <div class="bg-base-100 p-3 border border-base-300 flex flex-col gap-1">
                  <span class="text-base-content/40 uppercase text-[10px]">Tokens actifs</span>
                  <span class="font-bold text-success text-base">
                    {{ group.tokens.filter(t => t.is_active === 'ACTIVE').length }}
                  </span>
                </div>
              </div>
              <div class="flex justify-start">
                <button
                  @click.stop="openPresetTokensModal(group)"
                  class="px-4 py-2 font-code text-xs border border-base-300 hover:border-primary/40 text-base-content/70 hover:text-base-content bg-base-100 transition-colors"
                >
                  Afficher la liste complète des tokens ({{ group.tokens.length }})
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-if="activeTab === 'users_tokens_create'" class="w-full">
        <div class="grid grid-cols-1 xl:grid-cols-2 gap-8 items-start">
          <div class="border border-base-300 bg-base-200/40 p-6">
            <h2 class="font-titre font-bold text-lg text-base-content mb-4">Générer un token d'invitation</h2>
            <div class="flex flex-col gap-4">
              <div>
                <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40 block mb-1">Sélectionner un preset *</label>
                <select v-model="newTokenPreset" class="w-full bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-xs text-base-content">
                  <option value="">— Choisir un preset —</option>
                  <option v-for="p in allPresets" :key="p.id" :value="p.id">{{ p.name }} ({{ p.affiliation }})</option>
                </select>
              </div>
              <div>
                <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40 block mb-1">Utilisations maximales</label>
                <input v-model.number="newTokenMaxUses" type="number" min="1" placeholder="1" class="w-full bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-xs text-base-content" />
              </div>
              <div class="border border-base-300/60 bg-base-100/30 p-3 flex flex-col gap-3">
                <label class="flex items-center gap-2 cursor-pointer select-none">
                  <input v-model="enableName" type="checkbox" class="checkbox checkbox-xs checkbox-primary rounded-none" />
                  <span class="font-code text-xs text-base-content font-medium">Pré-remplir le Nom et Prénom</span>
                </label>
                <div v-if="enableName" class="grid grid-cols-2 gap-2 animate-fade-in">
                  <input v-model="newTokenFirstName" type="text" placeholder="Prénom" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-1.5 font-code text-xs text-base-content" />
                  <input v-model="newTokenLastName" type="text" placeholder="Nom" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-1.5 font-code text-xs text-base-content" />
                </div>
              </div>
              <div class="border border-base-300/60 bg-base-100/30 p-3 flex flex-col gap-3">
                <label class="flex items-center gap-2 cursor-pointer select-none">
                  <input v-model="enableClasse" type="checkbox" class="checkbox checkbox-xs checkbox-primary rounded-none" />
                  <span class="font-code text-xs text-base-content font-medium">Pré-remplir la Classe et le Niveau</span>
                </label>
                <div v-if="enableClasse" class="grid grid-cols-2 gap-2 animate-fade-in">
                  <input v-model="newTokenClasse" type="text" placeholder="Classe" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-1.5 font-code text-xs text-base-content" />
                  <input v-model="newTokenNiveau" type="text" placeholder="Niveau" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-1.5 font-code text-xs text-base-content" />
                </div>
              </div>
              <div class="border border-base-300/60 bg-base-100/30 p-3 flex flex-col gap-3">
                <label class="flex items-center gap-2 cursor-pointer select-none">
                  <input v-model="enableEmail" type="checkbox" class="checkbox checkbox-xs checkbox-primary rounded-none" />
                  <span class="font-code text-xs text-base-content font-medium">Pré-remplir l'Email</span>
                </label>
                <div v-if="enableEmail" class="animate-fade-in">
                  <input v-model="newTokenMail" type="email" placeholder="etudiant@guardiaschool.fr" class="w-full bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-1.5 font-code text-xs text-base-content" />
                </div>
              </div>
              <div class="border border-base-300/60 bg-base-100/30 p-3 flex flex-col gap-3">
                <label class="flex items-center gap-2 cursor-pointer select-none">
                  <input v-model="enableExpiration" type="checkbox" class="checkbox checkbox-xs checkbox-primary rounded-none" />
                  <span class="font-code text-xs text-base-content font-medium">Définir une date d'expiration</span>
                </label>
                <div v-if="enableExpiration" class="animate-fade-in">
                  <input v-model="newTokenExpiresAt" type="datetime-local" class="w-full bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-1.5 font-code text-xs text-base-content" />
                </div>
              </div>
              <div class="flex gap-3 mt-2">
                <button @click="createToken" :disabled="creatingToken || !newTokenPreset" class="px-5 py-2 bg-primary text-base-100 font-code text-xs hover:bg-primary/80 transition-colors disabled:opacity-30">
                  <span v-if="creatingToken" class="loading loading-xs"></span>
                  <span v-else>Générer le token</span>
                </button>
                <button @click="activeTab = 'users_tokens_list'" class="px-5 py-2 border border-base-300 font-code text-xs text-base-content/70 hover:text-base-content hover:bg-base-200 transition-colors">Annuler</button>
              </div>
            </div>
          </div>
          <div class="sticky top-6 border border-primary/30 bg-base-100/90 p-6 shadow-2xl backdrop-blur-md">
            <div class="flex items-center justify-between border-b border-base-300 pb-3 mb-6">
              <span class="font-code text-[10px] tracking-widest uppercase text-primary font-bold">Aperçu page d'inscription</span>
            </div>
            <div class="text-center">
              <div class="mb-6">
                <h1 class="text-2xl font-bold tracking-tight text-base-content m-0 font-titre">GUARDIHACK</h1>
                <p class="text-xs font-medium text-base-content/60 mt-0.5">Inscription</p>
                <p class="text-[10px] font-mono tracking-widest text-base-content/40 uppercase mt-2">
                  {{ enableClasse && newTokenNiveau ? newTokenNiveau : 'NIVEAU' }} / CLASSE {{ enableClasse && newTokenClasse ? newTokenClasse : 'CLASSE' }} <br>
                  {{ selectedPresetData?.affiliation || 'AFFILIATION' }}
                </p>
              </div>
              <div class="flex flex-col gap-4 text-left pointer-events-none opacity-90">
                <div class="grid grid-cols-2 gap-3">
                  <div class="flex flex-col gap-1">
                    <label class="text-[11px] text-base-content/70 font-medium">Prénom</label>
                    <div :class="['w-full border px-3 py-2 text-xs rounded-sm', enableName && newTokenFirstName ? 'bg-base-100 border-primary/40 text-base-content font-medium' : 'bg-base-200 border-base-content/10 text-base-content/40']">
                      {{ enableName && newTokenFirstName ? newTokenFirstName : 'Prénom' }}
                    </div>
                  </div>
                  <div class="flex flex-col gap-1">
                    <label class="text-[11px] text-base-content/70 font-medium">Nom</label>
                    <div :class="['w-full border px-3 py-2 text-xs rounded-sm', enableName && newTokenLastName ? 'bg-base-100 border-primary/40 text-base-content font-medium' : 'bg-base-200 border-base-content/10 text-base-content/40']">
                      {{ enableName && newTokenLastName ? newTokenLastName : 'Nom' }}
                    </div>
                  </div>
                </div>
                <div class="flex flex-col gap-1">
                  <label class="text-[11px] text-base-content/70 font-medium">Email</label>
                  <div :class="['w-full border px-3 py-2 text-xs rounded-sm', enableEmail && newTokenMail ? 'bg-base-100 border-primary/40 text-base-content font-medium' : 'bg-base-200 border-base-content/10 text-base-content/40']">
                    {{ enableEmail && newTokenMail ? newTokenMail : 'nom.prenom@guardiaschool.fr' }}
                  </div>
                </div>
                <div class="flex flex-col gap-1">
                  <label class="text-[11px] text-base-content/70 font-medium">Username</label>
                  <div class="w-full bg-base-200 border border-base-content/10 px-3 py-2 text-xs text-base-content/40 rounded-sm">ex: Haizer</div>
                </div>
                <div class="flex flex-col gap-1">
                  <label class="text-[11px] text-base-content/70 font-medium">Passphrase</label>
                  <div class="w-full bg-base-200 border border-base-content/10 px-3 py-2 text-xs text-base-content/40 rounded-sm">••••••</div>
                </div>
                <div class="w-full mt-2 bg-neutral text-neutral-content text-xs font-medium py-2.5 px-4 rounded-sm tracking-wide text-center font-mono">
                  Créer mon compte
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-if="activeTab === 'users_tokens_auto'" class="w-full">
        <div class="border border-base-300 bg-base-200/40 p-6 max-w-xl">
          <h2 class="font-titre font-bold text-lg text-base-content mb-2">Importation automatisée</h2>
          <p class="font-code text-xs text-base-content/60 mb-6">
            Sélectionnez un preset cible et importez un fichier CSV contenant les colonnes : <code class="text-primary">mail</code>, <code class="text-primary">first_name</code>, <code class="text-primary">last_name</code>, <code class="text-primary">classe</code>, <code class="text-primary">niveau</code>.
          </p>
          <div class="flex flex-col gap-4">
            <div>
              <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40 block mb-1">Preset cible *</label>
              <select v-model="autoTokenPreset" class="w-full bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-xs text-base-content">
                <option value="">— Choisir un preset —</option>
                <option v-for="p in allPresets" :key="p.id" :value="p.id">{{ p.name }} ({{ p.affiliation }})</option>
              </select>
            </div>
            <div>
              <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40 block mb-1">Fichier CSV *</label>
              <input @change="handleCsvFileSelect" type="file" accept=".csv" class="w-full bg-base-100 border border-base-300 focus:border-primary outline-none file:mr-4 file:py-2 file:px-4 file:border-0 file:bg-base-200 file:text-base-content file:font-code file:text-xs text-xs text-base-content/70 cursor-pointer" />
            </div>
            <div class="border border-base-300/60 bg-base-100/30 p-3">
              <label class="flex items-center gap-2 cursor-pointer select-none">
                <input v-model="autoSendEmail" type="checkbox" class="checkbox checkbox-xs checkbox-primary rounded-none" />
                <span class="font-code text-xs text-base-content font-medium">Envoyer automatiquement l'e-mail d'invitation</span>
              </label>
            </div>
            <div class="flex gap-3 mt-2">
              <button @click="submitAutoCreateTokens" :disabled="uploadingAutoTokens || !autoTokenPreset || !selectedCsvFile" class="px-5 py-2 bg-primary text-base-100 font-code text-xs hover:bg-primary/80 transition-colors disabled:opacity-30">
                <span v-if="uploadingAutoTokens" class="loading loading-xs"></span>
                <span v-else>Lancer l'import</span>
              </button>
              <button @click="activeTab = 'users_tokens_list'" class="px-5 py-2 border border-base-300 font-code text-xs text-base-content/70 hover:text-base-content hover:bg-base-200 transition-colors">Annuler</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <Teleport to="body">
    <div v-if="presetTokensModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4" @click.self="presetTokensModalOpen = false">
      <div class="w-full max-w-7xl max-h-[85vh] bg-base-200 border border-base-300 flex flex-col shadow-2xl">
        <div class="flex items-center justify-between px-5 py-3 border-b border-base-300">
          <p class="font-stitre font-bold text-sm text-base-content">Tokens — {{ selectedPresetForTokens?.presetName }}</p>
          <div class="flex items-center gap-4">
            <button @click="downloadModalTokensCsv" :disabled="exportingModalTokens || !modalTokensList.length" class="font-code text-xs text-base-content/40 hover:text-primary disabled:opacity-30">
              <span v-if="exportingModalTokens" class="loading loading-xs"></span>
              <span v-else>⬇ Exporter en CSV</span>
            </button>
            <button @click="presetTokensModalOpen = false" class="font-code text-xs text-error hover:text-error/70">Fermer</button>
          </div>
        </div>
        <div class="flex-1 overflow-y-auto px-5 py-3">
          <div v-if="loadingModalTokens" class="flex justify-center py-10">
            <span class="loading loading-dots loading-sm text-primary"></span>
          </div>
          <div v-else-if="!modalTokensList.length" class="text-center py-10 font-text text-sm text-base-content/25">Aucun token dans ce lot</div>
          <div v-else class="overflow-x-auto">
            <table class="w-full text-[11px] font-code">
              <thead>
                <tr class="text-base-content/40 border-b border-base-300">
                  <th class="text-left py-1.5 pr-3 font-normal">Valeur du Token</th>
                  <th class="text-left py-1.5 pr-3 font-normal">Email</th>
                  <th class="text-left py-1.5 pr-3 font-normal">Prénom</th>
                  <th class="text-left py-1.5 pr-3 font-normal">Nom</th>
                  <th class="text-left py-1.5 pr-3 font-normal">Niveau</th>
                  <th class="text-left py-1.5 pr-3 font-normal">Classe</th>
                  <th class="text-left py-1.5 pr-3 font-normal">Utilisations</th>
                  <th class="text-left py-1.5 pr-3 font-normal">Max</th>
                  <th class="text-left py-1.5 pr-3 font-normal">Expiration</th>
                  <th class="text-left py-1.5 pr-3 font-normal">Actif</th>
                  <th class="text-left py-1.5 pr-3 font-normal">Créé le</th>
                  <th class="text-left py-1.5 pr-3 font-normal">Généré par</th>
                  <th class="text-center py-1.5 pr-3 font-normal">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="t in modalTokensList" :key="t.id"
                  class="border-b border-base-300/50 hover:bg-base-300/30"
                >
                  <td class="py-2 pr-3 font-mono text-primary select-all">{{ t.token }}</td>
                  <td class="py-2 pr-3 text-base-content/80">{{ t.mail ?? '—' }}</td>
                  <td class="py-2 pr-3 text-base-content">{{ t.first_name ?? '—' }}</td>
                  <td class="py-2 pr-3 text-base-content font-medium">{{ t.last_name ?? '—' }}</td>
                  <td class="py-2 pr-3 text-base-content">{{ t.niveau ?? '—' }}</td>
                  <td class="py-2 pr-3 text-base-content">{{ t.classe ?? '—' }}</td>
                  <td class="py-2 pr-3 text-base-content/70">{{ t.uses }}</td>
                  <td class="py-2 pr-3 text-base-content/70">{{ t.max_uses ?? '∞' }}</td>
                  <td class="py-2 pr-3 text-base-content/50">{{ t.expires_at ?? 'Jamais' }}</td>
                  <td class="py-2 pr-3 font-bold" :class="t.is_active === 'ACTIVE' ? 'text-success' : 'text-error'">
                    {{ t.is_active === 'ACTIVE' ? 'Oui' : 'Non' }}
                  </td>
                  <td class="py-2 pr-3 text-base-content/50">{{ t.created_at ?? '—' }}</td>
                  <td class="py-2 pr-3 font-bold" :class="t.auto ? 'text-primary' : ''">
                    {{ t.created_by ?? '—' }}
                  </td>
                  <td class="py-2 pr-3">
                    <button @click="notifyToken(t.id)" class="text-primary hover:underline text-[10px]">Notifier</button>
                    <button @click="deleteToken(t.id)" class="text-error hover:underline text-[10px] ml-2">Révoquer</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
  <Teleport to="body">
    <div v-if="presetUsersPanelOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4" @click.self="presetUsersPanelOpen = false">
      <div class="w-full max-w-4xl max-h-[85vh] bg-base-200 border border-base-300 flex flex-col shadow-2xl">
        <div class="flex items-center justify-between px-5 py-3 border-b border-base-300">
          <p class="font-stitre font-bold text-sm text-base-content">Utilisateurs liés — {{ selectedPresetObj?.name }}</p>
          <div class="flex items-center gap-4">
            <button @click="downloadPresetUsersCsv" :disabled="exportingPresetUsers || !presetUsersList.length" class="font-code text-xs text-base-content/40 hover:text-primary disabled:opacity-30">
              <span v-if="exportingPresetUsers" class="loading loading-xs"></span>
              <span v-else>⬇ Exporter en CSV</span>
            </button>
            <button @click="presetUsersPanelOpen = false" class="font-code text-xs text-error hover:text-error/70">Fermer</button>
          </div>
        </div>
        <div class="flex-1 overflow-y-auto px-5 py-3">
          <div v-if="loadingPresetUsers" class="flex justify-center py-10">
            <span class="loading loading-dots loading-sm text-primary"></span>
          </div>
          <div v-else-if="!presetUsersList.length" class="text-center py-10 font-text text-sm text-base-content/25">Aucun utilisateur lié à ce preset</div>
          <div v-else class="overflow-x-auto">
            <table class="w-full text-[11px] font-code">
              <thead>
                <tr class="text-base-content/40 border-b border-base-300">
                  <th class="text-left py-1.5 pr-3 font-normal">ID</th>
                  <th class="text-left py-1.5 pr-3 font-normal">Nom</th>
                  <th class="text-left py-1.5 pr-3 font-normal">Prénom</th>
                  <th class="text-left py-1.5 pr-3 font-normal">Username</th>
                  <th class="text-left py-1.5 pr-3 font-normal">Email</th>
                  <th class="text-left py-1.5 pr-3 font-normal">Classe</th>
                  <th class="text-left py-1.5 pr-3 font-normal">Niveau</th>
                  <th class="text-left py-1.5 pr-3 font-normal">Affiliation</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="u in presetUsersList" :key="u.id"
                  class="border-b border-base-300/50 hover:bg-base-300/30"
                >
                  <td class="py-2 pr-3 text-base-content/60">{{ u.id }}</td>
                  <td class="py-2 pr-3 text-base-content font-medium">{{ u.last_name ?? '—' }}</td>
                  <td class="py-2 pr-3 text-base-content">{{ u.first_name ?? '—' }}</td>
                  <td class="py-2 pr-3 text-primary font-medium">{{ u.username }}</td>
                  <td class="py-2 pr-3 text-base-content/80">{{ u.mail }}</td>
                  <td class="py-2 pr-3 text-base-content/60">{{ u.classe ?? '—' }}</td>
                  <td class="py-2 pr-3 text-base-content/60">{{ u.niveau ?? '—' }}</td>
                  <td class="py-2 pr-3 text-base-content/60">{{ u.affiliation ?? '—' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
  <Teleport to="body">
    <div v-if="statusModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4" @click.self="statusModalOpen = false">
      <div class="w-full max-w-md bg-base-200 border border-base-300 flex flex-col shadow-2xl p-6 font-code">
        <div class="flex items-center justify-between border-b border-base-300 pb-3 mb-4">
          <div>
            <p class="text-[10px] uppercase text-base-content/40">Gestion du statut</p>
            <h3 class="font-titre font-bold text-base text-base-content">Modifier le statut de {{ targetUserForStatus?.username }}</h3>
          </div>
          <button @click="statusModalOpen = false" class="text-xs text-error hover:text-error/70">Fermer</button>
        </div>
        <div class="flex flex-col gap-4 text-xs">
          <div>
            <label class="block text-[10px] uppercase text-base-content/40 mb-1">Nouveau statut *</label>
            <select v-model="statusForm.new_status" class="w-full bg-base-100 border border-base-300 px-3 py-2 outline-none focus:border-primary">
              <option value="ACTIVE">ACTIVE</option>
              <option value="PENDING">PENDING</option>
              <option value="LOCKED">LOCKED (Verrouillé)</option>
              <option value="BANNED">BANNED (Banni)</option>
            </select>
          </div>
          <div v-if="['LOCKED', 'BANNED'].includes(statusForm.new_status)">
            <label class="block text-[10px] uppercase text-base-content/40 mb-1">Raison (Obligatoire pour verrouillage/bannissement) *</label>
            <textarea v-model="statusForm.reason" rows="3" placeholder="Motif de la sanction..." class="w-full bg-base-100 border border-base-300 px-3 py-2 outline-none focus:border-primary resize-none"></textarea>
          </div>
          <div v-if="statusForm.new_status === 'LOCKED'">
            <label class="block text-[10px] uppercase text-base-content/40 mb-1">Date de fin du verrouillage (Optionnel)</label>
            <input v-model="statusForm.ended_at" type="datetime-local" class="w-full bg-base-100 border border-base-300 px-3 py-2 outline-none focus:border-primary" />
          </div>
          <div class="flex justify-end gap-2 mt-4">
            <button @click="statusModalOpen = false" class="px-4 py-2 border border-base-300 text-base-content/70 hover:bg-base-300/30">Annuler</button>
            <button @click="submitStatusUpdate" :disabled="updatingStatus" class="px-4 py-2 bg-primary text-base-100 font-bold hover:bg-primary/80 disabled:opacity-30">
              <span v-if="updatingStatus" class="loading loading-xs"></span>
              <span v-else>Appliquer la modification</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
  <Teleport to="body">
    <div v-if="userBadgesModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4" @click.self="userBadgesModalOpen = false">
      <div class="w-full max-w-xl max-h-[85vh] bg-base-200 border border-base-300 flex flex-col shadow-2xl font-code">
        <div class="flex items-center justify-between px-5 py-3 border-b border-base-300">
          <p class="font-bold text-sm text-base-content">Badges — {{ selectedUser?.username }}</p>
          <div class="flex items-center gap-4">
            <button @click="downloadUserBadgesCsv" :disabled="exportingUserBadges || !detailedUserInfo?.inventory?.badges?.length" class="text-xs text-base-content/40 hover:text-primary disabled:opacity-30">
              <span v-if="exportingUserBadges" class="loading loading-xs"></span>
              <span v-else>⬇ Exporter en CSV</span>
            </button>
            <button @click="userBadgesModalOpen = false" class="text-xs text-error hover:text-error/70">Fermer</button>
          </div>
        </div>
        <div class="flex-1 overflow-y-auto px-5 py-4">
          <div v-if="!detailedUserInfo?.inventory?.badges?.length" class="text-center py-8 text-xs text-base-content/35">Aucun badge possédé</div>
          <div v-else class="flex flex-wrap gap-2">
            <span v-for="b in detailedUserInfo.inventory.badges" :key="b" class="px-2 py-1 bg-base-100 border border-base-300 text-xs">{{ b }}</span>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
  <Teleport to="body">
    <div v-if="userCosmeticsModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4" @click.self="userCosmeticsModalOpen = false">
      <div class="w-full max-w-xl max-h-[85vh] bg-base-200 border border-base-300 flex flex-col shadow-2xl font-code">
        <div class="flex items-center justify-between px-5 py-3 border-b border-base-300">
          <p class="font-bold text-sm text-base-content">Cosmétiques — {{ selectedUser?.username }}</p>
          <div class="flex items-center gap-4">
            <button @click="downloadUserCosmeticsCsv" :disabled="exportingUserCosmetics || !detailedUserInfo?.inventory?.cosmetics?.length" class="text-xs text-base-content/40 hover:text-primary disabled:opacity-30">
              <span v-if="exportingUserCosmetics" class="loading loading-xs"></span>
              <span v-else>⬇ Exporter en CSV</span>
            </button>
            <button @click="userCosmeticsModalOpen = false" class="text-xs text-error hover:text-error/70">Fermer</button>
          </div>
        </div>
        <div class="flex-1 overflow-y-auto px-5 py-4">
          <div v-if="!detailedUserInfo?.inventory?.cosmetics?.length" class="text-center py-8 text-xs text-base-content/35">Aucun cosmétique possédé</div>
          <div v-else class="flex flex-wrap gap-2">
            <span v-for="c in detailedUserInfo.inventory.cosmetics" :key="c" class="px-2 py-1 bg-base-100 border border-base-300 text-xs">{{ c }}</span>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
  <Teleport to="body">
    <div v-if="userStatusHistoryModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4" @click.self="userStatusHistoryModalOpen = false">
      <div class="w-full max-w-2xl max-h-[85vh] bg-base-200 border border-base-300 flex flex-col shadow-2xl font-code">
        <div class="flex items-center justify-between px-5 py-3 border-b border-base-300">
          <p class="font-bold text-sm text-base-content">Historique des statuts — {{ selectedUser?.username }}</p>
          <div class="flex items-center gap-4">
            <button @click="downloadUserStatusHistoryCsv" :disabled="exportingUserStatusHistory || !detailedUserInfo?.status_history?.length" class="text-xs text-base-content/40 hover:text-primary disabled:opacity-30">
              <span v-if="exportingUserStatusHistory" class="loading loading-xs"></span>
              <span v-else>⬇ Exporter en CSV</span>
            </button>
            <button @click="userStatusHistoryModalOpen = false" class="text-xs text-error hover:text-error/70">Fermer</button>
          </div>
        </div>
        <div class="flex-1 overflow-y-auto px-5 py-4">
          <div v-if="!detailedUserInfo?.status_history?.length" class="text-center py-8 text-xs text-base-content/35">Aucun historique de statut</div>
          <div v-else class="flex flex-col gap-2">
            <div v-for="(h, idx) in detailedUserInfo.status_history" :key="idx" class="p-3 bg-base-100 border border-base-300 text-xs">
              <div class="flex justify-between font-bold mb-1">
                <span class="text-warning">{{ h.status }}</span> 
                <span class="text-base-content/40">{{ h.created_at }}</span>
              </div>
              <p v-if="h.reason" class="text-base-content/70">Raison : {{ h.reason }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
  <Teleport to="body">
    <div v-if="userSubmissionsModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4" @click.self="userSubmissionsModalOpen = false">
      <div class="w-full max-w-3xl max-h-[85vh] bg-base-200 border border-base-300 flex flex-col shadow-2xl font-code">
        <div class="flex items-center justify-between px-5 py-3 border-b border-base-300">
          <p class="font-bold text-sm text-base-content">Historique des soumissions — {{ selectedUser?.username }}</p>
          <div class="flex items-center gap-4">
            <button @click="downloadUserSubmissionsCsv" :disabled="exportingUserSubmissions || !detailedUserInfo?.challenges_history?.length" class="text-xs text-base-content/40 hover:text-primary disabled:opacity-30">
              <span v-if="exportingUserSubmissions" class="loading loading-xs"></span>
              <span v-else>⬇ Exporter en CSV</span>
            </button>
            <button @click="userSubmissionsModalOpen = false" class="text-xs text-error hover:text-error/70">Fermer</button>
          </div>
        </div>
        <div class="flex-1 overflow-y-auto px-5 py-4">
          <div v-if="!detailedUserInfo?.challenges_history?.length" class="text-center py-8 text-xs text-base-content/35">Aucune soumission enregistrée</div>
          <div v-else class="overflow-x-auto">
            <table class="w-full text-xs">
              <thead>
                <tr class="text-base-content/40 border-b border-base-300">
                  <th class="text-left py-2 pr-3 font-normal">Challenge</th>
                  <th class="text-left py-2 pr-3 font-normal">Résultat</th>
                  <th class="text-left py-2 pr-3 font-normal">Date</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(sub, idx) in detailedUserInfo.challenges_history" :key="idx" class="border-b border-base-300/50 hover:bg-base-300/30">
                  <td class="py-2 pr-3 font-medium text-base-content">{{ sub.challenge_name }}</td>
                  <td class="py-2 pr-3" :class="sub.is_correct ? 'text-success' : 'text-error'">{{ sub.is_correct ? 'Correct' : 'Incorrect' }}</td>
                  <td class="py-2 pr-3 text-base-content/50">{{ sub.submitted_at }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
  <Teleport to="body">
    <div v-if="userAchievementsModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4" @click.self="userAchievementsModalOpen = false">
      <div class="w-full max-w-xl max-h-[85vh] bg-base-200 border border-base-300 flex flex-col shadow-2xl font-code">
        <div class="flex items-center justify-between px-5 py-3 border-b border-base-300">
          <p class="font-bold text-sm text-base-content">Succès validés — {{ selectedUser?.username }}</p>
          <div class="flex items-center gap-4">
            <button @click="downloadUserAchievementsCsv" :disabled="exportingUserAchievements || !detailedUserInfo?.achievements?.length" class="text-xs text-base-content/40 hover:text-primary disabled:opacity-30">
              <span v-if="exportingUserAchievements" class="loading loading-xs"></span>
              <span v-else>⬇ Exporter en CSV</span>
            </button>
            <button @click="userAchievementsModalOpen = false" class="text-xs text-error hover:text-error/70">Fermer</button>
          </div>
        </div>
        <div class="flex-1 overflow-y-auto px-5 py-4">
          <div v-if="!detailedUserInfo?.achievements?.length" class="text-center py-8 text-xs text-base-content/35">Aucun succès validé pour le moment</div>
          <div v-else class="flex flex-wrap gap-2">
            <span v-for="ach in detailedUserInfo.achievements" :key="ach" class="px-2 py-1 bg-primary/10 border border-primary/30 text-primary text-xs">{{ ach }}</span>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>