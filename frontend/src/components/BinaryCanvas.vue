<template>
  <canvas ref="canvasRef" class="fixed inset-0 z-0 w-full h-full bg-gray-900 pointer-events-none"></canvas>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const canvasRef = ref(null)
let animationFrameId = null

const drawMatrixEffect = () => {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  
  // Logique de ton animation binaire (simplifiée ici pour l'exemple)
  ctx.fillStyle = 'rgba(0, 0, 0, 0.05)'
  ctx.fillRect(0, 0, canvas.width, canvas.height)
  ctx.fillStyle = '#0F0' 
  ctx.font = '15px monospace'
  ctx.fillText(Math.random() > 0.5 ? '1' : '0', Math.random() * canvas.width, Math.random() * canvas.height)

  animationFrameId = requestAnimationFrame(drawMatrixEffect)
}

onMounted(() => {
  if (canvasRef.value) {
    canvasRef.value.width = window.innerWidth
    canvasRef.value.height = window.innerHeight
    drawMatrixEffect()
  }
})

onBeforeUnmount(() => {
  if (animationFrameId) cancelAnimationFrame(animationFrameId)
})
</script>