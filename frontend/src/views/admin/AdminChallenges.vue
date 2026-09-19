<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import { showToast } from './useAdminToast.js'
import PopUpConfirm from '../../components/PopUpConfirm.vue'

const props = defineProps({
  initialTab: {
    type: String,
    default: 'challenge',
  },
})
const challenges        = ref([])
const totalChallenges   = ref(0)
const categories        = ref([])
const dockerImagesList  = ref([])
const loadingChallenges = ref(false)
const expandedChallenge = ref(null)
const challengeDetail   = ref(null)
const revealedFlag      = ref(null)
const revealingFlag     = ref(false)
const challengeHistory  = ref([])
const historyOffset     = ref(0)
const loadingHistory    = ref(false)
const historyPanelOpen  = ref(false)
const exportingHistory  = ref(false)
const challengeRotation = ref([])
const rotationOffset    = ref(0)
const loadingRotation   = ref(false)
const rotationPanelOpen = ref(false)
const challengeFiles        = ref([])
const loadingChallengeFiles = ref(false)
const newFile               = ref(null)
const newFileInput          = ref(null)
const newFileType           = ref('MAIN')
const newFileName           = ref('')
const addingFile            = ref(false)
const deletingFileIds       = ref(new Set())
const search           = ref('')
const filterActive     = ref('')
const filterDifficulty = ref('')
const filterCategory   = ref('')
const filterType       = ref('')
const sortKey          = ref('name')
const sortDir          = ref('asc')
const currentPage    = ref(1)
const itemsPerPage   = 25
const expandedCategory          = ref(null)
const loadingCategoryChallenges = ref(false)
const categoryChallenges        = ref([])
const availableSearchQuery              = ref('')
const selectedChallengesToAddToRot      = ref([])
const selectedChallengesToRemoveFromRot = ref([])
const expandedRotCategory               = ref(null)
const rotationCategoryChallenges        = reactive({})
const filteredSearchedChallenges        = ref([])
const rotModal = reactive({ isOpen: false, mode: 'create' })
const catModal = reactive({ isOpen: false, mode: 'create' })
const geointTarget = ref(null)
const tabGroup = computed(() => TAB_GROUPS[props.initialTab] ?? TAB_GROUPS.challenge)
const activeTab = ref('challenge_list')
const filteredChallengesTable = computed(() => challenges.value)
const challengesInRot = computed(() => new Set(rotationChallenges.value.map(c => c.id)))
const selectedRotationObj = computed(() => {
  return rotations.value.find(r => r.id === selectedRotId.value) || null
})
const conflictingChallengeIds = computed(() => {
  const currentRot = selectedRotationObj.value
  if (!currentRot || !currentRot.start_time || !currentRot.end_time) return new Set()
  const conflicts = new Set()
  const currentStart = new Date(currentRot.start_time)
  const currentEnd = new Date(currentRot.end_time)
  rotations.value.forEach(rot => {
    if (rot.id === currentRot.id || !rot.start_time || !rot.end_time) return
    const rotStart = new Date(rot.start_time)
    const rotEnd = new Date(rot.end_time)
    const isOverlapping = rotStart <= currentEnd && rotEnd >= currentStart
    if (isOverlapping && rot.challenges) {
      rot.challenges.forEach(ch => conflicts.add(ch.id))
    }
  })
  return conflicts
})
const totalAvailableRotationsCount = computed(() => {
  let total = 0
  Object.keys(rotationCategoryChallenges).forEach(catId => {
    const list = rotationCategoryChallenges[catId] || []
    total += list.filter(ch => !challengesInRot.value.has(ch.id)).length
  })
  return total
})
const TAB_GROUPS = {
  challenge: [
    { id: 'challenge_list', label: 'Liste' },
    { id: 'challenge_create', label: 'Créer' },
    { id: 'challenge_edit', label: 'Modifier', locked: () => !editTarget.value },
  ],
  geoint: [
    { id: 'geoint_list', label: 'Liste' },
    { id: 'geoint_create', label: 'Créer' },
    { id: 'geoint_edit', label: 'Modifier', locked: () => !geointTarget.value },
  ],
  rotation: [
    { id: 'rotation_list', label: 'Liste' },
  ],
  category: [
    { id: 'category_list', label: 'Liste' },
  ],
}
const DIFF_MAP = {
  INTRO: 'bg-info/15 text-info border border-info/30',
  EASY:   'bg-success/15 text-success border border-success/30',
  MEDIUM: 'bg-warning/15 text-warning border border-warning/30',
  HARD:   'bg-error/15 text-error border border-error/30',
  EXPERT: 'bg-secondary/15 text-secondary border border-secondary/30',
}
const diffClass = d => DIFF_MAP[d] ?? 'bg-base-300 text-base-content/60 border border-base-300'
const typeClass = t => t === 'PERMANENT'
  ? 'bg-info/15 text-info border border-info/30'
  : 'bg-secondary/15 text-secondary border border-secondary/30'
const wrapFlag = f => f ? `GH{${f}}` : f
const breadcrumbSubCategory = computed(() => {
  if (activeTab.value.startsWith('challenge_')) return 'Challenges'
  if (activeTab.value.startsWith('geoint_')) return 'Geoint'
  if (activeTab.value.startsWith('category_')) return 'Catégories'
  if (activeTab.value.startsWith('rotation_')) return 'Rotations'
  return ''
})
const confirmModal = reactive({
  isOpen: false,
  title: '',
  message: '',
  onConfirm: null
})
const createDefaults = { 
  name: '', type: 'PERMANENT', description: '', category_id: '', 
  difficulty: 'MEDIUM', points: 100, access_type: 'none', 
  docker_image_id: null, external_url: '', flag_type: 'STATIC', master_flag: '' 
}
const createForm = reactive({ ...createDefaults })
const creating   = ref(false)
const editTarget   = ref(null)
const editForm     = reactive({ 
  name: '', type: '', description: '', category_id: '', difficulty: '', 
  points: 0, access_type: 'none', docker_image_id: null, external_url: '', 
  flag_type: '', master_flag: '', hidden: false 
})
const editing      = ref(false)
const existingFlag = ref('')
const rotations        = ref([])
const loadingRotations = ref(false)
const rotationForm     = reactive({ name: '', start_time: '', end_time: '' })
const creatingRotation = ref(false)
const expandedRotation = ref(null)
const editRotTarget    = ref(null)
const editRotForm      = reactive({ name: '', start_time: '', end_time: '' })
const editingRot       = ref(false)
const selectedRotId    = ref(null)
const rotationChallenges = ref([])
const toBackendDate = s => s ? s.replace('T', ' ') + ':00' : ''
const toLocalDate   = s => s ? s.substring(0, 16) : ''
const loadingCategories = ref(false)
const catForm           = reactive({ name: '', description: '' })
const creatingCat       = ref(false)
const editCatTarget     = ref(null)
const editCatForm       = reactive({ name: '', description: '' })
const toggleCategory = async (categoryId) => {
  if (expandedCategory.value === categoryId) {
    expandedCategory.value = null
    categoryChallenges.value = []
    return
  }
  expandedCategory.value = categoryId
  loadingCategoryChallenges.value = true
  categoryChallenges.value = []

  try {
    const response = await axios.get(`/api/admin/challenge/category/${categoryId}/challenges`)
    categoryChallenges.value = response.data?.challenges ?? []
  } catch {
    showToast('Impossible de charger les challenges de la catégorie', 'error')
  } finally {
    loadingCategoryChallenges.value = false
  }
}


function defaultTabForGroup(groupKey) {
  if (groupKey === 'geoint') return 'geoint_list'
  if (groupKey === 'rotation') return 'rotation_list'
  if (groupKey === 'category') return 'category_list'
  return 'challenge_list'
}
function onTabChange(tab) {
  activeTab.value = tab
  if (tab.startsWith('rotation_')) {
    fetchRotations()
    fetchCategoriesFull()
  }
  if (tab.startsWith('category_')) fetchCategoriesFull()
  if (tab === 'challenge_list') fetchChallenges()
}
function triggerConfirm(title, message, callback) {
  confirmModal.title = title
  confirmModal.message = message
  confirmModal.onConfirm = callback
  confirmModal.isOpen = true
}
function handleConfirmDialog() {
  if (confirmModal.onConfirm) confirmModal.onConfirm()
  closeConfirmDialog()
}
function closeConfirmDialog() {
  confirmModal.isOpen = false
  confirmModal.onConfirm = null
}
async function fetchChallenges() {
  loadingChallenges.value = true
  try {
    const offset = (currentPage.value - 1) * itemsPerPage
    const params = { offset, limit: itemsPerPage, sort_by: sortKey.value, sort_dir: sortDir.value }
    if (search.value.trim()) params.search = search.value.trim()
    if (filterDifficulty.value) params.difficulty = filterDifficulty.value
    if (filterCategory.value) params.category = filterCategory.value
    if (filterType.value) params.type = filterType.value
    if (filterActive.value) params.active = filterActive.value
    const res = await axios.get('/api/admin/challenge/list', { params })
    totalChallenges.value = res.data?.total_challenges ?? 0
    challenges.value = res.data?.challenges ?? []
  } catch {
    showToast('Impossible de charger les challenges', 'error')
  } finally {
    loadingChallenges.value = false
  }
}
async function fetchDockerImages() {
  try {
    const res = await axios.get('/api/admin/docker/image/list')
    dockerImagesList.value = res.data?.images ?? res.data?.data ?? []
  } catch {}
}
async function fetchCategories() {
  try {
    const res = await axios.get('/api/admin/challenge/category/list')
    categories.value = res.data?.categories ?? res.data?.data ?? []
  } catch {}
}
async function toggleChallenge(id) {
  if (expandedChallenge.value === id) {
    expandedChallenge.value = null
    challengeDetail.value   = null
    challengeHistory.value  = []
    challengeRotation.value = []
    challengeFiles.value    = []
    revealedFlag.value      = null
    historyPanelOpen.value  = false
    rotationPanelOpen.value = false
    return
  }
  expandedChallenge.value = id
  challengeDetail.value   = null
  challengeHistory.value  = []
  challengeRotation.value = []
  challengeFiles.value    = []
  revealedFlag.value      = null
  historyPanelOpen.value  = false
  historyOffset.value     = 0
  rotationPanelOpen.value = false
  newFile.value           = null
  newFileName.value       = ''
  if (newFileInput.value) newFileInput.value.value = ''
  try {
    const res = await axios.get(`/api/admin/challenge/${id}/info`)
    challengeDetail.value = res.data?.challenge ?? res.data?.data ?? res.data
    fetchRotation(challengeDetail.value?.rotations)
  } catch {
    showToast('Erreur lors du chargement', 'error')
  }
  fetchHistory(id, 0)
  fetchChallengeFiles(id)
}
async function fetchHistory(id, offset) {
  loadingHistory.value = true
  try {
    const res     = await axios.get(`/api/admin/challenge/${id}/history/${offset}`)
    const entries = res.data?.history ?? res.data?.data ?? []
    if (offset === 0) challengeHistory.value = entries
    else              challengeHistory.value.push(...entries)
    historyOffset.value = offset + entries.length
  } catch {
    showToast("Impossible de charger l'historique", 'error')
  } finally {
    loadingHistory.value = false
  }
}
async function fetchRotation(rotations) {
  loadingRotation.value = true
  try {
    challengeRotation.value = rotations ?? []
  } catch {
    showToast("Impossible de charger les rotations", 'error')
    challengeRotation.value = []
  } finally {
    loadingRotation.value = false
  }
}
async function downloadHistoryCsv() {
  if (!challengeDetail.value) return
  exportingHistory.value = true
  try {
    const challengeId = challengeDetail.value.id
    let offset = 0
    let allEntries = []
    while (true) {
      const res     = await axios.get(`/api/admin/challenge/${challengeId}/history/${offset}`)
      const entries = res.data?.history ?? res.data?.data ?? []
      allEntries.push(...entries)
      if (entries.length < 20) break
      offset += entries.length
    }
    if (!allEntries.length) {
      showToast("Aucune soumission à exporter", 'error')
      return
    }
    const headers = ['ID', 'Username', 'Flag soumis', 'Valide','Type de flag', 'Date de soumission']
    const escape = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`
    const rows = allEntries.map(e => [
      e.submission_id, e.username, e.flag_submitted, e.is_correct, e.flag_type, e.submitted_at,
    ].map(escape).join(','))
    const csv = [headers.join(','), ...rows].join('\n')
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const now = new Date()
    const pad = (n) => String(n).padStart(2, '0')
    const dateStr = `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}_${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`
    const safeName = (challengeDetail.value.name || 'challenge').trim().replace(/\s+/g, '-').replace(/[^a-zA-Z0-9_-]/g, '')
    const filename = `${safeName}_ID${challengeId}_soumission_${dateStr}.csv`
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    showToast("Impossible d'exporter l'historique", 'error')
  } finally {
    exportingHistory.value = false
  }
}
async function fetchChallengeFiles(id) {
  loadingChallengeFiles.value = true
  try {
    const res = await axios.get(`/api/admin/challenge/${id}/files/list`)
    challengeFiles.value = res.data?.files ?? res.data?.data ?? []
  } catch {
    challengeFiles.value = []
  } finally {
    loadingChallengeFiles.value = false
  }
}
async function revealFlag(id) {
  revealingFlag.value = true
  try {
    const res = await axios.get(`/api/admin/challenge/${id}/reveal_flag`)
    revealedFlag.value = res.data?.flag ?? ''
  } catch (e) {
    showToast(e.response?.data?.message ?? 'Erreur lors de la révélation du flag', 'error')
  } finally {
    revealingFlag.value = false
  }
}
function onNewFileChange(e) {
  newFile.value = e.target.files[0] ?? null
}
async function addChallengeFile(challengeId) {
  if (!newFile.value) { showToast('Sélectionne un fichier', 'error'); return }
  addingFile.value = true
  try {
    const formData = new FormData()
    formData.append('file', newFile.value)
    formData.append('file_type', newFileType.value)
    if (newFileName.value) formData.append('file_name', newFileName.value)
    await axios.post(`/api/admin/challenge/${challengeId}/files/add`, formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    showToast('Fichier ajouté')
    newFile.value      = null
    newFileName.value  = ''
    if (newFileInput.value) newFileInput.value.value = ''
    await fetchChallengeFiles(challengeId)
  } catch (e) {
    showToast(e.response?.data?.message ?? "Erreur lors de l'ajout", 'error')
  } finally {
    addingFile.value = false
  }
}
function removeChallengeFile(challengeId, fileId, fileName) {
  if (deletingFileIds.value.has(fileId)) return
  triggerConfirm(
    'Supprimer le fichier',
    `Voulez-vous vraiment supprimer le fichier "${fileName}" ? Cette action est irréversible.`,
    async () => {
      deletingFileIds.value.add(fileId)
      try {
        const response = await axios.post(`/api/admin/challenge/${challengeId}/files/${fileId}/remove`)
        if (response.data?.status === 'success') {
          showToast(response.data?.message || 'Fichier supprimé')
          await fetchChallengeFiles(challengeId)
        }
      } catch (e) {
        await fetchChallengeFiles(challengeId)
      } finally {
        deletingFileIds.value.delete(fileId)
      }
    }
  )
}
function deleteChallenge(id, name) {
  triggerConfirm(
    'Supprimer le challenge',
    `Voulez-vous vraiment supprimer le challenge "${name}" ? Cette action est irréversible.`,
    async () => {
      try {
        await axios.post(`/api/admin/challenge/${id}/delete`)
        showToast(`Challenge "${name}" supprimé`)
        if (expandedChallenge.value === id) { expandedChallenge.value = null; challengeDetail.value = null }
        await fetchChallenges()
      } catch (e) {
        showToast(e.response?.data?.message ?? 'Erreur suppression', 'error')
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
}
function clearFilters() {
  search.value           = ''
  filterActive.value     = ''
  filterDifficulty.value = ''
  filterCategory.value   = ''
  filterType.value       = ''
  currentPage.value      = 1
}
async function submitCreate() {
  creating.value = true
  try {
    const payload = { ...createForm }
    if (payload.master_flag) payload.master_flag = wrapFlag(payload.master_flag)
    if (payload.access_type === 'docker') delete payload.external_url
    else if (payload.access_type === 'external') delete payload.docker_image_id
    else { delete payload.docker_image_id; delete payload.external_url }
    delete payload.access_type

    await axios.post('/api/admin/challenge/create', payload)
    showToast(`Challenge "${createForm.name}" créé !`)
    Object.assign(createForm, { ...createDefaults })
    activeTab.value = 'challenge_list'
    await fetchChallenges()
  } catch (e) {
    showToast(e.response?.data?.message ?? 'Erreur création', 'error')
  } finally {
    creating.value = false
  }
}
async function openEdit(ch) {
  editTarget.value   = ch.id
  activeTab.value    = 'challenge_edit'
  existingFlag.value = ''
  await fetchDockerImages()
  try {
    const res = await axios.get(`/api/admin/challenge/${ch.id}/info`)
    const d   = res.data?.challenge ?? res.data?.data ?? res.data
    let accType = 'none'
    if (d.docker_image_id) accType = 'docker'
    else if (d.external_url) accType = 'external'
    Object.assign(editForm, {
      name:            d.name             ?? ch.name,
      type:            d.type             ?? ch.type             ?? 'PERMANENT',
      description:     d.description      ?? ch.description      ?? '',
      category_id:     d.category_id      ?? ch.category_id      ?? '',
      difficulty:      d.difficulty       ?? ch.difficulty,
      points:          d.points           ?? ch.points,
      access_type:     accType,
      docker_image_id: d.docker_image_id  ?? ch.docker_image_id  ?? null,
      external_url:    d.external_url     ?? ch.external_url     ?? '',
      flag_type:       d.flag_type        ?? ch.flag_type        ?? 'STATIC',
      master_flag:     '',
      hidden:          d.hidden           ?? ch.hidden           ?? false,
    })
    existingFlag.value = d.master_flag ?? ch.master_flag ?? ''
  } catch {
    showToast('Infos partielles chargées (fallback)', 'error')
  }
}
async function submitEdit() {
  editing.value = true
  try {
    const { master_flag, hidden, description, access_type, docker_image_id, external_url, ...rest } = editForm
    const payload = {
      new_name:            rest.name,
      new_type:            rest.type,
      new_description:     description ?? '',
      new_category_id:     rest.category_id,
      new_difficulty:      rest.difficulty,
      new_points:          rest.points,
      new_flag_type:       rest.flag_type,
      new_docker_image_id: access_type === 'docker' ? (docker_image_id ? Number(docker_image_id) : null) : null,
      new_external_url:    access_type === 'external' ? (external_url ? external_url.trim() : null) : null,
    }
    if (master_flag) payload.new_master_flag = wrapFlag(master_flag)
    await axios.post(`/api/admin/challenge/${editTarget.value}/modify`, payload)
    showToast('Challenge modifié !')
    activeTab.value  = 'challenge_list'
    editTarget.value = null
    await fetchChallenges()
  } catch (e) {
    showToast(e.response?.data?.message ?? 'Erreur modification', 'error')
  } finally {
    editing.value = false
  }
}
async function toggleVisibility(ch) {
  try {
    const endpoint = ch.hidden ? 'activate' : 'desactivate'
    await axios.post(`/api/admin/challenge/${ch.id}/${endpoint}`)
    showToast(`Challenge ${ch.name} ${ch.hidden ? 'rendu visible' : 'masqué'}`)
    await fetchChallenges()
  } catch (e) {
    showToast(e.response?.data?.message ?? 'Erreur visibilité', 'error')
  }
}
async function fetchRotations() {
  loadingRotations.value = true
  try {
    const res = await axios.get('/api/admin/challenge/rotation/list')
    rotations.value = res.data?.rotations ?? res.data?.data ?? []
  } catch {
    showToast('Impossible de charger les rotations', 'error')
  } finally {
    loadingRotations.value = false
  }
}
function openCreateRotModal() {
  Object.assign(rotationForm, { name: '', start_time: '', end_time: '' })
  rotModal.mode = 'create'
  rotModal.isOpen = true
}
async function createRotation() {
  if (!rotationForm.name || !rotationForm.start_time || !rotationForm.end_time) {
    showToast('Tous les champs sont requis', 'error'); return
  }
  creatingRotation.value = true
  try {
    await axios.post('/api/admin/challenge/rotation/create', {
      name:  rotationForm.name,
      start: toBackendDate(rotationForm.start_time),
      end:   toBackendDate(rotationForm.end_time),
    })
    showToast('Rotation créée !')
    rotModal.isOpen = false
    await fetchRotations()
  } catch (e) {
    showToast(e.response?.data?.message ?? 'Erreur création rotation', 'error')
  } finally {
    creatingRotation.value = false
  }
}
function openEditRotModal(rot) {
  editRotTarget.value = rot.id
  Object.assign(editRotForm, {
    name:       rot.name,
    start_time: toLocalDate(rot.start_time),
    end_time:   toLocalDate(rot.end_time),
  })
  rotModal.mode = 'edit'
  rotModal.isOpen = true
}
async function submitEditRot() {
  editingRot.value = true
  try {
    await axios.post(`/api/admin/challenge/rotation/${editRotTarget.value}/modify`, {
      new_name:  editRotForm.name,
      new_start: toBackendDate(editRotForm.start_time),
      new_end:   toBackendDate(editRotForm.end_time),
    })
    showToast('Rotation modifiée !')
    rotModal.isOpen = false
    editRotTarget.value = null
    await fetchRotations()
  } catch (e) {
    showToast(e.response?.data?.message ?? 'Erreur modification', 'error')
  } finally {
    editingRot.value = false
  }
}
function deleteRotation(id, name) {
  triggerConfirm(
    'Supprimer la rotation',
    `Voulez-vous vraiment supprimer la rotation "${name}" ? Cette action est irréversible.`,
    async () => {
      try {
        await axios.post(`/api/admin/challenge/rotation/${id}/delete`)
        showToast(`Rotation "${name}" supprimée`)
        if (selectedRotId.value === id) selectedRotId.value = null
        if (expandedRotation.value === id) expandedRotation.value = null
        await fetchRotations()
      } catch (e) {
        showToast(e.response?.data?.message ?? 'Erreur', 'error')
      }
    }
  )
}
async function fetchRotationChallenges(id) {
  try {
    const res = await axios.get(`/api/admin/challenge/rotation/${id}/info/`)
    rotationChallenges.value = res.data?.rotation?.challenges ?? []
  } catch {
    showToast('Impossible de charger les challenges de la rotation', 'error')
    rotationChallenges.value = []
  }
}
async function selectRotation(rot) {
  selectedRotId.value = rot.id
  await fetchRotationChallenges(rot.id)
}
function toggleSelectChallengeForRot(id) {
  if (conflictingChallengeIds.value.has(id)) return
  const index = selectedChallengesToAddToRot.value.indexOf(id)
  if (index > -1) selectedChallengesToAddToRot.value.splice(index, 1)
  else selectedChallengesToAddToRot.value.push(id)
}
function toggleSelectChallengeToRemoveFromRot(id) {
  const index = selectedChallengesToRemoveFromRot.value.indexOf(id)
  if (index > -1) selectedChallengesToRemoveFromRot.value.splice(index, 1)
  else selectedChallengesToRemoveFromRot.value.push(id)
}
async function addSelectedToRot() {
  if (!selectedChallengesToAddToRot.value.length || !selectedRotId.value) return
  try {
    await axios.post(`/api/admin/challenge/rotation/${selectedRotId.value}/add`, { challenge_id: selectedChallengesToAddToRot.value })
    showToast('Challenges ajoutés avec succès !')
    selectedChallengesToAddToRot.value = []
    
    await fetchRotations()
    await fetchRotationChallenges(selectedRotId.value)
    await fetchCategoriesFull()
    if (expandedRotCategory.value) {
      delete rotationCategoryChallenges[expandedRotCategory.value]
      await toggleRotationCategory(expandedRotCategory.value)
    }
  } catch (e) {
    showToast(e.response?.data?.message ?? 'Erreur lors de l\'ajout groupé', 'error')
  }
}
async function removeSelectedFromRot() {
  if (!selectedChallengesToRemoveFromRot.value.length || !selectedRotId.value) return
  try {
    await axios.post(`/api/admin/challenge/rotation/${selectedRotId.value}/remove`, { challenge_id: selectedChallengesToRemoveFromRot.value })
    showToast('Challenges retirés avec succès !')
    selectedChallengesToRemoveFromRot.value = []
    
    await fetchRotations()
    await fetchRotationChallenges(selectedRotId.value)
    await fetchCategoriesFull()
    if (expandedRotCategory.value) {
      delete rotationCategoryChallenges[expandedRotCategory.value]
      await toggleRotationCategory(expandedRotCategory.value)
    }
  } catch (e) {
    showToast(e.response?.data?.message ?? 'Erreur lors du retrait groupé', 'error')
  }
}
async function toggleRotationCategory(categoryId) {
  if (expandedRotCategory.value === categoryId) {
    expandedRotCategory.value = null
    return
  }
  expandedRotCategory.value = categoryId
  if (!rotationCategoryChallenges[categoryId]) {
    loadingCategoryChallenges.value = true
    try {
      const response = await axios.get(`/api/admin/challenge/category/${categoryId}/challenges`)
      const rawChallenges = response.data?.challenges ?? []
      rotationCategoryChallenges[categoryId] = rawChallenges.filter(ch => (ch.type || '').toUpperCase() === 'ROTATION')
    } catch {
      showToast('Impossible de charger les challenges de cette catégorie', 'error')
      rotationCategoryChallenges[categoryId] = []
    } finally {
      loadingCategoryChallenges.value = false
    }
  }
}
async function fetchCategoriesFull() {
  loadingCategories.value = true
  try {
    const res = await axios.get('/api/admin/challenge/category/list')
    categories.value = res.data?.categories ?? res.data?.data ?? []
  } catch {
    showToast('Impossible de charger les catégories', 'error')
  } finally {
    loadingCategories.value = false
  }
}
function openCreateCatModal() {
  Object.assign(catForm, { name: '', description: '' })
  catModal.mode = 'create'
  catModal.isOpen = true
}
async function createCategory() {
  creatingCat.value = true
  try {
    await axios.post('/api/admin/challenge/category/create', { category_name: catForm.name, category_description: catForm.description })
    showToast('Catégorie créée !')
    catModal.isOpen = false
    await fetchCategoriesFull()
  } catch (e) {
    showToast(e.response?.data?.message ?? 'Erreur', 'error')
  } finally {
    creatingCat.value = false
  }
}
function deleteCategory(id, name) {
  triggerConfirm(
    'Supprimer la catégorie',
    `Voulez-vous vraiment supprimer la catégorie "${name}" ? Cette action est irréversible.`,
    async () => {
      try {
        await axios.post(`/api/admin/challenge/category/${id}/delete`)
        showToast(`Catégorie "${name}" supprimée`)
        await fetchCategoriesFull()
      } catch (e) {
        showToast(e.response?.data?.message ?? 'Erreur', 'error')
      }
    }
  )
}
function openEditCatModal(cat) {
  editCatTarget.value = cat.id
  Object.assign(editCatForm, { name: cat.name, description: cat.description })
  catModal.mode = 'edit'
  catModal.isOpen = true
}
async function submitEditCat() {
  try {
    await axios.post(`/api/admin/challenge/category/${editCatTarget.value}/modify`, {
      new_category_name: editCatForm.name, new_category_description: editCatForm.description
    })
    showToast('Catégorie modifiée !')
    catModal.isOpen = false
    editCatTarget.value = null
    await fetchCategoriesFull()
  } catch (e) {
    showToast(e.response?.data?.message ?? 'Erreur', 'error')
  }
}

watch(
  () => props.initialTab,
  async (groupKey) => {
    activeTab.value = defaultTabForGroup(groupKey)
    if (groupKey === 'challenge') {
      await fetchChallenges()
      await fetchCategoriesFull()
      await fetchDockerImages()
    } else if (groupKey === 'rotation') {
      await fetchRotations()
      await fetchCategoriesFull()
    } else if (groupKey === 'category') {
      await fetchCategoriesFull()
    }
  },
  { immediate: true }
)
watch(
  [search, filterActive, filterDifficulty, filterCategory, filterType, sortKey, sortDir, currentPage],
  () => {
    fetchChallenges()
  }
)
watch([search, filterActive, filterDifficulty, filterCategory, filterType], () => {
  currentPage.value = 1
})
watch(availableSearchQuery, async (newVal) => {
  if (!newVal.trim()) {
    filteredSearchedChallenges.value = []
    return
  }
  try {
    const params = { search: newVal.trim(), limit: 50, type: 'ROTATION' }
    const res = await axios.get('/api/admin/challenge/list', { params })
    const allFound = res.data?.challenges ?? []
    filteredSearchedChallenges.value = allFound
      .filter(ch => (ch.type || '').toUpperCase() === 'ROTATION')
      .filter(ch => !challengesInRot.value.has(ch.id))
  } catch (e) {
    console.error("Erreur recherche challenges", e)
  }
})

onMounted(() => {
  fetchChallenges()
  fetchCategoriesFull()
  fetchRotations()
  fetchDockerImages()
})
</script>

<template>
  <div class="flex items-center justify-between mb-6">
    <div>
      <p class="font-code text-[10px] tracking-[0.18em] uppercase text-base-content/40 mb-1">Admin > {{ breadcrumbSubCategory }}</p>
      <h1 class="font-titre font-bold text-2xl text-base-content leading-none">{{ props.initialTab === 'geoint' ? 'Geoint' : 'Challenges' }}</h1>
    </div>
    <span v-if="activeTab === 'challenge_list'" class="font-code text-sm text-base-content/50 border border-secondary px-2 py-1">{{ challenges.length }} CHALLENGE{{ challenges.length > 1 ? 'S' : '' }}</span>
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
  <div class="flex gap-6 flex-1 min-h-0">
    <div v-if="activeTab === 'challenge_list'" class="flex flex-col gap-4 w-full">
    <div class="flex justify-start">
      <button
        @click="onTabChange('challenge_create')"
        class="flex items-center gap-2 bg-primary text-base-100 hover:bg-primary/80 px-4 py-2 font-code text-xs font-bold tracking-wider transition-colors shadow-sm"
      >
        <span>+ Créer un nouveau challenge</span>
      </button>
    </div>
    <div class="flex items-center gap-2 flex-wrap mb-2">
      <div class="relative flex-1 min-w-48">
        <span class="absolute left-3 top-1/2 -translate-y-1/2 font-code text-base-content/30 text-xs select-none">⌕</span>
        <input
          v-model="search"
          type="text"
          placeholder="Rechercher un challenge..."
          class="w-full bg-base-100 border border-base-300 focus:border-primary outline-none pl-7 pr-3 py-2 font-code text-xs text-base-content placeholder:text-base-content/25 transition-colors"
        />
      </div>
      <select v-model="filterActive" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-xs text-base-content transition-colors">
        <option value="">Tous les statuts</option>
        <option value="true">Actif</option>
        <option value="false">Inactif</option>
      </select>
      <select v-model="filterDifficulty" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-xs text-base-content transition-colors">
        <option value="">Toutes les difficultés</option>
        <option value="INRO">INTRO</option>
        <option value="EASY">EASY</option>
        <option value="MEDIUM">MEDIUM</option>
        <option value="HARD">HARD</option>
        <option value="EXPERT">EXPERT</option>
      </select>
      <select v-model="filterCategory" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-xs text-base-content transition-colors">
        <option value="">Toutes les catégories</option>
        <option v-for="cat in categories" :key="cat.id" :value="cat.name">{{ cat.name }}</option>
      </select>
      <select v-model="filterType" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-xs text-base-content transition-colors">
        <option value="">Tous les types</option>
        <option value="PERMANENT">PERMANENT</option>
        <option value="ROTATION">ROTATION</option>
      </select>
    </div>
    <div class="border border-base-300 overflow-hidden flex flex-col" style="max-height: calc(100vh - 220px);">
      <div class="grid grid-cols-[2fr_1.5fr_1fr_1fr_1fr_120px] bg-base-200 border-b border-base-300 shrink-0">
        <button
          v-for="col in [
            { key: 'id',          label: 'Nom'        },
            { key: 'category_name', label: 'Catégorie'  },
            { key: 'difficulty',    label: 'Difficulté' },
            { key: 'points',        label: 'Points'     },
            { key: 'type',          label: 'Type'       },
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
        <div v-if="loadingChallenges" class="flex justify-center py-16">
          <span class="loading loading-spinner loading-md text-primary"></span>
        </div>
        <div v-else-if="!filteredChallengesTable.length" class="flex flex-col items-center justify-center py-10 gap-1">
          <span class="font-code text-xs text-base-content/25">Aucun challenge trouvé</span>
        </div>
        <div v-else class="flex flex-col">
          <template v-for="ch in filteredChallengesTable" :key="ch.id">
            <div
              @click="toggleChallenge(ch.id)"
              :class="[
                'grid grid-cols-[2fr_1.5fr_1fr_1fr_1fr_120px] items-center border-b border-base-300/50 cursor-pointer transition-colors duration-100',
                expandedChallenge === ch.id ? 'bg-primary/8 border-l-2 border-l-primary' : 'hover:bg-base-300/30'
              ]"
            >
              <div class="px-4 py-3 flex items-center gap-2 min-w-0">
                <span class="font-code text-[10px] text-base-content/30 shrink-0">#{{ ch.id }}</span>
                <span class="font-code text-xs text-base-content font-medium truncate">{{ ch.name }}</span>
              </div>
              <div class="px-4 py-3 flex items-center">
                <span class="font-code text-xs text-base-content/70 truncate">{{ ch.category_name ?? '—' }}</span>
              </div>
              <div class="px-4 py-3 flex items-center">
                <span :class="['font-text text-[10px] px-2 py-0.5 leading-none', diffClass(ch.difficulty)]">{{ ch.difficulty }}</span>
              </div>
              <div class="px-4 py-3 flex items-center">
                <span class="font-code font-bold text-primary text-xs">{{ ch.points }}</span>
              </div>
              <div class="px-4 py-3 flex items-center">
                <span :class="['font-text text-[10px] px-2 py-0.5 leading-none', typeClass(ch.type)]">{{ ch.type }}</span>
              </div>
              <div class="px-4 py-3 flex items-center justify-end gap-1.5" @click.stop>
                <button @click="toggleVisibility(ch)" :class="['font-text text-[9px] px-1.5 py-0.5 border leading-none text-center', ch.hidden ? 'bg-error/15 text-error border-error/30' : 'bg-success/15 text-success border-success/30']">
                  {{ ch.hidden ? 'CACHÉ' : 'VISIBLE' }}
                </button>
                <button class="font-text text-xs text-info hover:text-info/70 px-1" @click="openEdit(ch)" title="Modifier">Modifier</button>
                <button class="font-text text-xs text-error hover:text-error/70 px-1" @click="deleteChallenge(ch.id, ch.name)" title="Supprimer">Supprimer</button>
              </div>
            </div>
            <div v-if="expandedChallenge === ch.id" class="border-b border-base-300 bg-base-300/50">
              <div v-if="!challengeDetail" class="flex justify-center py-10">
                <span class="loading loading-dots loading-sm text-primary"></span>
              </div>
              <div v-else class="p-5 grid grid-cols-1 lg:grid-col-2 gap-6">
                <div>
                  <p class="font-stitre text-[12px] tracking-widest uppercase text-primary/70 mb-3">Informations</p>
                  <div class="flex gap-32">
                    <dl class="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1.5 text-sm font-text">
                      <dt class="text-base-content/40">Créateur</dt>
                      <dd class="text-base-content">{{ challengeDetail.created_by }}</dd>
                      <dt class="text-base-content/40">ID</dt>
                      <dd class="text-base-content">{{ challengeDetail.id }}</dd>
                      <dt class="text-base-content/40">Type</dt>
                      <dd><span :class="['px-1.5 py-0.5 text-[10px]', typeClass(challengeDetail.type)]">{{ challengeDetail.type }}</span></dd>
                      <dt class="text-base-content/40">Difficulté</dt>
                      <dd><span :class="['px-1.5 py-0.5 text-[10px]', diffClass(challengeDetail.difficulty)]">{{ challengeDetail.difficulty }}</span></dd>
                      <dt class="text-base-content/40">Points</dt>
                      <dd class="font-code font-bold text-primary text-sm">{{ challengeDetail.points }}</dd>
                    </dl>
                    <dl class="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1.5 text-sm font-text">
                        <dt class="text-base-content/40">Date</dt>
                        <dd class="text-base-content">{{ challengeDetail.created_at }}</dd>
                        <dt class="text-base-content/40">Catégorie</dt>
                        <dd class="text-base-content">{{ challengeDetail.category_name }}</dd>
                        <dt class="text-base-content/40">Flag type</dt>
                        <dd class="text-base-content">{{ challengeDetail.flag_type ?? '—' }}</dd>
                        <dt class="text-base-content/40">Visibilité</dt>
                        <button @click.stop="toggleVisibility(ch)" :class="['font-text text-[9px] px-1.5 py-0.5 border leading-none w-[52px] text-center shrink-0', ch.hidden ? 'bg-error/15 text-error border-error/30' : 'bg-success/15 text-success border-success/30']">{{ ch.hidden ? 'CACHÉ' : 'VISIBLE' }}</button>
                        <template v-if="challengeDetail.docker_image_id">
                          <dt class="text-base-content/40">Image Docker</dt>
                          <dd class="text-base-content">{{ challengeDetail.docker_image_name }}</dd>
                        </template>
                        <template v-if="challengeDetail.external_url">
                          <dt class="text-base-content/40">URL Externe</dt>
                          <dd class="text-base-content truncate max-w-xs">{{ challengeDetail.external_url }}</dd>
                        </template>
                      </dl>
                      <div class="flex flex-col gap-2 justify-center">
                        <button
                          @click="historyPanelOpen = true"
                          class="flex items-center gap-2 px-3 py-2.5 font-code text-xs border border-base-300 hover:border-primary/40 text-base-content/60 hover:text-base-content transition-colors whitespace-nowrap"
                        >
                          <span v-if="loadingHistory && !challengeHistory.length">Chargement...</span>
                          <span v-else>Voir l'historique des soumissions ({{ challengeHistory.length }}{{ challengeHistory.length && challengeHistory.length % 20 === 0 ? '+' : '' }})</span>
                        </button>
                        <button v-if ="challengeDetail.type === 'ROTATION'"
                          @click="rotationPanelOpen = true"
                          class="flex items-center gap-2 px-3 py-2.5 font-code text-xs border border-base-300 hover:border-primary/40 text-base-content/60 hover:text-base-content transition-colors whitespace-nowrap"
                        >
                          <span v-if="loadingRotation && !challengeRotation.length">Chargement...</span>
                          <span v-else>Voir la liste des rotations ({{ challengeRotation.length }}{{ challengeRotation.length && challengeRotation.length % 20 === 0 ? '+' : '' }})</span>
                        </button>
                      </div>
                  </div>
                  <div class="mt-3">
                      <button v-if="revealedFlag === null" @click="revealFlag(challengeDetail.id)" :disabled="revealingFlag" class="w-full py-2 font-code text-xs tracking-wide border border-base-300 text-base-content/50 hover:text-base-content hover:border-base-content/30 transition-colors disabled:opacity-30">
                        <span v-if="revealingFlag" class="loading loading-xs"></span>
                        <span v-else>Révéler le Master flag</span>
                      </button>
                      <div v-else class="flex items-center gap-2 px-3 py-2 border border-primary/30 bg-primary/5">
                        <span class="flex-1 text-center font-code text-xs text-base-content break-all">{{ revealedFlag }}</span>
                        <button @click="revealedFlag = null" class="font-code text-[10px] text-base-content/40 hover:text-base-content shrink-0">masquer</button>
                      </div>
                    </div>
                  <div class="mt-4">
                    <p class="font-stitre text-[12px] tracking-widest uppercase text-primary/70 mb-2">Description</p>
                    <p class="text-sm text-base-content/70 bg-base-300/60 border border-base-100 px-3 py-2.5 leading-relaxed">{{ challengeDetail.description || 'Aucune description.' }}</p>
                  </div>
                </div>
                <div class="lg:col-span-2">
                  <p class="font-code text-[10px] tracking-widest uppercase text-primary/70 mb-3">Fichiers du challenge</p>
                  <div v-if="loadingChallengeFiles" class="flex justify-center py-6">
                    <span class="loading loading-dots loading-sm text-primary"></span>
                  </div>
                  <div v-else-if="!challengeFiles.length" class="text-center py-6 font-code text-xs text-base-content/25">Aucun fichier</div>
                  <div v-else class="flex flex-col gap-1.5 mb-4">
                    <div v-for="f in challengeFiles" :key="f.id" class="flex items-center gap-3 px-3 py-2 bg-base-200/60 border border-base-300 font-code text-xs">
                      <span :class="['px-1.5 py-0.5 text-[10px] leading-none shrink-0', f.file_role === 'AIDE' ? 'bg-info/15 text-info border border-info/30' : 'bg-primary/15 text-primary border border-primary/30']">{{ f.file_role }}</span>
                      <a :href="f.file_url" target="_blank" class="text-base-content flex-1 truncate hover:text-primary hover:underline">{{ f.file_name }}</a>
                      <span class="text-base-content/30 shrink-0 hidden md:block">
                        Taille : <strong class="text-base-content font-normal">{{ f.file_size }}</strong>
                      </span>
                      <span>|</span>
                      <span class="text-base-content/30 shrink-0 hidden md:block"> SHA256: <strong class="text-base-content font-normal">{{ f.sha256 }}</strong></span>
                      <span>|</span>
                      <span class="text-base-content/30 shrink-0 hidden md:block">Date : <strong class="text-base-content font-normal">{{ f.uploaded_at }}</strong></span>
                      <button @click="removeChallengeFile(ch.id, f.id, f.file_name)" class="text-error hover:text-error/70 transition-colors px-1 shrink-0" title="Supprimer">Supprimer</button>
                    </div>
                  </div>
                  <div class="flex flex-col sm:flex-row gap-2 items-stretch sm:items-end">
                    <div class="flex flex-col gap-1 flex-1">
                      <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Fichier</label>
                      <input ref="newFileInput" type="file" @change="onNewFileChange" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-xs text-base-content file:mr-3 file:px-2 file:py-1 file:border-0 file:bg-primary/15 file:text-primary file:font-code file:text-xs transition-colors" />
                    </div>
                    <div class="flex flex-col gap-1">
                      <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Rôle</label>
                      <select v-model="newFileType" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-xs text-base-content transition-colors">
                        <option value="MAIN">Fichier principal</option>
                        <option value="AIDE">Documentation / Aide</option>
                      </select>
                    </div>
                    <div class="flex flex-col gap-1 flex-1">
                      <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Nom (optionnel)</label>
                      <input v-model="newFileName" type="text" placeholder="Laisser vide pour garder le nom d'origine" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-xs text-base-content placeholder:text-base-content/20 transition-colors" />
                    </div>
                    <button @click="addChallengeFile(ch.id)" :disabled="addingFile" class="px-4 py-2 font-code text-xs tracking-wide bg-primary text-base-100 hover:bg-primary/80 transition-colors disabled:opacity-30 shrink-0">
                      <span v-if="addingFile" class="loading loading-xs"></span>
                      <span v-else>Ajouter</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
  <div v-if="activeTab === 'challenge_create'" class="w-full">
    <div class="grid grid-cols-1 xl:grid-cols-2 gap-8 items-start">
      <div class="border border-base-300 bg-base-200/40 p-6">
        <p class="font-code text-[10px] tracking-widest uppercase text-base-content/35 mb-1">Nouveau challenge</p>
        <h2 class="font-titre font-bold text-lg text-base-content mb-6">Créer un challenge</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div class="sm:col-span-2 flex flex-col gap-1">
            <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Nom *</label>
            <input v-model="createForm.name" type="text" placeholder="Web Exploitation 101" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content placeholder:text-base-content/20 transition-colors" />
          </div>
          <div class="flex flex-col gap-1">
            <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Type</label>
            <select v-model="createForm.type" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors">
              <option value="PERMANENT">PERMANENT</option>
              <option value="ROTATION">ROTATION</option>
            </select>
          </div>
          <div class="flex flex-col gap-1">
            <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Catégorie *</label>
            <select v-model="createForm.category_id" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors">
              <option value="">— Choisir —</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
            </select>
          </div>
          <div class="flex flex-col gap-1">
            <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Difficulté</label>
            <select v-model="createForm.difficulty" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors">
              <option>INTRO</option><option>EASY</option><option>MEDIUM</option><option>HARD</option><option>EXPERT</option>
            </select>
          </div>
          <div class="flex flex-col gap-1">
            <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Points</label>
            <input v-model.number="createForm.points" type="number" min="0" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors" />
          </div>
          <div class="flex flex-col gap-1">
            <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Type de flag</label>
            <select v-model="createForm.flag_type" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors">
              <option value="STATIC">STATIC</option>
              <option value="DYNAMIC">DYNAMIC</option>
            </select>
          </div>
          <div class="flex flex-col gap-1">
            <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Type d'accès</label>
            <select v-model="createForm.access_type" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors">
              <option value="none">Aucun</option>
              <option value="docker">Docker Image</option>
              <option value="external">URL Externe</option>
            </select>
          </div>
          <div v-if="createForm.access_type === 'docker'" class="flex flex-col gap-1 sm:col-span-2">
            <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Image Docker *</label>
            <select v-model.number="createForm.docker_image_id" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors">
              <option value="">— Choisir une image Docker —</option>
              <option v-for="img in dockerImagesList" :key="img.id" :value="img.id">
                {{ img.name }}:{{ img.image_tag }} (Port: {{ img.internal_port }})
              </option>
            </select>
          </div>
          <div v-if="createForm.access_type === 'external'" class="flex flex-col gap-1 sm:col-span-2">
            <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">URL Externe *</label>
            <input v-model="createForm.external_url" type="text" placeholder="https://challenge.url" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content placeholder:text-base-content/20 transition-colors" />
          </div>
          <div class="sm:col-span-2 flex flex-col gap-1">
            <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Master flag *</label>
            <div class="flex items-center border border-base-300 focus-within:border-primary bg-base-100 transition-colors">
              <span class="px-3 py-2 font-code text-sm text-base-content/40 border-r border-base-300 select-none">GH{</span>
              <input v-model="createForm.master_flag" type="text" placeholder="mon_flag_ici" class="flex-1 bg-transparent outline-none px-3 py-2 font-code text-sm text-base-content placeholder:text-base-content/20" />
              <span class="px-3 py-2 font-code text-sm text-base-content/40 border-l border-base-300 select-none">}</span>
            </div>
          </div>
          <div class="sm:col-span-2 flex flex-col gap-1">
            <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Description</label>
            <textarea v-model="createForm.description" rows="4" placeholder="Description du challenge..." class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content placeholder:text-base-content/20 transition-colors resize-none"></textarea>
          </div>
        </div>
        <div class="flex gap-3 mt-6">
          <button @click="submitCreate" :disabled="creating || !createForm.name || !createForm.master_flag" class="px-5 py-2 font-code text-xs tracking-wide bg-primary text-base-100 hover:bg-primary/80 transition-colors disabled:opacity-30 disabled:cursor-not-allowed">
            <span v-if="creating" class="loading loading-xs"></span>
            <span v-else>Créer le challenge</span>
          </button>
          <button @click="onTabChange('challenge_list')" class="px-5 py-2 font-code text-xs tracking-wide border border-base-300 text-base-content/50 hover:text-base-content hover:border-base-content/30 transition-colors">Annuler</button>
        </div>
      </div>
      <div class="sticky top-6 border border-primary/30 bg-base-100/80 p-6 shadow-2xl backdrop-blur-md">
        <div class="flex items-center justify-between border-b border-base-300 pb-3 mb-6">
          <span class="font-code text-[10px] tracking-widest uppercase text-primary font-bold">Prévisualisation du challenge</span>
        </div>
        <div class="space-y-6">
          <div><h1 class="text-3xl font-titre font-bold text-primary tracking-wide break-all">{{ createForm.name || 'Nom du challenge' }}</h1></div>
          <div class="bg-base-200/40 border border-base-300 p-5 shadow-inner">
            <h2 class="font-stitre text-[10px] opacity-50 uppercase tracking-widest mb-3">Description</h2>
            <div class="prose prose-invert max-w-none text-base-content/80 text-xs leading-relaxed font-text break-all" v-html="createForm.description || '<span class=\'opacity-30 italic\'>Aucune description pour le moment...</span>'"></div>
          </div>
          <div class="bg-base-200/40 border border-base-300 p-5 space-y-4">
            <div class="flex justify-center items-center gap-3 font-text text-xs bg-base-300/50 py-2 border border-base-300/50">
              <span class="font-bold uppercase text-[10px]">{{ categories.find(c => c.id === createForm.category_id)?.name || 'CATÉGORIE' }}</span>
              <span class="opacity-30">|</span>
              <span class="text-secondary font-bold font-code">{{ createForm.points || 0 }} points</span>
              <span class="opacity-30">|</span>
              <span class="font-bold uppercase text-[10px]" :class="createForm.difficulty === 'INTRO' ? 'text-info' : createForm.difficulty === 'EASY' ? 'text-success' : createForm.difficulty === 'MEDIUM' ? 'text-warning' : createForm.difficulty === 'HARD' ? 'text-error' : 'text-secondary'">{{ createForm.difficulty }}</span>
            </div>
            <div class="border-t border-base-300 pt-3">
              <span class="block text-[10px] opacity-50 font-stitre uppercase tracking-widest mb-2">Fichiers (Aperçu)</span>
              <div class="p-2.5 bg-base-100 border border-base-300 flex items-center justify-between text-xs font-code opacity-60"><span>📁 example_file.zip</span><span class="text-[10px]">Fichier principal</span></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div v-if="activeTab === 'challenge_edit' && editTarget" class="w-full">
    <div class="grid grid-cols-1 xl:grid-cols-2 gap-8 items-start">
      <div class="border border-base-300 bg-base-200/40 p-6">
        <p class="font-code text-[10px] tracking-widest uppercase text-base-content/35 mb-1">Challenge #{{ editTarget }}</p>
        <h2 class="font-titre font-bold text-lg text-base-content mb-6">Modifier le challenge</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div class="sm:col-span-2 flex flex-col gap-1">
            <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Nom</label>
            <input v-model="editForm.name" type="text" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors" />
          </div>
          <div class="flex flex-col gap-1">
            <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Type</label>
            <select v-model="editForm.type" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors">
              <option value="PERMANENT">PERMANENT</option>
              <option value="ROTATION">ROTATION</option>
            </select>
          </div>
          <div class="flex flex-col gap-1">
            <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Catégorie</label>
            <select v-model="editForm.category_id" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors">
              <option value="">— Choisir —</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
            </select>
          </div>
          <div class="flex flex-col gap-1">
            <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Difficulté</label>
            <select v-model="editForm.difficulty" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors">
              <option>INTRO</option><option>EASY</option><option>MEDIUM</option><option>HARD</option><option>EXPERT</option>
            </select>
          </div>
          <div class="flex flex-col gap-1">
            <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Points</label>
            <input v-model.number="editForm.points" type="number" min="0" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors" />
          </div>
          <div class="flex flex-col gap-1">
            <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Type de flag</label>
            <select v-model="editForm.flag_type" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors">
              <option value="STATIC">STATIC</option>
              <option value="DYNAMIC">DYNAMIC</option>
            </select>
          </div>
          <div class="flex flex-col gap-1">
            <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Type d'accès</label>
            <select v-model="editForm.access_type" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors">
              <option value="none">Aucun</option>
              <option value="docker">Docker Image</option>
              <option value="external">URL Externe</option>
            </select>
          </div>
          <div v-if="editForm.access_type === 'docker'" class="flex flex-col gap-1 sm:col-span-2">
            <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Image Docker</label>
            <select v-model.number="editForm.docker_image_id" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors">
              <option value="">— Choisir une image Docker —</option>
              <option v-for="img in dockerImagesList" :key="img.id" :value="img.id">
                {{ img.name }}:{{ img.image_tag }} (Port: {{ img.internal_port }})
              </option>
            </select>
          </div>
          <div v-if="editForm.access_type === 'external'" class="flex flex-col gap-1 sm:col-span-2">
            <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">URL Externe</label>
            <input v-model="editForm.external_url" type="text" placeholder="https://challenge.url" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content transition-colors" />
          </div>
          <div class="sm:col-span-2 flex flex-col gap-1">
            <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Nouveau flag <span class="text-base-content/25">(vide = inchangé)</span></label>
            <div class="flex items-center border border-base-300 focus-within:border-primary bg-base-100 transition-colors">
              <span class="px-3 py-2 font-code text-sm text-base-content/40 border-r border-base-300 select-none">GH{</span>
              <input v-model="editForm.master_flag" type="text" :placeholder="existingFlag ? '(inchangé)' : 'mon_flag_ici'" class="flex-1 bg-transparent outline-none px-3 py-2 font-code text-sm text-base-content placeholder:text-base-content/20" />
              <span class="px-3 py-2 font-code text-sm text-base-content/40 border-l border-base-300 select-none">}</span>
            </div>
          </div>
          <div class="sm:col-span-2 flex flex-col gap-1">
            <label class="font-code text-[10px] uppercase tracking-widest text-base-content/40">Description <span class="text-base-content/25">(optionnel)</span></label>
            <textarea v-model="editForm.description" rows="4" placeholder="Description du challenge..." class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm text-base-content placeholder:text-base-content/20 transition-colors resize-none"></textarea>
          </div>
        </div>
        <div class="flex gap-3 mt-6">
          <button @click="submitEdit" :disabled="editing" class="px-5 py-2 font-code text-xs tracking-wide bg-warning text-base-100 hover:bg-warning/80 transition-colors disabled:opacity-30">
            <span v-if="editing" class="loading loading-xs"></span>
            <span v-else>Sauvegarder</span>
          </button>
          <button @click="onTabChange('challenge_list'); editTarget = null" class="px-5 py-2 font-code text-xs tracking-wide border border-base-300 text-base-content/50 hover:text-base-content hover:border-base-content/30 transition-colors">Annuler</button>
        </div>
      </div>
      <div class="sticky top-6 border border-primary/30 bg-base-100/80 p-6 shadow-2xl backdrop-blur-md">
        <div class="flex items-center justify-between border-b border-base-300 pb-3 mb-6">
          <span class="font-code text-[10px] tracking-widest uppercase text-primary font-bold">Prévisualisation du challenge</span>
        </div>
        <div class="space-y-6">
          <div><h1 class="text-3xl font-titre font-bold text-primary tracking-wide break-all">{{ editForm.name || 'Nom du challenge' }}</h1></div>
          <div class="bg-base-200/40 border border-base-300 p-5 shadow-inner">
            <h2 class="font-stitre text-[10px] opacity-50 uppercase tracking-widest mb-3">Description</h2>
            <div class="prose prose-invert max-w-none text-base-content/80 text-xs leading-relaxed font-text break-all" v-html="editForm.description || '<span class=\'opacity-30 italic\'>Aucune description...</span>'"></div>
          </div>
          <div class="bg-base-200/40 border border-base-300 p-5 space-y-4">
            <div class="flex justify-center items-center gap-3 font-text text-xs bg-base-300/50 py-2 border border-base-300/50">
              <span class="font-bold uppercase text-[10px]">{{ categories.find(c => c.id === editForm.category_id)?.name || 'CATÉGORIE' }}</span>
              <span class="opacity-30">|</span>
              <span class="text-secondary font-bold font-code">{{ editForm.points || 0 }} points</span>
              <span class="opacity-30">|</span>
              <span class="font-bold uppercase text-[10px]" :class="editForm.difficulty === 'EASY' ? 'text-success' : editForm.difficulty === 'MEDIUM' ? 'text-warning' : editForm.difficulty === 'HARD' ? 'text-error' : 'text-secondary'">{{ editForm.difficulty }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div v-if="activeTab === 'rotation_list'" class="flex flex-col gap-4 w-full">
    <div class="flex justify-start">
      <button
        @click="openCreateRotModal"
        class="flex items-center gap-2 bg-primary text-base-100 hover:bg-primary/80 px-4 py-2 font-code text-xs font-bold tracking-wider transition-colors shadow-sm"
      >
        <span>+ Créer une nouvelle rotation</span>
      </button>
    </div>
    <div v-if="loadingRotations" class="flex justify-center py-20">
      <span class="loading loading-spinner loading-md text-primary"></span>
    </div>
    <div v-else-if="!rotations.length" class="flex flex-col items-center justify-center py-10 gap-1">
      <span class="font-text text-sm text-base-content/40">Aucune rotation trouvée.</span>
    </div>
    <div v-else class="flex flex-col gap-1.5">
      <div v-for="rot in rotations" :key="rot.id" class="border border-base-200/50 overflow-hidden">
        <div
          @click="selectRotation(rot); expandedRotation = expandedRotation === rot.id ? null : rot.id; selectedChallengesToAddToRot = []; selectedChallengesToRemoveFromRot = []; availableSearchQuery = ''; expandedRotCategory = null"
          class="flex items-center gap-3 px-4 py-3 cursor-pointer select-none hover:bg-base-300/40 transition-colors duration-150"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-base-content/50 transition-transform duration-200 shrink-0" :class="{ 'rotate-90': expandedRotation === rot.id }" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
          <span class="font-text text-[10px] px-2 py-0.5 leading-none bg-base-300 text-base-content/70 border border-base-300 shrink-0">
            {{ rot.challenge_count }} CHALLENGE{{ rot.challenge_count > 1 ? 'S' : '' }}
          </span>
          <span class="font-text font-semibold text-base-content text-sm flex-1 truncate">{{ rot.name }}</span>
          <span class="font-text text-base-content text-xs flex-1 truncate">Début : {{ rot.start_time }} | Fin : {{ rot.end_time }}</span>
          <button class="font-text text-xs text-info hover:text-info/70 px-1 shrink-0" @click.stop="openEditRotModal(rot)" title="Modifier">Modifier</button>
          <button class="font-text text-xs text-error hover:text-error/70 px-1 shrink-0" @click.stop="deleteRotation(rot.id, rot.name)" title="Supprimer">Supprimer</button>
        </div>
        <div v-if="expandedRotation === rot.id" class="bg-base-200/20 border-t border-base-200/50 p-4 animate-fade-in grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="flex flex-col gap-2">
            <div class="flex items-center justify-between">
              <p class="font-code text-[10px] uppercase text-base-content/40">
                Challenges disponibles
                <span class="text-primary font-bold ml-1">({{ totalAvailableRotationsCount }})</span>
              </p>
            </div>
            <input
              v-model="availableSearchQuery"
              type="text"
              placeholder="Rechercher par nom..."
              class="w-full bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-1.5 font-code text-xs text-base-content"
            />
            <div class=" overflow-y-auto border border-base-300 p-2 flex flex-col gap-1.5 bg-base-100">
              <template v-if="availableSearchQuery.trim()">
                <div v-if="loadingCategoryChallenges" class="flex justify-center py-4"><span class="loading loading-spinner loading-xs text-primary"></span></div>
                <div v-else-if="!filteredSearchedChallenges.length" class="text-center py-4 font-code text-xs text-base-content/25">Aucun challenge trouvé</div>
                <div
                  v-for="ch in filteredSearchedChallenges" :key="ch.id"
                  @click="toggleSelectChallengeForRot(ch.id)"
                  :class="[
                    'flex items-center justify-between px-3 py-2 border font-code text-xs transition-colors',
                    conflictingChallengeIds.has(ch.id) ? 'bg-base-300/40 border-base-300 text-base-content/40 cursor-not-allowed opacity-60' : 
                    selectedChallengesToAddToRot.includes(ch.id) ? 'bg-primary/15 border-primary text-primary font-bold cursor-pointer' : 'bg-base-200/60 border-base-300 text-base-content hover:bg-base-300/50 cursor-pointer'
                  ]"
                  :title="conflictingChallengeIds.has(ch.id) ? 'Conflit temporel : déjà planifié dans une autre rotation sur cette période' : ''"
                >
                  <span class="truncate">{{ ch.name }}</span>
                  <span class="text-[10px]">
                    {{ conflictingChallengeIds.has(ch.id) ? 'Conflit temporel' : selectedChallengesToAddToRot.includes(ch.id) ? '✓ Sélectionné' : 'Ajouter' }}
                  </span>
                </div>
              </template>
              <template v-else>
                <div v-if="!categories.length" class="text-center py-4 font-code text-xs text-base-content/25">Aucune catégorie disponible</div>
                
                <div v-for="cat in categories" :key="cat.id" class="border border-base-300/60 overflow-hidden">
                  <div
                    @click="toggleRotationCategory(cat.id)"
                    class="flex items-center justify-between px-3 py-2 bg-base-200/70 cursor-pointer hover:bg-base-300 transition-colors select-none"
                  >
                    <div class="flex items-center gap-2">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 text-base-content/50 transition-transform duration-200" :class="{ 'rotate-90': expandedRotCategory === cat.id }" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                      </svg>
                      <span class="font-code text-xs font-bold text-base-content">{{ cat.name }}</span>
                    </div>
                  </div>
                  <div v-if="expandedRotCategory === cat.id" class="p-2 flex flex-col gap-1.5 bg-base-100/50">
                    <div v-if="loadingCategoryChallenges" class="flex justify-center py-4"><span class="loading loading-spinner loading-xs text-primary"></span></div>
                    <div v-else-if="!rotationCategoryChallenges[cat.id]?.filter(ch => !challengesInRot.has(ch.id)).length" class="text-center py-3 text-xs text-base-content/50 font-code">
                      Aucun challenge de cette catégorie disponible.
                    </div>
                    <div
                      v-for="ch in rotationCategoryChallenges[cat.id]?.filter(ch => !challengesInRot.has(ch.id))" :key="ch.id"
                      @click="toggleSelectChallengeForRot(ch.id)"
                      :class="[
                        'flex items-center justify-between px-3 py-1.5 border font-code text-xs transition-colors',
                        conflictingChallengeIds.has(ch.id) ? 'bg-base-300/40 border-base-300 text-base-content/40 cursor-not-allowed opacity-60' : 
                        selectedChallengesToAddToRot.includes(ch.id) ? 'bg-primary/15 border-primary text-primary font-bold cursor-pointer' : 'bg-base-200/40 border-base-300 text-base-content hover:bg-base-300/60 cursor-pointer'
                      ]"
                      :title="conflictingChallengeIds.has(ch.id) ? 'Conflit temporel : déjà planifié dans une autre rotation sur cette période' : ''"
                    >
                      <span class="truncate">{{ ch.name }}</span>
                      <span class="text-[10px]">
                        {{ conflictingChallengeIds.has(ch.id) ? 'Conflit temporel' : selectedChallengesToAddToRot.includes(ch.id) ? '✓ Sélectionné' : 'Ajouter' }}
                      </span>
                    </div>
                  </div>
                </div>
              </template>
            </div>
            <button
              v-if="selectedChallengesToAddToRot.length > 0"
              @click="addSelectedToRot"
              class="w-full py-2 bg-primary text-base-100 hover:bg-primary/80 font-code text-xs font-bold tracking-wider transition-colors shadow-sm"
            >
              Ajouter la sélection ({{ selectedChallengesToAddToRot.length }})
            </button>
          </div>
          <div class="flex flex-col gap-2">
            <p class="font-code text-[10px] uppercase text-base-content/40 mb-2">
              Challenges dans la rotation <span class="text-base-content/25 ml-1">{{ rotationChallenges.length }}</span>
            </p>
            <div class="max-h-56 overflow-auto border border-base-300 p-2 flex flex-col gap-1.5 bg-base-100">
              <div v-if="!rotationChallenges.length" class="text-center py-4 font-code text-xs text-base-content/25">Aucun challenge dans cette rotation</div>
              <div
                v-for="c in rotationChallenges" :key="c.id"
                @click="toggleSelectChallengeToRemoveFromRot(c.id)"
                :class="[
                  'flex items-center justify-between px-3 py-2 border font-code text-xs cursor-pointer transition-colors',
                  selectedChallengesToRemoveFromRot.includes(c.id) ? 'bg-error/15 border-error text-error font-bold' : 'bg-primary/5 border-primary/25 text-base-content hover:bg-primary/10'
                ]"
              >
                <span class="truncate">{{ c.name }}</span>
                <span class="text-[10px] opacity-60">{{ selectedChallengesToRemoveFromRot.includes(c.id) ? '✓ Sélectionné' : 'Retirer' }}</span>
              </div>
            </div>
            <button
              v-if="selectedChallengesToRemoveFromRot.length > 0"
              @click="removeSelectedFromRot"
              class="w-full py-2 bg-error text-base-100 hover:bg-error/80 font-code text-xs font-bold tracking-wider transition-colors shadow-sm"
            >
              Retirer la sélection ({{ selectedChallengesToRemoveFromRot.length }})
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div v-if="activeTab === 'category_list'" class="flex flex-col gap-4 w-full">
    <div class="flex justify-start">
      <button
        @click="openCreateCatModal"
        class="flex items-center gap-2 bg-primary text-base-100 hover:bg-primary/80 px-4 py-2 font-code text-xs font-bold tracking-wider transition-colors shadow-sm"
      >
        <span>+ Créer une nouvelle catégorie</span>
      </button>
    </div>
    <div v-if="loadingCategories" class="flex justify-center py-20">
      <span class="loading loading-spinner loading-md text-primary"></span>
    </div>
    <div v-else-if="!categories.length" class="flex flex-col items-center justify-center py-10 gap-1">
      <span class="font-text text-sm text-base-content/40">Aucune catégorie trouvée.</span>
    </div>
    <div v-else class="flex flex-col gap-1.5">
      <div v-for="cat in categories" :key="cat.id" class="border border-base-200/50 overflow-hidden">
        <div
          @click="toggleCategory(cat.id)"
          class="flex items-center gap-3 px-4 py-3 cursor-pointer select-none hover:bg-base-300/40 transition-colors duration-150"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-base-content/50 transition-transform duration-200 shrink-0" :class="{ 'rotate-90': expandedCategory === cat.id }" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
          <span class="font-text text-[10px] px-2 py-0.5 leading-none bg-base-300 text-base-content/70 border border-base-300 shrink-0">
            {{ cat.challenge_count ?? 0 }} CHALLENGE{{ cat.challenge_count > 1 ? 'S' : '' }}
          </span>
          <span class="font-text font-semibold text-base-content text-sm flex-1 truncate">{{ cat.name }}</span>
          <span class="font-text text-base-content text-xs flex-1 truncate">{{ cat.description }}</span>
          <button class="font-text text-xs text-info hover:text-info/70 px-1 shrink-0" @click.stop="openEditCatModal(cat)" title="Modifier">Modifier</button>
          <button 
            class="font-text text-xs px-1 shrink-0 transition-colors"
            :class="(cat.challenge_count ?? 0) > 0 ? 'text-base-content/20 cursor-not-allowed' : 'text-error hover:text-error/70'"
            @click.stop="(cat.challenge_count ?? 0) === 0 && deleteCategory(cat.id, cat.name)" 
            :title="(cat.challenge_count ?? 0) > 0 ? 'Impossible de supprimer : des challenges sont liés à cette catégorie' : 'Supprimer'"
          >
            Supprimer
          </button>
        </div>
        <div v-if="expandedCategory === cat.id" class="bg-base-200/20 border-t border-base-200/50 p-3 animate-fade-in">
          <div v-if="loadingCategoryChallenges" class="flex justify-center py-4"><span class="loading loading-spinner loading-xs text-primary"></span></div>
          <div v-else-if="!categoryChallenges.length" class="text-center py-3 text-xs text-base-content/50 font-text">Aucun challenge dans cette catégorie.</div>
          <div v-else class="flex flex-col gap-1.5">
            <div v-for="chal in categoryChallenges" :key="chal.id" class="grid grid-cols-[1fr_100px_100px] items-center px-3 py-2 bg-base-100 border border-base-300 text-xs font-text gap-5">
              <span class="font-semibold text-base-content truncate min-w-0">{{ chal.name }}</span>
              <span class="text-[10px] text-base-content/40 font-code text-center">{{ chal.points }} points</span>
              <div class="flex justify-end gap-1">
                <span :class="['font-text text-[10px] px-2 py-0.5 leading-none', diffClass(chal.difficulty)]">{{ chal.difficulty }}</span>
                <span :class="['font-text text-[10px] px-2 py-0.5 leading-none', typeClass(chal.type)]">{{ chal.type }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  </div>
  <div v-if="rotModal.isOpen" class="fixed inset-0 z-40 flex items-center justify-center bg-base-300/80 backdrop-blur-sm p-4">
    <div class="bg-base-100 border border-base-300 shadow-2xl max-w-lg w-full p-6 animate-fade-in">
      <div class="flex justify-between items-center mb-6">
        <div>
          <p class="font-code text-[10px] tracking-widest uppercase text-base-content/35 mb-1">{{ rotModal.mode === 'create' ? 'Nouvelle rotation' : 'Rotation #' + editRotTarget }}</p>
          <h2 class="font-titre font-bold text-lg text-base-content">{{ rotModal.mode === 'create' ? 'Créer une rotation' : 'Modifier la rotation' }}</h2>
        </div>
        <button @click="rotModal.isOpen = false" class="text-base-content/50 hover:text-base-content text-xl leading-none">&times;</button>
      </div>
      <div class="flex flex-col gap-4">
        <input v-if="rotModal.mode === 'create'" v-model="rotationForm.name" type="text" placeholder="Semaine 1" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm w-full transition-colors" />
        <input v-else v-model="editRotForm.name" type="text" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm w-full transition-colors" />
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <input v-if="rotModal.mode === 'create'" v-model="rotationForm.start_time" type="datetime-local" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm w-full transition-colors" />
          <input v-else v-model="editRotForm.start_time" type="datetime-local" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm w-full transition-colors" />
          <input v-if="rotModal.mode === 'create'" v-model="rotationForm.end_time" type="datetime-local" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm w-full transition-colors" />
          <input v-else v-model="editRotForm.end_time" type="datetime-local" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm w-full transition-colors" />
        </div>
      </div>
      <div class="flex justify-end gap-3 mt-8">
        <button @click="rotModal.isOpen = false" class="py-2 px-5 border border-base-300 font-code text-xs text-base-content/70 hover:text-base-content hover:bg-base-200 transition-colors">Annuler</button>
        <button v-if="rotModal.mode === 'create'" @click="createRotation" :disabled="creatingRotation || !rotationForm.name || !rotationForm.start_time || !rotationForm.end_time" class="py-2 px-5 bg-primary text-base-100 font-code text-xs hover:bg-primary/80 disabled:opacity-50 transition-colors">
          <span v-if="creatingRotation" class="loading loading-spinner loading-xs"></span><span v-else>Créer</span>
        </button>
        <button v-else @click="submitEditRot" :disabled="editingRot" class="py-2 px-5 bg-warning text-base-100 font-code text-xs hover:bg-warning/80 disabled:opacity-50 transition-colors">
          <span v-if="editingRot" class="loading loading-spinner loading-xs"></span><span v-else>Sauvegarder</span>
        </button>
      </div>
    </div>
  </div>
  <div v-if="catModal.isOpen" class="fixed inset-0 z-40 flex items-center justify-center bg-base-300/80 backdrop-blur-sm p-4">
    <div class="bg-base-100 border border-base-300 shadow-2xl max-w-lg w-full p-6 animate-fade-in">
      <div class="flex justify-between items-center mb-6">
        <div>
          <p class="font-code text-[10px] tracking-widest uppercase text-base-content/35 mb-1">{{ catModal.mode === 'create' ? 'Nouvelle catégorie' : 'Catégorie #' + editCatTarget }}</p>
          <h2 class="font-titre font-bold text-lg text-base-content">{{ catModal.mode === 'create' ? 'Créer une catégorie' : 'Modifier la catégorie' }}</h2>
        </div>
        <button @click="catModal.isOpen = false" class="text-base-content/50 hover:text-base-content text-xl leading-none">&times;</button>
      </div>
      <div class="flex flex-col gap-4">
        <input v-if="catModal.mode === 'create'" v-model="catForm.name" type="text" placeholder="Nom de la catégorie..." class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm w-full transition-colors" />
        <input v-else v-model="editCatForm.name" type="text" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm w-full transition-colors" />
        <textarea v-if="catModal.mode === 'create'" v-model="catForm.description" rows="3" placeholder="Description de la catégorie..." class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm w-full resize-none transition-colors"></textarea>
        <textarea v-else v-model="editCatForm.description" rows="3" class="bg-base-100 border border-base-300 focus:border-primary outline-none px-3 py-2 font-code text-sm w-full resize-none transition-colors"></textarea>
      </div>
      <div class="flex justify-end gap-3 mt-8">
        <button @click="catModal.isOpen = false" class="py-2 px-5 border border-base-300 font-code text-xs text-base-content/70 hover:text-base-content hover:bg-base-200 transition-colors">Annuler</button>
        <button v-if="catModal.mode === 'create'" @click="createCategory" :disabled="creatingCat || !catForm.name" class="py-2 px-5 bg-primary text-base-100 font-code text-xs hover:bg-primary/80 disabled:opacity-50 transition-colors">
          <span v-if="creatingCat" class="loading loading-spinner loading-xs"></span><span v-else>Créer</span>
        </button>
        <button v-else @click="submitEditCat" class="py-2 px-5 bg-warning text-base-100 font-code text-xs hover:bg-warning/80 disabled:opacity-50 transition-colors">
          Sauvegarder
        </button>
      </div>
    </div>
  </div>
  <Teleport to="body">
    <div v-if="historyPanelOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4" @click.self="historyPanelOpen = false">
      <div class="w-full max-w-3xl max-h-[85vh] bg-base-200 border border-base-300 flex flex-col">
        <div class="flex items-center justify-between px-5 py-3 border-b border-base-300">
          <p class="font-stitre font-bold text-sm text-base-content">Soumissions — {{ challengeDetail?.name }}</p>
          <div class="flex items-center gap-4">
            <button @click="downloadHistoryCsv" :disabled="exportingHistory" class="font-code text-xs text-base-content/40 hover:text-primary disabled:opacity-30">
              <span v-if="exportingHistory" class="loading loading-xs"></span>
              <span v-else>⬇ Exporter en CSV</span>
            </button>
            <button @click="historyPanelOpen = false" class="font-code text-xs text-error hover:text-error/70">Fermer</button>
          </div>
        </div>
        <div class="flex-1 overflow-y-auto px-5 py-3">
          <div v-if="loadingHistory && !challengeHistory.length" class="flex justify-center py-10">
            <span class="loading loading-dots loading-sm text-primary"></span>
          </div>
          <div v-else-if="!challengeHistory.length" class="text-center py-10 font-text text-sm text-base-content/25">Aucune soumission</div>
          <div v-else class="overflow-x-auto">
            <table class="w-full text-[11px] font-code">
              <thead>
                <tr class="text-base-content/40 border-b border-base-300">
                  <th class="text-left py-1.5 pr-3 font-normal">ID</th>
                  <th class="text-left py-1.5 pr-3 font-normal">Username</th>
                  <th class="text-left py-1.5 pr-3 font-normal">Flag soumis</th>
                  <th class="text-left py-1.5 pr-3 font-normal">Valide</th>
                  <th class="text-left py-1.5 pr-3 font-normal">Type de flag</th>
                  <th class="text-left py-1.5 pr-3 font-normal">Date de soumission</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="entry in challengeHistory" :key="entry.submission_id"
                  :class="['border-b border-base-300/50', entry.is_correct ? 'bg-success/8' : 'bg-error/8']"
                >
                  <td class="py-1.5 pr-3 text-base-content/60">{{ entry.submission_id }}</td>
                  <td class="py-1.5 pr-3 text-base-content font-medium">{{ entry.username }}</td>
                  <td class="py-1.5 pr-3 text-base-content">{{ entry.flag_submitted ?? '—' }}</td>
                  <td class="py-1.5 pr-3" :class="entry.is_correct ? 'text-success' : 'text-error'">{{ entry.is_correct ? 'Oui' : 'Non' }}</td>
                  <td class="py-1.5 pr-3 text-base-content/60">{{ entry.flag_type ?? '—' }}</td>
                  <td class="py-1.5 pr-3 text-base-content/35">{{ entry.submitted_at }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <button
            v-if="challengeHistory.length && challengeHistory.length % 20 === 0"
            @click="fetchHistory(challengeDetail.value?.id ?? challengeDetail?.id, historyOffset)"
            :disabled="loadingHistory"
            class="mt-3 w-full py-1.5 font-code text-xs text-base-content/40 hover:text-base-content/70 border border-base-300 hover:border-base-content/20 transition-colors disabled:opacity-30"
          >
            <span v-if="loadingHistory" class="loading loading-xs"></span>
            <span v-else>Charger plus ↓</span>
          </button>
        </div>
      </div>
    </div>
  </Teleport>
  <Teleport to="body">
    <div v-if="rotationPanelOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4" @click.self="rotationPanelOpen = false">
      <div class="w-full max-w-3xl max-h-[85vh] bg-base-200 border border-base-300 flex flex-col">
        <div class="flex items-center justify-between px-5 py-3 border-b border-base-300">
          <p class="font-stitre font-bold text-sm text-base-content">Rotations — {{ challengeDetail?.name }}</p>
          <button @click="rotationPanelOpen = false" class="font-code text-xs text-error hover:text-error/70">Fermer</button>
        </div>
        <div class="flex-1 overflow-y-auto px-5 py-3">
          <div v-if="loadingRotation" class="flex justify-center py-10">
            <span class="loading loading-dots loading-sm text-primary"></span>
          </div>
          <div v-else-if="!challengeRotation.length" class="text-center py-10 font-text text-sm text-base-content/25">Aucune rotation associée à ce challenge</div>
          <div v-else class="overflow-x-auto">
            <table class="w-full text-[11px] font-code">
              <thead>
                <tr class="text-base-content/40 border-b border-base-300">
                  <th class="text-left py-1.5 pr-3 font-normal">ID</th>
                  <th class="text-left py-1.5 pr-3 font-normal">Nom de la rotation</th>
                  <th class="text-left py-1.5 pr-3 font-normal">Début</th>
                  <th class="text-left py-1.5 pr-3 font-normal">Fin</th>
                  <th class="text-left py-1.5 pr-3 font-normal">Active</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="rot in challengeRotation" :key="rot.id ?? rot"
                  class="border-b border-base-300/50 hover:bg-base-300/30"
                >
                  <td class="py-2 pr-3 text-base-content/60">{{ rot.id ?? '—' }}</td>
                  <td class="py-2 pr-3 text-base-content font-medium">{{ rot.name ?? ('Rotation #' + rot) }}</td>
                  <td class="py-2 pr-3 text-base-content/60">{{ rot.start_time ?? '—' }}</td>
                  <td class="py-2 pr-3 text-base-content/60">{{ rot.end_time ?? '—' }}</td>
                  <td class="py-1.5 pr-3" :class="rot.is_active ? 'text-success' : 'text-error'">{{ rot.is_active ? 'Oui' : 'Non' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
  <PopUpConfirm
    :is-open="confirmModal.isOpen"
    :title="confirmModal.title"
    :message="confirmModal.message"
    @confirm="handleConfirmDialog"
    @cancel="closeConfirmDialog"
  />
</template>