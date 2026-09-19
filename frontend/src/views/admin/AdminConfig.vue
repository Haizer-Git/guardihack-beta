<script setup>
import { ref } from 'vue'
import { showToast } from './useAdminToast.js'

// ════════════════════════════════════════════════════════
// CONFIGURATION
// ════════════════════════════════════════════════════════
// TODO: implémenter la configuration de la plateforme
// Exemples de paramètres à gérer :
//   - Nom de la CTF
//   - Dates de début / fin
//   - Inscription ouverte / fermée
//   - Mode équipe
//   - Score freezé
</script>

<template>
  <div>
    <div class="flex items-end justify-between mb-6">
      <div>
        <p class="font-code text-[10px] tracking-[0.18em] uppercase text-base-content/40 mb-1">Admin › Configuration</p>
        <h1 class="font-titre font-bold text-2xl text-base-content leading-none">Configuration</h1>
      </div>
    </div>

    <div class="flex flex-col items-center justify-center py-36 gap-4 text-center">
      <p class="font-code text-6xl opacity-10">⚙️</p>
      <h2 class="font-titre font-bold text-xl text-base-content/30">Configuration de la plateforme</h2>
      <p class="font-code text-xs text-base-content/20 tracking-wide">En cours de développement</p>
    </div>
  </div>
</template>
