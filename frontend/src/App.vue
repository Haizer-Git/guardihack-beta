<script setup>
import { ref, watch, onMounted } from 'vue'

// --- 1. GESTION DU THÈME ---
const isDark = ref(true)
const applyTheme = (darkState) => {
  const themeName = darkState ? 'piscine-dark' : 'piscine-light'
  document.documentElement.setAttribute('data-theme', themeName)
  localStorage.setItem('theme', themeName)
}
watch(isDark, (newVal) => applyTheme(newVal))

// --- 2. ÉTAT UTILISATEUR (Simulé) ---
const isAdmin = ref(true) 
const username = ref('GUARDIAROOT')
const level = ref(42)

// Pour générer des bulles/étoiles aléatoires
const particles = Array.from({ length: 40 }).map((_, i) => ({
  id: i,
  left: `${Math.random() * 100}%`,
  animationDuration: `${Math.random() * 5 + 5}s`, // entre 5 et 10s
  animationDelay: `${Math.random() * 5}s`,
  size: `${Math.random() * 4 + 2}px` // entre 2 et 6px
}))

// On initialise juste le thème au chargement global
onMounted(() => {
  const savedTheme = localStorage.getItem('theme') || 'piscine-dark'
  isDark.value = savedTheme === 'piscine-dark'
  applyTheme(isDark.value)
})
</script>

<template>
  
  <div class="flex flex-col min-h-screen bg-base-100 text-base-content font-sans">

    <nav class="sticky top-0 z-50 w-full bg-base-200/95 backdrop-blur-md border-b border-base-300 shadow-lg">
      <div class="max-w-[1800px] mx-auto px-4">
        <div class="flex items-center justify-between h-16">

          <div class="flex items-center gap-8">
            <div class="flex-shrink-0 flex items-center gap-2">
              <router-link to="/">
                <img src="/ghp-flag.png" alt="GuardiHack Logo" class="h-14 w-auto object-contain hover:opacity-80 transition-opacity" />
              </router-link>
            </div>

            <div class="hidden lg:flex items-center space-x-1">
              <router-link to="/rules" class="nav-link">Rules</router-link>
              <router-link to="/groups" class="nav-link">Groupes</router-link>
              <router-link to="/scoreboard" class="nav-link">Scoreboard</router-link>
              <router-link to="/tracks" class="nav-link">Tracks</router-link>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <a v-if="isAdmin" :href="'/admin'" class="nav-link text-secondary hover:text-secondary-focus hidden md:flex items-center gap-1">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37a1.724 1.724 0 002.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              Admin
            </a>

            <div class="dropdown dropdown-end">
              <label tabindex="0" class="btn btn-ghost flex items-center gap-3 px-2 ml-2">
                <div class="w-8 h-8 rounded bg-primary text-base-100 flex items-center justify-center font-bold">
                    {{ username[0] }}
                </div>
                <div class="text-right hidden sm:block">
                  <div class="text-xs font-bold leading-none">{{ username }}</div>
                  <div class="text-[10px] text-primary font-mono uppercase tracking-widest">LVL {{ level }}</div>
                </div>
              </label>
              <ul tabindex="0" class="mt-3 z-[1] p-2 shadow-2xl menu menu-sm dropdown-content bg-base-200 w-52 border border-base-300 rounded-box">
                <li><router-link to="/profile" class="py-3">👤 Mon profil</router-link></li>
                <li><router-link to="/profile/settings" class="py-3">⚙️ Paramètres</router-link></li>
                <li><a class="py-3 text-error font-bold">🚪 Déconnexion</a></li>
              </ul>
            </div>

            <div class="w-[1px] h-6 bg-base-content/20 mx-2"></div>

            <div class="dropdown dropdown-end">
              <button class="btn btn-ghost btn-circle btn-sm">
                <div class="indicator">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                  </svg>
                  <span class="badge badge-xs badge-primary indicator-item">3</span>
                </div>
              </button>
              <ul class="dropdown-content menu p-2 shadow-2xl bg-base-200 border border-base-300 rounded-box w-64 z-[1]">
                <li class="menu-title">
                  <span class="font-cyber font-bold text-primary">Notifications (3)</span>
                </li>
                <li><a class="py-3 border-b border-base-300">
                  <span class="badge badge-success badge-sm">✓</span>
                  <div class="flex flex-col gap-1 flex-1">
                    <span class="font-bold text-sm">Challenge résolu!</span>
                    <span class="text-xs opacity-60">Vous avez résolu 'SQLi Bypasser'</span>
                  </div>
                </a></li>
                <li><a class="py-3 border-b border-base-300">
                  <span class="badge badge-info badge-sm">!</span>
                  <div class="flex flex-col gap-1 flex-1">
                    <span class="font-bold text-sm">Nouvelle machine</span>
                    <span class="text-xs opacity-60">T02 déverrouillé: Fondamentaux Système</span>
                  </div>
                </a></li>
                <li><a class="py-3">
                  <span class="badge badge-warning badge-sm">⚠</span>
                  <div class="flex flex-col gap-1 flex-1">
                    <span class="font-bold text-sm">Classement mis à jour</span>
                    <span class="text-xs opacity-60">Vous êtes passé 1er avec 2500 pts</span>
                  </div>
                </a></li>
              </ul>
            </div>

            <label class="btn btn-ghost btn-circle btn-sm swap swap-rotate">
              <input type="checkbox" v-model="isDark" />
              <svg class="swap-on fill-current w-5 h-5 text-yellow-400" viewBox="0 0 24 24"><path d="M5.64,17l-.71.71a1,1,0,0,0,0,1.41,1,1,0,0,0,1.41,0l.71-.71A1,1,0,0,0,5.64,17ZM5,12a1,1,0,0,0-1-1H3a1,1,0,0,0,0,2H4A1,1,0,0,0,5,12Zm7-7a1,1,0,0,0,1-1V3a1,1,0,0,0-2,0V4A1,1,0,0,0,12,5ZM5.64,7.05a1,1,0,0,0,.7.29,1,1,0,0,0,0-1.41l-.71-.71A1,1,0,0,0,4.93,6.34Zm12,.29a1,1,0,0,0,.7-.29l.71-.71a1,1,0,1,0-1.41-1.41L17,5.64a1,1,0,0,0,0,1.41A1,1,0,0,0,17.66,7.34ZM21,11H20a1,1,0,0,0,0,2h1a1,1,0,0,0,0-2Zm-9,8a1,1,0,0,0-1,1v1a1,1,0,0,0,2,0V20A1,1,0,0,0,12,19ZM18.36,17A1,1,0,0,0,17,18.36l.71.71a1,1,0,0,0,1.41,0,1,1,0,0,0,0-1.41ZM12,6.5A5.5,5.5,0,1,0,17.5,12,5.51,5.51,0,0,0,12,6.5Zm0,9A3.5,3.5,0,1,1,15.5,12,3.5,3.5,0,0,1,12,15.5Z" /></svg>
              <svg class="swap-off fill-current w-5 h-5 text-primary" viewBox="0 0 24 24"><path d="M21.64,13a1,1,0,0,0-1.05-.14,8.05,8.05,0,0,1-3.37.73A8.15,8.15,0,0,1,9.08,5.49a8.59,8.59,0,0,1,.25-2A1,1,0,0,0,8,2.36,10.14,10.14,0,1,0,22,14.05,1,1,0,0,0,21.64,13Zm-9.5,6.69A8.14,8.14,0,0,1,7.08,5.22v.27A10.15,10.15,0,0,0,17.22,15.63a9.79,9.79,0,0,0,2.1-.22A8.11,8.11,0,0,1,12.14,19.73Z" /></svg>
            </label>
          </div>

        </div>
      </div>
    </nav>

    <main class="flex-grow mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
      <router-view />
    </main>

    <footer class="flex flex-col md:flex-row gap-4 items-center justify-around w-full py-6 text-sm bg-base-300 text-base-content/70 border-t border-base-100">
      <p class="font-medium">Copyright © 2026 <span class="text-primary font-cyber">GuardiHack</span>. All rights reserved.</p>
      <div class="flex items-center gap-6">
        <a href="#" class="hover:text-primary transition-all">Contact Us</a>
        <div class="h-6 w-px bg-base-content/20"></div>
        <a href="#" class="hover:text-primary transition-all">Privacy Policy</a>
        <div class="h-6 w-px bg-base-content/20"></div>
        <a href="#" class="hover:text-primary transition-all">Trademark Policy</a>
      </div>
    </footer>

  </div>
</template>

