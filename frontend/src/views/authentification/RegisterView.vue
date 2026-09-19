<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute(), router = useRouter()
const token = route.params.token.startsWith(':') ? route.params.token.substring(1) : route.params.token

const isTokenValid = ref(false), checkingToken = ref(true), loading = ref(false), errorMsg = ref('')
const form = ref({ token, username: '', passphrase: '', confirmpassphrase: '', mail: '', first_name: '', last_name: '' })
const presetInfo = ref(null)

// --- CONFIGURATION CANVAS GRILLE DE BINAIRE (Similaire à LoginView) ---
const canvasRef = ref(null)
let ctx = null, grid = null, rafId = null, pointer = null, maskRects = [], frameCount = 0

const gap = 20 // Écartement idéal pour la grille
const radiusVmin = 25 // Rayon d'action du curseur

const SHAPE_TYPES = ['zero', 'one']

// Variable pour stocker la couleur dynamique du texte Tailwind pour le Canvas
let textColorRGB = '245, 245, 245'

const rnd = (min, max) => Math.random() * (max - min) + min
const pick = (arr) => arr[Math.floor(Math.random() * arr.length)]
const durationToFactor = (sec) => sec <= 0 ? 1 : 1 - Math.pow(0.05, 1 / (60 * sec))

// Extraction dynamique de la couleur de texte configurée dans Tailwind
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

const checkToken = async () => {
  try {
    const res = await axios.get(`/api/auth/token/${token}`)
    if (res.data.status === 'success') {
      isTokenValid.value = true; presetInfo.value = res.data.preset
      form.value.mail = res.data.preset.mail || ''; form.value.first_name = res.data.preset.first_name || ''; form.value.last_name = res.data.preset.last_name || ''
    }
  } catch (err) { errorMsg.value = err.response?.data?.message || "Jeton d'invitation invalide." }
  finally { checkingToken.value = false }
}

onMounted(() => {
  if (canvasRef.value) {
    ctx = canvasRef.value.getContext('2d'); init(); rafId = requestAnimationFrame(tick)
    window.addEventListener('resize', init)
    window.addEventListener('pointermove', e => { pointer = { x: e.clientX, y: e.clientY } })
    window.addEventListener('pointerleave', () => { pointer = null })
  }
  checkToken()
})

onUnmounted(() => {
  window.removeEventListener('resize', init)
  if (rafId) cancelAnimationFrame(rafId)
})

const handleRegister = async () => {
  if (form.value.passphrase !== form.value.confirmpassphrase) {
    errorMsg.value = "Les passphrases ne correspondent pas."
    return
  }
  loading.value = true; errorMsg.value = ''
  try { 
    const res = await axios.post('/api/auth/register', form.value) 
    if (res.data.status === 'success') router.push('/') 
  }
  catch (err) { errorMsg.value = err.response?.data?.message || "Erreur de création du compte." }
  finally { loading.value = false }
}
</script>

<template>
  <div class="flex flex-col h-[calc(100vh-89px)] relative w-full text-base-content overflow-y-auto">
    
    <canvas ref="canvasRef" 
            class="fixed top-0 left-0 w-screen h-screen z-0 pointer-events-none bg-base-100">
    </canvas>

    <div class="flex-1 flex items-center justify-center py-6 px-4 relative z-10 my-auto">
      <div data-shape-mask class="w-full max-w-[440px] bg-base-100/95 backdrop-blur-md p-8 rounded-sm shadow-2xl border border-base-content/5 text-center my-auto">

        <div v-if="checkingToken" class="py-12 flex flex-col items-center gap-4 text-base-content/60">
          <span class="w-6 h-6 border-2 border-base-content/20 border-t-base-content rounded-full animate-spin"></span>
          <p class="text-[14px] tracking-wider uppercase font-mono animate-pulse">Vérification de la clé d'accès...</p>
        </div>

        <div v-else-if="!isTokenValid" class="py-6">
          <h1 class="text-[22px] font-semibold text-error mb-2 uppercase tracking-wide font-titre">Accès Refusé</h1>
          <p class="text-[13px] text-error mb-6 bg-error/10 border border-error/20 p-3 rounded-sm font-code">
            {{ errorMsg }}
          </p>
        </div>

        <div v-else>
          <div class="mb-8">
            <h1 class="text-[32px] font-bold tracking-tight text-base-content m-0 font-titre">GUARDIHACK</h1>
            <p class="text-[15px] font-stitre text-base-content/60 mt-0.5">Inscription</p>
            <p class="text-[11px] font-mono tracking-widest text-base-content/40 uppercase mt-2">
              <template v-if="presetInfo?.niveau && presetInfo?.classe">
                {{ presetInfo.niveau }} / Classe {{ presetInfo.classe }}
              </template>
              <template v-else>
                {{ presetInfo?.type || 'COMPTE' }}
              </template>
              <br> 
              {{ presetInfo?.affiliation || 'PARIS' }}
            </p>
          </div>

          <form @submit.prevent="handleRegister" class="flex flex-col gap-5 text-left">

            <div class="grid grid-cols-2 gap-4">
              <div class="flex flex-col gap-1.5">
                <label class="text-[13px] text-base-content/70 font-medium">Prénom</label>
                <input v-model="form.first_name" type="text" required
                  class="w-full bg-base-200 border border-base-content/10 focus:border-primary focus:bg-base-300 text-base-content px-3 py-2.5 text-[14px] outline-none transition-all rounded-sm font-sans" />
              </div>
              <div class="flex flex-col gap-1.5">
                <label class="text-[13px] text-base-content/70 font-medium">Nom</label>
                <input v-model="form.last_name" type="text" required
                  class="w-full bg-base-200 border border-base-content/10 focus:border-primary focus:bg-base-300 text-base-content px-3 py-2.5 text-[14px] outline-none transition-all rounded-sm font-sans" />
              </div>
            </div>

            <div class="flex flex-col gap-1.5" :class="{ 'opacity-60': presetInfo?.mail }">
              <label class="text-[13px] text-base-content/70 font-medium">Email</label>
              <input v-model="form.mail" type="email" :readonly="!!presetInfo?.mail" :tabindex="presetInfo?.mail ? '-1' : '0'" required
                :class="[
                  'w-full bg-base-200 border text-base-content px-3 py-2.5 text-[14px] outline-none transition-all rounded-sm font-sans',
                  presetInfo?.mail ? 'border-base-content/5 text-base-content/40 cursor-not-allowed' : 'border-base-content/10 focus:border-primary focus:bg-base-300'
                ]" />
            </div>

            <div class="flex flex-col gap-1.5">
              <label class="text-[13px] text-base-content/70 font-medium">Username</label>
              <input v-model="form.username" type="text" placeholder="Username" required
                class="w-full bg-base-200 border border-base-content/10 focus:border-primary focus:bg-base-300 text-base-content px-3 py-2.5 text-[14px] outline-none transition-all rounded-sm placeholder:text-base-content/30 font-sans" />
            </div>

            <div class="flex flex-col gap-1.5">
              <label class="text-[13px] text-base-content/70 font-medium flex items-center gap-1.5">
                Passphrase
                <div 
                  class="tooltip tooltip-right before:whitespace-pre-line before:text-left" 
                  data-tip="Correspond au mot de passe de votre compte ex: MOT DE PASSE DU COMPTE">
                  <svg xmlns="http://www.w3.org/2000/svg"
                    class="h-3.5 w-3.5 opacity-60 hover:opacity-100 hover:text-primary cursor-help transition-all"
                    fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </label>

              <input v-model="form.passphrase" type="password" placeholder="••••••" required
                class="w-full bg-base-200 border border-base-content/10 focus:border-primary focus:bg-base-300 text-base-content px-3 py-2.5 text-[14px] outline-none transition-all rounded-sm placeholder:text-base-content/30 font-sans" />
            </div>

            <div class="flex flex-col gap-1.5">
              <label class="text-[13px] text-base-content/70 font-medium flex items-center gap-1.5">
                Confirmer la Passphrase
              </label>

              <input v-model="form.confirmpassphrase" type="password" placeholder="••••••" required
                class="w-full bg-base-200 border border-base-content/10 focus:border-primary focus:bg-base-300 text-base-content px-3 py-2.5 text-[14px] outline-none transition-all rounded-sm placeholder:text-base-content/30 font-sans" />
            </div>

            <div v-if="errorMsg"
              class="text-[13px] text-error bg-error/10 border border-error/20 p-2.5 rounded-sm font-mono">
              {{ errorMsg }}
            </div>

            <button type="submit" :disabled="loading"
              class="w-full mt-2 bg-neutral text-neutral-content hover:opacity-90 text-[14px] font-medium py-3 px-4 rounded-sm tracking-wide transition-all active:scale-[0.99] disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2 font-mono">
              <span v-if="loading"
                class="w-4 h-4 border-2 border-neutral-content/30 border-t-neutral-content rounded-full animate-spin"></span>
              <span>{{ loading ? 'Création en cours...' : 'Créer mon compte' }}</span>
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
/* Autorise le défilement si l'écran est petit, tout en gardant l'harmonie */
:global(body) {
  overflow-y: auto !important;
}
</style>