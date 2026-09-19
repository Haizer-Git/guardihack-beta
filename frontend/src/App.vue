<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import { getAssetUrl } from './utils/assets'

const router = useRouter()
const route = useRoute()
const isDark = ref(true)
const applyTheme = (darkState) => {
  const themeName = darkState ? 'piscine-dark' : 'piscine-light'
  document.documentElement.setAttribute('data-theme', themeName)
  localStorage.setItem('theme', themeName)
}
const isAdmin = ref(false)
const username = ref('')
const avatar = ref(null)
const avatarUrl = ref('')
const userLoaded = ref(false)
const level = ref(0)
const showLevelUp = ref(false)
const newLevelReached = ref(0)
const xpPercentage = ref(0)
const unreadNotifications = ref([])
const unreadCount = ref(0)
const fetchNotifications = async () => {
  if (!userLoaded.value) return
  try {
    const res = await axios.get('/api/user/notification/new')
    if (res.data?.status === 'success') {
      unreadNotifications.value = res.data.notifications || []
      unreadCount.value = res.data.unread_count ?? unreadNotifications.value.length
    }
  } catch (err) {
    console.warn("Erreur lors de la récupération des notifications:", err)
  }
}
const handleMarkRead = async (notif) => {
  console.log("Clic détecté sur la notification :", notif) // <-- Ajoute ça
  try {
    const endpoint = (notif.type === 'global')
      ? `/api/user/notification/global/${notif.id}/read`
      : `/api/user/notification/${notif.id}/read`
    const res = await axios.post(endpoint)
    if (res.data?.status === 'success') {
      unreadNotifications.value = unreadNotifications.value.filter(n => n.id !== notif.id)
      if (unreadCount.value > 0) unreadCount.value--
    }
  } catch (err) {
    console.error("Erreur lors du marquage de la notification:", err)
  }
}
const checkUserSession = async () => {
  try {
    const response = await axios.get('/api/user/me')
    if (response.data.status === 'success') {
      const u = response.data.profile
      username.value = u.username
      isAdmin.value = u.type === 'ADMIN'
      level.value = u.level
      avatar.value = u.avatar
      avatarUrl.value = u.avatar_url || u.avatar || ''
      userLoaded.value = true
      fetchNotifications()
    } else {
      resetUserState()
    }
  } catch (err) {
    resetUserState()
    const publicRoutes = ['/', '/rules', '/register', '/login']
    const currentPath = router.currentRoute.value.path
    const isPublic = publicRoutes.some(route => currentPath.startsWith(route))
    if (!isPublic) {
      router.push('/login')
    }
  }
}
const resetUserState = () => {
  username.value = ''
  avatar.value = null
  avatarUrl.value = ''
  userLoaded.value = false
  isAdmin.value = false
  unreadNotifications.value = []
}
const handleLogout = async () => {
  try {
    await axios.post('/api/auth/logout')
    resetUserState()
    router.push('/login')
  } catch (err) {
    console.error("Erreur déconnexion", err)
  }
}
const isRegisterPage = ref(false)
const checkIsRegisterPage = () => {
  isRegisterPage.value = router.currentRoute.value.path.startsWith('/register')
}
const closeDropdown = () => {
  if (document.activeElement) {
    document.activeElement.blur()
  }
}

watch(isDark, (newVal) => applyTheme(newVal))
watch(level, (newLevel, oldLevel) => {
  if (oldLevel > 0 && newLevel > oldLevel) {
    newLevelReached.value = newLevel
    showLevelUp.value = true
    xpPercentage.value = 0
    const duration = 2100
    const intervalTime = 20
    const increment = 100 / (duration / intervalTime)
    const timer = setInterval(() => {
      if (xpPercentage.value < 100) {
        xpPercentage.value = Math.min(100, Math.round(xpPercentage.value + increment))
      } else {
        clearInterval(timer)
      }
    }, intervalTime)
    setTimeout(() => {
      showLevelUp.value = false
    }, 4500)
  }
})
watch(
  () => router.currentRoute.value.path,
  () => {
    checkIsRegisterPage()
    checkUserSession()
  }
)
window.testLevelUp = (from = 1, to = 2) => {
  level.value = from
  setTimeout(() => {
    level.value = to
  }, 100)
}
window.refreshGlobalAvatar = () => {
  checkUserSession()
}
onMounted(() => {
  const savedTheme = localStorage.getItem('theme') || 'piscine-dark'
  isDark.value = savedTheme === 'piscine-dark'
  applyTheme(isDark.value)
  checkIsRegisterPage()
  checkUserSession()
})
</script>

<template>
  <div class="flex flex-col h-screen overflow-y-auto text-base-content bg-base-300 font-text">
    <div class="background-grid pointer-events-none">
      <div class="grid-3d"></div>
    </div>
    <nav v-if="!isRegisterPage && route.name !== 'not-found' && route.path !== '/admin'"
      class="sticky top-0 z-50 w-full backdrop-blur-sm border-b border-primary shadow-lg">
      <div class="max-w-[1800px] mx-auto px-4">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center gap-8">
            <div class="flex-shrink-0 flex items-center gap-2">
              <router-link to="/" class="flex items-center" active-class="" exact-active-class="">
                <img src="./assets/V2.2-Sombre.png" alt="GuardiHack Logo"
                  class="h-12 w-auto object-contain hover:opacity-80 transition-opacity" />
              </router-link>
            </div>
            <div class="hidden lg:flex items-center space-x-1">
              <template v-if="userLoaded">
                <router-link to="/challenges" class="nav-link">Challenges</router-link>
                <router-link to="/scoreboard" class="nav-link">Scoreboard</router-link>
                <router-link to="/users" class="nav-link">Joueurs</router-link>
              </template>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <template v-if="userLoaded">
              <a v-if="isAdmin" :href="'/admin'"
                class="nav-link text-red-500 hover:text-secondary-focus hidden md:flex items-center gap-1">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24"
                  stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37a1.724 1.724 0 002.572-1.065z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                Admin
              </a>
              <div class="dropdown dropdown-end">
                <label tabindex="0" class="flex item-center btn btn-ghost rounded-none gap-3 px-2 ml-2">
                  <div class="w-9 h-9 flex items-center justify-center bg-transparent overflow-hidden">
                    <img v-if="avatarUrl" :src="getAssetUrl(avatarUrl)" class="max-w-full max-h-full object-contain"
                      alt="Avatar Navbar" />
                    <span v-else class="text-sm font-bold text-primary">
                      {{ username?.[0]?.toUpperCase() || 'U' }}
                    </span>
                  </div>
                  <div class="text-right hidden sm:block">
                    <div class="text-[15px] text-primary font-text leading-none">{{ username }}</div>
                    <div class="text-[10px] text-primary font-text tracking-widest">lvl {{ level }}</div>
                  </div>
                </label>
                <ul tabindex="0"
                  class="mt-3 z-[50] p-2 shadow-2xl menu bg-base-200 border border-base-300 w-65 dropdown-content gap-1">
                  <li><router-link to="/profile" @click="closeDropdown" class="flex items-center py-2 px-4 min-h-[36px]">Mon profil</router-link></li>
                  <li><router-link to="/profile/settings" @click="closeDropdown" class="flex items-center py-2 px-4 min-h-[36px]">Paramètres</router-link></li>
                  <li><router-link to="/support" @click="closeDropdown" class="flex items-center py-2 px-4 min-h-[36px]">Support</router-link></li>
                  <li><a @click="handleLogout" class="flex items-center py-2 px-4 text-error font-bold cursor-pointer min-h-[36px]">Déconnexion</a></li>
                </ul>
              </div>
              <div class="w-[1px] h-6 bg-base-content/20 mx-2"></div>
              <div class="dropdown dropdown-end">
                <button class="btn btn-ghost btn-circle btn-sm">
                  <div class="indicator">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24"
                      stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                    </svg>
                    <span v-if="unreadNotifications.length > 0" class="badge badge-xs badge-primary indicator-item">
                      {{ unreadNotifications.length }}
                    </span>
                  </div>
                </button>
                <ul class="dropdown-content menu p-2 shadow-2xl bg-base-200 border border-base-300 rounded w-72 z-[50] max-h-96 overflow-y-auto">
                  <li class="menu-title">
                    <span class="font-cyber font-bold text-primary">
                      Notifications ({{ unreadNotifications.length }})
                    </span>
                  </li>
                  <template v-if="unreadNotifications.length > 0">
                    <li v-for="notif in unreadNotifications" :key="notif.id">
                      <a @mousedown.stop.prevent="handleMarkRead(notif)"
                        class="py-3 border border-base-100 flex items-start gap-2 hover:bg-base-300/50 transition-colors cursor-pointer">
                        <span class="badge badge-sm badge-primary mt-0.5">
                          {{ notif.type === 'global' ? '📢' : '🔔' }}
                        </span>
                        <div class="flex flex-col gap-0.5 flex-1">
                          <span class="font-bold text-xs text-base-content">{{ notif.title || 'Système' }}</span>
                          <span class="text-xs opacity-75 whitespace-normal break-words leading-tight">
                            {{ notif.message }}
                          </span>
                        </div>
                      </a>
                    </li>
                  </template>
                  <template v-else>
                    <li>
                      <div class="py-4 text-center text-xs opacity-50 italic text-base-content">
                        Aucune nouvelle notification
                      </div>
                    </li>
                  </template>
                  <li class="mt-2 sticky bottom-0 z-10 bg-transparent pt-1">
                    <router-link to="/notifications" class="text-xs font-text text-primary/80 tracking-wider py-3">
                      Voir tout
                    </router-link>
                  </li>
                </ul>
              </div>
            </template>
            <template v-else>
              <router-link to="/login" class="nav-link" active-class="active">Login</router-link>
            </template>
          </div>
        </div>
      </div>
    </nav>
    <main class="flex-1 w-full max-w-[1800px] mx-auto" :class="{ 'px-4 sm:px-6 lg:px-8 py-8': !isRegisterPage }">
      <router-view />
    </main>
    <footer v-if="!isRegisterPage && route.name !== 'not-found'"
      style="background-color: #0d1117 !important;"
      class="w-full relative z-40 mt-auto border-t border-primary/20 text-base-content/70 text-sm pt-[18px] pb-6 px-6 shadow-2xl flex-shrink-0">
      <div class="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        <p class="font-medium text-xs sm:text-sm text-center md:text-left">
          Copyright © 2026 <span class="text-primary font-bold font-cyber tracking-wider">GuardiHack</span>. All rights reserved.
        </p>
        <div class="flex items-center flex-wrap justify-center gap-4 sm:gap-6 text-xs sm:text-sm">
          <a href="#" class="hover:text-primary transition-colors duration-200">Contact Us</a>
          <span class="h-4 w-px bg-base-content/20"></span>
          <a href="#" class="hover:text-primary transition-colors duration-200">Privacy Policy</a>
          <span class="h-4 w-px bg-base-content/20"></span>
          <a href="#" class="hover:text-primary transition-colors duration-200">Trademark Policy</a>
        </div>
      </div>
    </footer>
    <transition name="fade-scale">
      <div v-if="showLevelUp" class="fixed inset-0 z-[100] flex items-center justify-center bg-base-300/40 backdrop-blur-md select-none">
        <div class="text-center flex flex-col items-center">
          <div class="absolute w-64 h-64 bg-primary/20 rounded-full blur-[100px] animate-pulse"></div>
          <h2 class="relative z-10 text-5xl md:text-7xl font-black font-titre uppercase tracking-widest text-primary drop-shadow-[0_0_15px_rgba(var(--p),0.5)] mb-2 animate-bounce">
            Level Up !
          </h2>
          <div class="relative z-10 w-64 sm:w-80 my-4 space-y-1.5 text-left">
            <div class="flex justify-between text-xs font-code font-bold text-primary tracking-wider">
              <span>XP_SYNC_COMPLETE</span>
              <span>{{ xpPercentage }}%</span>
            </div>
            <div class="w-full h-2.5 bg-base-100 border border-primary/40 p-0.5 rounded-sm shadow-inner">
              <div class="h-full bg-primary animate-xp-fill rounded-xs shadow-[0_0_10px_rgba(var(--p),0.8)]"></div>
            </div>
          </div>
          <div class="relative z-10 flex items-center gap-4 bg-base-100 border border-base-content/10 px-8 py-3 rounded-sm shadow-lg mt-2">
            <span class="text-base-content/70 font-code tracking-widest text-sm uppercase">Vous passez au LVL</span>
            <span class="text-3xl font-code font-bold text-base-content">{{ newLevelReached }}</span>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<style>
.background-grid {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 0;
  perspective: 1000px;
  overflow: hidden;
  opacity: 0.3;
  pointer-events: none;
}
.grid-3d {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 200%;
  height: 200%;
  transform: translate(-50%, -50%) rotateX(60deg) rotateZ(0deg);
  animation: gridRotate 20s linear infinite;
  background-image:
    linear-gradient(0deg,
      transparent 25%,
      color-mix(in srgb, theme('colors.primary') 60%, transparent) 25%,
      color-mix(in srgb, theme('colors.white') 100%, transparent) 26%,
      transparent 27%,
      transparent 74%,
      color-mix(in srgb, theme('colors.secondary') 50%, transparent) 75%,
      color-mix(in srgb, theme('colors.white') 100%, transparent) 76%,
      transparent 77%,
      transparent),
    linear-gradient(90deg,
      transparent 24%,
      color-mix(in srgb, theme('colors.primary') 60%, transparent) 25%,
      transparent 27%,
      transparent 74%,
      color-mix(in srgb, theme('colors.secondary') 50%, transparent) 75%,
      transparent 77%,
      transparent);
  background-size: 50px 50px;
}
.fade-scale-enter-active,
.fade-scale-leave-active {
  transition: all 0.5s ease-out;
}
.fade-scale-enter-from,
.fade-scale-leave-to {
  opacity: 0;
  transform: scale(0.9);
}
@keyframes xpFill {
  0% {
    width: 0%;
  }
  100% {
    width: 100%;
  }
}
.animate-xp-fill {
  animation: xpFill 2.1s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
@keyframes gridRotate {
  0% {
    transform: translate(-50%, -50%) rotateX(60deg) rotateZ(0deg);
  }
  100% {
    transform: translate(-50%, -50%) rotateX(60deg) rotateZ(360deg);
  }
}
</style>