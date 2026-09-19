<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import ChallengeCard from '../../components/ChallengeCard.vue'
import PageTitle from '../../components/PageTitle.vue'

const router = useRouter()
const STORAGE_KEY = 'guardiahack_categories_state'

// --- ÉTATS ---
const categoriesData = ref([])
const loading = ref(true)
const activeFilter = ref('Tous')

// --- LISTE DES FILTRES (Dynamique à partir des données de l'API) ---
const filterList = computed(() => ['Tous', ...categoriesData.value.map(c => c.name)])

// --- LOGIQUE DE FILTRAGE ---
const filteredCategories = computed(() => {
    if (activeFilter.value === 'Tous') return categoriesData.value
    return categoriesData.value.filter(cat => cat.name === activeFilter.value)
})

// --- VERIFICATION DU NOMBRE TOTAL DE CHALLENGES ---
const hasChallenges = computed(() => {
    return categoriesData.value.some(cat => cat.challenges && cat.challenges.length > 0)
})

// --- RÉCUPÉRATION DES DONNÉES DE L'API ---
const fetchChallengesData = async () => {
    loading.value = true
    try {
        // Un seul appel API puisqu'il contient déjà tout !
        const response = await axios.get('/api/user/challenge/list')

        // Sécurisation de l'extraction des données
        const allChallenges = response.data.challenges || response.data.list || response.data || []
        
        const groups = {}
        
        allChallenges.forEach(chal => {
            // Récupère le nom de la catégorie
            const catName = chal.category?.name || chal.category || chal.category_name || 'DIVERS'
            
            if (!groups[catName]) {
                groups[catName] = {
                    name: catName,
                    isCollapsed: false,
                    challenges: []
                }
            }

            // --- GESTION DES COULEURS DE DIFFICULTÉ ---
            const diffLower = (chal.difficulty || '').toLowerCase()
            let diffColor = 'text-base-content/70' // Couleur par défaut
            
            if (diffLower === 'easy' || diffLower === 'facile') {
                diffColor = 'text-success' // Vert
            } else if (diffLower === 'medium' || diffLower === 'moyen') {
                diffColor = 'text-warning' // Orange
            } else if (diffLower === 'hard' || diffLower === 'difficile') {
                diffColor = 'text-error' // Rouge
            } else if (diffLower === 'insane' || diffLower === 'extrême') {
                diffColor = 'text-[#a855f7]' // Violet (Code couleur Tailwind purple-500)
            }

            // Normalisation des propriétés pour ton composant <ChallengeCard />
            groups[catName].challenges.push({
                id: chal.id,
                title: chal.title || chal.name,
                difficulty: chal.difficulty || 'Non défini',
                difficultyColor: diffColor, // <-- La couleur passe ici !
                points: chal.points || 0,
                is_validated: !!chal.is_validated, // Le flag de l'API list
                has_active_instance: !!chal.has_active_instance,
                solves: chal.solves !== undefined ? chal.solves : (chal.solve_count || 0),
                type: chal.type
            })
        })

        // Restauration de l'état de collapse depuis le localStorage
        const savedState = localStorage.getItem(STORAGE_KEY)
        const parsedState = savedState ? JSON.parse(savedState) : {}

        categoriesData.value = Object.values(groups).map(cat => {
            if (parsedState[cat.name] !== undefined) {
                cat.isCollapsed = parsedState[cat.name]
            }
            return cat
        })

    } catch (error) {
        console.error("Erreur lors de la récupération des challenges :", error)
    } finally {
        loading.value = false
    }
}

// --- PERSISTANCE ---
onMounted(() => {
    fetchChallengesData()
})

const toggleCategory = (cat) => {
    cat.isCollapsed = !cat.isCollapsed
    const stateToSave = {}
    categoriesData.value.forEach(c => stateToSave[c.name] = c.isCollapsed)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(stateToSave))
}

const getProgress = (challenges) => {
    if (!challenges.length) return 0
    return Math.round((challenges.filter(c => c.is_validated).length / challenges.length) * 100)
}

const goToChallenge = (id) => {
    router.push(`/challenges/${id}`)
}
</script>

<template>
    <div class="w-full animate-fade-in pb-20 px-6">

        <PageTitle text="Challenges" />

        <div v-if="loading" class="flex flex-col items-center justify-center py-20 gap-4 text-primary">
            <span class="loading loading-ring loading-lg"></span>
            <p class="font-mono text-sm uppercase tracking-wider opacity-70 animate-pulse">Chargement des challenges...</p>
        </div>

        <div v-else>
            <div v-if="!hasChallenges" class="flex flex-col items-center justify-center py-16 px-4 border border-dashed border-base-content/20 rounded-md bg-base-200/20 max-w-xl mx-auto text-center font-mono">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-base-content/30 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <h3 class="text-lg font-bold uppercase tracking-wide mb-1">Oups...</h3>
                <p class="text-sm opacity-60">Aucun challenge n'a encore été publié sur la plateforme.</p>
            </div>

            <div v-else>
                <div class="flex flex-col md:flex-row justify-between items-center gap-4 bg-base-200/50 backdrop-blur-md p-4 rounded-md border border-base-300 mb-8">
                    <span class="text-sm font-text opacity-60 uppercase">Filtrer par catégorie :</span>
                    <div class="flex flex-wrap gap-2 justify-center">
                        <button v-for="filter in filterList" :key="filter" @click="activeFilter = filter"
                            :class="['btn btn-sm font-code px-6', activeFilter === filter ? 'btn-primary' : 'btn-ghost border border-base-content/10']">
                            {{ filter }}
                        </button>
                    </div>
                </div>

                <div class="space-y-12">
                    <div v-for="cat in filteredCategories" :key="cat.name" class="w-full">

                        <div class="flex flex-col sm:flex-row justify-between items-center py-4 border-b border-primary/20 gap-4 cursor-pointer hover:bg-primary/5 px-4 rounded-t-lg bg-base-200/30" @click="toggleCategory(cat)">
                            <div class="flex items-center gap-10">
                                <h2 class="text-xl font-text text-primary tracking-widest">{{ cat.name }}</h2>
                                <div class="badge badge-outline opacity-80 font-code">{{ cat.challenges.length }}</div>
                            </div>

                            <div class="flex items-center gap-10">
                                <div class="flex items-center gap-5">
                                    <progress class="progress progress-primary w-32 md:w-48 bg-base-300" :value="getProgress(cat.challenges)" max="100"></progress>
                                    <span class="font-code text-sm opacity-80">{{ getProgress(cat.challenges) }}%</span>
                                </div>
                                <button class="btn btn-circle btn-ghost transition-transform duration-300" :class="{ 'rotate-180': cat.isCollapsed }">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
                                    </svg>
                                </button>
                            </div>
                        </div>

                        <transition name="expand">
                            <div v-show="!cat.isCollapsed" class="overflow-hidden">
                                <div class="grid grid-cols-1 xl:grid-cols-8 md:grid-cols-4 lg:grid-cols-6 gap-4 2xl:grid-cols-8 py-8">
                                    <div v-for="chal in cat.challenges" :key="chal.id" class="relative">
                                        <div v-if="chal.has_active_instance" class="absolute -top-2 -right-2 z-20 flex items-center gap-1 bg-warning/90 text-warning-content px-2 py-0.5 rounded-full text-[9px] font-mono font-bold uppercase shadow-lg animate-pulse border border-warning">
                                            <span class="w-1.5 h-1.5 rounded-full bg-error animate-ping"></span>
                                            Instance en cours
                                        </div>
                                        <ChallengeCard :challenge="chal" @open="goToChallenge" />
                                    </div>
                                </div>
                            </div>
                        </transition>

                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.animate-fade-in {
    animation: fadeIn 0.4s ease-out forwards;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* ANIMATION EXPAND */
.expand-enter-active,
.expand-leave-active {
    transition: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    max-height: 2000px;
}

.expand-enter-from,
.expand-leave-to {
    max-height: 0;
    opacity: 0;
    transform: translateY(-10px);
}

@media (min-width: 1920px) {
    .grid-cols-8 {
        grid-template-columns: repeat(8, minmax(0, 1fr));
    }
}
</style>