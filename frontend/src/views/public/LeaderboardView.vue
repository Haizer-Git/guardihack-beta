<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import axios from 'axios'
import PageTitle from '../../components/PageTitle.vue'
import * as echarts from 'echarts'
import { getAssetUrl } from '../../utils/assets.js'

import Top1Img from '../../assets/top1.png';
import Top2Img from '../../assets/top2.png';
import Top3Img from '../../assets/top3.png';


// --- ÉTAT ---
const viewMode = ref('global')

// Données dynamiques issues de l'API
const top10Users = ref([])          // Les 10 premiers (pour le graph)
const top3Users = ref([])           // Le podium fixe
const tableUsers = ref([])          // Joueurs dans le tableau
const initialTableUsers = ref([])   // Cache page 1
const totalUsers = ref(0)           // Total joueurs

// Configuration de la Pagination
const currentPage = ref(1)
const itemsPerPage = 15
const totalPages = computed(() => Math.ceil(totalUsers.value / itemsPerPage))

// Palette de couleurs CTFd / Plotly
const chartColors = [
    '#2ecc71', // Vert Vexx
    '#f1c40f', // Jaune Antoine
    '#d35400', // Orange Alexandre
    '#9b59b6', // Violet Amelie
    '#3498db', // Bleu
    '#e74c3c', // Rouge
    '#1abc9c', // Turquoise
    '#e67e22', // Orange foncé
    '#34495e', // Gris foncé
    '#8e44ad'  // Pourpre
]

// Variable d'instance ECharts non réactive pour éviter les conflits avec Vue Proxy
let chartInstance = null
const chartRef = ref(null)
const isChartLoading = ref(false)

// --- CHARGEMENT INITIAL DU LEADERBOARD ---
const loadLeaderboardData = async () => {
    try {
        const res = await axios.get('/api/user/score/leaderboard/0')
        if (res.data?.status === 'success' && res.data.leaderboard) {
            const data = res.data.leaderboard || []
            totalUsers.value = res.data.total_users || data.length

            top10Users.value = data.slice(0, 10).map((user, index) => ({
                ...user,
                avatar_url: user.avatar || user.avatar_url || null,
                color: chartColors[index] || '#4b5563'
            }))

            top3Users.value = top10Users.value.slice(0, 3)

            initialTableUsers.value = data.slice(3, 15).map(user => {
                const matchedTop10 = top10Users.value.find(u => u.username === user.username)
                return {
                    ...user,
                    avatar_url: user.avatar || user.avatar_url || null,
                    color: matchedTop10 ? matchedTop10.color : '#4b5563'
                }
            })

            tableUsers.value = initialTableUsers.value
            currentPage.value = 1

            await nextTick()
            await loadChartHistory()
        }
    } catch (error) {
        console.error('Erreur lors du chargement du leaderboard :', error)
    }
}

// --- PAGINATION TABLEAU ---
const fetchTableRanks = async (page) => {
    try {
        if (page === 1) {
            tableUsers.value = initialTableUsers.value
            currentPage.value = 1
            return
        }

        const offset = (page - 1) * itemsPerPage
        const res = await axios.get(`/api/user/score/leaderboard/${offset}`)
        
        if (res.data?.status === 'success' && res.data.leaderboard) {
            const leaderboardData = res.data.leaderboard || []

            tableUsers.value = leaderboardData.map(user => {
                const matchedTop10 = top10Users.value.find(u => u.username === user.username)
                return {
                    ...user,
                    avatar_url: user.avatar || user.avatar_url || null,
                    color: matchedTop10 ? matchedTop10.color : '#4b5563'
                }
            })

            currentPage.value = page
        }
    } catch (error) {
        console.error(`Erreur lors du chargement de la page ${page} :`, error)
    }
}

// ===================================================
// --- LOGIQUE DU GRAPHIQUE (CORRIGÉE & SÉCURISÉE) ---
// ===================================================

// Parsing ultra-robuste des dates pour éviter tout NaN
const parseTimestamp = (val) => {
    if (!val) return new Date()
    if (typeof val === 'number') return new Date(val)
    
    let str = String(val).trim()
    
    // Format SQL "YYYY-MM-DD HH:mm:ss" -> ISO "YYYY-MM-DDTHH:mm:ss"
    if (/^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}/.test(str)) {
        str = str.replace(' ', 'T')
    }
    
    // Format "DD/MM/YYYY HH:mm:ss"
    if (str.includes('/') && str.includes(':')) {
        const parts = str.split(' ')
        if (parts.length === 2) {
            const [d, m, y] = parts[0].split('/')
            const [h, min, s] = parts[1].split(':')
            const dateObj = new Date(y, parseInt(m) - 1, d, h || 0, min || 0, s || 0)
            if (!isNaN(dateObj.getTime())) return dateObj
        }
    }

    const d = new Date(str)
    return isNaN(d.getTime()) ? new Date() : d
}

const loadChartHistory = async () => {
    await nextTick()
    if (top10Users.value.length === 0 || !chartRef.value) return

    isChartLoading.value = true

    try {
        if (!chartInstance) {
            chartInstance = echarts.init(chartRef.value)
        }

        const historyPromises = top10Users.value.map(user =>
            axios.get(`/api/user/${user.username}/score/history?filter_type=YEAR`)
                .then(res => ({
                    username: user.username,
                    history: res.data?.status === 'success' ? res.data.history : []
                }))
                .catch(() => ({ username: user.username, history: [] }))
        )

        const allHistories = await Promise.all(historyPromises)
        const now = Date.now()

        // Trouver la date de début la plus ancienne
        let globalMinTime = Infinity
        allHistories.forEach(h => {
            h.history.forEach(item => {
                const t = parseTimestamp(item.timestamp).getTime()
                if (!isNaN(t) && t < globalMinTime) globalMinTime = t
            })
        })

        if (globalMinTime === Infinity || isNaN(globalMinTime)) {
            globalMinTime = now - (24 * 3600 * 1000) // 24h en arrière par défaut
        } else {
            globalMinTime = globalMinTime - (2 * 3600 * 1000) // 2h avant le 1er flag
        }

        const echartSeries = top10Users.value.map((user) => {
            const userObj = allHistories.find(h => h.username === user.username)
            const userHistory = userObj ? userObj.history : []

            let rawPoints = userHistory.map(h => {
                const t = parseTimestamp(h.timestamp).getTime()
                return {
                    time: isNaN(t) ? now : t,
                    score: Number(h.score_total || h.score || 0),
                    challenge: h.challenge_title || h.challenge_name || h.title || '',
                    gained: Number(h.score || h.points || 0)
                }
            }).filter(pt => !isNaN(pt.time))

            rawPoints.sort((a, b) => a.time - b.time)

            const dataPoints = []

            // Toujours démarrer la ligne au temps initial à 0 pt
            dataPoints.push([globalMinTime, 0, 'Début', 0])

            if (rawPoints.length > 0) {
                rawPoints.forEach(pt => {
                    dataPoints.push([pt.time, pt.score, pt.challenge, pt.gained])
                })
                // Prolonger la ligne jusqu'à maintenant avec le dernier score connu
                const lastScore = rawPoints[rawPoints.length - 1].score
                dataPoints.push([now, lastScore, '', 0])
            } else {
                // Aucun challenge résolu : ligne plate à 0 pt jusqu'à maintenant
                dataPoints.push([now, 0, '', 0])
            }

            return {
                name: user.username,
                type: 'line',
                symbol: 'circle',
                symbolSize: 6,
                showSymbol: true,
                itemStyle: { color: user.color },
                lineStyle: { width: 2 },
                emphasis: { focus: 'series', lineStyle: { width: 3.5 } },
                data: dataPoints
            }
        })

        renderChart(echartSeries)
    } catch (err) {
        console.error('Erreur lors du tracé du graphique :', err)
    } finally {
        isChartLoading.value = false
    }
}

const renderChart = (seriesData) => {
    const isDark = document.documentElement.getAttribute('data-theme') !== 'light'
    const textColor = isDark ? '#d1d5db' : '#374151'
    const gridLineColor = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'

    const option = {
        backgroundColor: 'transparent',
        title: {
            text: 'Top 10',
            left: 'center',
            top: 10,
            textStyle: {
                color: textColor,
                fontSize: 18,
                fontWeight: 'normal',
                fontFamily: 'sans-serif'
            }
        },
        tooltip: {
            trigger: 'axis',
            backgroundColor: isDark ? 'rgba(17, 24, 39, 0.95)' : 'rgba(255, 255, 255, 0.95)',
            borderColor: isDark ? '#374151' : '#e5e7eb',
            borderWidth: 1,
            padding: [10, 14],
            textStyle: { color: textColor, fontFamily: 'monospace', fontSize: 12 },
            formatter: (params) => {
                if (!params || params.length === 0) return ''
                const dateVal = new Date(params[0].value[0])
                const dateStr = dateVal.toLocaleString('fr-FR', {
                    day: '2-digit', month: 'short', year: 'numeric',
                    hour: '2-digit', minute: '2-digit'
                })

                let res = `<div style="font-weight:bold;margin-bottom:6px;border-bottom:1px solid rgba(150,150,150,0.2);padding-bottom:4px;">${dateStr}</div>`
                const sortedParams = [...params].sort((a, b) => (b.value[1] || 0) - (a.value[1] || 0))

                sortedParams.forEach(item => {
                    const score = item.value[1] ?? 0
                    const challenge = item.value[2]
                    const gained = item.value[3]

                    res += `<div style="display:flex;align-items:center;justify-content:space-between;gap:16px;margin:2px 0;">
                        <span style="display:flex;align-items:center;gap:6px;">
                            <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background-color:${item.color};"></span>
                            <strong>${item.seriesName}</strong>
                        </span>
                        <span style="font-family:monospace;font-weight:bold;">${score} pts</span>
                    </div>`

                    if (challenge && challenge !== 'Début') {
                        res += `<div style="font-size:10px;opacity:0.75;padding-left:14px;margin-bottom:2px;">🚩 ${challenge} (+${gained} pts)</div>`
                    }
                })
                return res
            }
        },
        legend: {
            bottom: 10,
            left: 'center',
            icon: 'circle',
            itemWidth: 8,
            itemHeight: 8,
            data: top10Users.value.map(u => u.username),
            textStyle: { color: textColor, fontFamily: 'sans-serif', fontSize: 12 },
            inactiveColor: isDark ? 'rgba(255, 255, 255, 0.2)' : 'rgba(0, 0, 0, 0.2)'
        },
        grid: {
            top: 55,
            left: '4%',
            right: '4%',
            bottom: 75,
            containLabel: true
        },
        xAxis: {
            type: 'time',
            splitLine: { show: false },
            axisLine: { show: true, lineStyle: { color: textColor, width: 1 } },
            axisTick: { show: true, lineStyle: { color: textColor } },
            axisLabel: {
                show: true,
                color: textColor,
                fontFamily: 'sans-serif',
                fontSize: 11,
                formatter: (value) => {
                    const d = new Date(value)
                    const hours = String(d.getHours()).padStart(2, '0') + ':00'
                    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                    const dateStr = `${months[d.getMonth()]} ${d.getDate()}, ${d.getFullYear()}`
                    return `${hours}\n${dateStr}`
                }
            }
        },
        yAxis: {
            type: 'value',
            min: 0,
            splitLine: { show: true, lineStyle: { color: gridLineColor, type: 'dashed' } },
            axisLine: { show: false },
            axisTick: { show: false },
            axisLabel: { show: true, color: textColor, fontFamily: 'sans-serif', fontSize: 11 }
        },
        series: seriesData
    }

    chartInstance.setOption(option, true)
}

const handleResize = () => {
    if (chartInstance) chartInstance.resize()
}

// ===================================================
// --- TOP 1 PIXEL-CANVAS HOVER EFFECT ---
// ===================================================
const top1Canvas = ref(null)
let top1Cleanup = null

const setupTop1PixelEffect = async () => {
    await nextTick()

    if (top1Cleanup) top1Cleanup()

    const canvas = top1Canvas.value
    if (!canvas) return

    const card = canvas.parentElement
    const ctx = canvas.getContext('2d')
    if (!card || !ctx) return

    const gap = 6
    const colors = ['#ffd700', '#fef08a', '#eab308']
    let pixels = []
    let animationId = null
    let resizeObserver = null
    let hovered = false
    let width = 1
    let height = 1

    class Pixel {
        constructor(x, y, color, delay) {
            this.x = x
            this.y = y
            this.color = color
            this.size = 0
            this.minSize = 0.5
            this.maxSize = Math.random() * 1.5 + 0.5
            this.sizeStep = Math.random() * 0.4 + 0.15
            this.delay = delay
            this.counter = 0
            this.counterStep = Math.random() * 4 + (width + height) * 0.01
            this.speed = (Math.random() * 0.5 + 0.1) * 0.2
            this.shimmer = false
            this.reverse = false
            this.idle = false
        }

        draw() {
            if (this.size <= 0) return
            const offset = 1 - this.size * 0.5
            ctx.fillStyle = this.color
            ctx.fillRect(this.x + offset, this.y + offset, this.size, this.size)
        }

        appear() {
            this.idle = false

            if (this.counter < this.delay) {
                this.counter += this.counterStep
                return
            }

            if (this.size >= this.maxSize) this.shimmer = true

            if (this.shimmer) {
                if (this.size >= this.maxSize) this.reverse = true
                if (this.size <= this.minSize) this.reverse = false
                this.size += this.reverse ? -this.speed : this.speed
            } else {
                this.size += this.sizeStep
            }

            this.draw()
        }

        disappear() {
            this.shimmer = false
            this.counter = 0
            this.size -= 0.16

            if (this.size <= 0) {
                this.size = 0
                this.idle = true
                return
            }

            this.draw()
        }
    }

    const resize = () => {
        const rect = card.getBoundingClientRect()
        width = Math.max(1, Math.floor(rect.width))
        height = Math.max(1, Math.floor(rect.height))

        const dpr = Math.min(window.devicePixelRatio || 1, 2)
        canvas.width = Math.floor(width * dpr)
        canvas.height = Math.floor(height * dpr)
        canvas.style.width = `${width}px`
        canvas.style.height = `${height}px`

        ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
        pixels = []

        for (let x = 0; x < width; x += gap) {
            for (let y = 0; y < height; y += gap) {
                const dx = x - width / 2
                const dy = y - height / 2
                const delay = Math.sqrt(dx * dx + dy * dy) * 0.45
                const color = colors[Math.floor(Math.random() * colors.length)]
                pixels.push(new Pixel(x, y, color, delay))
            }
        }

        ctx.clearRect(0, 0, width, height)
    }

    const animate = (mode) => {
        if (animationId) cancelAnimationFrame(animationId)

        const frame = () => {
            ctx.clearRect(0, 0, width, height)

            for (const pixel of pixels) {
                pixel[mode]()
            }

            const finished = mode === 'disappear'
                ? pixels.every(pixel => pixel.idle)
                : false

            if (!finished && (mode === 'appear' ? hovered : !hovered)) {
                animationId = requestAnimationFrame(frame)
            } else {
                animationId = null
                if (!hovered) ctx.clearRect(0, 0, width, height)
            }
        }

        animationId = requestAnimationFrame(frame)
    }

    const enter = () => {
        hovered = true
        canvas.style.opacity = '1'
        animate('appear')
    }

    const leave = () => {
        hovered = false
        animate('disappear')

        setTimeout(() => {
            if (!hovered) canvas.style.opacity = '0'
        }, 500)
    }

    resize()

    resizeObserver = new ResizeObserver(resize)
    resizeObserver.observe(card)

    card.addEventListener('mouseenter', enter)
    card.addEventListener('mouseleave', leave)

    top1Cleanup = () => {
        if (animationId) cancelAnimationFrame(animationId)
        resizeObserver?.disconnect()
        card.removeEventListener('mouseenter', enter)
        card.removeEventListener('mouseleave', leave)
        ctx.clearRect(0, 0, width, height)
        canvas.style.opacity = '0'
        top1Cleanup = null
    }
}

// Le canvas est initialisé après le rendu du podium.
watch(
    () => top3Users.value[0],
    async (user) => {
        if (!user) return
        await setupTop1PixelEffect()
    },
    { flush: 'post' }
)

// --- LIFECYCLE CONTROLS ---
onMounted(async () => {
    await loadLeaderboardData()
    window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
    window.removeEventListener('resize', handleResize)
    if (top1Cleanup) top1Cleanup()
    if (chartInstance) {
        chartInstance.dispose()
        chartInstance = null
    }
})

watch(viewMode, async (newVal) => {
    if (newVal === 'global') {
        await nextTick()
        if (top10Users.value.length > 0) {
            await loadChartHistory()
        }
    }
})
</script>

<template>
    <div class="w-full animate-fade-in pb-20 px-4">

        <PageTitle text="Scoreboard" />

        <div v-if="viewMode === 'global'" class="w-full animate-fade-in flex flex-col items-center max-w-7xl mx-auto">

            <!-- GRAPHIQUE PERFORMANCE TOP 10 -->
            <div class="w-full mb-12">
                <div class="bg-base-300 border border-base-200 p-4 rounded-sm w-full relative">
                    <div v-if="isChartLoading"
                        class="absolute inset-0 z-10 flex items-center justify-center bg-base-100 bg-opacity-80">
                        <span class="loading loading-spinner text-primary loading-lg"></span>
                    </div>

                    <div ref="chartRef" class="w-full h-[450px]"></div>
                </div>
            </div>

            <!-- PODIUM -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 w-full mb-12" v-if="top3Users.length > 0">
                
                <!-- RANK #2 -->
                <div v-if="top3Users[1]"
                    class="bg-base-300 border border-base-300 rounded-sm p-6 flex flex-col items-center justify-center text-center shadow-lg relative overflow-hidden group hover:border-[#c0c0c0]/50 transition-colors"
                    :style="{ backgroundImage: `url(${Top2Img})`, backgroundSize: 'cover', backgroundPosition: 'center', backgroundColor: 'rgba(0,0,0,0.95)', backgroundBlendMode: 'multiply' }">
                    <div class="absolute top-0 left-0 w-full h-1 bg-[#c0c0c0]"></div>
                    <router-link :to="`/profile/${top3Users[1].username}`" class="w-16 h-16 rounded-sm bg-[#c0c0c0]/10 flex items-center justify-center font-bold text-2xl uppercase mb-4 border border-[#c0c0c0]/30 shadow-inner overflow-hidden hover:scale-105 transition-transform"
                        style="color: #c0c0c0">
                        <img v-if="top3Users[1].avatar_url" :src="getAssetUrl(top3Users[1].avatar_url)"
                            class="w-full h-full object-cover" />
                        <span v-else>{{ top3Users[1].username.charAt(0) }}</span>
                    </router-link>
                    <div class="text-[#c0c0c0] font-cyber text-xs opacity-80 mb-1">#2</div>
                    <h3 class="text-xl font-bold font-titre text-white mb-2">
                        <router-link :to="`/profile/${top3Users[1].username}`" class="hover:text-primary transition-colors">
                            {{ top3Users[1].username }}
                        </router-link>
                    </h3>
                    <div class="text-[#c0c0c0] font-mono font-bold text-lg">{{ top3Users[1].global_score }} <span
                            class="text-xs opacity-50 uppercase">pts</span></div>
                </div>

                <!-- RANK #1 (CHAMPION) -->
                <div v-if="top3Users[0]" class="group bg-base-300 border border-[#ffd700] rounded-sm p-6 flex flex-col items-center justify-center text-center shadow-[0_0_20px_rgba(255,215,0,0.1)] transition-all duration-300 hover:shadow-[0_0_35px_rgba(255,215,0,0.25)] relative overflow-hidden transform md:-translate-y-4"
                    :style="{ backgroundImage: `url(${Top1Img})`, backgroundSize: 'cover', backgroundPosition: 'center', backgroundColor: 'rgba(0,0,0,0.50)', backgroundBlendMode: 'multiply' }"
                >

                <div class="absolute inset-0 bg-black opacity-0 group-hover:opacity-100 transition-opacity duration-300 z-0 pointer-events-none"></div>

                <!-- ANIMATION PIXEL -->
                <canvas ref="top1Canvas" class="top1-pixel-bg absolute inset-0 w-full h-full opacity-0 z-10 pointer-events-none"></canvas>

                <!-- LIGNE DORÉE -->
                <div class="absolute top-0 left-0 w-full h-1 bg-[#ffd700] z-30"></div>

                <!-- CONTENU -->
                <div class="relative z-20 flex flex-col items-center">

                    <!-- AVATAR -->
                    <router-link
                        :to="`/profile/${top3Users[0].username}`"
                        class="w-20 h-20 rounded-sm bg-[#ffd700]/10 flex items-center justify-center font-bold text-3xl uppercase mb-4 border border-[#ffd700]/50 shadow-[0_0_15px_rgba(255,215,0,0.2)] overflow-hidden hover:scale-105 transition-transform"
                        style="color: #ffd700"
                    >
                        <img
                            v-if="top3Users[0].avatar_url"
                            :src="getAssetUrl(top3Users[0].avatar_url)"
                            class="w-full h-full object-cover"
                        />

                        <span v-else>
                            {{ top3Users[0].username.charAt(0) }}
                        </span>
                    </router-link>

                    <!-- RANK -->
                    <div class="text-[#ffd700] font-code text-sm mb-1 font-bold">
                        #1
                    </div>

                    <!-- PSEUDO -->
                    <h3 class="text-2xl font-bold font-titre text-[#ffd700] mb-2">
                        <router-link
                            :to="`/profile/${top3Users[0].username}`"
                            class="hover:text-primary transition-colors"
                        >
                            {{ top3Users[0].username }}
                        </router-link>
                    </h3>

                    <!-- SCORE -->
                    <div class="text-[#ffd700] font-mono font-bold text-xl">
                        {{ top3Users[0].global_score }}

                        <span class="text-xs opacity-50 uppercase">
                            pts
                        </span>
                    </div>

                    </div>
                </div>

                <!-- RANK #3 -->
                <div v-if="top3Users[2]"
                    class="bg-base-300 border border-base-300 rounded-sm p-6 flex flex-col items-center justify-center text-center shadow-lg relative overflow-hidden group hover:border-[#cd7f32]/50 transition-colors"
                    :style="{ backgroundImage: `url(${Top3Img})`, backgroundSize: 'cover', backgroundPosition: 'center', backgroundColor: 'rgba(0,0,0,0.95)', backgroundBlendMode: 'multiply' }">
                    <div class="absolute top-0 left-0 w-full h-1 bg-[#cd7f32]"></div>
                    <router-link :to="`/profile/${top3Users[2].username}`" class="w-16 h-16 rounded-sm bg-[#cd7f32]/10 flex items-center justify-center font-bold text-2xl uppercase mb-4 border border-[#cd7f32]/30 shadow-inner overflow-hidden hover:scale-105 transition-transform"
                        style="color: #cd7f32">
                        <img v-if="top3Users[2].avatar_url" :src="getAssetUrl(top3Users[2].avatar_url)"
                            class="w-full h-full object-cover" />
                        <span v-else>{{ top3Users[2].username.charAt(0) }}</span>
                    </router-link>
                    <div class="text-[#cd7f32] font-cyber text-xs opacity-80 mb-1">#3</div>
                    <h3 class="text-xl font-bold font-titre text-white mb-2">
                        <router-link :to="`/profile/${top3Users[2].username}`" class="hover:text-primary transition-colors">
                            {{ top3Users[2].username }}
                        </router-link>
                    </h3>
                    <div class="text-[#cd7f32] font-mono font-bold text-lg">{{ top3Users[2].global_score }} <span
                            class="text-xs opacity-50 uppercase">pts</span></div>
                </div>

            </div>

            <!-- TABLEAU DES JOUEURS -->
            <div class="w-full overflow-x-auto bg-base-300 border border-base-200 rounded-sm shadow-sm mb-6">
                <table class="table w-full">
                    <thead class="bg-base-200/50">
                        <tr>
                            <th class="w-16 text-center font-titre text-base-content/70 uppercase tracking-widest text-xs">Rank</th>
                            <th class="font-titre text-base-content/70 uppercase tracking-widest text-xs">Joueurs</th>
                            <th class="font-titre text-base-content/70 text-right uppercase tracking-widest text-xs">Score</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="user in tableUsers" :key="user.username" class="hover:bg-base-200/30 transition-colors">
                            <td class="text-center font-mono font-bold text-base-content/70">
                                #{{ user.rank }}
                            </td>
                            <td>
                                <div class="flex items-center gap-4">
                                    <router-link :to="`/profile/${user.username}`" class="w-10 h-10 rounded-sm bg-base-300 flex items-center justify-center font-bold text-sm uppercase overflow-hidden border" :style="user.color !== '#4b5563' ? `color: ${user.color}; border-color: ${user.color}40; background-color: ${user.color}10` : 'border-color: var(--fallback-bc,oklch(var(--bc)/0.2))'">
                                        <img v-if="user.avatar_url" :src="getAssetUrl(user.avatar_url)" class="w-full h-full object-cover" />
                                        <span v-else>{{ user.username.charAt(0) }}</span>
                                    </router-link>
                                    <div>
                                        <router-link :to="`/profile/${user.username}`" class="font-bold text-base-content hover:text-primary transition-colors text-sm">
                                            {{ user.username }}
                                        </router-link>
                                        <div v-if="user.affiliation" class="text-[10px] text-base-content/50 uppercase tracking-wider mt-0.5">
                                            {{ user.affiliation }}
                                        </div>
                                    </div>
                                </div>
                            </td>
                            <td class="text-right font-mono font-bold text-primary text-base">
                                {{ user.global_score }} <span class="text-[10px] text-base-content/40 uppercase font-normal ml-1">pts</span>
                            </td>
                        </tr>
                        <tr v-if="tableUsers.length === 0">
                            <td colspan="3" class="text-center py-12 text-base-content/40 font-mono text-sm uppercase tracking-widest">
                                Aucun autre joueur classé.
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- PAGINATION -->
            <div class="join mt-2 flex justify-center w-full shadow-lg" v-if="totalPages > 1">
                <button class="join-item btn btn-outline btn-primary" :disabled="currentPage === 1"
                    @click="fetchTableRanks(currentPage - 1)">
                    «
                </button>
                <button v-for="page in totalPages" :key="page"
                    :class="['join-item btn btn-outline btn-primary font-mono', { 'btn-active text-base-100': page === currentPage }]"
                    @click="fetchTableRanks(page)">
                    {{ page }}
                </button>
                <button class="join-item btn btn-outline btn-primary" :disabled="currentPage === totalPages"
                    @click="fetchTableRanks(currentPage + 1)">
                    »
                </button>
            </div>

        </div>

    </div>
</template>

<style scoped>
.top1-pixel-bg {
    opacity: 0;
    pointer-events: none;
    z-index: 10;
}

.font-cyber {
    font-family: 'Orbitron', sans-serif;
}

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
</style>