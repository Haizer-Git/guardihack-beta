<script setup>
import { ref, reactive, computed, watch } from 'vue'
import axios from 'axios'
import { showToast } from './useAdminToast.js'
import PopUpConfirm from '../../components/PopUpConfirm.vue'
import { getAssetUrl } from '../../utils/assets'

const props = defineProps({
  initialTab: {
    type: String,
    default: 'achievement_list',
  },
})
const achievements          = ref([])
const loadingAchievements   = ref(false)
const selectedAchievement   = ref(null)
const requirementsPanelOpen = ref(false)
const rewardsPanelOpen      = ref(false)
const usersPanelOpen        = ref(false)
const exportingCsv          = ref(false)
const achievementModal      = reactive({ isOpen: false })
const allChallenges         = ref([])
const allCategories         = ref([])
const allBadges             = ref([])
const allCosmetics          = ref('')
const search                = ref('')
const sortKey               = ref('id')
const sortDir               = ref('desc')
const requirementTypeLabels = {
  "CHALLENGE_COMPLETION": "Complétion d'un challenge spécifique",
  "CHALLENGE_COMPLETION_COUNT": "Nombre de challenges validés",
  "CATEGORY_COMPLETION": "Complétion d'une catégorie",
  "CATEGORY_COMPLETION_COUNT": "Nombre de challenges par catégorie",
  "COSMETIC_OWNERSHIP": "Possession d'un cosmétique",
  "COSMETIC_OWNERSHIP_COUNT": "Nombre de cosmétiques possédés",
  "BADGE_OWNERSHIP": "Possession d'un badge",
  "BADGE_OWNERSHIP_COUNT": "Nombre de badges possédés",
  "POINTS_EARNED": "Points totaux gagnés",
  "LEVEL_REACHED": "Niveau atteint",
  "CONNECTION_DATE": "Date de connexion spécifique",
  "CONNECTION_STREAK": "Série de connexions consécutives (Streak)"
}
const achievementFormDefaults = { name: '', description: '' }
const achievementForm = reactive({ ...achievementFormDefaults })
const creatingAchievement = ref(false)
const batchReqTargetId = ref('')
const requirementRows = ref([
  { type: 'CHALLENGE_COMPLETION', challenge_id: '', category_id: '', count: '', target_date: '', badge_id: '', cosmetic_id: '' }
])
const addingBatchRequirements = ref(false)
const batchRewTargetId = ref('')
const rewardRows = ref([
  { type: 'BADGE', reward_id: '', value: '' }
])
const addingBatchRewards = ref(false)
const badges        = ref([])
const loadingBadges = ref(false)
const expandedBadge = ref(null)
const badgeSearch     = ref('')
const badgeFilterType = ref('')
const filteredBadgesTable = computed(() => {
  return badges.value.filter(b => {
    const matchesSearch = !badgeSearch.value.trim() || 
      b.name.toLowerCase().includes(badgeSearch.value.trim().toLowerCase()) || 
      b.description.toLowerCase().includes(badgeSearch.value.trim().toLowerCase())
    const matchesType = !badgeFilterType.value || b.type === badgeFilterType.value
    return matchesSearch && matchesType
  })
})
const TYPE_MAP = {
  CHALLENGE:    'bg-info/15 text-info border border-info/30',
  ACHIEVEMENT:  'bg-primary/15 text-primary border border-primary/30',
  SPECIAL:      'bg-secondary/15 text-secondary border border-secondary/30',
  ADMIN:        'bg-warning/15 text-warning border border-warning/30',
}
const typeClass = t => TYPE_MAP[t] ?? 'bg-base-300 text-base-content/60 border border-base-300'
const createDefaults = { type: 'SPECIAL', name: '', description: '', icon_id: null, icon_url: '' }
const createForm = reactive({ ...createDefaults })
const creating   = ref(false)
const editTarget = ref(null)
const editForm   = reactive({ type: '', name: '', description: '', icon_id: null, icon_url: '' })
const editing    = ref(false)
const assignModalOpen = ref(false)
const targetBadge     = ref(null)
const assignQuery     = ref('')
const assignResults   = ref([])
const assignSearching = ref(false)
const assigning       = ref(false)
const explorerOpen     = ref(false)
const explorerStep     = ref('root')
const explorerCategory = ref(null)
const explorerSubtype  = ref(null)
const explorerIcons    = ref([])
const loadingIcons     = ref(false)
const confirmModal = reactive({ isOpen: false, title: '', message: '', loading: false, onConfirm: null })
const loadingBatchReqs = ref(false)
const batchSelectedAchievementDetails = ref(null)
const TAB_GROUPS = {
  achievement: [
    { id: 'achievement_list', label: 'Liste' },
    { id: 'achievement_requirements', label: 'Prérequis' },
    { id: 'achievement_rewards', label: 'Récompenses' },
  ],
  badges: [
    { id: 'badges_list', label: 'Liste' },
    { id: 'badges_create', label: 'Créer' },
    { id: 'badges_edit', label: 'Modifier', locked: () => !editTarget.value },
  ],
}
const tabGroup = computed(() => {
  if (props.initialTab.startsWith('badges')) return TAB_GROUPS.badges
  return TAB_GROUPS.achievement
})
const activeTab = ref('achievement_list')
const filteredAchievements = computed(() => {
  if (!search.value.trim()) return achievements.value
  const term = search.value.trim().toLowerCase()
  return achievements.value.filter(a => 
    a.name.toLowerCase().includes(term) || a.description.toLowerCase().includes(term)
  )
})
const breadcrumbSubCategory = computed(() => {
  if (activeTab.value.startsWith('badges_')) return 'Succès > Badges'
  return 'Succès > Succès'
})
let assignDebounceTimer = null


function openAssignModal(b) {
  targetBadge.value = b
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
async function toggleUserBadge(user, assign) {
  if (!targetBadge.value) return
  assigning.value = true
  try {
    await axios.post(`/api/admin/badge/${targetBadge.value.id}/assign`, { 
      user_id: user.id,
      assign: assign 
    })
    showToast(`Badge ${assign ? 'attribué à' : 'retiré de'} ${user.username}`)
    await fetchBadges()
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
function onTabChange(tab) {
  activeTab.value = tab
  if (tab === 'achievement_list') fetchAchievements()
  if (['achievement_requirements', 'achievement_rewards', 'achievement_list'].includes(tab)) {
    loadReferences()
  }
  if (tab === 'badges_list') fetchBadges()
}
function getRequirementLabel(type) {
  return requirementTypeLabels[type] ?? type
}
function addRequirementRow() {
  requirementRows.value.push({
    type: 'CHALLENGE_COMPLETION', challenge_id: '', category_id: '', count: '', target_date: '', badge_id: '', cosmetic_id: ''
  })
}
function removeRequirementRow(index) { requirementRows.value.splice(index, 1) }
function addRewardRow() { rewardRows.value.push({ type: 'BADGE', reward_id: '', value: '' }) }
function removeRewardRow(index) { rewardRows.value.splice(index, 1) }
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
    } catch (e) {} finally { confirmModal.loading = false }
  } else { closeConfirmDialog() }
}
function closeConfirmDialog() {
  confirmModal.isOpen = false
  confirmModal.loading = false
  confirmModal.onConfirm = null
}
async function fetchAchievements() {
  loadingAchievements.value = true
  try {
    const res = await axios.get('/api/admin/achievement/list')
    achievements.value = res.data?.achievements ?? res.data?.message ?? []
  } catch { achievements.value = [] } finally { loadingAchievements.value = false }
}
async function loadReferences() {
  try {
    const [cr, catr, br, cosr] = await Promise.all([
      axios.get('/api/admin/challenge/list').catch(() => ({ data: [] })),
      axios.get('/api/admin/challenge/category/list').catch(() => ({ data: [] })),
      axios.get('/api/admin/badge/list').catch(() => ({ data: [] })),
      axios.get('/api/admin/cosmetic/list').catch(() => ({ data: [] }))
    ])
    allChallenges.value = cr.data?.challenges ?? cr.data?.data ?? (Array.isArray(cr.data) ? cr.data : [])
    allCategories.value = catr.data?.categories ?? catr.data?.data ?? (Array.isArray(catr.data) ? catr.data : [])
    allBadges.value = br.data?.badges ?? br.data?.data ?? (Array.isArray(br.data) ? br.data : [])
    allCosmetics.value = cosr.data?.cosmetics ?? cosr.data?.data ?? (Array.isArray(cosr.data) ? cosr.data : [])
  } catch (e) {
    console.error("Erreur chargement références", e)
  }
}
async function openDetailsPanel(achId, panelType) {
  try {
    const res = await axios.get(`/api/admin/achievement/${achId}/info`)
    selectedAchievement.value = res.data?.message ?? res.data?.data ?? null
    if (panelType === 'requirements') requirementsPanelOpen.value = true
    if (panelType === 'rewards') rewardsPanelOpen.value = true
    if (panelType === 'users') usersPanelOpen.value = true
  } catch {
    showToast('Erreur lors du chargement des détails', 'error')
  }
}
async function deleteAchievement(id, name) {
  triggerConfirm('Supprimer l\'achievement', `Voulez-vous vraiment supprimer l'achievement "${name}" ?`, async () => {
    try {
      await axios.post(`/api/admin/achievement/${id}/delete`)
      showToast(`Achievement "${name}" supprimé`)
      await fetchAchievements()
    } catch (e) {
      showToast(e.response?.data?.message ?? 'Erreur lors de la suppression', 'error')
      throw e
    }
  })
}
async function deleteRequirement(reqId, achId) {
  triggerConfirm('Supprimer le prérequis', 'Voulez-vous vraiment supprimer ce prérequis ?', async () => {
    try {
      await axios.post(`/api/admin/achievement/requirement/${reqId}/delete`)
      showToast('Prérequis supprimé')
      const res = await axios.get(`/api/admin/achievement/${achId}/info`)
      selectedAchievement.value = res.data?.message ?? res.data?.data ?? null
    } catch (e) { showToast(e.response?.data?.message ?? 'Erreur', 'error'); throw e }
  })
}
async function deleteReward(rewardId, achId) {
  triggerConfirm('Supprimer la récompense', 'Voulez-vous vraiment supprimer cette récompense ?', async () => {
    try {
      await axios.post(`/api/admin/achievement/reward/${rewardId}/delete`)
      showToast('Récompense supprimée')
      const res = await axios.get(`/api/admin/achievement/${achId}/info`)
      selectedAchievement.value = res.data?.message ?? res.data?.data ?? null
    } catch (e) { showToast(e.response?.data?.message ?? 'Erreur', 'error'); throw e }
  })
}
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
function toggleBadge(id) { expandedBadge.value = expandedBadge.value === id ? null : id }
async function deleteBadge(id, name) {
  triggerConfirm('Supprimer le badge', `Supprimer le badge "${name}" ? Action irréversible.`, async () => {
    try {
      await axios.post(`/api/admin/badge/${id}/delete`)
      showToast(`Badge "${name}" supprimé`)
      if (expandedBadge.value === id) expandedBadge.value = null
      await fetchBadges()
    } catch (e) {
      showToast(e.response?.data?.message ?? 'Erreur suppression', 'error')
      throw e
    }
  })
}
async function submitCreate() {
  if (!createForm.name || !createForm.description) {
    showToast('Le nom et la description sont requis', 'error'); return
  }
  if (!createForm.icon_id) {
    showToast('Veuillez sélectionner une icône depuis l\'explorateur', 'error'); return
  }
  creating.value = true
  try {
    await axios.post('/api/admin/badge/create', {
      type: createForm.type, 
      name: createForm.name, 
      description: createForm.description,
      icon_id: createForm.icon_id
    })

    await fetchBadges()
    showToast(`Badge "${createForm.name}" créé !`)
    Object.assign(createForm, { ...createDefaults })
    activeTab.value = 'badges_list'
  } catch (e) {
    showToast(e.response?.data?.message ?? 'Erreur création', 'error')
  } finally { creating.value = false }
}
function openEdit(b) {
  editTarget.value = b.id
  activeTab.value = 'badges_edit'
  Object.assign(editForm, {
    type: b.type ?? 'SPECIAL', 
    name: b.name ?? '', 
    description: b.description ?? '',
    icon_id: b.icon_id ?? null,
    icon_url: b.icon_url ?? '',
  })
}
async function submitEdit() {
  if (!editForm.name || !editForm.description) {
    showToast('Le nom et la description sont requis', 'error'); return
  }
  editing.value = true
  try {
    const payload = {
      new_name: editForm.name, 
      new_description: editForm.description, 
      new_type: editForm.type,
    }
    if (editForm.icon_id) {
      payload.new_icon_id = editForm.icon_id
    }
    await axios.post(`/api/admin/badge/${editTarget.value}/modify`, payload)
    showToast('Badge modifié !')
    activeTab.value = 'badges_list'
    editTarget.value = null
    await fetchBadges()
  } catch (e) {
    showToast(e.response?.data?.message ?? 'Erreur modification', 'error')
  } finally { editing.value = false }
}
function exportTableToCsv(type) {
  if (!selectedAchievement.value) return
  exportingCsv.value = true
  try {
    let headers = []
    let rows = []
    let filenamePrefix = ''
    const escape = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`
    if (type === 'requirements') {
      headers = ['ID', 'Type', 'Challenge ID', 'Category ID', 'Badge ID', 'Cosmetic ID', 'Count', 'Target Date']
      rows = (selectedAchievement.value.requirements || []).map(r => [
        r.id, r.type, r.challenge_id ?? '', r.category_id ?? '', r.badge_id ?? '', r.cosmetic_id ?? '', r.count ?? '', r.target_date ?? ''
      ].map(escape).join(','))
      filenamePrefix = 'requirements'
    } else if (type === 'rewards') {
      headers = ['ID', 'Type', 'Reward ID', 'Value']
      rows = (selectedAchievement.value.rewards || []).map(w => [
        w.id, w.type, w.reward_id ?? '', w.value ?? ''
      ].map(escape).join(','))
      filenamePrefix = 'rewards'
    } else if (type === 'users') {
      headers = ['ID', 'User ID', 'Username', 'Unlocked At', 'Is Read', 'Reward Claimed']
      rows = (selectedAchievement.value.users || []).map(u => [
        u.id, u.user_id, u.username ?? '', u.unlocked_at ?? '', u.is_read ? 'Oui' : 'Non', u.reward_claimed ? 'Oui' : 'Non'
      ].map(escape).join(','))
      filenamePrefix = 'users'
    }
    if (!rows.length) { showToast("Aucune donnée à exporter", 'error'); return }
    const csv = [headers.join(','), ...rows].join('\n')
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const now = new Date()
    const pad = (n) => String(n).padStart(2, '0')
    const dateStr = `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}_${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`
    const safeName = (selectedAchievement.value.name || 'achievement').trim().replace(/\s+/g, '-').replace(/[^a-zA-Z0-9_-]/g, '')
    const filename = `${safeName}_${filenamePrefix}_${dateStr}.csv`
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    showToast("Impossible d'exporter le fichier CSV", 'error')
  } finally { exportingCsv.value = false }
}
function openCreateAchievementModal() {
  Object.assign(achievementForm, { ...achievementFormDefaults })
  achievementModal.isOpen = true
}
async function submitCreateAchievement() {
  if (!achievementForm.name.trim() || !achievementForm.description.trim()) {
    showToast('Le nom et la description sont requis', 'error')
    return
  }
  creatingAchievement.value = true
  try {
    await axios.post('/api/admin/achievement/create', {
      name: achievementForm.name.trim(), description: achievementForm.description.trim()
    })
    showToast('Achievement créé avec succès !')
    achievementModal.isOpen = false
    Object.assign(achievementForm, { ...achievementFormDefaults })
    await fetchAchievements()
  } catch (e) {
    showToast(e.response?.data?.message ?? 'Erreur lors de la création', 'error')
  } finally { creatingAchievement.value = false }
}
async function submitBatchRequirements() {
  if (!batchReqTargetId.value) { showToast('Veuillez sélectionner un succès cible', 'error'); return }
  addingBatchRequirements.value = true
  try {
    const payload = requirementRows.value.map(row => {
      let data = { type: row.type }
      if (['CHALLENGE_COMPLETION', 'CHALLENGE_COMPLETION_COUNT'].includes(row.type)) data.challenge_id = Number(row.challenge_id)
      if (['CATEGORY_COMPLETION', 'CATEGORY_COMPLETION_COUNT'].includes(row.type)) data.category_id = Number(row.category_id)
      if (['COSMETIC_OWNERSHIP', 'COSMETIC_OWNERSHIP_COUNT'].includes(row.type)) data.cosmetic_id = Number(row.cosmetic_id)
      if (['BADGE_OWNERSHIP', 'BADGE_OWNERSHIP_COUNT'].includes(row.type)) data.badge_id = Number(row.badge_id)
      if (['CHALLENGE_COMPLETION_COUNT', 'CATEGORY_COMPLETION_COUNT', 'COSMETIC_OWNERSHIP_COUNT', 'BADGE_OWNERSHIP_COUNT', 'POINTS_EARNED', 'LEVEL_REACHED', 'CONNECTION_STREAK'].includes(row.type)) {
        data.count = Number(row.count)
      }
      if (row.type === 'CONNECTION_DATE') data.target_date = row.target_date
      return data
    })
    await axios.post(`/api/admin/achievement/${batchReqTargetId.value}/requirements/add`, { requirements: payload })
    showToast('Prérequis ajoutés en masse avec succès !')
    requirementRows.value = [{ type: 'CHALLENGE_COMPLETION', challenge_id: '', category_id: '', count: '', target_date: '', badge_id: '', cosmetic_id: '' }]
    batchReqTargetId.value = ''
    activeTab.value = 'achievement_list'
  } catch (e) {
    showToast(e.response?.data?.message ?? 'Erreur lors de l\'ajout groupé', 'error')
  } finally { addingBatchRequirements.value = false }
}
async function submitBatchRewards() {
  if (!batchRewTargetId.value) { showToast('Veuillez sélectionner un succès cible', 'error'); return }
  addingBatchRewards.value = true
  try {
    const payload = rewardRows.value.map(row => {
      let data = { type: row.type }
      if (['POINTS', 'XP'].includes(row.type)) {
        data.value = Number(row.value)
      } else {
        data.reward_id = Number(row.reward_id)
      }
      return data
    })
    await axios.post(`/api/admin/achievement/${batchRewTargetId.value}/reward/add`, { rewards: payload })
    showToast('Récompenses ajoutées en masse avec succès !')
    rewardRows.value = [{ type: 'BADGE', reward_id: '', value: '' }]
    batchRewTargetId.value = ''
    activeTab.value = 'achievement_list'
  } catch (e) {
    showToast(e.response?.data?.message ?? 'Erreur lors de l\'ajout groupé', 'error')
  } finally { addingBatchRewards.value = false }
}
function setSort(key) {
  if (sortKey.value === key) { sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc' } 
  else { sortKey.value = key; sortDir.value = 'asc' }
  achievements.value.sort((a, b) => {
    let mod = sortDir.value === 'asc' ? 1 : -1
    return a[sortKey.value] > b[sortKey.value] ? mod : -1 * mod
  })
}
watch(
  () => props.initialTab,
  async (newTab) => {
    activeTab.value = newTab
    if (newTab.startsWith('badges')) {
      await fetchBadges()
    } else {
      await fetchAchievements()
      await loadReferences()
    }
  },
  { immediate: true }
)
watch(batchReqTargetId, async (newId) => {
  if (!newId) {
    batchSelectedAchievementDetails.value = null
    return
  }
  loadingBatchReqs.value = true
  try {
    const res = await axios.get(`/api/admin/achievement/${newId}/info`)
    batchSelectedAchievementDetails.value = res.data?.message ?? res.data?.data ?? res.data
  } catch {
    batchSelectedAchievementDetails.value = null
  } finally {
    loadingBatchReqs.value = false
  }
})
async function deleteBatchReward(rewardId) {
  triggerConfirm('Supprimer la récompense', 'Voulez-vous vraiment supprimer cette récompense ?', async () => {
    try {
      await axios.post(`/api/admin/achievement/reward/${rewardId}/delete`)
      showToast('Récompense supprimée')
      if (batchRewTargetId.value) {
        const res = await axios.get(`/api/admin/achievement/${batchRewTargetId.value}/info`)
        batchSelectedRewardAchievementDetails.value = res.data?.message ?? res.data?.data ?? res.data
        await fetchAchievements()
      }
    } catch (e) {
      showToast(e.response?.data?.message ?? 'Erreur', 'error')
      throw e
    }
  })
}
function formatRequirementDetails(req) {
  if (['CHALLENGE_COMPLETION'].includes(req.type)) {
    const chall = allChallenges.value.find(c => c.id === req.challenge_id)
    return chall ? `Challenge : ${chall.name}` : `Challenge ID #${req.challenge_id}`
  }
  if (['CATEGORY_COMPLETION', 'CATEGORY_COMPLETION_COUNT'].includes(req.type)) {
    const cat = allCategories.value.find(c => c.id === req.category_id)
    const catName = cat ? cat.name : `ID #${req.category_id}`
    return req.type === 'CATEGORY_COMPLETION_COUNT' 
      ? `Catégorie : ${catName} (${req.count} requis)` 
      : `Catégorie : ${catName}`
  }
  if (['BADGE_OWNERSHIP'].includes(req.type)) {
    const badge = allBadges.value.find(b => b.id === req.badge_id)
    return badge ? `Badge : ${badge.name}` : `Badge ID #${req.badge_id}`
  }
  if (['COSMETIC_OWNERSHIP'].includes(req.type)) {
    const cos = allCosmetics.value.find(c => c.id === req.cosmetic_id)
    return cos ? `Cosmétique : ${cos.name}` : `Cosmétique ID #${req.cosmetic_id}`
  }
  if (['CHALLENGE_COMPLETION_COUNT', 'COSMETIC_OWNERSHIP_COUNT', 'BADGE_OWNERSHIP_COUNT', 'POINTS_EARNED', 'LEVEL_REACHED', 'CONNECTION_STREAK'].includes(req.type)) {
    return `Valeur / Quantité : ${req.count}`
  }
  if (['CONNECTION_DATE'].includes(req.type)) {
    return `Date : ${req.target_date ?? '—'}`
  }
  return '—'
}
function formatRewardDetails(rew) {
  if (rew.type === 'BADGE') {
    const badge = allBadges.value.find(b => b.id === rew.reward_id)
    return badge ? `Badge : ${badge.name}` : `Badge ID #${rew.reward_id}`
  }
  if (rew.type === 'COSMETIC') {
    const cos = allCosmetics.value.find(c => c.id === rew.reward_id)
    return cos ? `Cosmétique : ${cos.name}` : `Cosmétique ID #${rew.reward_id}`
  }
  if (['POINTS', 'XP'].includes(rew.type)) {
    return `Valeur : ${rew.value} ${rew.type}`
  }
  return '—'
}
async function deleteBatchRequirement(reqId) {
  triggerConfirm('Supprimer le prérequis', 'Voulez-vous vraiment supprimer ce prérequis ?', async () => {
    try {
      await axios.post(`/api/admin/achievement/requirement/${reqId}/delete`)
      showToast('Prérequis supprimé')
      if (batchReqTargetId.value) {
        const res = await axios.get(`/api/admin/achievement/${batchReqTargetId.value}/info`)
        batchSelectedAchievementDetails.value = res.data?.message ?? res.data?.data ?? res.data
        await fetchAchievements()
      }
    } catch (e) {
      showToast(e.response?.data?.message ?? 'Erreur', 'error')
      throw e
    }
  })
}

watch(batchRewTargetId, async (newId) => {
  if (!newId) {
    batchSelectedRewardAchievementDetails.value = null
    return
  }
  loadingBatchRewardsList.value = true
  try {
    const res = await axios.get(`/api/admin/achievement/${newId}/info`)
    batchSelectedRewardAchievementDetails.value = res.data?.message ?? res.data?.data ?? res.data
  } catch {
    batchSelectedRewardAchievementDetails.value = null
  } finally {
    loadingBatchRewardsList.value = false
  }
})
</script>

<template>
  <div class="flex flex-col h-full">
    <div class="flex items-center justify-between mb-6">
      <div>
        <p class="font-code text-[10px] tracking-[0.18em] uppercase text-base-content/40 mb-1">Admin > {{ breadcrumbSubCategory }}</p>
        <h1 class="font-titre font-bold text-2xl text-base-content leading-none">{{activeTab.startsWith('badges') ? 'Badges' : 'Succès' }}</h1>
      </div>
      <span v-if="activeTab === 'achievement_list'" class="font-code text-sm text-base-content/50 border border-secondary px-2 py-1">{{ achievements.length }} SUCCÈS</span>
      <span v-if="activeTab === 'badges_list'" class="font-code text-sm text-base-content/50 border border-secondary px-2 py-1">{{ badges.length }} BADGE{{ badges.length > 1 ? 'S' : '' }}</span>
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
    <div v-if="activeTab === 'achievement_list'" class="flex flex-col gap-4">
      <div class="flex items-center gap-2">
        <button @click="openCreateAchievementModal" class="bg-primary text-base-100 hover:bg-primary/80 px-4 py-2 font-code text-xs font-bold transition-colors">
          <span>+ Créer un nouveau succès</span>
        </button>
      </div>
      <div class="flex items-center gap-2 flex-wrap mb-2">
        <div class="relative flex-1 min-w-48">
          <span class="absolute left-3 top-1/2 -translate-y-1/2 font-code text-base-content/30 text-xs">⌕</span>
          <input v-model="search" type="text" placeholder="Rechercher un succès..." 
          class="w-full bg-base-100 border border-base-300 focus:border-primary outline-none pl-7 pr-3 py-2 font-code text-xs text-base-content placeholder:text-base-content/25 transition-colors" />
        </div>
      </div>
      <div class="border border-base-300 overflow-hidden flex flex-col" style="max-height: calc(100vh - 220px);">
        <div class="grid grid-cols-[1fr_2.5fr_1fr_1fr_1fr_120px] bg-base-200 border-b border-base-300 shrink-0">
          <button v-for="col in [{ key: 'name', label: 'Nom' }, { key: 'description', label: 'Description' }, { key: 'requirement_count', label: 'Prérequis' }, { key: 'reward_count', label: 'Récompenses' }, { key: 'users_count', label: 'Validé par' }]" :key="col.key" @click="setSort(col.key)" class="flex items-center gap-1 px-4 py-2.5 font-code text-[10px] uppercase text-base-content/40 hover:text-base-content">
            {{ col.label }} <span v-if="sortKey === col.key" class="text-primary">{{ sortDir === 'asc' ? '↑' : '↓' }}</span>
          </button>
          <div class="px-4 py-2.5 font-code text-[10px] uppercase text-base-content/40 text-right">Actions</div>
        </div>
        <div class="flex-1 overflow-y-auto">
          <div v-if="loadingAchievements" class="flex justify-center py-16"><span class="loading loading-spinner text-primary"></span></div>
          <div v-else-if="!filteredAchievements.length" class="flex justify-center py-10"><span class="font-code text-xs text-base-content/25">Aucun succès</span></div>
          <div v-else class="flex flex-col">
            <template v-for="ach in filteredAchievements" :key="ach.id">
              <div class="grid grid-cols-[1fr_2.5fr_1fr_1fr_1fr_120px] items-center border-b border-base-300/50 hover:bg-base-300/30 transition-colors">
                <div class="px-4 py-3 font-code text-xs font-medium truncate">#{{ ach.id }} - {{ ach.name }}</div>
                <div class="px-4 py-3 font-code text-xs text-base-content/70 truncate">{{ ach.description }}</div>
                <div class="px-4 py-3 font-code text-xs">
                  <button @click="openDetailsPanel(ach.id, 'requirements')" class="text-primary hover:underline font-bold">{{ ach.requirement_count ?? 0 }} prérequis</button>
                </div>
                <div class="px-4 py-3 font-code text-xs">
                  <button @click="openDetailsPanel(ach.id, 'rewards')" class="text-primary hover:underline font-bold">{{ ach.reward_count ?? 0 }} récompense{{ ach.reward_count > 1 ? 's' : '' }}</button>
                </div>
                <div class="px-4 py-3 font-code text-xs">
                  <button @click="openDetailsPanel(ach.id, 'users')" class="text-primary hover:underline font-bold">{{ ach.users_count ?? 0 }} utilisateur{{ ach.users_count > 1 ? 's' : '' }}</button>
                </div>
                <div class="px-4 py-3 flex justify-end">
                  <button class="text-xs text-error hover:text-error/70" @click="deleteAchievement(ach.id, ach.name)">Supprimer</button>
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>
    <div v-if="activeTab === 'achievement_requirements'" class="max-w-4xl border border-base-300 bg-base-200/40 p-6 flex flex-col gap-4">
      <h2 class="font-titre font-bold text-lg">Ajouter des prérequis</h2>
      <div class="flex flex-col gap-1">
        <label class="font-code text-[10px] uppercase text-base-content/50">Sélectionner le succès cible *</label>
        <select v-model="batchReqTargetId" class="bg-base-100 border border-base-300 px-3 py-2 font-code text-sm outline-none">
          <option value="">-- Choisir un succès --</option>
          <option v-for="ach in achievements" :key="ach.id" :value="ach.id">#{{ ach.id }} - {{ ach.name }}</option>
        </select>
      </div>
      <div v-if="batchReqTargetId" class="flex flex-col gap-2 bg-base-100 border border-base-300 p-4">
        <p class="font-code text-[10px] uppercase tracking-widest text-primary font-bold">Prérequis actuels du succès</p>
        <div v-if="loadingBatchReqs" class="py-2 text-xs font-code text-base-content/40">Chargement...</div>
        <div v-else-if="!batchSelectedAchievementDetails?.requirements?.length" class="text-xs font-code text-base-content/40">Aucun prérequis enregistré pour le moment.</div>
        <div v-else class="flex flex-col gap-1.5 max-h-48 overflow-y-auto">
          <div v-for="req in batchSelectedAchievementDetails.requirements" :key="req.id" class="flex items-center justify-between bg-base-200/60 border border-base-300 px-3 py-2 font-code text-xs">
            <div class="flex flex-col gap-0.5">
              <span class="font-bold text-base-content">{{ getRequirementLabel(req.type) }}</span>
              <span class="text-base-content/60 text-[11px]">{{ formatRequirementDetails(req) }}</span>
            </div>
            <button @click="deleteBatchRequirement(req.id)" class="text-error hover:text-error/70 font-bold px-2 py-0.5 text-sm" title="Supprimer">×</button>
          </div>
        </div>
      </div>
      <div class="flex flex-col gap-3 mt-4">
        <div v-for="(row, index) in requirementRows" :key="index" class="flex items-center gap-2 bg-base-100 border border-base-300 p-3">
          <select v-model="row.type" class="bg-base-200 border border-base-300 px-2 py-1.5 font-code text-xs outline-none">
            <option value="CHALLENGE_COMPLETION">Complétion d'un challenge spécifique</option>
            <option value="CHALLENGE_COMPLETION_COUNT">Nombre de challenges validés</option>
            <option value="CATEGORY_COMPLETION">Complétion d'une catégorie</option>
            <option value="CATEGORY_COMPLETION_COUNT">Nombre de challenges d'une catégorie</option>
            <option value="COSMETIC_OWNERSHIP">Possession d'un cosmétique</option>
            <option value="COSMETIC_OWNERSHIP_COUNT">Nombre de cosmétiques possédés</option>
            <option value="BADGE_OWNERSHIP">Possession d'un badge</option>
            <option value="BADGE_OWNERSHIP_COUNT">Nombre de badges possédés</option>
            <option value="POINTS_EARNED">Score global</option>
            <option value="LEVEL_REACHED">Niveau atteint</option>
            <option value="CONNECTION_DATE">Date de connexion spécifique</option>
            <option value="CONNECTION_STREAK">Série de connexions consécutives (Streak)</option>
          </select>
          <select v-if="['CHALLENGE_COMPLETION'].includes(row.type)" v-model="row.challenge_id" class="bg-base-200 border border-base-300 px-2 py-1.5 font-code text-xs outline-none flex-1">
            <option value="">-- Challenge --</option>
            <option v-for="c in allChallenges" :key="c.id" :value="c.id">{{ c.name }} - {{ c.category }}</option>
          </select>
          <select v-if="['CATEGORY_COMPLETION', 'CATEGORY_COMPLETION_COUNT'].includes(row.type)" v-model="row.category_id" class="bg-base-200 border border-base-300 px-2 py-1.5 font-code text-xs outline-none flex-1">
            <option value="">-- Catégorie --</option>
            <option v-for="cat in allCategories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
          </select>
          <select v-if="['BADGE_OWNERSHIP'].includes(row.type)" v-model="row.badge_id" class="bg-base-200 border border-base-300 px-2 py-1.5 font-code text-xs outline-none flex-1">
            <option value="">-- Badge --</option>
            <option v-for="b in allBadges" :key="b.id" :value="b.id">{{ b.name }}</option>
          </select>
          <select v-if="['COSMETIC_OWNERSHIP'].includes(row.type)" v-model="row.cosmetic_id" class="bg-base-200 border border-base-300 px-2 py-1.5 font-code text-xs outline-none flex-1">
            <option value="">-- Cosmétique --</option>
            <option v-for="cos in allCosmetics" :key="cos.id" :value="cos.id">{{ cos.name }}</option>
          </select>
          <input v-if="['CHALLENGE_COMPLETION_COUNT', 'CATEGORY_COMPLETION_COUNT', 'COSMETIC_OWNERSHIP_COUNT', 'BADGE_OWNERSHIP_COUNT', 'POINTS_EARNED', 'LEVEL_REACHED', 'CONNECTION_STREAK'].includes(row.type)" v-model="row.count" type="number" placeholder="Quantité" class="bg-base-200 border border-base-300 px-2 py-1.5 font-code text-xs outline-none w-28" />
          <input v-if="row.type === 'CONNECTION_DATE'" v-model="row.target_date" type="datetime-local" class="bg-base-200 border border-base-300 px-2 py-1.5 font-code text-xs outline-none" />
          <button @click="removeRequirementRow(index)" v-if="requirementRows.length > 1" class="text-error font-bold px-2">×</button>
        </div>
      </div>
      <div class="flex items-center justify-between mt-2">
        <button @click="addRequirementRow" class="bg-secondary/20 text-secondary border border-secondary px-3 py-1.5 font-code text-xs">+ Ajouter un prérequis</button>
        <button @click="submitBatchRequirements" :disabled="addingBatchRequirements" class="bg-primary text-base-100 px-5 py-2 font-code text-xs font-bold">Valider</button>
      </div>
    </div>
    <div v-if="activeTab === 'achievement_rewards'" class="max-w-4xl border border-base-300 bg-base-200/40 p-6 flex flex-col gap-4">
      <h2 class="font-titre font-bold text-lg">Ajouter des récompenses</h2>
      
      <div class="flex flex-col gap-1">
        <label class="font-code text-[10px] uppercase text-base-content/50">Sélectionner le succès cible *</label>
        <select v-model="batchRewTargetId" class="bg-base-100 border border-base-300 px-3 py-2 font-code text-sm outline-none">
          <option value="">-- Choisir un succès --</option>
          <option v-for="ach in achievements" :key="ach.id" :value="ach.id">#{{ ach.id }} - {{ ach.name }}</option>
        </select>
      </div>
      <div v-if="batchRewTargetId" class="flex flex-col gap-2 bg-base-100 border border-base-300 p-4">
        <p class="font-code text-[10px] uppercase tracking-widest text-primary font-bold">Récompenses actuelles du succès</p>
        <div v-if="loadingBatchRewardsList" class="py-2 text-xs font-code text-base-content/40">Chargement...</div>
        <div v-else-if="!batchSelectedRewardAchievementDetails?.rewards?.length" class="text-xs font-code text-base-content/40">Aucune récompense enregistrée pour le moment.</div>
        <div v-else class="flex flex-col gap-1.5 max-h-48 overflow-y-auto">
          <div v-for="rew in batchSelectedRewardAchievementDetails.rewards" :key="rew.id" class="flex items-center justify-between bg-base-200/60 border border-base-300 px-3 py-2 font-code text-xs">
            <div class="flex flex-col gap-0.5">
              <span class="font-bold text-base-content">{{ rew.type }}</span>
              <span class="text-base-content/60 text-[11px]">{{ formatRewardDetails(rew) }}</span>
            </div>
            <button @click="deleteBatchReward(rew.id)" class="text-error hover:text-error/70 font-bold px-2 py-0.5 text-sm" title="Supprimer">×</button>
          </div>
        </div>
      </div>
      <div class="flex flex-col gap-3 mt-4">
        <div v-for="(row, index) in rewardRows" :key="index" class="flex items-center gap-2 bg-base-100 border border-base-300 p-3">
          <select v-model="row.type" class="bg-base-200 border border-base-300 px-2 py-1.5 font-code text-xs outline-none">
            <option value="BADGE">BADGE</option>
            <option value="COSMETIC">COSMETIC</option>
            <option value="POINTS">POINTS</option>
            <option value="XP">XP</option>
          </select>
          <select v-if="row.type === 'BADGE'" v-model="row.reward_id" class="bg-base-200 border border-base-300 px-2 py-1.5 font-code text-xs outline-none flex-1">
            <option value="">-- Choisir un badge --</option>
            <option v-for="b in allBadges" :key="b.id" :value="b.id">{{ b.name }}</option>
          </select>
          <select v-if="row.type === 'COSMETIC'" v-model="row.reward_id" class="bg-base-200 border border-base-300 px-2 py-1.5 font-code text-xs outline-none flex-1">
            <option value="">-- Choisir un cosmétique --</option>
            <option v-for="cos in allCosmetics" :key="cos.id" :value="cos.id">{{ cos.name }}</option>
          </select>
          <input v-if="['POINTS', 'XP'].includes(row.type)" v-model="row.value" type="number" placeholder="Valeur (ex: 500)" class="bg-base-200 border border-base-300 px-2 py-1.5 font-code text-xs outline-none flex-1" />
          <button @click="removeRewardRow(index)" v-if="rewardRows.length > 1" class="text-error font-bold px-2">×</button>
        </div>
      </div>
      <div class="flex items-center justify-between mt-2">
        <button @click="addRewardRow" class="bg-secondary/20 text-secondary border border-secondary px-3 py-1.5 font-code text-xs">+ Ajouter une récompense</button>
        <button @click="submitBatchRewards" :disabled="addingBatchRewards" class="bg-primary text-base-100 px-5 py-2 font-code text-xs font-bold">Valider</button>
      </div>
    </div>
    <div v-if="activeTab === 'badges_list'" class="flex flex-col gap-4">
      <div class="flex items-center justify-between gap-2 flex-wrap">
        <button @click="activeTab = 'badges_create'" class="bg-primary text-base-100 hover:bg-primary/80 px-4 py-2 font-code text-xs font-bold transition-colors shadow-sm">
          <span>+ Créer un nouveau badge</span>
        </button>
      </div>
      <div class="flex items-center gap-2 flex-wrap mb-2">
        <div class="relative flex-1 min-w-48">
          <span class="absolute left-3 top-1/2 -translate-y-1/2 font-code text-base-content/30 text-xs select-none">⌕</span>
          <input
            v-model="badgeSearch"
            type="text"
            placeholder="Rechercher un badge..."
            class="w-full bg-base-100 border border-base-300 focus:border-primary outline-none pl-7 pr-3 py-2 font-code text-xs text-base-content placeholder:text-base-content/25 transition-colors"
          />
        </div>
        <select
          v-model="badgeFilterType"
          class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-xs text-base-content transition-colors"
        >
          <option value="">Tous les types</option>
          <option value="CHALLENGE">Challenge</option>
          <option value="ACHIEVEMENT">Succès</option>
          <option value="SPECIAL">Special</option>
          <option value="ADMIN">Admin</option>
        </select>
      </div>
      <div class="border border-base-300 overflow-hidden flex flex-col" style="max-height: calc(100vh - 220px);">
        <div class="grid grid-cols-[1fr_2.5fr_1.5fr_1.5fr_120px] bg-base-200 border-b border-base-300 shrink-0">
          <div class="px-4 py-2.5 font-code text-[10px] uppercase tracking-widest text-base-content/40">Aperçu</div>
          <div class="px-4 py-2.5 font-code text-[10px] uppercase tracking-widest text-base-content/40">Nom</div>
          <div class="px-4 py-2.5 font-code text-[10px] uppercase tracking-widest text-base-content/40">Type</div>
          <div class="px-4 py-2.5 font-code text-[10px] uppercase tracking-widest text-base-content/40">Description</div>
          <div class="px-4 py-2.5 font-code text-[10px] uppercase tracking-widest text-base-content/40 text-right">Actions</div>
        </div>
        <div class="flex-1 overflow-y-auto">
          <div v-if="loadingBadges" class="flex justify-center py-16"><span class="loading loading-spinner text-primary"></span></div>
          <div v-else-if="!filteredBadgesTable.length" class="flex justify-center py-10"><span class="font-code text-xs text-base-content/25">Aucun badge trouvé</span></div>
          <div v-else class="flex flex-col">
            <template v-for="b in filteredBadgesTable" :key="b.id">
              <div @click="toggleBadge(b.id)" :class="['grid grid-cols-[1fr_2.5fr_1.5fr_1.5fr_120px] items-center border-b border-base-300/50 cursor-pointer transition-colors duration-100', expandedBadge === b.id ? 'bg-primary/8 border-l-2 border-l-primary' : 'hover:bg-base-300/30']">
                <div class="px-4 py-2">
                  <div class="w-8 h-8 bg-base-100 border border-base-300 flex items-center justify-center overflow-hidden">
                    <img v-if="b.icon_url" :src="getAssetUrl(b.icon_url)" class="w-full h-full object-contain" @error="$event.target.style.display='none'" />
                    <span v-else class="text-xs opacity-20">🏅</span>
                  </div>
                </div>
                <div class="px-4 py-3 font-code text-xs font-medium truncate">#{{ b.id }} - {{ b.name }}</div>
                <div class="px-4 py-3 font-code text-xs"><span :class="['px-2 py-0.5 text-[10px]', typeClass(b.type)]">{{ b.type }}</span></div>
                <div class="px-4 py-3 font-code text-xs text-base-content/70 truncate">{{ b.description || '—' }}</div>
                <div class="px-4 py-3 flex justify-end gap-1.5" @click.stop>
                  <button class="font-text text-xs text-info hover:text-info/70 px-1" @click="openEdit(b)" title="Modifier">Modifier</button>
                  <button class="font-text text-xs text-error hover:text-error/70 px-1" @click="deleteBadge(b.id, b.name)" title="Supprimer">Supprimer</button>
                </div>
              </div>
              <div v-if="expandedBadge === b.id" class="border-b border-base-300 bg-base-300/50 p-6" @click.stop>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 items-start">
                  <div class="flex flex-col gap-4">
                    <div class="flex items-center gap-4">
                      <div class="w-16 h-16 bg-base-100 border border-base-300 flex items-center justify-center overflow-hidden shrink-0">
                        <img v-if="b.icon_url" :src="getAssetUrl(b.icon_url)" class="max-w-full max-h-full object-contain" @error="$event.target.style.display='none'" />
                        <span v-else class="text-xl opacity-20">🏅</span>
                      </div>
                      <div>
                        <p class="font-code text-xs text-base-content/40">#{{ b.id }}</p>
                        <h3 class="font-titre font-bold text-base text-base-content">{{ b.name }}</h3>
                        <span :class="['inline-block mt-1 px-2 py-0.5 text-[10px] font-code uppercase', typeClass(b.type)]">{{ b.type }}</span>
                      </div>
                    </div>
                    <dl class="grid grid-cols-2 gap-2 text-xs font-code bg-base-100/40 p-3 border border-base-300">
                      <dt class="text-base-content/40">Créateur</dt><dd class="text-base-content font-medium text-right">{{ b.created_by ?? '—' }}</dd>
                    </dl>
                  </div>
                  <div class="flex flex-col gap-4">
                    <p class="font-code text-[10px] tracking-widest uppercase text-primary/70">Statistiques</p>
                    <div class="bg-base-100/60 border border-base-300 p-3 text-center">
                      <p class="font-titre font-bold text-primary text-xl leading-none">{{ b.user_count ?? 0 }}</p>
                      <p class="font-code text-[9px] uppercase tracking-widest text-base-content/40 mt-1">Utilisateur{{ b.user_count > 1 ? 's' : '' }} posséde{{ b.user_count > 1 ? 'nt' : '' }} ce badge</p>
                    </div>
                    <div>
                      <p class="font-code text-[10px] tracking-widest uppercase text-base-content/40 mb-1">Description</p>
                      <p class="text-xs text-base-content/70 bg-base-200/60 border border-base-300 p-3 leading-relaxed">{{ b.description || 'Aucune description.' }}</p>
                    </div>
                  </div>
                  <div class="flex flex-col justify-between h-full bg-base-100/30 p-4 border border-base-300">
                    <div>
                      <p class="font-code text-[10px] tracking-widest uppercase text-primary/70 mb-2">Gestion des attributions</p>
                      <p class="text-xs text-base-content/60 mb-4">Attribuez ou retirez manuellement ce badge à des utilisateurs via une fenêtre dédiée.</p>
                    </div>
                    <button
                      @click="openAssignModal(b)"
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
    <div v-if="activeTab === 'badges_create'" class="w-full">
      <div class="grid grid-cols-1 xl:grid-cols-2 gap-8 items-start">
        <div class="border border-base-300 bg-base-200/40 p-6">
          <p class="font-code text-[10px] tracking-widest uppercase text-base-content/35 mb-1">Nouveau badge</p>
          <h2 class="font-titre font-bold text-lg text-base-content mb-6">Créer un badge</h2>
          <div class="flex flex-col gap-4">
            <div class="flex flex-col gap-1">
              <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Nom *</label>
              <input v-model="createForm.name" type="text" placeholder="Premier sang" class="bg-base-100 border border-base-300 px-3 py-2 font-code text-sm text-base-content" />
            </div>
            <div class="flex flex-col gap-1">
              <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Type</label>
              <select v-model="createForm.type" class="bg-base-100 border border-base-300 px-3 py-2 font-code text-sm text-base-content">
                <option value="CHALLENGE">CHALLENGE</option>
                <option value="ACHIEVEMENT">SUCCÈS</option>
                <option value="SPECIAL">SPECIAL</option>
                <option value="ADMIN">ADMIN</option>
              </select>
            </div>
            <div class="flex flex-col gap-1">
              <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Description *</label>
              <textarea v-model="createForm.description" rows="3" placeholder="Description du badge..." class="bg-base-100 border border-base-300 px-3 py-2 font-code text-sm text-base-content resize-none"></textarea>
            </div>
          </div>
          <div class="flex gap-3 mt-6">
            <button @click="submitCreate" :disabled="creating || !createForm.name || !createForm.icon_id" class="px-5 py-2 font-code text-xs tracking-wide bg-primary text-base-100 hover:bg-primary/80 transition-colors disabled:opacity-30 flex items-center gap-2">
              <span v-if="creating" class="loading loading-xs"></span>
              <span>Créer le badge</span>
            </button>
            <button @click="activeTab = 'badges_list'" class="px-5 py-2 font-code text-xs tracking-wide border border-base-300 text-base-content/50 hover:text-base-content transition-colors">Annuler</button>
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
    <div v-if="activeTab === 'badges_edit' && editTarget" class="w-full">
      <div class="grid grid-cols-1 xl:grid-cols-2 gap-8 items-start">
        <div class="border border-base-300 bg-base-200/40 p-6">
          <p class="font-code text-[10px] tracking-widest uppercase text-base-content/35 mb-1">Badge #{{ editTarget }}</p>
          <h2 class="font-titre font-bold text-lg text-base-content mb-6">Modifier le badge</h2>
          <div class="flex flex-col gap-4">
            <div class="flex flex-col gap-1">
              <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Nom *</label>
              <input v-model="editForm.name" type="text" class="bg-base-100 border border-base-300 px-3 py-2 font-code text-sm text-base-content" />
            </div>
            <div class="flex flex-col gap-1">
              <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Type</label>
              <select v-model="editForm.type" class="bg-base-100 border border-base-300 px-3 py-2 font-code text-sm text-base-content">
                <option value="CHALLENGE">CHALLENGE</option>
                <option value="ACHIEVEMENT">ACHIEVEMENT</option>
                <option value="SPECIAL">SPECIAL</option>
                <option value="ADMIN">ADMIN</option>
              </select>
            </div>
            <div class="flex flex-col gap-1">
              <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Description *</label>
              <textarea v-model="editForm.description" rows="3" class="bg-base-100 border border-base-300 px-3 py-2 font-code text-sm text-base-content resize-none"></textarea>
            </div>
          </div>
          <div class="flex gap-3 mt-6">
            <button @click="submitEdit" :disabled="editing" class="px-5 py-2 font-code text-xs tracking-wide bg-primary text-base-100 hover:bg-primary/80 transition-colors disabled:opacity-30 flex items-center gap-2">
              <span v-if="editing" class="loading loading-xs"></span>
              <span>Sauvegarder</span>
            </button>
            <button @click="activeTab = 'badges_list'; editTarget = null" class="px-5 py-2 font-code text-xs tracking-wide border border-base-300 text-base-content/50 hover:text-base-content transition-colors">Annuler</button>
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
  </div>
  <Teleport to="body">
    <div v-if="assignModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4" @click.self="assignModalOpen = false">
      <div class="w-full max-w-lg bg-base-200 border border-base-300 flex flex-col shadow-2xl p-6">
        <div class="flex items-center justify-between border-b border-base-300 pb-3 mb-4">
          <div>
            <p class="font-code text-[10px] uppercase text-base-content/40">Attribution manuelle</p>
            <h3 class="font-titre font-bold text-base text-base-content">{{ targetBadge?.name }}</h3>
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
                    @click="toggleUserBadge(u, true)"
                    :disabled="assigning"
                    class="px-2.5 py-1 bg-primary text-base-100 hover:bg-primary/80 text-[10px] font-bold"
                  >
                    Attribuer
                  </button>
                  <button
                    @click="toggleUserBadge(u, false)"
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
  <div v-if="achievementModal.isOpen" class="fixed inset-0 z-40 flex items-center justify-center bg-base-300/80 backdrop-blur-sm p-4">
    <div class="bg-base-100 border border-base-300 shadow-2xl max-w-lg w-full p-6 animate-fade-in">
      <div class="flex justify-between items-center mb-6">
        <div>
          <p class="font-code text-[10px] tracking-widest uppercase text-base-content/35 mb-1">Nouveau succès</p>
          <h2 class="font-titre font-bold text-lg text-base-content">Créer un nouveau succès</h2>
        </div>
        <button @click="achievementModal.isOpen = false" class="text-base-content/50 hover:text-base-content text-xl leading-none">&times;</button>
      </div>
      <div class="flex flex-col gap-4">
        <input v-model="achievementForm.name" type="text" placeholder="Nom du succès..." class="bg-base-100 border border-base-300 px-3 py-2 font-code text-sm w-full" />
        <textarea v-model="achievementForm.description" rows="3" placeholder="Description..." class="bg-base-100 border border-base-300 px-3 py-2 font-code text-sm w-full resize-none"></textarea>
      </div>
      <div class="flex justify-end gap-3 mt-8">
        <button @click="achievementModal.isOpen = false" class="py-2 px-5 border border-base-300 font-code text-xs text-base-content/70">Annuler</button>
        <button @click="submitCreateAchievement" :disabled="creatingAchievement || !achievementForm.name.trim()" class="py-2 px-5 bg-primary text-base-100 font-code text-xs">Créer</button>
      </div>
    </div>
  </div>
  <Teleport to="body">
    <div v-if="requirementsPanelOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4" @click.self="requirementsPanelOpen = false">
      <div class="w-full max-w-3xl max-h-[85vh] bg-base-200 border border-base-300 flex flex-col shadow-2xl">
        <div class="flex items-center justify-between px-5 py-3 border-b border-base-300">
          <p class="font-titre font-bold text-sm text-base-content">Prérequis — {{ selectedAchievement?.name }}</p>
          <div class="flex items-center gap-4">
            <button @click="exportTableToCsv('requirements')" :disabled="exportingCsv" class="font-code text-xs text-base-content/40 hover:text-primary">⬇ Exporter en CSV</button>
            <button @click="requirementsPanelOpen = false" class="font-code text-xs text-error">Fermer</button>
          </div>
        </div>
        <div class="flex-1 overflow-y-auto px-5 py-3">
          <div v-if="!selectedAchievement?.requirements?.length" class="text-center py-10 font-text text-sm text-base-content/25">Aucun prérequis associé</div>
          <table v-else class="w-full text-[11px] font-code">
            <thead>
              <tr class="text-base-content/40 border-b border-base-300"><th class="text-left py-1.5 pr-3">ID</th><th class="text-left py-1.5 pr-3">Type</th><th class="text-left py-1.5 pr-3">Cibles / Valeurs</th><th class="text-right py-1.5 pr-3">Action</th></tr>
            </thead>
            <tbody>
              <tr v-for="req in selectedAchievement.requirements" :key="req.id" class="border-b border-base-300/50">
                <td class="py-2 pr-3">{{ req.id }}</td><td class="py-2 pr-3">{{ getRequirementLabel(req.type) }}</td>
                <td class="py-2 pr-3">Chall: {{ req.challenge_id || '-' }} | Cat: {{ req.category_id || '-' }} | Count: {{ req.count || '-' }}</td>
                <td class="py-2 pr-3 text-right"><button @click="deleteRequirement(req.id, selectedAchievement.id)" class="text-error text-[10px]">Supprimer</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </Teleport>
  <Teleport to="body">
    <div v-if="rewardsPanelOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4" @click.self="rewardsPanelOpen = false">
      <div class="w-full max-w-3xl max-h-[85vh] bg-base-200 border border-base-300 flex flex-col shadow-2xl">
        <div class="flex items-center justify-between px-5 py-3 border-b border-base-300">
          <p class="font-titre font-bold text-sm text-base-content">Récompenses — {{ selectedAchievement?.name }}</p>
          <div class="flex items-center gap-4">
            <button @click="exportTableToCsv('rewards')" :disabled="exportingCsv" class="font-code text-xs text-base-content/40 hover:text-primary">⬇ Exporter en CSV</button>
            <button @click="rewardsPanelOpen = false" class="font-code text-xs text-error">Fermer</button>
          </div>
        </div>
        <div class="flex-1 overflow-y-auto px-5 py-3">
          <div v-if="!selectedAchievement?.rewards?.length" class="text-center py-10 font-text text-sm text-base-content/25">Aucune récompense associée</div>
          <table v-else class="w-full text-[11px] font-code">
            <thead>
              <tr class="text-base-content/40 border-b border-base-300"><th class="text-left py-1.5 pr-3">ID</th><th class="text-left py-1.5 pr-3">Type</th><th class="text-left py-1.5 pr-3">Détails</th><th class="text-right py-1.5 pr-3">Action</th></tr>
            </thead>
            <tbody>
              <tr v-for="rew in selectedAchievement.rewards" :key="rew.id" class="border-b border-base-300/50">
                <td class="py-2 pr-3">{{ rew.id }}</td><td class="py-2 pr-3">{{ rew.type }}</td>
                <td class="py-2 pr-3">Reward ID: {{ rew.reward_id || '-' }} | Valeur: {{ rew.value || '-' }}</td>
                <td class="py-2 pr-3 text-right"><button @click="deleteReward(rew.id, selectedAchievement.id)" class="text-error text-[10px]">Supprimer</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </Teleport>
  <Teleport to="body">
    <div v-if="usersPanelOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4" @click.self="usersPanelOpen = false">
      <div class="w-full max-w-3xl max-h-[85vh] bg-base-200 border border-base-300 flex flex-col shadow-2xl">
        <div class="flex items-center justify-between px-5 py-3 border-b border-base-300">
          <p class="font-titre font-bold text-sm text-base-content">Utilisateurs — {{ selectedAchievement?.name }}</p>
          <div class="flex items-center gap-4">
            <button @click="exportTableToCsv('users')" :disabled="exportingCsv" class="font-code text-xs text-base-content/40 hover:text-primary">⬇ Exporter en CSV</button>
            <button @click="usersPanelOpen = false" class="font-code text-xs text-error">Fermer</button>
          </div>
        </div>
        <div class="flex-1 overflow-y-auto px-5 py-3">
          <div v-if="!selectedAchievement?.users?.length" class="text-center py-10 font-text text-sm text-base-content/25">Aucun utilisateur</div>
          <table v-else class="w-full text-[11px] font-code">
            <thead>
              <tr class="text-base-content/40 border-b border-base-300"><th class="text-left py-1.5 pr-3">ID Liaison</th><th class="text-left py-1.5 pr-3">Username</th><th class="text-left py-1.5 pr-3">Débloqué le</th><th class="text-left py-1.5 pr-3">Lu</th><th class="text-left py-1.5 pr-3">Reçue</th></tr>
            </thead>
            <tbody>
              <tr v-for="u in selectedAchievement.users" :key="u.id" class="border-b border-base-300/50">
                <td class="py-2 pr-3">{{ u.id }}</td><td class="py-2 pr-3">{{ u.username ?? '—' }}</td>
                <td class="py-2 pr-3">{{ u.unlocked_at ?? '—' }}</td><td class="py-2 pr-3" :class="u.is_read === true ? 'text-success' : 'text-error'">{{ u.is_read ? 'Oui' : 'Non' }}</td><td class="py-2 pr-3" :class="u.reward_claimed === true ? 'text-success' : 'text-error'">{{ u.reward_claimed ? 'Oui' : 'Non' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </Teleport>
  <PopUpConfirm :is-open="confirmModal.isOpen" :title="confirmModal.title" :message="confirmModal.message" :loading="confirmModal.loading" @confirm="handleConfirmDialog" @cancel="closeConfirmDialog" />
</template>