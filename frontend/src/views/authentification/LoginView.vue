<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

const mode = ref('login') // 'login' ou 'forgot_request'
const mail = ref('')
const passphrase = ref('')
const loading = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

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

const handleLogin = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    const response = await axios.post('/api/auth/login', {
      mail: mail.value,
      passphrase: passphrase.value
    })
    if (response.data.status === 'success') {
      router.push('/')
    }
  } catch (err) {
    errorMsg.value = err.response?.data?.message || "Identifiants invalides ou erreur système."
  } finally {
    loading.value = false
  }
}

const handleRequestReset = async () => {
  loading.value = true
  errorMsg.value = ''
  successMsg.value = ''
  try {
    const response = await axios.post('/api/auth/passphrase/reset/url', {
      mail: mail.value
    })
    if (response.data.status === 'success') {
      successMsg.value = response.data.message || "Si un compte associé à ce mail existe, un lien a été envoyé."
    }
  } catch (err) {
    errorMsg.value = err.response?.data?.message || "Erreur lors de la demande de réinitialisation."
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
})

onUnmounted(() => {
  window.removeEventListener('resize', init)
  if (rafId) cancelAnimationFrame(rafId)
})
</script>

<template>
  <div class="flex flex-col h-[calc(100vh-89px)] relative w-full text-base-content">
    
    <canvas ref="canvasRef" 
            class="fixed top-0 left-0 w-screen h-screen z-0 pointer-events-none bg-base-100">
    </canvas>

    <div class="flex-1 flex items-center justify-center py-2 px-4 relative z-10">
      <div data-shape-mask class="w-full max-w-[440px] bg-base-100/95 backdrop-blur-md p-8 rounded-sm shadow-2xl border border-base-content/5">

        <div class="text-center mb-8">
          <h1 class="text-[32px] font-bold tracking-tight text-base-content m-0 font-titre">GUARDIHACK</h1>
          <p class="text-[15px] font-stitre text-base-content/60 mt-0.5">
            {{ mode === 'login' ? 'Login' : 'Récupération de compte' }}
          </p>
        </div>

        <!-- FORMULAIRE LOGIN -->
        <form v-if="mode === 'login'" @submit.prevent="handleLogin" class="flex flex-col gap-5 text-left">
          <div class="flex flex-col gap-1.5">
            <label class="text-[13px] text-base-content/70 font-medium">Email</label>
            <input
              v-model="mail"
              type="email"
              placeholder="agent@guardiaschool.fr"
              required
              class="w-full bg-base-200 border border-base-content/10 focus:border-primary focus:bg-base-300 text-base-content px-3 py-2.5 text-[14px] outline-none transition-all rounded-sm placeholder:text-base-content/30 font-sans"
            />
          </div>

          <div class="flex flex-col gap-1.5">
            <div class="flex justify-between items-center">
              <label class="text-[13px] text-base-content/70 font-medium">Passphrase</label>
              <button 
                type="button" 
                @click="mode = 'forgot_request'; errorMsg = ''; successMsg = ''" 
                class="text-[12px] text-primary hover:underline font-sans cursor-pointer">
                Passphrase oubliée ?
              </button>
            </div>
            <input
              v-model="passphrase"
              type="password"
              placeholder="••••••••"
              required
              class="w-full bg-base-200 border border-base-content/10 focus:border-primary focus:bg-base-300 text-base-content px-3 py-2.5 text-[14px] outline-none transition-all rounded-sm placeholder:text-base-content/30 font-sans"
            />
          </div>

          <div v-if="errorMsg" class="text-[13px] text-error bg-error/10 border border-error/20 p-2.5 rounded-sm font-mono">
            {{ errorMsg }}
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full mt-2 bg-neutral text-neutral-content hover:opacity-90 text-[14px] font-medium py-3 px-4 rounded-sm tracking-wide transition-all active:scale-[0.99] disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2 font-mono"
          >
            <span v-if="loading" class="w-4 h-4 border-2 border-neutral-content/30 border-t-neutral-content rounded-full animate-spin"></span>
            <span>{{ loading ? 'Connexion...' : 'Se connecter' }}</span>
          </button>
        </form>

        <!-- FORMULAIRE DEMANDE MOT DE PASSE OUBLIÉ -->
        <form v-else @submit.prevent="handleRequestReset" class="flex flex-col gap-5 text-left">
          <p class="text-[13px] text-base-content/70 font-sans leading-relaxed">
            Entrez votre adresse e-mail pour recevoir le lien de réinitialisation.
          </p>

          <div class="flex flex-col gap-1.5">
            <label class="text-[13px] text-base-content/70 font-medium">Email</label>
            <input
              v-model="mail"
              type="email"
              placeholder="agent@guardiaschool.fr"
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

          <div class="flex flex-col gap-2 mt-2">
            <button
              type="submit"
              :disabled="loading"
              class="w-full bg-neutral text-neutral-content hover:opacity-90 text-[14px] font-medium py-3 px-4 rounded-sm tracking-wide transition-all active:scale-[0.99] disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2 font-mono"
            >
              <span v-if="loading" class="w-4 h-4 border-2 border-neutral-content/30 border-t-neutral-content rounded-full animate-spin"></span>
              <span>{{ loading ? 'Envoi...' : 'Envoyer le lien' }}</span>
            </button>

            <button
              type="button"
              @click="mode = 'login'; errorMsg = ''; successMsg = ''"
              class="w-full bg-transparent border border-base-content/10 text-base-content/70 hover:bg-base-200 text-[13px] font-medium py-2.5 px-4 rounded-sm transition-all"
            >
              Retour au login
            </button>
          </div>
        </form>

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
  overflow: hidden !important;
}
</style>