<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

axios.defaults.withCredentials = true

const route = useRoute()
const router = useRouter()
const activeTab = ref('challenge')
const loading = ref(true)
const submitting = ref(false)
const justValidated = ref(false)
const justFailed = ref(false)
const challenge = ref({
  id: route.params.id,
  title: '',
  category: '',
  points: 0,
  difficulty: '',
  solves: 0,
  hasInstance: false,
  description: '',
  files: [],
  solvers: [],
  is_validated: false,
  type: '',
  rotation: null,
  is_active: true,
  docker_image_id: null,
  external_url: null,
  rotation_start: null,
  has_other_instance: false
})
const flag = ref('')
const submissionStatus = ref(null)
const submissionMessage = ref('')
const launchingInstance = ref(false)
const stoppingInstance = ref(false)
const dockerInstanceUrl = ref(null)
const dockerExpiresAt = ref(null)
const dockerTimeLeftStr = ref('')
let dockerTimerInterval = null
const updateDockerCountdown = () => {
  if (!dockerExpiresAt.value) {
    dockerTimeLeftStr.value = ''
    return
  }
  const now = new Date()
  const end = new Date(dockerExpiresAt.value)
  const diff = end - now
  if (diff <= 0) {
    dockerTimeLeftStr.value = "Expiré"
    dockerInstanceUrl.value = null
    dockerExpiresAt.value = null
    return
  }
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
  const seconds = Math.floor((diff % (1000 * 60)) / 1000)
  let segments = []
  if (hours > 0) segments.push(`${hours}h`)
  segments.push(`${minutes}m`, `${seconds}s`)
  dockerTimeLeftStr.value = segments.join(' ')
}
const handleChallengeAccess = async () => {
  if (challenge.value.external_url) {
    let url = challenge.value.external_url.trim()
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      url = 'https://' + url
    }
    window.open(url, '_blank')
    return
  }
  if (challenge.value.docker_image_id) {
    if (dockerInstanceUrl.value) {
      let instanceUrl = dockerInstanceUrl.value.trim()
      if (!instanceUrl.startsWith('http://') && !instanceUrl.startsWith('https://')) {
        instanceUrl = 'https://' + instanceUrl
      }
      window.open(instanceUrl, '_blank')
      return
    }
    launchingInstance.value = true
    try {
      const challengeId = route.params.id
      const response = await axios.post(`/api/user/challenge/${challengeId}/launch`)
      if (response.data?.status === 'success') {
        dockerInstanceUrl.value = response.data.instance_url
        dockerExpiresAt.value = response.data.instance_expires_at
        
        if (dockerTimerInterval) clearInterval(dockerTimerInterval)
        dockerTimerInterval = setInterval(updateDockerCountdown, 1000)
        updateDockerCountdown()
      }
    } catch (error) {
      alert(error.response?.data?.message || "Impossible de lancer l'instance.")
    } finally {
      launchingInstance.value = false
    }
  }
}
const stopInstance = async () => {
  stoppingInstance.value = true
  try {
    const challengeId = route.params.id
    const response = await axios.post(`/api/user/challenge/${challengeId}/instance/stop`)
    if (response.data?.status === 'success') {
      dockerInstanceUrl.value = null
      dockerExpiresAt.value = null
      dockerTimeLeftStr.value = ''
      if (dockerTimerInterval) clearInterval(dockerTimerInterval)
      // Recharge les détails pour actualiser l'état global du challenge
      await fetchChallengeDetails()
    }
  } catch (error) {
    alert(error.response?.data?.message || "Impossible de fermer l'instance.")
  } finally {
    stoppingInstance.value = false
  }
}
const selectedFile = ref(null)
const openFileModal = (file) => {
  selectedFile.value = file
}
const timeLeftStr = ref('')
let timerInterval = null
const updateCountdown = () => {
  if (!challenge.value || (challenge.value.type || '').toUpperCase() !== 'ROTATION') {
    timeLeftStr.value = ''
    return
  }
  const now = new Date()
  let targetDate = null
  let isOpening = false
  if (!challenge.value.is_active && challenge.value.rotation_start) {
    const [datePart, timePart] = challenge.value.rotation_start.split(' ')
    const [day, month, year] = datePart.split('/')
    targetDate = new Date(`${year}-${month}-${day}T${timePart}`)
    isOpening = true
  } else if (challenge.value.is_active && challenge.value.rotation_end) {
    const [datePart, timePart] = challenge.value.rotation_end.split(' ')
    const [day, month, year] = datePart.split('/')
    targetDate = new Date(`${year}-${month}-${day}T${timePart}`)
    isOpening = false
  }
  if (!targetDate) {
    timeLeftStr.value = ''
    return
  }
  const diff = targetDate - now
  if (diff <= 0) {
    timeLeftStr.value = isOpening ? "Ouverture imminente..." : "Expiré"
    return
  }
  const oneDayMs = 24 * 60 * 60 * 1000
  const prefix = isOpening ? "Ouverture dans : " : "Temps restant : "
  if (diff > oneDayMs) {
    const days = Math.floor(diff / oneDayMs)
    const hours = Math.floor((diff % oneDayMs) / (1000 * 60 * 60))
    let segments = []
    if (days > 0) segments.push(`${days}j`)
    if (hours > 0 || days === 0) segments.push(`${hours}h`)
    timeLeftStr.value = `${prefix}${segments.join(' ')}`
  } 
  else {
    const hours = Math.floor(diff / (1000 * 60 * 60))
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
    const seconds = Math.floor((diff % (1000 * 60)) / 1000)
    let segments = []
    if (hours > 0) segments.push(`${hours}h`)
    segments.push(`${minutes}m`, `${seconds}s`)
    timeLeftStr.value = `${prefix}${segments.join(' ')}`
  }
}
const difficultyColor = computed(() => {
  const diffLower = (challenge.value.difficulty || '').toLowerCase()
  if (diffLower === 'easy' || diffLower === 'facile') return 'text-success'
  if (diffLower === 'medium' || diffLower === 'moyen') return 'text-warning'
  if (diffLower === 'hard' || diffLower === 'difficile') return 'text-error'
  if (diffLower === 'insane' || diffLower === 'extrême') return 'text-[#a855f7]'
  return 'text-base-content/70'
})
const fetchChallengeDetails = async () => {
  loading.value = true
  try {
    const challengeId = route.params.id
    const response = await axios.get(`/api/user/challenge/${challengeId}/info`)
    const resData = response.data.challenge || response.data
    console.log("Détails du challenge récupérés :", resData)
    challenge.value = {
      id: resData.id,
      title: resData.name || 'Sans titre',
      category: resData.category?.name || resData.category || 'DIVERS',
      points: resData.points || 0,
      difficulty: resData.difficulty || 'Non défini',
      description: resData.description || 'Aucune description fournie.',
      is_active: resData.is_active ?? true,
      is_validated: !!resData.is_validated,
      hasInstance: resData.type === 'DYNAMIC' || !!resData.is_dynamic,
      files: [],
      solvers: resData.success_history || [],
      solves: resData.success_history ? resData.success_history.length : 0,
      type: resData.type || 'PERMANENT',
      rotation: resData.rotation || null,
      rotation_start: resData.rotation_start || null,
      rotation_end: resData.rotation_end || null,
      docker_image_id: resData.docker_image_id ?? null,
      external_url: resData.external_url ?? null,
      has_other_instance: !!resData.has_other_instance
    }
    if (resData.active_instance) {
      dockerInstanceUrl.value = resData.active_instance.url
      dockerExpiresAt.value = resData.active_instance.expires_at
      
      if (dockerTimerInterval) clearInterval(dockerTimerInterval)
      dockerTimerInterval = setInterval(updateDockerCountdown, 1000)
      updateDockerCountdown()
    } else {
      dockerInstanceUrl.value = null
      dockerExpiresAt.value = null
      dockerTimeLeftStr.value = ''
      if (dockerTimerInterval) clearInterval(dockerTimerInterval)
    }
    if (challenge.value.is_active) {
      try {
        const file = await axios.get(`/api/user/challenge/${challengeId}/files/list`)
        challenge.value.files = (file.data.files || []).map(f => {
          let cleanUrl = f.file_url || ''
          if (cleanUrl.startsWith('.')) {
            cleanUrl = cleanUrl.substring(1)
          }
          const fullFileUrl = `http://127.0.0.1:9414${cleanUrl}`
          return {
            name: f.file_name,
            url: fullFileUrl,
            type: f.file_type,
            role: f.file_role,
            sha: f.sha256,
            size: f.file_size
          }
        })
      } catch (fileErr) {
        console.warn("Impossible de récupérer les fichiers du challenge", fileErr)
      }
    }
    if (challenge.value.is_validated) {
      submissionStatus.value = 'success'
      submissionMessage.value = 'Vous avez déjà validé ce challenge !'
    }
  } catch (error) {
    console.error("Erreur lors de la récupération des détails du challenge :", error)
  } finally {
    loading.value = false
  }
}
const showSuccessPopup = ref(false)
const animatedPoints = ref(0)
const animatedXP = ref(0)
const animateValue = (refVar, endValue, duration) => {
  let startTimestamp = null
  const step = (timestamp) => {
    if (!startTimestamp) startTimestamp = timestamp
    const progress = Math.min((timestamp - startTimestamp) / duration, 1)
    const easeOutQuart = 1 - Math.pow(1 - progress, 4)
    refVar.value = Math.floor(easeOutQuart * endValue)
    if (progress < 1) {
      window.requestAnimationFrame(step)
    }
  }
  window.requestAnimationFrame(step)
}
const submitFlag = async () => {
  if (!flag.value || !challenge.value.is_active) return
  submitting.value = true
  submissionStatus.value = null
  const payload = { flag: flag.value.trim() }
  try {
    const challengeId = route.params.id
    const response = await axios.post(`/api/user/challenge/${challengeId}/validate`, payload)
    if (response.data?.status === 'success' || response.data?.success || response.status === 200) {
      const points = response.data?.points_awarded
      const xp = response.data?.xp_awarded
      triggerSuccess(points, xp)
    } else {
      throw new Error('Faux négatif')
    }
  } catch (error) {
    justFailed.value = true
    setTimeout(() => { justFailed.value = false }, 2500)
    try {
      const verifyRes = await axios.get(`/api/user/challenge/${route.params.id}/info`)
      const chalData = verifyRes.data.challenge || verifyRes.data
      if (chalData.is_validated) {
        triggerSuccess(chalData.points, chalData.points)
        return
      }
    } catch (e) { }
    submissionStatus.value = 'error'
    submissionMessage.value = error.response?.data?.message || 'Flag incorrect. Essayez encore !'
    setTimeout(() => { if (submissionStatus.value === 'error') submissionStatus.value = null }, 5000)
  } finally {
    submitting.value = false
  }
}
const triggerSuccess = (pointsGained = challenge.value.points, xpGained = challenge.value.xp) => {
  submissionStatus.value = 'success'
  submissionMessage.value = 'Correct ! Vous avez validé ce challenge.'
  challenge.value.is_validated = true
  flag.value = '01100110 01101100 01100001 01100111'
  justValidated.value = true
  animatedPoints.value = 0
  animatedXP.value = 0
  showSuccessPopup.value = true
  animateValue(animatedPoints, pointsGained, 1500)
  setTimeout(() => {
    animateValue(animatedXP, xpGained, 1500)
  }, 600)
  setTimeout(() => {
    showSuccessPopup.value = false
  }, 6000)
  fetchChallengeDetails()
}
const startInstance = async () => {
  if (!challenge.value.is_active) return
  try {
    const challengeId = route.params.id
    const response = await axios.post(`/api/user/challenge/${challengeId}/generate`)
    alert(response.data.message || "Instance démarrée avec succès !")
  } catch (error) {
    alert("Impossible de démarrer l'environnement dynamique.")
  }
}


async function downloadFile(file) {
  try {
    const response = await axios.get(file.url, { responseType: 'blob' })
    const blob = new Blob([response.data])
    const link = document.createElement('a')
    link.href = window.URL.createObjectURL(blob)
    link.download = file.name 
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(link.href)
  } catch (error) {
    console.error("Erreur lors du téléchargement", error)
  }
}

watch(() => challenge.value.type, () => {
  updateCountdown()
})


onMounted(() => {
  fetchChallengeDetails()
  timerInterval = setInterval(updateCountdown, 1000)
})
onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
  if (dockerTimerInterval) clearInterval(dockerTimerInterval)
})
</script>
<template>
  <div v-if="challenge.is_validated" class="fixed top-[65px] bottom-[65px] left-0 right-0 pointer-events-none z-[100]"
    :class="justValidated ? 'animate-glow-success' : 'static-glow-success'"></div>
  <div v-if="justFailed"
    class="fixed top-[65px] bottom-[65px] left-0 right-0 pointer-events-none z-[100] animate-glow-error"></div>
  <div class="max-w-[1800px] mx-auto w-full animate-fade-in pb-20 pt-6 px-4 relative z-10">
    <div class="flex justify-between items-center mb-8">
      <button @click="router.push('/challenges')"
        class="btn btn-sm btn-ghost font-text text-base-content/60 hover:text-primary gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        Retour aux challenges
      </button>
      <div v-if="timeLeftStr"
        class="flex items-center gap-2 font-text text-xs bg-warning/10 text-warning border border-warning/20 py-1.5 px-3 rounded-lg">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-warning" fill="none" viewBox="0 0 24 24"
          stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span class="font-mono font-bold tracking-wide">{{ timeLeftStr }}</span>
      </div>
    </div>
    <div v-if="loading" class="flex flex-col items-center justify-center py-20 gap-4 text-primary">
      <span class="loading loading-ring loading-lg"></span>
      <p class="font-mono text-sm uppercase tracking-wider opacity-70 animate-pulse">Chargement du challenge...</p>
    </div>
    <div v-else>
      <div class="flex border-b border-base-300 mb-8 w-full">
        <button @click="activeTab = 'challenge'"
          class="flex-1 py-3 text-center font-titre text-lg transition duration-100"
          :class="activeTab === 'challenge' ? 'text-primary border-b-2 border-primary' : 'hover:bg-base-200/50 text-base-content/60'">
          CHALLENGE
        </button>
        <button @click="activeTab = 'solves'" class="flex-1 py-3 text-center font-titre text-lg transition duration-100"
          :class="activeTab === 'solves' ? 'text-primary border-b-2 border-primary' : 'hover:bg-base-200/50 text-base-content/60'">
          {{ challenge.solves }} RÉSOLUTION{{ challenge.solves > 1 ? 'S' : '' }}
        </button>
      </div>
      <div class="min-h-[400px] w-full">
        <div v-show="activeTab === 'challenge'" class="animate-fade-in w-full">
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
            <div class="lg:col-span-2 space-y-6">
              <div>
                <h1
                  class="text-4xl md:text-5xl font-titre font-bold text-primary mb-2 tracking-wide flex items-center gap-4">
                  {{ challenge.title }}
                  <span v-if="challenge.is_validated"
                    class="text-success text-2xl drop-shadow-[0_0_10px_rgba(0,255,0,0.5)]" title="Validé">✔</span>
                </h1>
              </div>
              <div class="bg-base-200/40 border border-base-300 p-6 md:p-8 shadow-xl backdrop-blur-xs">
                <h2 class="font-stitre text-xs opacity-50 uppercase tracking-widest mb-6 flex items-center gap-2">
                  Description du challenge
                </h2>
                <div class="prose prose-invert max-w-none text-base-content/80 leading-relaxed font-text"
                  v-html="challenge.description"></div>
              </div>
              <div
                class="bg-base-200/40 border border-base-300 p-6 md:p-8 shadow-xl backdrop-blur-xs transition-colors duration-500"
                :class="{ 'border-success/40 bg-success/5 shadow-[0_0_30px_rgba(0,255,0,0.1)]': challenge.is_validated }">
                <h2 class="font-stitre text-xs opacity-50 uppercase tracking-widest border-b border-base-300 pb-2 mb-4">
                  Flag
                </h2>
                <div v-if="!challenge.is_active" 
                  class="w-full py-12 px-6 bg-error/10 border border-error/30 backdrop-blur-md flex flex-col items-center justify-center text-center gap-3 shadow-[0_0_30px_rgba(239,68,68,0.15)]">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-error animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                  <div>
                    <h3 class="font-titre font-bold text-lg text-error tracking-wider uppercase">Challenge Verrouillé</h3>
                    <p class="font-text text-xs text-base-content/60 mt-1">Ce challenge n'est pas actif actuellement.</p>
                  </div>
                </div>
                <div v-else>
                  <form @submit.prevent="submitFlag" class="w-full">
                    <div class="flex w-full gap-2">
                      <input v-model="flag" type="text" 
                        :placeholder="challenge.is_validated ? '01100110 01101100 01100001 01101111' : 'GH{flag_ici_xxxx}'"
                        class="input input-sm input-bordered w-full bg-base-100 focus:border-primary font-text text-center"
                        required :disabled="challenge.is_validated" />
                      <button type="submit" class="btn btn-primary btn-sm px-8 font-bold font-titre"
                        :disabled="challenge.is_validated || flag.length === 0 || submitting">
                        <span v-if="submitting" class="loading loading-spinner loading-xs"></span>
                        <span v-else>SOUMETTRE</span>
                      </button>
                    </div>
                  </form>
                </div>
                <transition name="fade">
                  <div v-if="submissionStatus" class="pt-2">
                    <div v-if="submissionStatus === 'success'"
                      class="alert alert-success flex items-center justify-center gap-3 py-2 rounded-lg">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 shrink-0 stroke-current" fill="none"
                        viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span class="font-text text-xs font-bold">{{ submissionMessage }}</span>
                    </div>
                    <div v-if="submissionStatus === 'error'"
                      class="alert alert-error flex items-center justify-center gap-3 py-2 rounded-lg">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 shrink-0 stroke-current" fill="none"
                        viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span class="font-text text-xs font-bold">{{ submissionMessage }}</span>
                    </div>
                  </div>
                </transition>
              </div>
            </div>
            <div class="space-y-8">
              <div class="bg-base-200/40 border border-base-300 p-8 shadow-xl backdrop-blur-xs">
                <div
                  class="flex justify-center items-center gap-3 font-text text-sm mb-6 bg-base-300/50 py-2 border border-base-300/50">
                  <span class="font-bold font-text uppercase text-xs">{{ challenge?.category || 'DIVERS' }}</span>
                  <span class="opacity-30">|</span>
                  <span class="text-secondary font-bold text-base font-code">{{ challenge?.points || 0 }} points</span>
                  <span class="opacity-30">|</span>
                  <span class="font-bold uppercase text-xs" :class="difficultyColor">{{ challenge?.difficulty || 'Nondéfini' }}</span>
                </div>
                <div v-if="challenge.is_active">
                  <div v-if="challenge?.files && challenge.files.length > 0">
                    <span
                      class="block text-[10px] opacity-50 font-stitre uppercase tracking-widest mb-3 border-b border-base-300 pb-2">
                      Fichiers
                    </span>
                    <div class="space-y-2">
                      <div v-for="(file, fIdx) in challenge.files" :key="fIdx" @click="openFileModal(file)"
                        class="flex items-center justify-between p-3 bg-base-100 border border-base-300 hover:border-primary/50 cursor-pointer transition-colors group font-text text-xs">
                        
                        <div class="flex items-center gap-2.5 min-w-0 pr-2">
                          <span class="text-[9px] uppercase font-mono px-1.5 py-0.5 bg-primary/10 text-primary border border-primary/20 shrink-0">
                            {{ file.role || file.type || 'Fichier' }}
                          </span>
                          <span class="truncate font-semibold font-code text-base-content/90 group-hover:text-primary transition-colors" :title="file.name">
                            {{ file.name }}
                          </span>
                        </div>
                        <span class="text-[10px] text-base-content/40 group-hover:text-primary transition-colors">
                          Détails →
                        </span>
                      </div>
                    </div>
                  </div>
                  <div v-else class="text-center opacity-50 text-xs font-text py-4">
                    Aucun fichier attaché.
                  </div>
                </div>
                <div v-else 
                  class="w-full py-10 px-6 bg-error/10 border border-error/30 backdrop-blur-md flex flex-col items-center justify-center text-center gap-2 shadow-[0_0_20px_rgba(239,68,68,0.1)]">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-error animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                  <div>
                    <h3 class="font-titre font-bold text-sm text-error tracking-wider uppercase">Fichiers Verrouillés</h3>
                    <p class="font-text text-[11px] text-base-content/60 mt-0.5">Ce challenge n'est pas actif actuellement.</p>
                  </div>
                </div>
                <div v-if="challenge.is_active && (challenge.docker_image_id || challenge.external_url)" class="mt-6 pt-4 border-t border-base-300">
                  <div v-if="challenge.has_other_instance && !dockerInstanceUrl" class="text-center">
                    <button disabled class="btn btn-disabled btn-sm w-full font-text font-bold tracking-wider opacity-60">
                      Impossible de lancer le challenge
                    </button>
                    <p class="font-mono text-[10px] text-error mt-1.5">
                      Vous avez un challenge déjà lancé. Fermez-le avant de lancer un autre challenge.
                    </p>
                  </div>
                  <div v-else>
                    <button @click="handleChallengeAccess" :disabled="launchingInstance" class="btn btn-primary btn-sm w-full font-text font-bold tracking-wider gap-2 relative flex items-center justify-center">
                      <span v-if="launchingInstance" class="loading loading-spinner loading-xs absolute"></span>
                      <span :class="{ 'opacity-0': launchingInstance }">
                        {{ challenge.external_url || dockerInstanceUrl ? 'ACCÉDER AU CHALLENGE' : 'LANCER LE CHALLENGE' }}
                      </span>
                    </button>
                    <div v-if="dockerInstanceUrl && dockerTimeLeftStr" class="mt-3 flex flex-col gap-2 items-center">
                      <div class="font-mono text-[11px] text-warning">
                        Expire dans : {{ dockerTimeLeftStr }}
                      </div>
                      <button @click="stopInstance" :disabled="stoppingInstance" class="btn btn-error btn-xs font-text tracking-wider w-full">
                        <span v-if="stoppingInstance" class="loading loading-spinner loading-xs"></span>
                        <span v-else>FERMER L'INSTANCE</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              <div v-if="challenge.hasInstance"
                class="bg-base-200/40 border border-base-300 p-5 shadow-xl flex flex-col gap-4 items-center justify-center backdrop-blur-xs text-center">
                <div class="flex items-center gap-3 font-text text-sm text-secondary">
                  <span class="relative flex h-3 w-3">
                    <span
                      class="animate-ping absolute inline-flex h-full w-full rounded-full bg-error opacity-75"></span>
                    <span class="relative inline-flex rounded-full h-3 w-3 bg-error"></span>
                  </span>
                  <span class="font-semibold opacity-80">Environnement Dynamique</span>
                </div>
                <button @click="startInstance" class="btn btn-primary btn-sm w-full font-text font-bold tracking-wider">
                  DÉMARRER L'INSTANCE
                </button>
              </div>
            </div>
          </div>
        </div>
        <div v-show="activeTab === 'solves'" class="animate-fade-in w-full">
          <div class="max-w-6xl mx-auto">
            <table class="table table-zebra w-full">
              <thead>
                <tr class="text-base-content/70 border-b border-base-300 text-lg font-text">
                  <th class="font-text text-lg pb-3">Utilisateurs</th>
                  <th class="font-text text-lg pb-3">Date de validation</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(solver, index) in challenge.solvers" :key="index" class="border-none hover:bg-base-300/30">
                  <td class="py-4">
                    <div class="flex items-center gap-3">
                      <span class="font-bold font-text text-lg text-primary">
                        {{ solver.username || solver.user?.username }}
                      </span>
                      <div v-if="index === 0"
                        class="relative inline-flex items-center justify-center px-6 py-1 mx-2 select-none">
                        <svg
                          class="absolute inset-0 w-full h-full text-error drop-shadow-[0_2px_8px_rgba(239,68,68,0.5)]"
                          viewBox="0 0 100 30" preserveAspectRatio="none">
                          <path d="M 0 15 C 12 2, 88 2, 100 15 C 88 28, 12 28, 0 15 Z" fill="currentColor" />
                        </svg>
                        <span class="relative z-10 text-white text-[8.5px] font-titre font-bold uppercase">
                          First Blood
                        </span>
                      </div>
                    </div>
                  </td>
                  <td class="py-4 text-left text-base-content/60 font-code text-sm">
                    {{ solver.submitted_at }}
                  </td>
                </tr>
                <tr v-if="!challenge.solvers || challenge.solvers.length === 0">
                  <td colspan="2" class="text-center py-8 opacity-50 font-text">
                    Aucune résolution pour le moment. Soyez le premier !
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
  <dialog :class="['modal', { 'modal-open': selectedFile }]">
    <div class="modal-box bg-base-100 border border-base-300 rounded-none shadow-2xl p-6 max-w-lg">
      <div class="flex items-center justify-between border-b border-base-300 pb-3 mb-4">
        <h3 class="font-titre font-bold text-base text-primary uppercase tracking-wider">Informations du fichier</h3>
        <button @click="selectedFile = null" class="btn btn-sm btn-ghost font-code">✕</button>
      </div>
      <div v-if="selectedFile" class="space-y-4 font-text text-xs">
        <div>
          <span class="block text-[10px] uppercase tracking-widest opacity-50 font-stitre mb-1">Nom du fichier</span>
          <p class="font-code font-semibold text-sm text-base-content break-all bg-base-200/50 p-2 border border-base-300">
            {{ selectedFile.name }}
          </p>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <span class="block text-[10px] uppercase tracking-widest opacity-50 font-stitre mb-1">Type / Rôle</span>
            <p class="font-code text-base-content/85 bg-base-200/50 p-2 border border-base-300 uppercase">
              {{ selectedFile.role || selectedFile.type || 'N/A' }}
            </p>
          </div>
          <div>
            <span class="block text-[10px] uppercase tracking-widest opacity-50 font-stitre mb-1">Taille</span>
            <p class="font-code text-base-content/85 bg-base-200/50 p-2 border border-base-300">
              {{ selectedFile.size || 'Inconnue' }}
            </p>
          </div>
        </div>
        <div>
          <span class="block text-[10px] uppercase tracking-widest opacity-50 font-stitre mb-1">Empreinte SHA256</span>
          <p class="font-mono text-[11px] text-primary break-all bg-base-200/50 p-2.5 border border-base-300 select-all">
            {{ selectedFile.sha || 'Non disponible' }}
          </p>
        </div>
      </div>
      <div class="modal-action mt-6 pt-4 border-t border-base-300 flex justify-between items-center">
        <button @click="selectedFile = null" class="btn btn-sm btn-ghost font-code text-xs">Fermer</button>
        <button v-if="selectedFile" @click="downloadFile(selectedFile)"
          class="btn btn-primary btn-sm font-titre font-bold tracking-wide gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          TÉLÉCHARGER
        </button>
      </div>
    </div>
    <form method="dialog" class="modal-backdrop">
      <button @click="selectedFile = null">fermer</button>
    </form>
  </dialog>
  <transition name="slide-up">
    <div v-if="showSuccessPopup"
      class="fixed bottom-6 right-6 z-[200] bg-base-100/95 backdrop-blur-xl border border-success/30 p-6 rounded-lg shadow-[0_15px_50px_rgba(34,197,94,0.25)] w-80 flex flex-col gap-4">
      <div class="flex items-center gap-4 border-b border-base-300 pb-3">
        <div class="bg-success/20 text-success p-2.5 rounded-full relative">
          <span class="absolute inset-0 rounded-full bg-success/20 animate-ping"></span>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 relative z-10" fill="none" viewBox="0 0 24 24"
            stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <div>
          <h3 class="font-titre font-bold text-lg text-base-content leading-none">Challenge Validé !</h3>
          <p class="text-xs font-text text-base-content/50 mt-1">Données sécurisées avec succès.</p>
        </div>
      </div>
      <div class="flex justify-between items-center mt-1">
        <div class="flex flex-col">
          <span class="text-[10px] font-stitre uppercase opacity-50 tracking-widest mb-1">Points</span>
          <span class="font-code text-3xl font-bold text-success drop-shadow-[0_0_8px_rgba(34,197,94,0.5)]">
            +{{ animatedPoints }}
          </span>
        </div>
        <div class="flex flex-col text-right">
          <span class="text-[10px] font-stitre uppercase opacity-50 tracking-widest mb-1">Expérience</span>
          <span class="font-code text-3xl font-bold text-[#a855f7] drop-shadow-[0_0_8px_rgba(168,85,247,0.5)]">
            +{{ animatedXP }} <span class="text-sm">XP</span>
          </span>
        </div>
      </div>
      <div class="w-full h-1 bg-base-300 rounded-full overflow-hidden mt-1">
        <div class="h-full bg-success animate-shrink-bar"></div>
      </div>
    </div>
  </transition>
</template>
<style scoped>
.animate-fade-in {
  animation: fadeIn 0.3s ease-out forwards;
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
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-5px);
}
.static-glow-success {
  box-shadow: inset 0 0 150px rgba(34, 197, 94, 0.15), inset 0 0 20px rgba(34, 197, 94, 0.25);
  pointer-events: none;
}
.animate-glow-success {
  animation: glow-flash 2.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  pointer-events: none;
}
@keyframes glow-flash {
  0% {
    box-shadow: inset 0 0 0px rgba(34, 197, 94, 0);
  }

  15% {
    box-shadow: inset 0 0 250px rgba(34, 197, 94, 0.7), inset 0 0 60px rgba(34, 197, 94, 0.6);
  }

  100% {
    box-shadow: inset 0 0 100px rgba(34, 197, 94, 0.15), inset 0 0 20px rgba(34, 197, 94, 0.25);
  }
}
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}
.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(30px) scale(0.95);
}
@keyframes shrink-bar {
  0% {
    width: 100%;
  }
  100% {
    width: 0%;
  }
}
.animate-shrink-bar {
  animation: shrink-bar 6s linear forwards;
}
.animate-glow-error {
  animation: glow-flash-error 8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  pointer-events: none;
}
@keyframes glow-flash-error {
  0% {
    box-shadow: inset 0 0 0px rgba(239, 68, 68, 0);
  }
  15% {
    box-shadow: inset 0 0 250px rgba(239, 68, 68, 0.6), inset 0 0 60px rgba(239, 68, 68, 0.5);
  }
  100% {
    box-shadow: inset 0 0 0px rgba(239, 68, 68, 0);
  }
}
</style>