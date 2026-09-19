<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

const viewMode = ref('global')
const chartRef = ref(null)
let chartInstance = null
const chartOptions = computed(() => {
  const startTime = new Date('2026-04-21T09:00:00').getTime()
  return {
    title: {
      text: 'ÉVOLUTION DU TOP 10',
      left: 'center',
      top: 10,
      textStyle: { color: '#a6adbb', fontSize: 16, fontFamily: 'Orbitron', fontWeight: 'bold' }
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(20, 20, 20, 0.9)',
      borderColor: '#333',
      textStyle: { color: '#fff' },
      formatter: function (params) {
        if (!params.length) return '';
        let date = new Date(params[0].value[0]).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
        let tooltipStr = `<div style="font-weight:bold;margin-bottom:5px;border-bottom:1px solid #444;pb-1">${date}</div>`;
        params.forEach(p => {
          tooltipStr += `<div style="display:flex;justify-content:space-between;gap:15px;font-size:12px;">
            <span><span style="display:inline-block;width:8px;height:8px;background-color:${p.color};border-radius:50%;margin-right:5px;"></span>${p.seriesName}</span>
            <span style="font-weight:bold;">${p.value[1]} pts</span>
          </div>`;
        });
        return tooltipStr;
      }
    },
    legend: { type: 'scroll', bottom: 0, textStyle: { color: '#888' }, data: top10Users.value.map(u => u.username) },
    grid: { left: '4%', right: '4%', bottom: '15%', top: '15%', containLabel: true },
    xAxis: {
      type: 'time',
      axisLabel: { color: '#888', formatter: '{HH}:{mm}' },
      splitLine: { show: false }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#888' },
      splitLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.05)' } }
    },
    series: top10Users.value.map(user => {
      const submission1 = startTime + Math.random() * 3600000;
      const submission2 = submission1 + Math.random() * 7200000;
      const submission3 = submission2 + Math.random() * 7200000;
      return {
        name: user.username,
        type: 'line',
        step: 'end',
        data: [
          [startTime, 0], 
          [submission1, Math.floor(user.score * 0.3)], 
          [submission2, Math.floor(user.score * 0.7)], 
          [submission3, user.score]
        ],
        itemStyle: { color: user.color || '#4b5563' },
        lineStyle: { width: 2 },
        symbol: 'circle'
      }
    })
  }
})
const initChart = () => {
  if (chartRef.value) {
    if (!chartInstance) chartInstance = echarts.init(chartRef.value)
    chartInstance.setOption(chartOptions.value)
  }
}
const resizeChart = () => { if (chartInstance) chartInstance.resize() }

onMounted(() => {
  initChart()
  window.addEventListener('resize', resizeChart)
})
onUnmounted(() => {
  window.removeEventListener('resize', resizeChart)
  if (chartInstance) chartInstance.dispose()
})
watch(viewMode, async (newVal) => {
  if (newVal === 'global') {
    await nextTick()
    initChart()
  }
})
</script>

<template>
  <div class="w-full animate-fade-in pb-20 px-4">
    <div class="mb-10">
      <h1 class="block w-full text-center text-3xl font-cyber font-bold bg-primary text-base-100 py-3 uppercase tracking-widest shadow-lg">
        Scoreboard
      </h1>
    </div>
    <div class="flex justify-center mb-12 w-full">
      <div class="tabs tabs-boxed bg-base-300 p-1">
        <button 
          @click="viewMode = 'global'" 
          :class="['tab tab-lg px-10 font-cyber transition-all', viewMode === 'global' ? 'tab-active bg-primary text-base-100' : '']"
        >
          Joueurs
        </button>
        <button 
          @click="viewMode = 'teams'" 
          :class="['tab tab-lg px-10 font-cyber transition-all', viewMode === 'teams' ? 'tab-active bg-primary text-base-100' : '']"
        >
          Équipes
        </button>
      </div>
    </div>
    <div v-if="viewMode === 'global'" class="w-full animate-fade-in flex flex-col items-center max-w-7xl mx-auto">
      <div class="w-full bg-base-200/50 pt-4 pb-2 px-2 rounded-xl border border-base-300 mb-16 shadow-2xl">
        <div ref="chartRef" class="w-full h-[450px]"></div>
      </div>
      <div class="flex justify-center items-end gap-4 md:gap-10 w-full mb-20 pt-4">
        
        <div class="flex flex-col items-center gap-2">
          <div class="card-neumorph second flex flex-col items-center justify-center p-4 text-center relative overflow-hidden"
              :style="{ backgroundImage: `linear-gradient(rgba(30,30,30,0.85), rgba(30,30,30,0.95)), url(${top10Users[1].avatar})`, backgroundSize: 'cover' }">
            <div class="text-3xl mb-1">🥈</div>
            <div class="font-bold text-sm truncate w-full px-1 text-white">{{ top10Users[1].username }}</div>
            <div class="text-gray-400 font-mono text-xs">{{ top10Users[1].score }} pts</div>
          </div>
          <div class="text-xs font-cyber opacity-60">RANK #2</div>
        </div>
        <div class="flex flex-col items-center gap-2 z-10">
          <div class="card-neumorph first flex flex-col items-center justify-center p-4 text-center relative overflow-hidden"
              :style="{ backgroundImage: `linear-gradient(rgba(20,20,20,0.8), rgba(20,20,20,0.9)), url(${top10Users[0].avatar})`, backgroundSize: 'cover' }">
            <div class="text-6xl mb-2 animate-pulse">👑</div>
            <div class="font-black text-lg truncate w-full px-1 text-white">{{ top10Users[0].username }}</div>
            <div class="text-yellow-400 font-mono text-lg font-bold">{{ top10Users[0].score }} pts</div>
          </div>
          <div class="text-sm font-cyber text-yellow-400 font-bold">CHAMPION #1</div>
        </div>
        <div class="flex flex-col items-center gap-2">
          <div class="card-neumorph third flex flex-col items-center justify-center p-4 text-center relative overflow-hidden"
              :style="{ backgroundImage: `linear-gradient(rgba(30,30,30,0.85), rgba(30,30,30,0.95)), url(${top10Users[2].avatar})`, backgroundSize: 'cover' }">
            <div class="text-3xl mb-1">🥉</div>
            <div class="font-bold text-sm truncate w-full px-1 text-white">{{ top10Users[2].username }}</div>
            <div class="text-orange-400 font-mono text-xs">{{ top10Users[2].score }} pts</div>
          </div>
          <div class="text-xs font-cyber opacity-60">RANK #3</div>
        </div>
      </div>
      <div class="w-full bg-base-200/30 rounded-2xl border border-white/5 overflow-hidden shadow-xl">
        <table class="table w-full">
          <thead>
            <tr class="bg-base-300/50 text-base-content/70">
              <th class="py-4 pl-8">Rank</th>
              <th>Utilisateur</th>
              <th>Score</th>
              <th class="pr-8">Niveau</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(user, index) in top10Users.slice(3)" :key="user.id" class="hover:bg-primary/5 transition-colors border-b border-white/5">
              <td class="font-mono font-bold opacity-40 text-xl pl-8">#{{ index + 4 }}</td>
              <td class="py-4">
                <div class="flex items-center gap-4">
                  <img :src="user.avatar" class="w-10 h-10 rounded-xl bg-base-300 border border-white/10 shadow-sm" />
                  <span class="font-bold text-lg">{{ user.username }}</span>
                </div>
              </td>
              <td class="font-mono font-bold text-primary">{{ user.score }} <span class="text-[10px] opacity-50 uppercase ml-1">pts</span></td>
              <td class="pr-8">
                <div class="badge badge-primary badge-outline font-mono">{{ user.lvl }}</div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 w-full animate-fade-in px-4 max-w-7xl mx-auto">
      <div v-for="(team, index) in teams" :key="team.id" 
        class="card bg-base-200/50 border border-base-300 hover:border-primary/50 transition-all hover:shadow-2xl overflow-hidden group">
        <figure class="relative h-32 overflow-hidden bg-black">
          <img :src="team.image" :alt="team.name" class="w-full h-full object-cover opacity-30 group-hover:opacity-50 transition-all group-hover:scale-110" />
          <div class="absolute inset-0 flex items-center justify-center">
            <span class="text-4xl filter drop-shadow-lg">{{ index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : '#' + (index + 1) }}</span>
          </div>
        </figure>
        <div class="card-body p-6">
          <h2 :class="['card-title text-xl font-cyber uppercase tracking-wider', team.color]">{{ team.name }}</h2>
          <div class="space-y-3 my-4">
            <div class="flex justify-between items-center p-3 bg-base-100 rounded-lg border border-white/5">
              <span class="text-xs opacity-50 uppercase font-bold">Total Points</span>
              <span class="font-mono text-xl text-primary">{{ team.score }}</span>
            </div>
            <div class="flex justify-between items-center p-3 bg-base-100 rounded-lg border border-white/5">
              <span class="text-xs opacity-50 uppercase font-bold">Effectif</span>
              <span class="font-bold">{{ team.members }} / 5</span>
            </div>
          </div>
          <button class="btn btn-primary btn-outline btn-sm w-full font-cyber tracking-widest mt-2 group-hover:bg-primary group-hover:text-white">
            Détails Team
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
<style scoped>
.font-cyber { font-family: 'Orbitron', sans-serif; }
.animate-fade-in { animation: fadeIn 0.4s ease-out forwards; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.card-neumorph {
  width: 160px;
  height: 210px;
  border-radius: 24px;
  background-color: #1a1a1a;
  box-shadow: 15px 15px 30px rgba(0, 0, 0, 0.4), -5px -5px 15px rgba(255, 255, 255, 0.02);
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  border: 1px solid rgba(255,255,255,0.05);
}
.card-neumorph.first {
  width: 200px;
  height: 280px;
  border: 2px solid #ffd700;
  box-shadow: 0px 0px 40px rgba(255, 215, 0, 0.1);
}
.card-neumorph:hover {
  transform: translateY(-10px) scale(1.02);
}
.second { border-bottom: 6px solid #c0c0c0; }
.third { border-bottom: 6px solid #cd7f32; }
@media (max-width: 768px) {
  .card-neumorph { width: 110px; height: 160px; }
  .card-neumorph.first { width: 130px; height: 200px; }
}
</style>