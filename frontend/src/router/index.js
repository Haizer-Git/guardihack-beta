import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import GroupsView from '../views/GroupsView.vue'
import ScoreboardView from '../views/ScoreboardView.vue'
import TracksView from '../views/TracksView.vue'
import ChallengesView from '../views/ChallengesView.vue'
import RouteDetailView from '../views/RouteDetailView.vue'
import ProfileView from '../views/ProfileView.vue'
import ProfileSettingsView from '../views/ProfileSettingsView.vue'
import RulesView from '../views/RulesView.vue'
import MachineDetailView from '../views/MachineDetailView.vue'
import AdminView from '../views/AdminView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue' 

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView},
    { path: '/groups', name: 'groups', component: GroupsView},
    { path: '/scoreboard', name: 'scoreboard', component: ScoreboardView},
    { path: '/tracks', name: 'tracks', component: TracksView},
    { path: '/rules', name: 'rules', component: RulesView},
    { path: '/profile', name: 'profile', component: ProfileView},
    { path: '/profile/settings', name: 'profile-settings', component: ProfileSettingsView},
    { path: '/admin', name: 'admin', component: AdminView},
    { path: '/login', name: 'login', component: LoginView },
    { path: '/register', name: 'register', component: RegisterView },

    { path: '/challenges/:id', name: 'challenge-list', component: ChallengesView },
    { path: '/challenge-detail/:id', name: 'challenge-detail', component: () => import('../views/ChallengeDetailView.vue') },

    { path: '/routes/:id', name: 'route-detail', component: RouteDetailView },
    { path: '/machine/:id', name: 'machine-detail', component: MachineDetailView },
  ]
})
export default router