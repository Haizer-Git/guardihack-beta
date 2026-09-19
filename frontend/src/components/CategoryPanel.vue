<script setup>
import { ref, watch, onMounted } from 'vue'

const props = defineProps({
  categoryName: {
    type: String,
    required: true
  },
  count: {
    type: Number,
    default: 0
  }
})
const isOpen = ref(true)
const storageKey = `guardihack_category_${props.categoryName}`
const togglePanel = () => {
  isOpen.value = !isOpen.value
}

watch(isOpen, (newValue) => {
  localStorage.setItem(storageKey, newValue)
})

onMounted(() => {
  const savedState = localStorage.getItem(storageKey)
  if (savedState !== null) {
    isOpen.value = savedState === 'true'
  }
})
</script>
<template>
  <div class="mb-6 bg-gray-800/50 rounded-xl overflow-hidden border border-gray-700">
    <button 
      @click="togglePanel"
      class="w-full flex items-center justify-between p-4 bg-gray-800 hover:bg-gray-700 transition-colors"
    >
      <h2 class="text-xl font-bold text-white">
        {{ categoryName }} <span class="text-sm text-gray-400">({{ count }})</span>
      </h2>
      <span class="text-cyan-500 transform transition-transform" :class="{ 'rotate-180': isOpen }">
        ▼
      </span>
    </button>
    <div v-show="isOpen" class="p-6">
      <slot></slot>
    </div>
  </div>
</template>