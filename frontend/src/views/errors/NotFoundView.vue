<template>
  <div class="flex flex-col h-screen relative w-full text-base-content overflow-hidden">
    
    <canvas ref="canvasRef" 
            class="fixed top-0 left-0 w-scree h-screen z-0 pointer-events-none bg-base-300">
    </canvas>

    

    <div class="flex-1 flex flex-col items-center justify-center p-4 text-center relative z-10 w-full h-full">
      <div data-shape-mask class="flex flex-col items-center justify-center w-full max-w-md">
        
        <h1 class="text-9xl font-black text-primary font-code mb-4 drop-shadow-[0_0_25px_rgba(var(--p),0.6)] animate-pulse">
          404
        </h1>
        
        <div class="bg-base-200/90 border border-base-300 px-8 py-6 rounded-sm shadow-2xl w-full backdrop-blur-md">
          <h2 class="text-2xl font-titre font-bold mb-2 text-base-content">Page Introuvable</h2>
          <p class="text-base-content/70 font-text text-sm mb-6">
            La page que vous tentez d'atteindre n'existe pas ou a été déplacée.
          </p>
          
          <button 
            @click="goHome" 
            class="btn btn-primary w-full font-text uppercase tracking-widest group"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 transition-transform group-hover:-translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            Retour à l'accueil
          </button>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/') 
}

// ==========================================
// CONFIGURATION CANVAS GRILLE DE BINAIRE
// ==========================================
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
  temp.className = 'text-base-content'
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
    ctx.fillText(s.type === 'zero' ? '4' : '0', 0, 0)
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

onMounted(() => {
  if (canvasRef.value) {
    ctx = canvasRef.value.getContext('2d')
    init()
    rafId = requestAnimationFrame(tick)
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

<style scoped>
/* Empêche le scroll global et maintient la vue fixe */
:global(body) {
  overflow: hidden !important;
  margin: 0;
  padding: 0;
}
</style>