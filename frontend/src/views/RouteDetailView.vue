<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// --- DONNÉES SIMULÉES (Provenant normalement de l'API/Admin) ---
const routeData = ref({
  track: "T01",
  title: "Fondamentaux du Web",
  currentTaskIndex: 0,
  tasks: [
    {
      id: 1,
      title: "Introduction au protocole HTTP",
      content: `
        <p>Le protocole <b>HTTP (HyperText Transfer Protocol)</b> est la base de tout échange sur le Web. Il fonctionne sur un modèle Requête-Réponse.</p>
        <pre class="bg-base-300 p-4 rounded-lg my-4 font-mono text-xs">
GET /index.html HTTP/1.1
Host: target.com
User-Agent: Mozilla/5.0</pre>
        <p>Les codes d'état (Status Codes) sont essentiels : 200 (OK), 404 (Not Found), 500 (Server Error).</p>
      `,
      questions: [
        { id: 101, text: "Quel code d'état indique une redirection permanente ?", answer: "301", points: 2, solved: true },
        { id: 102, text: "Quelle méthode HTTP est utilisée pour envoyer des données sensibles (formulaires) ?", answer: "POST", points: 3, solved: false }
      ]
    },
    {
      id: 2,
      title: "Analyse des En-têtes (Headers)",
      content: `<p>Les headers permettent de passer des informations supplémentaires comme le type de contenu ou les cookies...</p>`,
      questions: [
        { id: 201, text: "Quel header est utilisé pour gérer les sessions ?", answer: "Set-Cookie", points: 5, solved: false }
      ]
    }
  ]
})

// --- LOGIQUE ---
const currentTask = computed(() => routeData.value.tasks[routeData.value.currentTaskIndex])
const userAnswers = ref({})
const feedback = ref({}) // Pour afficher 'Correct' ou 'Faux'

const checkAnswer = (question) => {
  const input = userAnswers.value[question.id]?.trim()
  if (input?.toLowerCase() === question.answer.toLowerCase()) {
    question.solved = true
    feedback.value[question.id] = { type: 'success', msg: 'Correct !' }
  } else {
    feedback.value[question.id] = { type: 'error', msg: 'Réponse incorrecte.' }
  }
}

const totalPoints = computed(() => {
  return routeData.value.tasks.reduce((acc, task) => {
    return acc + task.questions.reduce((qAcc, q) => q.solved ? qAcc + q.points : qAcc, 0)
  }, 0)
})
</script>

<template>
  <div class="w-full min-h-screen flex flex-col animate-fade-in">
    
    <div class="mb-6 px-6">
      <h1 class="block w-full text-center text-3xl font-cyber font-bold bg-primary text-base-100 py-3 uppercase tracking-widest shadow-sm">
        Route : {{ routeData.track }} - {{ routeData.title }}
      </h1>
    </div>

    <div class="flex flex-col lg:flex-row flex-grow px-6 gap-8 pb-10">
      
      <aside class="w-full lg:w-80 flex flex-col gap-4">
        <button @click="router.back()" class="btn btn-outline btn-sm font-cyber gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
          Retour aux Tracks
        </button>

        <div class="bg-base-200/50 border border-white/5 rounded-xl overflow-hidden">
          <div class="p-4 bg-primary/10 border-b border-primary/20 flex justify-between items-center">
            <span class="font-cyber text-xs tracking-tighter">Progression</span>
            <span class="font-mono text-primary font-bold">{{ totalPoints }} pts</span>
          </div>
          
          <nav class="p-2 space-y-1">
            <button 
              v-for="(task, index) in routeData.tasks" :key="task.id"
              @click="routeData.currentTaskIndex = index"
              :class="['w-full text-left p-3 rounded-lg flex items-center gap-3 transition-all', 
                        routeData.currentTaskIndex === index ? 'bg-primary text-base-100 shadow-lg' : 'hover:bg-primary/10']"
            >
              <span class="font-mono text-xs opacity-50">#{{ index + 1 }}</span>
              <span class="text-sm font-bold truncate flex-grow">{{ task.title }}</span>
              <span v-if="task.questions.every(q => q.solved)" class="text-success">✔</span>
            </button>
          </nav>
        </div>
      </aside>

      <main class="flex-grow flex flex-col gap-8">
        
        <section class="card bg-base-200/40 border border-white/5 p-8">
          <div class="flex items-center gap-4 mb-6">
            <span class="bg-primary text-base-100 px-3 py-1 font-cyber text-sm">TASK {{ routeData.currentTaskIndex + 1 }}</span>
            <h2 class="text-2xl font-bold uppercase tracking-tight">{{ currentTask.title }}</h2>
          </div>
          
          <div class="prose prose-invert max-w-none mb-10" v-html="currentTask.content"></div>

          <div class="divider opacity-10">QUESTIONS</div>

          <div class="space-y-6">
            <div v-for="q in currentTask.questions" :key="q.id" 
                 :class="['p-6 rounded-xl border transition-all', q.solved ? 'border-success/30 bg-success/5' : 'border-white/5 bg-base-300/30']">
              
              <div class="flex justify-between items-start mb-4">
                <p class="font-bold text-lg">{{ q.text }}</p>
                <div class="badge badge-outline font-mono text-[10px]">{{ q.points }} pts</div>
              </div>

              <div class="flex flex-wrap gap-4">
                <input 
                  v-model="userAnswers[q.id]"
                  :disabled="q.solved"
                  type="text" 
                  placeholder="Votre réponse..." 
                  class="input input-bordered flex-grow font-mono focus:border-primary"
                  @keyup.enter="checkAnswer(q)"
                />
                <button 
                  @click="checkAnswer(q)"
                  :disabled="q.solved"
                  class="btn btn-primary px-8 font-cyber"
                >
                  {{ q.solved ? 'Validé' : 'Soumettre' }}
                </button>
              </div>

              <p v-if="feedback[q.id]" :class="['text-xs mt-3 font-mono', feedback[q.id].type === 'success' ? 'text-success' : 'text-error']">
                {{ feedback[q.id].msg }}
              </p>
            </div>
          </div>
        </section>

        <div class="flex justify-between items-center">
          <button 
            :disabled="routeData.currentTaskIndex === 0"
            @click="routeData.currentTaskIndex--"
            class="btn btn-ghost gap-2"
          >
            ← Précédent
          </button>
          <button 
            :disabled="routeData.currentTaskIndex === routeData.tasks.length - 1"
            @click="routeData.currentTaskIndex++"
            class="btn btn-ghost gap-2"
          >
            Suivant →
          </button>
        </div>

      </main>
    </div>
  </div>
</template>

<style scoped>
.font-cyber { font-family: 'Orbitron', 'Rajdhani', sans-serif; }
.animate-fade-in { animation: fadeIn 0.4s ease-out forwards; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

/* Style pour le contenu injecté (v-html) */
:deep(p) { margin-bottom: 1rem; color: rgba(255,255,255,0.7); line-height: 1.6; }
:deep(b) { color: white; }
</style>