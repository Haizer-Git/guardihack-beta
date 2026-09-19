<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()

// Nettoyage éventuel du token si préfixé par ":"
const token = route.params.token.startsWith(':') ? route.params.token.substring(1) : route.params.token

const isValidating = ref(true)
const isTokenValid = ref(false)
const loading = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

const newPassphrase = ref('')
const confirmPassphrase = ref('')

// --- CONFIGURATION CANVAS GRILLE DE BINAIRE ---
const canvasRef = ref(null)
let ctx = null, grid = null, rafId = null, pointer = null, maskRects = [], frameCount = 0

const gap = 20 
const radiusVmin = 25 
const SHAPE_TYPES = ['zero', 'one']
let textColorRGB = '245, 245, 245'

const rnd = (min, max) => Math.random() * (max - min) + min
const pick = (arr) => arr[Math.floor(Math.random() * arr.length)]
const durationToFactor = (sec) => sec <= 0 ? 1 : 1 - Math.pow(0.05, 1 / (60 * sec))

function updateThemeColors() {
  const temp = document.createElement('div')
  temp.className = 'text-primary'
  document.body.appendChild(temp)
  let color = window.getComputedStyle(temp).color
  
  if (color === 'rgba(0, 0, 0, 0)' || color === 'transparent') {
    temp.className = 'text-white'
    color = window.getComputedStyle(temp).color
  }
  document.body.removeChild(temp)

  const match = color.match(/\d+/g)
  if (match && match.length >= 3) {
    textColorRGB = `${match[0]}, ${match[1]}, ${match[2]}`
  }
}

function drawShape(ctx, s, influence) {
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'

  if (influence < 0.1) {
    ctx.font = `bold ${s.size * 1.1}px monospace`
    ctx.fillStyle = `rgba(${textColorRGB}, 0.15)`
    ctx.fillText('.', 0, -2)
  } else {
    ctx.font = `bold ${s.size * 1.9}px monospace`
    const finalAlpha = influence * s.maxAlpha
    ctx.fillStyle = `rgba(${textColorRGB}, ${finalAlpha})`
    ctx.fillText(s.type === 'zero' ? '0' : '1', 0, 0)
  }
}

function buildGrid() {
  if (!canvasRef.value) return null
  const W = window.innerWidth
  const H = window.innerHeight
  const cols = Math.floor(W / gap), rows = Math.floor(H / gap)
  const offsetX = (W - (cols - 1) * gap) / 2, offsetY = (H - (rows - 1) * gap) / 2, shapes = []
  
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      shapes.push({ 
        x: offsetX + c * gap, 
        y: offsetY + r * gap, 
        type: pick(SHAPE_TYPES), 
        size: gap * 0.35,
        maxAlpha: rnd(0.25, 1.0), 
        currentInfluence: 0
      })
    }
  }
  return { shapes, width: W, height: H }
}

function init() {
  const canvas = canvasRef.value; if (!canvas) return
  const W = window.innerWidth
  const H = window.innerHeight
  const dpr = window.devicePixelRatio || 1
  
  canvas.width = W * dpr
  canvas.height = H * dpr
  canvas.style.width = W + 'px'
  canvas.style.height = H + 'px'
  ctx.setTransform(1, 0, 0, 1, 0, 0)
  ctx.scale(dpr, dpr)
  
  updateThemeColors()
  grid = buildGrid()
}

function tick() {
  if (!grid) { rafId = requestAnimationFrame(tick); return }
  const { shapes, width, height } = grid
  const radius = Math.min(width, height) * (radiusVmin / 100)

  ctx.clearRect(0, 0, width, height)
  
  frameCount++
  if (frameCount % 10 === 0) maskRects = Array.from(document.querySelectorAll('[data-shape-mask]')).map(el => el.getBoundingClientRect())

  const canvasBounds = canvasRef.value ? canvasRef.value.getBoundingClientRect() : { left: 0, top: 0 }

  for (let i = 0; i < shapes.length; i++) {
    const s = shapes[i], pad = gap / 2
    
    if (maskRects.some(r => (s.x + canvasBounds.left) >= r.left - pad && (s.x + canvasBounds.left) <= r.right + pad && (s.y + canvasBounds.top) >= r.top - pad && (s.y + canvasBounds.top) <= r.bottom + pad)) {
      s.currentInfluence += (0 - s.currentInfluence) * durationToFactor(0.2)
      continue
    }
    
    let targetInfluence = 0
    if (pointer) {
      const localPointerX = pointer.x - canvasBounds.left
      const localPointerY = pointer.y - canvasBounds.top
      const dist = Math.sqrt((s.x - localPointerX)**2 + (s.y - localPointerY)**2)
      if (dist < radius) targetInfluence = 1 - (dist / radius)
    }

    s.currentInfluence += (targetInfluence - s.currentInfluence) * durationToFactor(0.16)

    ctx.save()
    ctx.translate(s.x, s.y)
    drawShape(ctx, s, s.currentInfluence)
    ctx.restore()
  }
  rafId = requestAnimationFrame(tick)
}

// Vérification du token à l'arrivée sur la page via l'API
const verifyToken = async () => {
  try {
    const res = await axios.get(`/api/auth/passphrase/reset/${token}`)
    if (res.data.status === 'success') {
      isTokenValid.value = true
    }
  } catch (err) {
    errorMsg.value = err.response?.data?.message || "Le lien de réinitialisation est invalide ou a expiré."
  } finally {
    isValidating.value = false
  }
}

const handleResetPassphrase = async () => {
  if (newPassphrase.value !== confirmPassphrase.value) {
    errorMsg.value = "Les nouvelles passphrases ne correspondent pas."
    return
  }
  loading.value = true
  errorMsg.value = ''
  successMsg.value = ''
  try {
    const res = await axios.post('/api/auth/passphrase/reset', {
      token: token,
      new_passphrase: newPassphrase.value
    })
    if (res.data.status === 'success') {
      successMsg.value = res.data.message || "Passphrase réinitialisée avec succès."
      setTimeout(() => {
        router.push('/login')
      }, 2000)
    }
  } catch (err) {
    errorMsg.value = err.response?.data?.message || "Erreur lors de la mise à jour de la passphrase."
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (canvasRef.value) {
    ctx = canvasRef.value.getContext('2d'); init(); rafId = requestAnimationFrame(tick)
    window.addEventListener('resize', init)
    window.addEventListener('pointermove', e => { pointer = { x: e.clientX, y: e.clientY } })
    window.addEventListener('pointerleave', () => { pointer = null })
  }
  verifyToken()
})

onUnmounted(() => {
  window.removeEventListener('resize', init)
  if (rafId) cancelAnimationFrame(rafId)
})
</script>

<template>
  <div class="flex flex-col h-[calc(100vh-89px)] relative w-full text-base-content overflow-y-auto">
    
    <canvas ref="canvasRef" 
            class="fixed top-0 left-0 w-screen h-screen z-0 pointer-events-none bg-base-100">
    </canvas>

    <div class="flex-1 flex items-center justify-center py-6 px-4 relative z-10 my-auto">
      <div data-shape-mask class="w-full max-w-[440px] bg-base-100/95 backdrop-blur-md p-8 rounded-sm shadow-2xl border border-base-content/5 text-center my-auto">

        <!-- ÉTAPE DE CHARGEMENT / VÉRIFICATION DU TOKEN -->
        <div v-if="isValidating" class="py-12 flex flex-col items-center gap-4 text-base-content/60">
          <span class="w-6 h-6 border-2 border-base-content/20 border-t-base-content rounded-full animate-spin"></span>
          <p class="text-[14px] tracking-wider uppercase font-mono animate-pulse">Vérification du lien...</p>
        </div>

        <!-- ERREUR SI TOKEN INVALIDE -->
        <div v-else-if="!isTokenValid" class="py-6">
          <h1 class="text-[22px] font-semibold text-error mb-2 uppercase tracking-wide font-titre">Lien Invalide</h1>
          <p class="text-[13px] text-error mb-6 bg-error/10 border border-error/20 p-3 rounded-sm font-code">
            {{ errorMsg }}
          </p>
          <router-link to="/login" class="inline-block w-full bg-neutral text-neutral-content hover:opacity-90 text-[14px] font-medium py-3 px-4 rounded-sm tracking-wide text-center font-mono transition-all">
            Retour à la connexion
          </router-link>
        </div>

        <!-- FORMULAIRE DE CHANGEMENT DE MOT DE PASSE SI TOKEN VALIDE -->
        <div v-else>
          <div class="mb-8 text-center">
            <h1 class="text-[32px] font-bold tracking-tight text-base-content m-0 font-titre">GUARDIHACK</h1>
            <p class="text-[15px] font-stitre text-base-content/60 mt-0.5">Nouvelle passphrase</p>
          </div>

          <form @submit.prevent="handleResetPassphrase" class="flex flex-col gap-5 text-left">
            <div class="flex flex-col gap-1.5">
              <label class="text-[13px] text-base-content/70 font-medium">Nouvelle passphrase</label>
              <input
                v-model="newPassphrase"
                type="password"
                placeholder="••••••••"
                required
                class="w-full bg-base-200 border border-base-content/10 focus:border-primary focus:bg-base-300 text-base-content px-3 py-2.5 text-[14px] outline-none transition-all rounded-sm placeholder:text-base-content/30 font-sans"
              />
            </div>

            <div class="flex flex-col gap-1.5">
              <label class="text-[13px] text-base-content/70 font-medium">Confirmer la passphrase</label>
              <input
                v-model="confirmPassphrase"
                type="password"
                placeholder="••••••••"
                required
                class="w-full bg-base-200 border border-base-content/10 focus:border-primary focus:bg-base-300 text-base-content px-3 py-2.5 text-[14px] outline-none transition-all rounded-sm placeholder:text-base-content/30 font-sans"
              />
            </div>

            <div v-if="errorMsg" class="text-[13px] text-error bg-error/10 border border-error/20 p-2.5 rounded-sm font-mono">
              {{ errorMsg }}
            </div>
            <div v-if="successMsg" class="text-[13px] text-success bg-success/10 border border-success/20 p-2.5 rounded-sm font-mono">
              {{ successMsg }}
            </div>

            <button
              type="submit"
              :disabled="loading"
              class="w-full mt-2 bg-neutral text-neutral-content hover:opacity-90 text-[14px] font-medium py-3 px-4 rounded-sm tracking-wide transition-all active:scale-[0.99] disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2 font-mono"
            >
              <span v-if="loading" class="w-4 h-4 border-2 border-neutral-content/30 border-t-neutral-content rounded-full animate-spin"></span>
              <span>{{ loading ? 'Mise à jour...' : 'Confirmer le changement' }}</span>
            </button>
          </form>
        </div>

      </div>
    </div>

  </div>
</template>

<style scoped>
:global(footer) {
  background-color: hsl(var(--b3, 0 0% 5%)) !important;
  position: relative !important;
  z-index: 20 !important;
}
:global(body) {
  overflow-y: auto !important;
}
</style>