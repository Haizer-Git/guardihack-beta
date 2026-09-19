import { createRouter, createWebHistory } from 'vue-router'
import axios from 'axios'

// Authentification
import LoginView from '../views/authentification/LoginView.vue'
import RegisterView from '../views/authentification/RegisterView.vue'
import ResetPassphraseView from '../views/authentification/ResetPassphraseView.vue'

// Admin
import AdminView from '../views/admin/AdminView.vue'

// Public
import HomeView from '../views/public/HomeView.vue'
import RulesView from '../views/public/RulesView.vue'
import LeaderboardView from '../views/public/LeaderboardView.vue'
import UserListView from '../views/public/UserListView.vue'
import EventsView from '../views/public/EventsView.vue'
import NotificationView from '../views/public/NotificationView.vue'

// Profil
import ProfileView from '../views/profil/ProfileView.vue'
import ProfileSettingView from '../views/profil/ProfileSettingView.vue'
import ProfileSelectView from '../views/profil/ProfileSelectView.vue'
import SupportView from '../views/profil/SupportView.vue'

// Challenge
import ChallengesView from '../views/challenges/ChallengesView.vue'
import ChallengesDetailsView from '../views/challenges/ChallengesDetailsView.vue'

// errors
import NotFoundView from '../views/errors/NotFoundView.vue'

// -------- GUARDIHACKPOOL ---------
import PoolLayout from '../layouts/PoolLayout.vue'
import PoolHomeView from '../views/pool/PoolHomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { 
      path: '/admin', 
      name: 'admin', 
      component: AdminView,
      beforeEnter: async (to, from, next) => {
        try {
          const res = await axios.get('/api/user/me/profile')
          const userType = (res.data?.profile?.type || res.data?.user?.type || '').toLowerCase()
          if (userType === 'admin') {
            return next()
          }
        } catch (err) {
        }
        return next({
          name: 'not-found',
          params: { pathMatch: to.path.substring(1).split('/') },
          query: to.query,
          hash: to.hash,
          replace: true
        })
      }
    },
    { 
      path: '/login', 
      name: 'login', 
      component: LoginView,
      meta: { requiresGuest: true } 
    },
    { path: 
      '/reset/passphrase/:token', 
      name: 'reset-passphrase', 
      component: ResetPassphraseView 
    },
    { 
      path: '/register/:token', 
      name: 'register-token', 
      component: RegisterView,
      meta: { requiresGuest: true } 
    },
    { path: '/profile', name: 'profile', component: ProfileView },
    { 
      path: '/profile/:username', 
      name: 'user-profile', 
      component: ProfileView,
      beforeEnter: async (to, from, next) => {
        try {
          const res = await axios.get('/api/user/me/profile')
          const myUsername = res.data?.profile?.username || res.data?.user?.username
          if (myUsername && to.params.username.toLowerCase() === myUsername.toLowerCase()) {
            return next({ name: 'profile' })
          }
        } catch (err) {
        }
        next()
      }
    },
    { path: '/profile/select', name: 'profile-select', component: ProfileSelectView },
    { path: '/profile/settings', name: 'profile-settings', component: ProfileSettingView },
    { path: '/support', name: 'support', component: SupportView },
    { path: '/scoreboard', name: 'scoreboard', component: LeaderboardView },
    { path: '/users', name: 'users', component: UserListView },
    { path: '/rules', name: 'rules', component: RulesView },
    { path: '/events', name: 'events', component: EventsView },
    { path: '/challenges', name: 'challenges', component: ChallengesView },
    { path: '/challenges/:id', name: 'challenges-details', component: ChallengesDetailsView },
    { path: '/notifications', name: 'notifications', component: NotificationView },

    // --- TES ROUTES POOL (GuardiHack Pool) ---
    {
      path: '/pool',
      component: PoolLayout,
      children: [
        { path: '', name: 'pool-home', component: PoolHomeView },
      ]
    },

    // Le Not Found doit toujours rester à la TOUTE FIN
    { path: '/:pathMatch(.*)*', name: 'not-found', component: NotFoundView }
  ]
})

// Garde de navigation global pour empêcher l'accès à /login et /register si connecté
router.beforeEach(async (to, from, next) => {
  if (to.meta.requiresGuest) {
    try {
      const res = await axios.get('/api/auth/session')
      // Si l'API renvoie qu'une session est active (ajuste la condition selon la structure de ta réponse ex: res.data.logged_in ou res.data.user_id)
      if (res.data && (res.data.logged_in || res.data.user_id || res.data.status === 'success')) {
        return next({ name: 'home' })
      }
    } catch (err) {
    }
  }
  next()
})

export default router