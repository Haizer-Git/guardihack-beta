<template>
  <PageTitle text="Support" />

  <!-- Toast -->
  <Transition
    enter-active-class="transition duration-300 ease-out"
    enter-from-class="opacity-0 translate-y-4"
    enter-to-class="opacity-100 translate-y-0"
    leave-active-class="transition duration-200 ease-in"
    leave-from-class="opacity-100 translate-y-0"
    leave-to-class="opacity-0 translate-y-4">
    <div v-if="toast.show"
      :class="toast.type === 'success' ? 'border-success text-success' : 'border-error text-error'"
      class="fixed bottom-6 right-6 z-50 bg-secondary border px-5 py-3 rounded-sm shadow-2xl font-mono text-sm flex items-center gap-3">
      <span>{{ toast.type === 'success' ? '✅' : '❌' }}</span>
      <span>{{ toast.message }}</span>
    </div>
  </Transition>

  <div class="text-base-content antialiased md:p-8">
    <div class="max-w-7xl mx-auto flex flex-col gap-6">

      <!-- FAQ -->
      <div class="bg-base-300 backdrop-blur-md border border-base-100 p-6 shadow-xl rounded-sm">
        <h2 class="text-xl font-titre font-bold mb-6 uppercase tracking-wider">Questions fréquentes</h2>
        <div class="flex flex-col gap-2">
          <div v-for="(item, i) in faq" :key="i" class="border border-base-300 rounded-sm overflow-hidden">
            <button
              @click="toggleFaq(i)"
              class="w-full flex items-center justify-between px-5 py-3 bg-base-100 hover:bg-neutral transition font-text text-sm font-bold uppercase tracking-wider text-left">
              <span>{{ item.q }}</span>
              <span class="text-secondary font-bold text-lg leading-none">{{ openFaq === i ? '−' : '+' }}</span>
            </button>
            <Transition
              enter-active-class="transition-all duration-200 ease-out"
              enter-from-class="opacity-0 max-h-0"
              enter-to-class="opacity-100 max-h-40"
              leave-active-class="transition-all duration-150 ease-in"
              leave-from-class="opacity-100 max-h-40"
              leave-to-class="opacity-0 max-h-0">
              <div v-if="openFaq === i" class="px-5 py-4 bg-base-100/50 text-base-content/70 font-mono text-sm border-t border-base-300">
                {{ item.a }}
              </div>
            </Transition>
          </div>
        </div>
      </div>

      <!-- Formulaire de contact -->
      <div class="bg-base-100 backdrop-blur-md border border-base-300 p-6 shadow-xl rounded-sm">
        <h2 class="text-xl font-titre font-bold mb-6 uppercase tracking-wider">Contacter le support</h2>

        <div class="flex flex-col gap-5 max-w-2xl">
          <div>
            <label class="block text-xs font-stitre text-base-content/50 mb-1.5 uppercase tracking-wider">Catégorie</label>
            <select v-model="form.category"
              class="w-full bg-base-100 border border-neutral px-4 py-2.5 text-base-content font-text focus:outline-none focus:border-primary transition rounded-sm">
              <option value="">-- Sélectionner --</option>
              <option value="bug">Bug / Erreur technique</option>
              <option value="challenge">Problème sur un challenge</option>
              <option value="account">Problème de compte</option>
              <option value="other">Autre</option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-stitre text-base-content/50 mb-1.5 uppercase tracking-wider">Sujet</label>
            <input v-model="form.subject" type="text" placeholder="Décrivez brièvement votre problème"
              class="w-full bg-base-100 border border-neutral px-4 py-2.5 text-base-content font-text focus:outline-none focus:border-primary transition rounded-sm" />
          </div>

          <div>
            <label class="block text-xs font-stitre text-base-content/50 mb-1.5 uppercase tracking-wider">Message</label>
            <textarea v-model="form.message" rows="5" placeholder="Décrivez votre problème en détail..."
              class="w-full bg-base-100 border border-neutral px-4 py-2.5 text-base-content font-text focus:outline-none focus:border-primary transition rounded-sm resize-none"></textarea>
          </div>

          <div class="flex justify-end">
            <button @click="submitTicket" :disabled="isLoading"
              class="px-6 py-3 bg-base-300 hover:bg-base-content/10 text-base-content border border-base-content/20 font-mono font-bold uppercase tracking-wider text-xs transition shadow-md disabled:opacity-50 rounded-sm cursor-pointer">
              {{ isLoading ? 'Envoi en cours...' : 'Envoyer le ticket' }}
            </button>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import PageTitle from '../../components/PageTitle.vue'

const openFaq = ref(null)
const isLoading = ref(false)
const toast = ref({ show: false, message: '', type: 'success' })

const form = ref({
  category: '',
  subject: '',
  message: ''
})

const faq = [
  {
    q: "Comment signaler un flag incorrect ?",
    a: "Si vous pensez qu'un flag est incorrect ou que le challenge contient une erreur, utilisez le formulaire ci-dessous en sélectionnant la catégorie 'Problème sur un challenge'. Décrivez le problème avec le nom du challenge."
  },
  {
    q: "Ma machine est bloquée / ne répond plus, que faire ?",
    a: "Essayez d'abord de reset la machine depuis la page du challenge. Si le problème persiste après quelques minutes, contactez le support avec la catégorie 'Bug / Erreur technique' en précisant le nom de la machine."
  },
  {
    q: "Je n'arrive pas à me connecter à mon compte.",
    a: "Vérifiez vos identifiants et que le Caps Lock n'est pas activé. Si vous avez oublié votre mot de passe, utilisez la fonctionnalité de réinitialisation sur la page de login. Pour tout autre problème, contactez le support."
  },
  {
    q: "Comment changer mon pseudo ou mon email ?",
    a: "Rendez-vous dans Paramètres (menu en haut à droite) pour modifier votre pseudo. La modification d'email n'est pas disponible en libre-service ; contactez le support si nécessaire."
  },
  {
    q: "Mes points ne s'affichent pas correctement.",
    a: "Le scoreboard peut mettre quelques minutes à se mettre à jour. Si le problème persiste plus de 10 minutes après la résolution d'un challenge, signalez-le via le formulaire ci-dessous."
  }
]

let toastTimer = null
function showToast(message, type = 'success') {
  if (toastTimer) clearTimeout(toastTimer)
  toast.value = { show: true, message, type }
  toastTimer = setTimeout(() => toast.value.show = false, 3000)
}

function toggleFaq(i) {
  openFaq.value = openFaq.value === i ? null : i
}

async function submitTicket() {
  if (!form.value.category || !form.value.subject.trim() || !form.value.message.trim()) {
    return showToast("Veuillez remplir tous les champs.", 'error')
  }
  isLoading.value = true
  try {
    await axios.post('/api/support/ticket', {
      category: form.value.category,
      subject: form.value.subject,
      message: form.value.message
    })
    showToast("Ticket envoyé ! Nous vous répondrons par mail.")
    form.value = { category: '', subject: '', message: '' }
  } catch (e) {
    showToast(e.response?.data?.message || "Erreur lors de l'envoi du ticket.", 'error')
  } finally {
    isLoading.value = false
  }
}
</script>