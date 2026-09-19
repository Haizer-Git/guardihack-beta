<template>
    <div class="w-full animate-fade-in pb-20 px-4 max-w-[1600px] mx-auto font-sans">

        <PageTitle text="Calendrier" />

        <div v-if="error" class="alert alert-error shadow-lg mb-6 max-w-4xl mx-auto">
            <span>{{ error }}</span>
        </div>

        <div class="flex flex-col lg:flex-row gap-8">
            
            <div class="flex-grow lg:w-2/3 bg-base-200/50 rounded-xl border border-base-300 shadow-xl overflow-hidden flex flex-col">

                <div class="flex items-center justify-between p-4 bg-base-300/80 border-b border-base-300">
                    <button @click="changeMonth(-1)" class="btn btn-sm btn-ghost hover:bg-primary hover:text-base-100">
                        « Précédent
                    </button>
                    <div class="flex items-center gap-4">
                        <h2 class="text-lg font-mono font-bold text-primary uppercase tracking-widest">
                            {{ currentMonthName }} {{ currentYear }}
                        </h2>
                        <button @click="goToToday" class="btn btn-xs btn-outline btn-primary">Aujourd'hui</button>
                    </div>
                    <button @click="changeMonth(1)" class="btn btn-sm btn-ghost hover:bg-primary hover:text-base-100">
                        Suivant »
                    </button>
                </div>

                <div class="grid grid-cols-7 bg-base-300/50 border-b border-base-300">
                    <div v-for="day in weekDays" :key="day" class="py-2 text-center font-mono text-sm opacity-60 uppercase">
                        {{ day }}
                    </div>
                </div>

                <div class="flex-grow grid grid-cols-7 grid-rows-5 gap-px bg-base-300 relative">
                    <div v-for="(dayObj, index) in calendarDays" :key="index" 
                         class="min-h-[110px] bg-base-100 p-1 transition-colors relative group hover:bg-base-200 flex flex-col justify-between" 
                         :class="{
                             'opacity-40': !dayObj.isCurrentMonth,
                             'bg-primary/5 border border-primary/30': isToday(dayObj.date)
                         }">
                        
                        <span class="font-mono text-sm pl-1 pt-1 block" :class="{
                            'text-primary font-bold': isToday(dayObj.date),
                            'opacity-70': !isToday(dayObj.date)
                        }">
                            {{ dayObj.date.getDate() }}
                        </span>

                        <div class="mt-1 space-y-1 flex-grow">
                            <div v-for="(event, trackIndex) in computedGridEvents[index]?.slice(0, 3)" :key="trackIndex" class="h-[22px]">
                                <div v-if="event"
                                    @click.stop="selectedEvent = event" 
                                    class="text-[10px] h-full flex items-center cursor-pointer transition-all border-y border-transparent hover:border-white/40 font-mono select-none z-10 relative" 
                                    :class="{
                                        'bg-accent/20 text-accent': event.format === 'Jeopardy',
                                        'bg-secondary/20 text-secondary': event.format !== 'Jeopardy',
                                        'font-bold': isSameDay(dayObj.date, new Date()) || (new Date() >= new Date(event.start) && new Date() <= new Date(event.finish)),
                                        'rounded-l border-l pl-1.5': !checkLeft(index, trackIndex, event.id),
                                        'rounded-r border-r pr-1.5': !checkRight(index, trackIndex, event.id),
                                        'border-l-0 -ml-[5px] pl-[5px]': checkLeft(index, trackIndex, event.id),
                                        'border-r-0 -mr-[5px] pr-[5px]': checkRight(index, trackIndex, event.id)
                                    }" 
                                    :title="event.title">
                                    <span v-if="!checkLeft(index, trackIndex, event.id)" class="truncate w-full">{{ event.title }}</span>
                                </div>
                                <div v-else class="h-full invisible"></div>
                            </div>
                        </div>

                        <div v-if="getDisplayCount(index) > 3"
                            class="text-[9px] text-center opacity-60 font-mono pb-1 bg-base-100/80 w-full">
                            +{{ getDisplayCount(index) - 3 }} autres
                        </div>
                    </div>

                    <div v-if="loading" class="absolute inset-0 bg-base-100/60 backdrop-blur-xs flex justify-center items-center z-20">
                        <span class="loading loading-ring loading-lg text-primary"></span>
                    </div>
                </div>

            </div>

            <div class="lg:w-1/3 flex flex-col gap-4">
                <div class="bg-base-200/50 rounded-xl border border-base-300 shadow-xl p-6 h-full flex flex-col">
                    <div class="flex items-center gap-3 mb-6 pb-4 border-b border-base-300">
                        <div class="w-3 h-3 bg-red-500 rounded-full animate-pulse shadow-[0_0_10px_#ef4444]"></div>
                        <h3 class="font-cyber text-xl font-bold uppercase tracking-wider">Prochains CTF</h3>
                    </div>

                    <div class="flex-grow overflow-y-auto pr-2 space-y-4 no-scrollbar max-h-[600px] lg:max-h-none">
                        <div v-if="upcomingEvents.length === 0 && !loading" class="text-center opacity-50 font-mono py-10">
                            Aucun événement trouvé sur cette période.
                        </div>

                        <div v-for="event in upcomingEvents.slice(0, 10)" :key="event.id"
                             @click="selectedEvent = event"
                             class="block bg-base-100 border border-base-300 hover:border-primary/50 rounded-lg p-4 transition-all hover:shadow-lg group cursor-pointer">
                            <div class="flex items-start gap-4">
                                <div class="w-12 h-12 rounded bg-base-300 flex-shrink-0 flex items-center justify-center overflow-hidden">
                                    <img v-if="event.logo" :src="event.logo" :alt="event.title" class="w-full h-full object-cover" />
                                    <span v-else class="text-xl font-cyber">{{ event.title.charAt(0) }}</span>
                                </div>

                                <div class="flex-grow min-w-0">
                                    <h4 class="font-bold text-sm truncate group-hover:text-primary transition-colors">{{ event.title }}</h4>
                                    <div class="flex items-center gap-2 mt-1 text-xs opacity-70">
                                        <span class="font-mono">{{ formatDateShort(event.start) }}</span>
                                        <span>→</span>
                                        <span class="font-mono">{{ formatDateShort(event.finish) }}</span>
                                    </div>
                                    <div class="flex gap-2 mt-2">
                                        <span class="badge badge-xs badge-outline" :class="event.format === 'Jeopardy' ? 'badge-accent' : 'badge-secondary'">
                                            {{ event.format || 'Unknown' }}
                                        </span>
                                        <span class="badge badge-xs badge-ghost">
                                            {{ formatDuration(event.duration) }}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="mt-4 pt-4 border-t border-base-300 text-center text-xs opacity-50 font-mono flex justify-center items-center gap-2">
                        Propulsé par
                        <a href="https://ctftime.org/" target="_blank" class="hover:text-primary transition-colors font-bold">CTFtime.org</a>
                    </div>
                </div>
            </div>
        </div>

        <Teleport to="body">
            <div v-if="selectedEvent" class="modal modal-open backdrop-blur-sm transition-all z-50">
                <div class="modal-box bg-base-200 border-2 border-primary shadow-[0_0_30px_rgba(var(--p),0.2)] max-w-2xl relative">
                    <button @click="selectedEvent = null" class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">✕</button>
                    
                    <div class="flex flex-col sm:flex-row gap-5 mt-4">
                        <div class="w-20 h-20 rounded bg-base-300 flex-shrink-0 flex items-center justify-center overflow-hidden border border-base-300 mx-auto sm:mx-0">
                            <img v-if="selectedEvent.logo" :src="selectedEvent.logo" :alt="selectedEvent.title" class="w-full h-full object-cover" />
                            <span class="text-3xl font-cyber text-primary">{{ selectedEvent.title.charAt(0) }}</span>
                        </div>

                        <div class="flex-grow text-center sm:text-left">
                            <span class="badge badge-primary uppercase font-mono text-xs mb-1">
                                {{ selectedEvent.format || 'Format Inconnu' }}
                            </span>
                            <h3 class="font-cyber text-2xl font-bold text-primary mb-2">
                                {{ selectedEvent.title }}
                            </h3>
                        </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs font-mono my-6 bg-base-300/50 p-4 rounded-lg border border-base-300">
                        <div>📅 <span class="opacity-60">Début :</span> <span class="text-secondary font-bold">{{ formatDateFull(selectedEvent.start) }}</span></div>
                        <div>🏁 <span class="opacity-60">Fin :</span> <span class="text-secondary font-bold">{{ formatDateFull(selectedEvent.finish) }}</span></div>
                        <div>⏳ <span class="opacity-60">Durée :</span> <span class="text-accent font-bold">{{ formatDuration(selectedEvent.duration) }}</span></div>
                        <div v-if="selectedEvent.weight">⚖️ <span class="opacity-60">Poids CTFtime :</span> <span class="text-accent font-bold">{{ selectedEvent.weight }}</span></div>
                    </div>

                    <div v-if="selectedEvent.description" class="my-4">
                        <h4 class="text-sm font-bold uppercase tracking-wider mb-2 opacity-70 font-mono">Description :</h4>
                        <p class="text-sm text-base-content/80 leading-relaxed bg-base-100 p-3 rounded border border-base-300 max-h-40 overflow-y-auto no-scrollbar whitespace-pre-line">
                            {{ selectedEvent.description }}
                        </p>
                    </div>

                    <div class="modal-action border-t border-base-300 pt-4 flex flex-wrap gap-2 justify-end">
                        <a v-if="selectedEvent.url" :href="selectedEvent.url" target="_blank" class="btn btn-primary btn-sm font-mono">
                            Site Web Officiel
                        </a>
                        <a v-if="selectedEvent.ctftime_url" :href="selectedEvent.ctftime_url" target="_blank" class="btn btn-outline btn-secondary btn-sm font-mono">
                            Page CTFtime
                        </a>
                        <button @click="selectedEvent = null" class="btn btn-sm btn-ghost">Fermer</button>
                    </div>
                </div>
                <div class="modal-backdrop" @click="selectedEvent = null"></div>
            </div>
        </Teleport>

    </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import PageTitle from '../../components/PageTitle.vue'

// --- ÉTATS ---
const loading = ref(true)
const error = ref(null)
const events = ref([])
const selectedEvent = ref(null)

const currentDate = ref(new Date()) // Date qui contrôle le mois affiché
const weekDays = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']

// --- VARIABLES DU CALENDRIER ---
const currentYear = computed(() => currentDate.value.getFullYear())
const currentMonth = computed(() => currentDate.value.getMonth())
const currentMonthName = computed(() => {
    return currentDate.value.toLocaleDateString('fr-FR', { month: 'long' })
})

// --- LOGIQUE DE CRÉATION DE LA GRILLE DU CALENDRIER ---
const calendarDays = computed(() => {
    const year = currentYear.value
    const month = currentMonth.value

    const firstDayOfMonth = new Date(year, month, 1)
    const lastDayOfMonth = new Date(year, month + 1, 0)

    let firstDayIndex = firstDayOfMonth.getDay() - 1
    if (firstDayIndex === -1) firstDayIndex = 6

    const days = []

    const prevMonthLastDay = new Date(year, month, 0).getDate()
    for (let i = firstDayIndex - 1; i >= 0; i--) {
        days.push({
            date: new Date(year, month - 1, prevMonthLastDay - i),
            isCurrentMonth: false
        })
    }

    for (let i = 1; i <= lastDayOfMonth.getDate(); i++) {
        days.push({
            date: new Date(year, month, i),
            isCurrentMonth: true
        })
    }

    const remainingDays = 42 - days.length
    for (let i = 1; i <= remainingDays; i++) {
        days.push({
            date: new Date(year, month + 1, i),
            isCurrentMonth: false
        })
    }

    return days
})

// --- ALGORITHME D'ALIGNEMENT HORIZONTAL DES ÉVÉNEMENTS (TRACKS) ---
const computedGridEvents = computed(() => {
    const days = calendarDays.value
    if (!days.length) return Array(42).fill().map(() => [])
    
    const grid = Array(42).fill().map(() => [])

    // Analyse ligne par ligne (semaine par semaine = 6 semaines de 7 jours)
    for (let w = 0; w < 6; w++) {
        const weekStartIndex = w * 7
        const weekDaysList = days.slice(weekStartIndex, weekStartIndex + 7)
        
        const startOfWeek = weekDaysList[0].date
        const endOfWeek = weekDaysList[6].date

        // Filtrer les événements actifs durant cette semaine spécifique
        const activeEvents = events.value.filter(event => {
            const startCheck = new Date(new Date(event.start).setHours(0,0,0,0))
            const finishCheck = new Date(new Date(event.finish).setHours(23,59,59,999))
            const wStart = new Date(startOfWeek.setHours(0,0,0,0))
            const wEnd = new Date(endOfWeek.setHours(23,59,59,999))
            return finishCheck >= wStart && startCheck <= wEnd
        })

        // Tri : Plus hâtif d'abord, puis plus long d'abord
        activeEvents.sort((a, b) => {
            const startA = new Date(a.start).getTime()
            const startB = new Date(b.start).getTime()
            if (startA !== startB) return startA - startB
            return new Date(b.finish).getTime() - new Date(a.finish).getTime()
        })

        // Registre d'occupation des pistes verticales pour la semaine en cours
        const tracks = [] 

        activeEvents.forEach(event => {
            const normStart = new Date(new Date(event.start).setHours(0,0,0,0))
            const normFinish = new Date(new Date(event.finish).setHours(23,59,59,999))
            
            let startCol = -1
            let endCol = -1

            // Détecter les intersections de colonnes (0 à 6) dans cette semaine
            for (let d = 0; d < 7; d++) {
                const normDay = new Date(new Date(weekDaysList[d].date).setHours(12,0,0,0))
                if (normDay >= normStart && normDay <= normFinish) {
                    if (startCol === -1) startCol = d
                    endCol = d
                }
            }

            if (startCol === -1) return

            // Trouver la première piste verticale libre de startCol à endCol
            let targetTrack = -1
            for (let t = 0; t < tracks.length; t++) {
                let isOpen = true
                for (let c = startCol; c <= endCol; c++) {
                    if (!tracks[t][c]) { isOpen = false; break }
                }
                if (isOpen) { targetTrack = t; break }
            }

            // Si aucune piste n'est libre, on en crée une nouvelle
            if (targetTrack === -1) {
                tracks.push(Array(7).fill(true))
                targetTrack = tracks.length - 1
            }

            // Réserver la piste et l'injecter dans la structure finale
            for (let c = startCol; c <= endCol; c++) {
                tracks[targetTrack][c] = false
                const gridIndex = weekStartIndex + c
                
                while (grid[gridIndex].length <= targetTrack) {
                    grid[gridIndex].push(null)
                }
                grid[gridIndex][targetTrack] = event
            }
        })
    }
    return grid
})

// --- RÉCUPÉRATION DES DONNÉES (CTFTIME API VIA PROXY/VITE) ---
const fetchEvents = async () => {
    try {
        loading.value = true
        error.value = null

        const startStamp = Math.floor(new Date(currentYear.value, currentMonth.value - 1, 1).getTime() / 1000)
        const finishStamp = Math.floor(new Date(currentYear.value, currentMonth.value + 2, 0).getTime() / 1000)

        // Tente d'appeler via le proxy local de dev Vite (/api-ctftime), sinon bascule sur Allorigins
        let response;
        try {
            response = await axios.get(`/api-ctftime/api/v1/events/?limit=100&start=${startStamp}&finish=${finishStamp}`)
        } catch {
            const targetUrl = encodeURIComponent(`https://ctftime.org/api/v1/events/?limit=100&start=${startStamp}&finish=${finishStamp}`)
            response = await axios.get(`https://api.allorigins.win/raw?url=${targetUrl}`)
        }
        
        events.value = response.data || []

    } catch (err) {
        console.error("Erreur API CTFtime:", err)
        error.value = "Impossible de récupérer les données vivantes depuis CTFtime. Affichage du mode démo."

        // Mode Secours/Démo persistant
        events.value = [
            {
                id: 1, title: 'GuardiHack 2026', format: 'Jeopardy',
                start: new Date(currentYear.value, currentMonth.value, 12, 9, 0).toISOString(),
                finish: new Date(currentYear.value, currentMonth.value, 15, 18, 0).toISOString(),
                duration: { days: 3, hours: 0 }, url: 'https://guardiaschool.fr',
                ctftime_url: 'https://ctftime.org', description: 'Le grand CTF annuel inter-campus de Guardia Cybersecurity School ! Venez affronter les meilleures équipes sur des épreuves de Web, Reverse, Crypto et Pwn.'
            },
            {
                id: 2, title: 'Mini-CTF Interne', format: 'Attack-Defense',
                start: new Date(currentYear.value, currentMonth.value, 14, 14, 0).toISOString(),
                finish: new Date(currentYear.value, currentMonth.value, 14, 22, 0).toISOString(),
                duration: { days: 0, hours: 8 }, url: '', ctftime_url: '',
                description: 'Entraînement de mi-semaine axé sur les architectures systèmes durcies.'
            }
        ]
    } finally {
        loading.value = false
    }
}

// --- OUTILS DE VÉRIFICATION DE LIENS INTER-JOURS ---
const checkLeft = (index, trackIndex, eventId) => {
    if (index % 7 === 0) return false // Début de ligne (Lundi), on casse le bloc visuel
    return computedGridEvents.value[index - 1]?.[trackIndex]?.id === eventId
}

const checkRight = (index, trackIndex, eventId) => {
    if (index % 7 === 6) return false // Fin de ligne (Dimanche), on casse le bloc visuel
    return computedGridEvents.value[index + 1]?.[trackIndex]?.id === eventId
}

const getDisplayCount = (index) => {
    if (!computedGridEvents.value[index]) return 0
    return computedGridEvents.value[index].filter(e => e !== null).length
}

const isSameDay = (d1, d2) => {
    return d1.getFullYear() === d2.getFullYear() &&
        d1.getMonth() === d2.getMonth() &&
        d1.getDate() === d2.getDate()
}

const isToday = (date) => {
    return isSameDay(date, new Date())
}

// Prochains événements (Panneau latéral)
const upcomingEvents = computed(() => {
    const today = new Date()
    today.setHours(0, 0, 0, 0)

    return events.value
        .filter(event => new Date(event.finish) >= today)
        .sort((a, b) => new Date(a.start) - new Date(b.start))
})

// --- ACTIONS CALENDRIER ---
const changeMonth = (offset) => {
    currentDate.value = new Date(currentYear.value, currentMonth.value + offset, 1)
}

const goToToday = () => {
    currentDate.value = new Date()
}

// --- UTILITAIRES DE FORMATAGE ---
const formatDateShort = (dateString) => {
    const d = new Date(dateString)
    return d.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' })
}

const formatDateFull = (dateString) => {
    const d = new Date(dateString)
    return d.toLocaleDateString('fr-FR', { 
        day: '2-digit', month: 'long', year: 'numeric', 
        hour: '2-digit', minute: '2-digit' 
    }) + ' UTC'
}

const formatDuration = (durationObj) => {
    if (!durationObj) return 'N/A'
    if (durationObj.days > 0) return `${durationObj.days} jours`
    return `${durationObj.hours} heures`
}

// --- LIFECYCLE ---
onMounted(() => {
    fetchEvents()
})

watch(currentMonth, () => {
    fetchEvents()
})
</script>

<style scoped>
.animate-fade-in {
    animation: fadeIn 0.4s ease-out forwards;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.font-cyber {
    font-family: 'Orbitron', 'Press Start 2P', sans-serif;
}

.no-scrollbar::-webkit-scrollbar {
    display: none;
}

.no-scrollbar {
    -ms-overflow-style: none;
    scrollbar-width: none;
}
</style>