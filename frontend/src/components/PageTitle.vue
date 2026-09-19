<script setup>
defineProps({
  text: {
    type: String,
    required: true
  }
})
</script>
<template>
  <div class="mb-10">
    <h1 class="block w-full text-center text-3xl font-stitre font-bold bg-primary text-base-100 py-2 uppercase tracking-[0.75em] shadow-sm">
      {{ text }}
    </h1>
  </div>
</template>