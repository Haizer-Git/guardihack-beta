<template>
  <PageTitle text="Paramètre du profil" />
  <Transition enter-active-class="transition duration-300 ease-out" enter-from-class="opacity-0 translate-y-4"
    enter-to-class="opacity-100 translate-y-0" leave-active-class="transition duration-200 ease-in"
    leave-from-class="opacity-100 translate-y-0" leave-to-class="opacity-0 translate-y-4">
    <div v-if="toast.show" :class="toast.type === 'success' ? 'border-success text-success' : 'border-error text-error'"
      class="fixed bottom-6 right-6 z-50 bg-base-200 border px-5 py-3 rounded-sm shadow-2xl font-text text-sm flex items-center gap-3">
      <span>{{ toast.type === 'success' ? '' : '' }}</span>
      <span>{{ toast.message }}</span>
    </div>
  </Transition>

  <div class="text-base-content antialiased md:p-8">
    <div class="max-w-7xl mx-auto flex flex-col gap-10">
      <div class="bg-base-300 backdrop-blur-md border-[2px] border-base-200 p-6">
        <div class="space-y-6 pb-6 border-b  border-base-300">
          <div>
            <label class="block text-sm font-titre text-base-content/50 mb-1.5 uppercase tracking-widest">Nom
              d'utilisateur (Pseudo)</label>
            <input v-model="profile.username" type="text" placeholder="Votre pseudo"
              class="w-full bg-base-100 border border-base-300 px-4 py-2.5 text-base-content font-text focus:outline-none focus:border-primary" />
          </div>
          <div>
            <label class="block text-sm font-titre text-base-content/50 mb-1.5 uppercase tracking-widest">Mode de
              confidentialité</label>
            <div class="flex gap-4">
              <button @click="profile.is_private = false"
                :class="!profile.is_private ? 'bg-base-300 text-base-content shadow-lg border-base-content/20' : 'bg-base-100 text-base-content/40 border-base-300 hover:bg-base-200'"
                class="flex-1 py-3 font-text font-bold uppercase tracking-wider text-sm border cursor-pointer">
                Public</button>
              <button @click="profile.is_private = true"
                :class="profile.is_private ? 'bg-base-300 text-base-content shadow-lg border-base-content/20' : 'bg-base-100 text-base-content/40 border-base-300 hover:bg-base-200'"
                class="flex-1 py-3 font-text font-bold uppercase tracking-wider text-sm border cursor-pointer">
                Privé</button>
            </div>
            <p class="text-xs text-base-content/40 mt-2 font-text">* En mode privé, votre prénom et nom ne seront pas visibles par les autres utilisateurs.</p>
          </div>
        </div>
        <div class="pt-6 flex justify-end">
          <button @click="saveProfile" :disabled="isLoading || !hasChanges"
            class="px-6 py-3 bg-base-300 hover:bg-base-content/10 text-base-content border border-base-content/20 font-titre uppercase tracking-wider text-sm shadow-sm disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer">
            {{ isLoading ? 'Enregistrement...' : 'Sauvegarder le profil' }}
          </button>
        </div>
      </div>
      <div class="bg-base-300 backdrop-blur-md border-[2px] border-base-200 p-6">
        <h2 class="text-2xl font-titre font-bold mb-6 uppercase tracking-wider">Sécurité du compte</h2>
        <div
          class="relative bg-base-100 border border-base-300 p-8 flex flex-col items-center justify-center min-h-[220px] text-center max-w-3xl mx-auto">
          <div v-if="step === 'request'"
            class="absolute inset-0 flex flex-col items-center justify-center gap-4 px-8 pointer-events-none select-none opacity-60 z-0">
            <p class="text-sm font-text text-warning uppercase tracking-wider font-bold">Un code de sécurité a été
              envoyé sur votre boîte mail.</p>
            <div
              class="w-full max-w-sm bg-base-200 border border-base300 ,px-4 py-3 font-code font-bold text-2xl tracking-[12px] text-center">
              000000</div>
            <div class="flex gap-3 w-full max-w-sm">
              <div class="flex-1 border border-base-300 text-basec-content/40 py-2.5 font-titre text-sm text-center">
                Retour</div>
              <div class="flex-1 bg-base-300 border border-base-content/20 py-2.5 font-titre text-sm text-center">
                Valider le code</div>
            </div>
          </div>
          <div v-if="step === 'request'"
            class="absolute inset-0 bg-base-100/30 backdrop-blur-md z-[1] pointer-events-none"></div>
          <div class="relative z-10 w-full flex flex-col items-center">
            <div v-if="step === 'request'" class="space-y-5 w-full flex flex-col items-center">
              <p class="text-l font-text text-base-content/50 max-w-md">Pour modifier votre passphrase, vous devez
                valider votre identité via un code temporaire.</p>
              <button @click="requestSecurityCode" :disabled="isLoading"
                class="px-6 py-3 bg-base-300 hover:bg-base-content/10 text-base-content border border-base-content/20 font-text font-bold text-sm disabled:opacity-50 cursor-pointer">
                {{ isLoading ? 'Envoi du mail...' : 'Recevoir un code de sécurité par mail' }}
              </button>
            </div>
            <div v-if="step === 'verify'" class="space-y-5 max-w-sm w-full">
              <p class="text-sm font-text text-green-500 font-bold">Merci d'entrer le code de sécurité reçu sur le mail 
                lié au compte.</p>
              <input v-model="securityCode" type="text" maxlength="6" placeholder="000000"
                class="w-full bg-base-100 border border-base-300 px-4 py-2.5 text-base-content font-code focus:outline-none focus:border-primary text-center tracking-[12px] text-2xl font-bold" />
              <div v-if="overlayError"
                class="text-xs font-text text-error bg-error/10 border border-error/20 p-2 rounded-sm text-center">{{
                  overlayError }}</div>
              <div class="flex gap-3">
                <button @click="step = 'request'"
                  class="flex-1 bg-transparent border border-base-300 text-base-content/40 py-2.5 rounded-sm font-titre text-xs uppercase tracking-wider hover:text-base-content transition">Retour</button>
                <button @click="verifySecurityCode" :disabled="isLoading"
                  class="flex-1 px-6 py-2.5 bg-base-300 hover:bg-base-content/10 text-base-content border border-base-content/20 font-titre font-bold uppercase tracking-wider text-xs transition disabled:opacity-50 rounded-sm">
                  {{ isLoading ? 'Vérification...' : 'Valider le code' }}
                </button>
              </div>
            </div>
            <div v-if="step === 'reset'" class="space-y-4 w-full max-w-md text-left">
              <p class="text-sm font-text text-success tracking-wider font-bold text-center mb-2">Code
                validé. Définissez votre nouveau mot de passe.</p>
              <div class="space-y-3">
                <div>
                  <label class="block text-xs font-text text-base-content/50 mb-1.5 uppercase tracking-wider">Nouveau
                    mot de passe</label>
                  <input v-model="passphraseForm.new_passphrase" type="password" placeholder="••••••••"
                    class="w-full bg-base-100 border border-base-300 px-4 py-2.5 text-base-content font-text focus:outline-none focus:border-primary transition rounded-sm" />
                </div>
                <div>
                  <label class="block text-xs font-text text-base-content/50 mb-1.5 uppercase tracking-wider">Confirmer
                    le mot de passe</label>
                  <input v-model="passphraseForm.confirm_passphrase" type="password" placeholder="••••••••"
                    class="w-full bg-base-100 border border-base-300 px-4 py-2.5 text-base-content font-text focus:outline-none focus:border-primary transition rounded-sm" />
                </div>
              </div>
              <div class="flex gap-3 pt-2">
                <button @click="step = 'verify'"
                  class="bg-transparent border border-base-300 text-base-content/40 px-4 py-2.5 rounded-sm font-titre text-xs uppercase tracking-wider hover:text-base-content transition">Retour</button>
                <button @click="submitNewpassphrase" :disabled="isLoading"
                  class="flex-1 px-6 py-2.5 bg-base-300 hover:bg-base-content/10 text-base-content border border-base-content/20 font-titre font-bold uppercase tracking-wider text-xs transition disabled:opacity-50 rounded-sm">
                  {{ isLoading ? 'Mise à jour...' : 'Confirmer le changement' }}
                </button>
              </div>
            </div>

          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import PageTitle from '../../components/PageTitle.vue'

const profile = ref({ username: '', is_private: false })
const initialProfile = ref({ username: '', is_private: false })

const isLoading = ref(false)
const step = ref('request')
const securityCode = ref('')
const overlayError = ref('')
const passphraseForm = ref({ new_passphrase: '', confirm_passphrase: '' })
const toast = ref({ show: false, message: '', type: 'success' })

let toastTimer = null
function showToast(message, type = 'success') {
  if (toastTimer) clearTimeout(toastTimer)
  toast.value = { show: true, message, type }
  toastTimer = setTimeout(() => toast.value.show = false, 3000)
}

const hasChanges = computed(() => {
  return (
    profile.value.username !== initialProfile.value.username ||
    profile.value.is_private !== initialProfile.value.is_private
  )
})

async function loadUserSettings() {
  try {
    const { data } = await axios.get('/api/auth/session')
    const userData = data.session || data.user || data
    if (userData) {
      const uname = userData.username || ''
      const isPriv = !!userData.is_private
      console.log('Données utilisateur chargées :', userData)
      profile.value.username = uname
      profile.value.is_private = isPriv

      initialProfile.value.username = uname
      initialProfile.value.is_private = isPriv
    }
  } catch (e) { console.error(e) }
}

async function saveProfile() {
  isLoading.value = true
  
  const usernameChanged = profile.value.username !== initialProfile.value.username
  const privacyChanged = profile.value.is_private !== initialProfile.value.is_private

  try {
    const requests = []
    if (usernameChanged) {
      requests.push(axios.post('/api/user/update/username', { new_username: profile.value.username }))
    }
    if (privacyChanged) {
      requests.push(axios.post('/api/user/update/privacy', { new_privacy_mode: profile.value.is_private }))
    }
    if (requests.length > 0) {
      await Promise.all(requests)
      initialProfile.value.username = profile.value.username
      initialProfile.value.is_private = profile.value.is_private
      showToast("Profil mis à jour avec succès !")
    }
  } catch (e) {
    showToast(e.response?.data?.message || "Erreur lors de la sauvegarde.", 'error')
  } finally { 
    isLoading.value = false 
  }
}

async function requestSecurityCode() {
  isLoading.value = true
  overlayError.value = ''
  try {
    await axios.get('/api/user/update/passphrase/code')
    step.value = 'verify'
  } catch (e) {
    showToast(e.response?.data?.message || "Impossible d'envoyer le code de sécurité.", 'error')
  } finally { isLoading.value = false }
}

async function verifySecurityCode() {
  if (securityCode.value.length !== 6) { overlayError.value = "Le code doit comporter 6 chiffres."; return }
  isLoading.value = true
  overlayError.value = ''
  try {
    const { status } = await axios.post('/api/user/update/passphrase/verify', { code: securityCode.value })
    if (status === 200) step.value = 'reset'
  } catch (e) {
    overlayError.value = e.response?.data?.message || "Code invalide ou expiré."
  } finally { isLoading.value = false }
}

async function submitNewpassphrase() {
  if (!passphraseForm.value.new_passphrase || !passphraseForm.value.confirm_passphrase) return showToast("Veuillez remplir tous les champs.", 'error')
  if (passphraseForm.value.new_passphrase !== passphraseForm.value.confirm_passphrase) return showToast("Les deux mots de passe ne correspondent pas.", 'error')
  isLoading.value = true
  try {
    const response = await axios.post('/api/user/update/passphrase', {
      code: securityCode.value,
      new_passphrase: passphraseForm.value.new_passphrase
    })

    if (response.status === 200) {
      alert("Mot de passe mis à jour avec succès !")
      step.value = 'request'
      securityCode.value = ''
      passphraseForm.value.new_passphrase = ''
      passphraseForm.value.confirm_passphrase = ''
    }
  } catch (error) {
    alert(error.response?.data?.message || "Erreur lors de la mise à jour.")
  } finally {
    isLoading.value = false
  }
}

onMounted(loadUserSettings)
</script>