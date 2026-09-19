import { createRouter, createWebHistory } from 'vue-router'
import axios from 'axios'

import LoginView from '../views/authentification/LoginView.vue'
import RegisterView from '../views/authentification/RegisterView.vue'
import ResetPassphraseView from '../views/authentification/ResetPassphraseView.vue'
import AdminView from '../views/admin/AdminView.vue'
import HomeView from '../views/public/HomeView.vue'
import LeaderboardView from '../views/public/LeaderboardView.vue'
import UserListView from '../views/public/UserListView.vue'
import NotificationView from '../views/public/NotificationView.vue'
import ProfileView from '../views/profil/ProfileView.vue'
import ProfileSettingView from '../views/profil/ProfileSettingView.vue'
import ChallengesView from '../views/challenges/ChallengesView.vue'
import ChallengesDetailsView from '../views/challenges/ChallengesDetailsView.vue'
import NotFoundView from '../views/errors/NotFoundView.vue'

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
    { path: '/profile/settings', name: 'profile-settings', component: ProfileSettingView },
    { path: '/scoreboard', name: 'scoreboard', component: LeaderboardView },
    { path: '/users', name: 'users', component: UserListView },
    { path: '/challenges', name: 'challenges', component: ChallengesView },
    { path: '/challenges/:id', name: 'challenges-details', component: ChallengesDetailsView },
    { path: '/notifications', name: 'notifications', component: NotificationView },
    { path: '/:pathMatch(.*)*', name: 'not-found', component: NotFoundView }
  ]
})

router.beforeEach(async (to, from, next) => {
  if (to.meta.requiresGuest) {
    try {
      const res = await axios.get('/api/auth/session')
      if (res.data && (res.data.logged_in || res.data.user_id || res.data.status === 'success')) {
        return next({ name: 'home' })
      }
    } catch (err) {
    }
  }
  next()
})

export default router