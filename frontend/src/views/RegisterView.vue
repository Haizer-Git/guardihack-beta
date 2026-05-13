<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')

const handleRegister = () => {
  if (password.value !== confirmPassword.value) {
    alert("Les mots de passe ne correspondent pas !")
    return
  }
  console.log("Compte créé pour :", username.value)
  router.push('/login') // Redirige vers le login après inscription
}
</script>

<template>
  <div class="min-h-[80vh] flex items-center justify-center px-4">
    <div class="card w-full max-w-md bg-base-200 shadow-2xl border border-secondary/20 p-8">
      <div class="text-center mb-10">
        <h1 class="text-3xl font-cyber font-bold text-secondary tracking-widest uppercase">Register</h1>
        <p class="text-xs opacity-50 font-mono mt-2 italic">Nouveau profil détecté. Créez vos identifiants.</p>
      </div>

      <form @submit.prevent="handleRegister" class="space-y-4">
        <div class="form-control">
          <label class="label"><span class="label-text font-cyber text-xs uppercase">Username</span></label>
          <input v-model="username" type="text" placeholder="Vex_Root" class="input input-bordered focus:border-secondary font-mono" required />
        </div>

        <div class="form-control">
          <label class="label"><span class="label-text font-cyber text-xs uppercase">Email</span></label>
          <input v-model="email" type="email" placeholder="agent@guardihack.io" class="input input-bordered focus:border-secondary font-mono" required />
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="form-control">
            <label class="label"><span class="label-text font-cyber text-xs uppercase text-[10px]">Password</span></label>
            <input v-model="password" type="password" placeholder="••••" class="input input-bordered focus:border-secondary font-mono text-xs" required />
          </div>
          <div class="form-control">
            <label class="label"><span class="label-text font-cyber text-xs uppercase text-[10px]">Confirm</span></label>
            <input v-model="confirmPassword" type="password" placeholder="••••" class="input input-bordered focus:border-secondary font-mono text-xs" required />
          </div>
        </div>

        <button type="submit" class="btn btn-secondary w-full font-cyber tracking-widest uppercase mt-6">
          Générer l'accès
        </button>
      </form>

      <p class="text-center text-sm mt-8">
        Déjà inscrit ? 
        <router-link to="/login" class="text-secondary font-bold hover:underline">Se connecter</router-link>
      </p>
    </div>
  </div>
</template>