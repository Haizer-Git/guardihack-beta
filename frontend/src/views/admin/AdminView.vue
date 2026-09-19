<script setup>
import { ref, onMounted } from 'vue'
import AdminChallenges from './AdminChallenges.vue'
import AdminUsers from './AdminUsers.vue'
import AdminCosmetics from './AdminCosmetics.vue'
import AdminAchievements from './AdminAchievements.vue'
import AdminCommunication from './AdminCommunication.vue'
import AdminConfig from './AdminConfig.vue'
import AdminDocker from './AdminDocker.vue'
import AdminUploads from './AdminUploads.vue'

const activeSection = ref('challenges')
const activeSubTab = ref('challenge')

// ─── TOAST ───────────────────────────────────────────────────────────────────
import { toast, showToast } from './useAdminToast.js'

// ─── NAVIGATION ───────────────────────────────────────────────────────────────
function onSectionChange(section) {
  activeSection.value = section
  // Définir un sous-onglet par défaut selon la section principale
  if (section === 'challenges') {
    activeSubTab.value = 'challenge'
  } else if (section === 'cosmetics') {
    activeSubTab.value = 'item'
  } else if (section === 'communication') {
    activeSubTab.value = 'communication'
  } else if (section === 'config') {
    activeSubTab.value = 'setting'
  } else if (section === 'uploads') {
    activeSubTab.value = 'upload'
  } else if (section === 'docker') {
    activeSubTab.value = 'image'
  } else if (section === 'users') {
    activeSubTab.value = 'user'
  } else if (section === 'achievements') {
    activeSubTab.value = 'achievement_list'
  } else {
    activeSubTab.value = section 
  }
}

function onSubTabChange(subTab) {
  activeSubTab.value = subTab
}
</script>

<template>
  <div class="flex min-h-[calc(100vh-8.5rem)] relative font-text">

    <!-- TOAST -->
    <transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="translate-x-full opacity-0"
      enter-to-class="translate-x-0 opacity-100"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="translate-x-0 opacity-100"
      leave-to-class="translate-x-full opacity-0"
    >
      <div
        v-if="toast.show"
        :class="[
          'fixed top-20 right-6 z-50 flex items-center gap-3 px-4 py-3 border text-sm font-code shadow-2xl w-80',
          toast.type === 'error' ? 'bg-error/10 border-error/40 text-error' : 'bg-success/10 border-success/40 text-success'
        ]"
      >
        <span class="text-base leading-none">{{ toast.type === 'error' ? '✗' : '✓' }}</span>
        <span>{{ toast.message }}</span>
      </div>
    </transition>

    <!-- SIDEBAR AVEC SOUS-ONGLETS -->
    <aside class="w-60 shrink-0 flex flex-col py-5 px-4 gap-2 bg-base-300 border-r border-secondary overflow-y-auto">
      <div class="px-3 mb-4">
        <p class="font-code text-[10px] tracking-[0.2em] uppercase text-base-content/40 mb-0.5">Panel Admin</p>
        <RouterLink to="/" class="hover:opacity-70">
          <p class="font-titre text-xl font-bold text-base-content leading-none">GuardiHack</p>
        </RouterLink>
      </div>

      <!-- GROUPE : CHALLENGES -->
      <div class="flex flex-col">
        <button
          @click="onSectionChange('challenges')"
          :class="[
            'flex items-center justify-between w-full px-3 py-2.5 text-sm font-medium font-stitre text-left transition-colors',
            activeSection === 'challenges'
              ? 'bg-base-200 text-base-content border-l-2 border-primary font-bold'
              : 'text-base-content/60 hover:bg-primary/20 hover:text-base-content border-l-2 border-transparent'
          ]"
        >
          <span>Challenges</span>
          <span class="text-xs">{{ activeSection === 'challenges' ? '▼' : '▶' }}</span>
        </button>

        <div v-if="activeSection === 'challenges'" class="flex flex-col pl-4 mt-1 space-y-1 border-l border-secondary/40 ml-3">
          <button
            @click="onSubTabChange('challenge')"
            :class="['text-xs text-left px-2 py-1.5 font-code transition-colors', activeSubTab === 'challenge' ? 'text-primary font-bold' : 'text-base-content/50 hover:text-base-content']"
          >
            > Challenges
          </button>
          <button
            @click="onSubTabChange('rotation')"
            :class="['text-xs text-left px-2 py-1.5 font-code transition-colors', activeSubTab === 'rotation' ? 'text-primary font-bold' : 'text-base-content/50 hover:text-base-content']"
          >
            > Rotations
          </button>
          <button
            @click="onSubTabChange('category')"
            :class="['text-xs text-left px-2 py-1.5 font-code transition-colors', activeSubTab === 'category' ? 'text-primary font-bold' : 'text-base-content/50 hover:text-base-content']"
          >
            > Catégories
          </button>
        </div>
      </div>

      <!-- 🟢 GROUPE : DOCKER (NOUVEAU) -->
      <div class="flex flex-col">
        <button
          @click="onSectionChange('docker')"
          :class="[
            'flex items-center justify-between w-full px-3 py-2.5 text-sm font-medium font-stitre text-left transition-colors',
            activeSection === 'docker'
              ? 'bg-base-200 text-base-content border-l-2 border-primary font-bold'
              : 'text-base-content/60 hover:bg-primary/20 hover:text-base-content border-l-2 border-transparent'
          ]"
        >
          <span>Docker</span>
          <span class="text-xs">{{ activeSection === 'docker' ? '▼' : '▶' }}</span>
        </button>

        <!-- Sous-onglets de Docker (Images & Instances) -->
        <div v-if="activeSection === 'docker'" class="flex flex-col pl-4 mt-1 space-y-1 border-l border-secondary/40 ml-3">
          <button
            @click="onSubTabChange('image')"
            :class="['text-xs text-left px-2 py-1.5 font-code transition-colors', activeSubTab === 'image' ? 'text-primary font-bold' : 'text-base-content/50 hover:text-base-content']"
          >
            > Images
          </button>
          <button
            @click="onSubTabChange('instance')"
            :class="['text-xs text-left px-2 py-1.5 font-code transition-colors', activeSubTab === 'instance' ? 'text-primary font-bold' : 'text-base-content/50 hover:text-base-content']"
          >
            > Instances
          </button>
        </div>
      </div>

      <!-- GROUPE : UTILISATEURS -->
      <div class="flex flex-col">
        <button
          @click="onSectionChange('users')"
          :class="[
            'flex items-center justify-between w-full px-3 py-2.5 text-sm font-medium font-stitre text-left transition-colors',
            activeSection === 'users'
              ? 'bg-base-200 text-base-content border-l-2 border-primary font-bold'
              : 'text-base-content/60 hover:bg-primary/20 hover:text-base-content border-l-2 border-transparent'
          ]"
        >
          <span>Utilisateurs</span>
          <span class="text-xs">{{ activeSection === 'users' ? '▼' : '▶' }}</span>
        </button>

        <div v-if="activeSection === 'users'" class="flex flex-col pl-4 mt-1 space-y-1 border-l border-secondary/40 ml-3">
          <button
            @click="onSubTabChange('user')"
            :class="['text-xs text-left px-2 py-1.5 font-code transition-colors', activeSubTab === 'user' ? 'text-primary font-bold' : 'text-base-content/50 hover:text-base-content']"
          >
            > Utilisateurs
          </button>
          <button
            @click="onSubTabChange('preset')"
            :class="['text-xs text-left px-2 py-1.5 font-code transition-colors', activeSubTab === 'preset' ? 'text-primary font-bold' : 'text-base-content/50 hover:text-base-content']"
          >
            > Presets
          </button>
          <button
            @click="onSubTabChange('token')"
            :class="['text-xs text-left px-2 py-1.5 font-code transition-colors', activeSubTab === 'token' ? 'text-primary font-bold' : 'text-base-content/50 hover:text-base-content']"
          >
            > Tokens
          </button>
        </div>
      </div>

      <!-- GROUPE : COSMÉTIQUES -->
      <button
        @click="onSectionChange('cosmetics')"
        :class="[
          'flex items-center justify-between w-full px-3 py-2.5 text-sm font-medium font-stitre text-left transition-colors',
          activeSection === 'cosmetics'
            ? 'bg-base-200 text-base-content border-l-2 border-primary font-bold'
            : 'text-base-content/60 hover:bg-primary/20 hover:text-base-content border-l-2 border-transparent'
        ]"
      >
        <span>Cosmétiques</span>
      </button>
      
      <!-- GROUPE : ACHIEVEMENTS -->
      <div class="flex flex-col">
        <button
          @click="onSectionChange('achievements')"
          :class="[
            'flex items-center justify-between w-full px-3 py-2.5 text-sm font-medium font-stitre text-left transition-colors',
            activeSection === 'achievements'
              ? 'bg-base-200 text-base-content border-l-2 border-primary font-bold'
              : 'text-base-content/60 hover:bg-primary/20 hover:text-base-content border-l-2 border-transparent'
          ]"
        >
          <span>Succès</span>
          <span class="text-xs">{{ activeSection === 'achievements' ? '▼' : '▶' }}</span>
        </button>

        <div v-if="activeSection === 'achievements'" class="flex flex-col pl-4 mt-1 space-y-1 border-l border-secondary/40 ml-3">
          <button
            @click="onSubTabChange('achievement_list')"
            :class="['text-xs text-left px-2 py-1.5 font-code transition-colors', activeSubTab === 'achievement_list' ? 'text-primary font-bold' : 'text-base-content/50 hover:text-base-content']"
          >
            > Succès
          </button>
          <button
            @click="onSubTabChange('badges_list')"
            :class="['text-xs text-left px-2 py-1.5 font-code transition-colors', activeSubTab === 'badges_list' ? 'text-primary font-bold' : 'text-base-content/50 hover:text-base-content']"
          >
            > Badges
          </button>
        </div>
      </div>

      <!-- GROUPE : COMMUNICATION -->
      <button
        @click="onSectionChange('communication')"
        :class="[
          'flex items-center justify-between w-full px-3 py-2.5 text-sm font-medium font-stitre text-left transition-colors',
          activeSection === 'communication'
            ? 'bg-base-200 text-base-content border-l-2 border-primary font-bold'
            : 'text-base-content/60 hover:bg-primary/20 hover:text-base-content border-l-2 border-transparent'
        ]"
      >
        <span>Communication</span>
      </button>

      <!-- GROUPE : UPLOADS -->
      <button
        @click="onSectionChange('uploads')"
        :class="[
          'flex items-center justify-between w-full px-3 py-2.5 text-sm font-medium font-stitre text-left transition-colors',
          activeSection === 'uploads'
            ? 'bg-base-200 text-base-content border-l-2 border-primary font-bold'
            : 'text-base-content/60 hover:bg-primary/20 hover:text-base-content border-l-2 border-transparent'
        ]"
      >
        <span>Photothèque</span>
      </button>

      <!-- GROUPE : CONFIGURATION -->
      <button
        @click="onSectionChange('config')"
        :class="[
          'flex items-center justify-between w-full px-3 py-2.5 text-sm font-medium font-stitre text-left transition-colors',
          activeSection === 'config'
            ? 'bg-base-200 text-base-content border-l-2 border-primary font-bold'
            : 'text-base-content/60 hover:bg-primary/20 hover:text-base-content border-l-2 border-transparent'
        ]"
      >
        <span>Configuration</span>
      </button>
    </aside>

    <!-- CONTENU PRINCIPAL -->
    <main class="flex-1 overflow-y-auto px-8 py-2">
      <AdminChallenges v-if="activeSection === 'challenges'" :initial-tab="activeSubTab" />
      <AdminUsers      v-else-if="activeSection === 'users'" :initial-tab="activeSubTab" />
      <AdminDocker     v-else-if="activeSection === 'docker'" :initial-tab="activeSubTab" />
      <AdminCommunication v-else-if="activeSection === 'communication'" :initial-tab="activeSubTab" />
      <AdminCosmetics  v-else-if="activeSection === 'cosmetics'" />
      <AdminAchievements v-else-if="activeSection === 'achievements'" :initial-tab="activeSubTab" />
      <AdminUploads    v-else-if="activeSection === 'uploads'" :initial-tab="activeSubTab" />
      <AdminConfig     v-else-if="activeSection === 'config'" />
    </main>
  </div>
</template>