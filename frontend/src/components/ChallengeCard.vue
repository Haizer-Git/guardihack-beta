<script setup>
import { computed } from 'vue'

const props = defineProps({
  challenge: { type: Object, required: true }
})

defineEmits(['open'])

const marqueeText = computed(() => (props.challenge.title + ' — ').repeat(6))

// Calcul dynamique de la couleur basé sur la difficulté
const difficultyColor = computed(() => {
  const diff = (props.challenge.difficulty || '').toLowerCase()
  if (diff === 'easy' || diff === 'facile') return 'text-success border-success'
  if (diff === 'medium' || diff === 'moyen') return 'text-warning border-warning'
  if (diff === 'hard' || diff === 'difficile') return 'text-error border-error'
  if (diff === 'insane' || diff === 'extrême' || diff === 'extreme') return 'text-[#a855f7] border-[#a855f7]'
  return 'text-info border-info'
})
</script>

<template>
  <a href="#" class="card" @click.prevent="$emit('open', challenge.id)">

    <div class="card-container border transition-all duration-300" :class="{
      'border-success bg-success/5 shadow-[0_0_20px_rgba(34,197,94,0.2)]': challenge.is_validated,
      'border-base-300': !challenge.is_validated,
    }">

      <div class="absolute top-2 left-2 z-10">
        <span class="px-2.5 py-0.5 text-[10px] font-text border rounded bg-base-100/50 backdrop-blur-sm"
          :class="difficultyColor">
          {{ challenge.difficulty }}
        </span>
      </div>

      <!-- 1. BLOC ROTATION (Nettoyé : contient uniquement l'horloge orange désormais) -->
      <div v-if="challenge.type === 'ROTATION'"
        class="absolute top-2 right-2 z-10 flex items-center gap-1.5 bg-base-300/80 backdrop-blur-md px-2 py-1 rounded text-xs border border-warning/10 shadow-sm">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-warning" fill="none" viewBox="0 0 24 24"
          stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>

      <!-- 2. BLOC DU GROS ✔ (Position dynamique avec :class) -->
      <div v-if="challenge.is_validated" class="absolute top-1.5 z-30 font-code font-bold text-sm"
        :class="challenge.type === 'ROTATION' ? 'right-14' : 'right-3'">
        <span class="text-success text-2xl drop-shadow-[0_0_5px_rgba(34,197,94,0.5)]">✔</span>
      </div>

      <div class="card-icon font-code text-3xl opacity-50">
        {{ challenge.points }} pts
      </div>

      <div class="preview-text font-text font-bold text-lg flex items-center gap-2">
        {{ challenge.title }}
      </div>

      <div class="card-circle" :class="challenge.is_validated ? 'bg-success' : 'bg-primary'"></div>
      <div class="text-wrapper text-base-100 font-titre">{{ marqueeText }}</div>

    </div>
  </a>
</template>

<style scoped>
.card {
  text-decoration: none;
  display: block;
  width: 100%;
}

.card-container {
  position: relative;
  background: var(--fallback-b2, oklch(var(--b2)));
  color: var(--fallback-bc, oklch(var(--bc)));
  width: 100%;
  height: 150px;
  overflow: hidden;
  border-radius: 8px;
}

.card-container:hover {
  transform: translateY(-4px);
}

.card-container:hover .card-circle {
  transform: translate(-50%, -50%) scale(2.5);
}

.card-container:hover .card-icon {
  opacity: 0;
}

.card-container:hover .preview-text {
  color: var(--fallback-b1, oklch(var(--b1)));
}

.card-icon {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  white-space: nowrap;
  transition: opacity 0.2s ease;
}

.preview-text {
  position: absolute;
  bottom: 0;
  left: 0;
  padding: 10px;
  z-index: 10;
  transition: color 0.2s ease;
}

.card-circle {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) scale(0);
  width: 250px;
  height: 250px;
  border-radius: 100%;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 1;
}

.text-wrapper {
  position: absolute;
  top: 50%;
  left: -20%;
  transform: translate(0, -50%);
  font-size: 35px;
  font-weight: 900;
  text-transform: uppercase;
  white-space: nowrap;
  animation: float-left 15s linear infinite;
  z-index: 2;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.3s ease-out;
}

@keyframes float-left {
  0% {
    transform: translate(0, -50%);
  }

  100% {
    transform: translate(-50%, -50%);
  }
}

.card-container:hover .text-wrapper {
  opacity: 0.3;
}
</style>