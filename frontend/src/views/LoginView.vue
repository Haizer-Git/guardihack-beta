<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const email = ref('')
const password = ref('')
const loading = ref(false)

const handleLogin = () => {
  loading.ref = true
  // Simulation d'authentification
  setTimeout(() => {
    console.log("Connecté avec :", email.value)
    router.push('/') // Redirige vers l'accueil
  }, 1500)
}
</script>

<template>
  <div class="min-h-[80vh] flex items-center justify-center px-4">
    <div class="card w-full max-w-md bg-base-200 shadow-2xl border border-primary/20 p-8">
      <div class="text-center mb-10">
        <h1 class="text-3xl font-cyber font-bold text-primary tracking-widest uppercase">Login</h1>
        <p class="text-xs opacity-50 font-mono mt-2 italic">Entrez vos accès pour accéder au réseau</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-6">
        <div class="form-control">
          <label class="label"><span class="label-text font-cyber text-xs uppercase">Email / Username</span></label>
          <input v-model="email" type="text" placeholder="agent@guardihack.io" class="input input-bordered focus:border-primary font-mono" required />
        </div>

        <div class="form-control">
          <label class="label"><span class="label-text font-cyber text-xs uppercase">Password</span></label>
          <input v-model="password" type="password" placeholder="••••••••" class="input input-bordered focus:border-primary font-mono" required />
          <label class="label mt-1 text-right">
            <a href="#" class="label-text-alt link link-hover opacity-50">Forgot password?</a>
          </label>
        </div>

        <button type="submit" class="btn btn-primary w-full font-cyber tracking-widest uppercase">
          <span v-if="loading" class="loading loading-spinner"></span>
          Initialiser la session
        </button>
      </form>

      <div class="divider font-mono text-[10px] opacity-20 uppercase my-8">New Agent?</div>

      <p class="text-center text-sm">
        Pas encore de compte ? 
        <router-link to="/register" class="text-primary font-bold hover:underline">S'enregistrer</router-link>
      </p>
    </div>
  </div>
</template>