<template>
  <div class="mb-10">
    <h1 class="block w-full text-center text-3xl font-stitre font-bold bg-primary text-base-100 py-2 uppercase tracking-[0.75em] shadow-sm">
      {{ text }}
    </h1>
  </div>
</template>

<script setup>
// On définit les propriétés que le composant peut recevoir
defineProps({
  text: {
    type: String,
    required: true // Rend ce paramètre obligatoire
  }
})
</script>