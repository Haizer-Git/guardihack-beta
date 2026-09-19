<template>

  <div v-if="loading" class="min-h-screen bg-[#1a1a1a] text-white flex items-center justify-center">
    <p class="text-xl font-text animate-pulse">Chargement des données du profil...</p>
  </div>

  <div v-else-if="error" class="min-h-screen bg-[#1a1a1a] text-white flex items-center justify-center">
    <div class="text-center">
      <p class="text-xl font-text text-red-500 mb-4">{{ error }}</p>
      <button @click="loadProfile" class="px-4 py-2 bg-[#d4a500] text-[#1a1a1a] rounded font-bold hover:opacity-80">
        Réessayer
      </button>
    </div>
  </div>


  <div v-else class="text-white antialiased min-h-screen md:p-8">
    <div id="global-container" class="max-w-7xl mx-auto flex flex-col gap-6">

      <div class="bg-base-300 backdrop-blur-md border-[2px] border-base-200 p-6 flex flex-col lg:flex-row gap-6">
        <div class="flex-1 p-6 flex flex-col items-center justify-between rounded-[5px] relative group min-h-[320px]"
          :style="{
            backgroundImage: profile.banner_url ? `url(${getAssetUrl(profile.banner_url)})` : 'none',
            backgroundColor: profile.banner_url ? 'rgba(0, 0, 0, 0.2)' : '#1d232a',
            backgroundSize: 'cover',
            backgroundPosition: 'center center',
            backgroundBlendMode: profile.banner_url ? 'multiply' : 'normal'
          }">
          <!-- Bouton Modifier -->
          <button v-if='isOwnProfile' @click="openCosmeticModal" title="Modifier l'apparence"
            class="absolute top-4 right-4 btn btn-circle btn-sm btn-neutral border border-base-content/10 shadow-lg hover:scale-110 hover:text-primary transition-all z-20">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"></path>
            </svg>
          </button>

          <!-- Box carrée invisible pour l'Avatar (Garde les proportions sans crop rond) -->
          <div class="mb-4">
            <div class="w-[120px] h-[120px] flex items-center justify-center bg-transparent overflow-hidden">
              <img :src="profile.avatar_url ? getAssetUrl(profile.avatar_url) : 'http://127.0.0.1:9414/static/hero.png'"
                class="max-w-full max-h-full object-contain" :alt="profile.username" />
            </div>
          </div>

          <!-- Infos Utilisateur -->
          <div class="text-center mb-4 w-full">
            <p class="text-xl font-bold font-text mb-2">{{ profile.first_name && profile.last_name ?
              `${profile.first_name}
              ${profile.last_name}` : profile.username }}</p>
            <span :class="affiliationColors"
              class="inline-block text-white px-3 py-1 rounded text-sm font-bold font-stitre mb-2">
              {{ profile.affiliation || 'N/A' }}
            </span>
            <p class="text-sm font-text text-gray-400">
              <template v-if="profile.niveau && profile.classe">
                {{ profile.niveau }} - Classe {{ profile.classe }}
              </template>
              <template v-else>
                {{ profile.type || 'COMPTE' }}
              </template>
            </p>
          </div>

          <!-- Barre d'XP style -->
          <div class="w-full">
            <!-- 1. Textes adaptés au thème (text-base-content) -->
            <p class="text-center text-xs text-base-content/70 mb-2 font-code tracking-widest uppercase">
              XP: {{ profile.xp }} <span class="text-base-content/30 mx-1">/</span> {{ profile.next_xp_level }}
            </p>

            <div class="flex items-center gap-4">
              <!-- Niveau actuel discret -->
              <span class="ont-text font-bold text-sm text-primary/50">LVL {{ profile.level }}</span>

              <!-- 2. Conteneur de la barre (Fond creux adaptatif) -->
              <div
                class="flex-1 h-5 bg-base-300 border border-primary overflow-hidden relative shadow-inner">

                <!-- Binaire d'arrière-plan (désactivé / transparent) -->
                <div
                  class="absolute inset-0 flex items-center text-base-content/10 font-code text-[10px] sm:text-xs whitespace-nowrap overflow-hidden select-none">
                  {{ '01001011 01100101 01111001 '.repeat(4) }}
                </div>

                <!-- 3. Remplissage de la barre -->
                <div
                  class="h-full bg-primary/20 border-r-2 border-primary transition-all duration-1000 ease-out relative overflow-hidden flex items-center shadow-[0_0_15px_rgba(var(--p),0.3)]"
                  :style="{ width: scorePercentage + '%' }">
                  <!-- Binaire actif (Couleur primaire lumineuse + défilement) -->
                  <div
                    class="absolute left-0 text-primary font-code text-[10px] sm:text-xs whitespace-nowrap font-bold select-none binary-scroll">
                    {{ '01001011 01100101 01111001 '.repeat(25) }}
                  </div>
                </div>

              </div>

              <!-- Niveau suivant mis en avant -->
              <span class="font-text font-bold text-sm text-primary">LVL {{ profile.level + 1 }}</span>
            </div>
          </div>

        </div>

        <div class="flex-1 flex flex-col gap-6">
          <div class="flex justify-center items-center gap-4">
            <h2 class="text-3xl font-bold font-titre">[ {{ profile.username }} ]</h2>
            <span class="player-badge bg-secondary text-[#1a1a1a] px-3 py-1 rounded font-stitre text-sm">{{ profile.type
              === 'USER' ? 'PLAYER' : profile.type }}</span>
          </div>
          <div class="flex-1">
            <div class="stats-grid grid grid-cols-3 gap-4 h-full">
              <div
                class="stat-item relative bg-base-100 border-2 border-base-300 p-4 text-center flex flex-col justify-center items-center rounded-sm"
                :style="{ backgroundImage: `url(${rankImg})`, backgroundSize: 'cover', backgroundPosition: 'center', backgroundColor: 'rgba(0,0,0,0.50)', backgroundBlendMode: 'multiply' }">
                <span
                  class="group info-icon absolute top-2 right-2 w-[18px] h-[18px] bg-[#444444] border border-[#666666] rounded-full flex items-center justify-center text-[10px] text-gray-400 cursor-help font-text transition-colors hover:bg-gray-600 hover:text-white">
                  ?

                  <div
                    class="absolute bottom-full right-[-4px] mb-2 hidden group-hover:flex flex-col items-end z-50 w-48 pointer-events-none">
                    <div class="bg-base-300 border border-gray-600 p-2.5 rounded-md shadow-xl text-left w-full">
                      <p class="font-titre text-[#d4a500] text-xs font-bold uppercase tracking-wider mb-1">Rank Global
                      </p>
                      <p
                        class="text-gray-300 text-[11px] font-text font-normal leading-relaxed normal-case tracking-normal">
                        Votre positionnement actuel au classement général par rapport à l'ensemble des joueurs.
                      </p>
                    </div>
                    <div class="w-2 h-2 bg-base-300 border-r border-b border-gray-600 transform rotate-45 -mt-1 mr-2">
                    </div>
                  </div>
                </span>

                <p class="stat-label text-xs text-white uppercase tracking-wider mb-1 font-bold font-stitre">Rank</p>
                <p class="stat-value text-2xl font-bold font-code">{{ profile.rank }}</p>
              </div>
              <div
                class="stat-item relative bg-base-100 border-2 border-base-300 p-4 text-center flex flex-col justify-center items-center rounded-sm"
                :style="{ backgroundImage: `url(${challImg})`, backgroundSize: 'cover', backgroundPosition: 'center', backgroundColor: 'rgba(0,0,0,0.50)', backgroundBlendMode: 'multiply' }">
                <span
                  class="group info-icon absolute top-2 right-2 w-[18px] h-[18px] bg-[#444444] border border-[#666666] rounded-full flex items-center justify-center text-[10px] text-gray-400 cursor-help font-bold transition-colors hover:bg-gray-600 hover:text-white">
                  ?

                  <div
                    class="absolute bottom-full right-[-4px] mb-2 hidden group-hover:flex flex-col items-end z-50 w-48 pointer-events-none">
                    <div class="bg-base-300 border border-gray-600 p-2.5 rounded-md shadow-xl text-left w-full">
                      <p class="font-titre text-[#d4a500] text-xs font-bold uppercase tracking-wider mb-1">Challenges
                        Résolus
                      </p>
                      <p
                        class="text-gray-300 text-[11px] font-text font-normal leading-relaxed normal-case tracking-normal">
                        Nombre total de challenges de sécurité que vous avez réussi à flagger sur la plateforme.</p>
                    </div>
                    <div class="w-2 h-2 bg-base-300 border-r border-b border-gray-600 transform rotate-45 -mt-1 mr-2">
                    </div>
                  </div>
                </span>
                <p class="stat-label text-xs text-white uppercase tracking-wider mb-1 font-bold font-stitre">Chall</p>
                <p class="stat-value text-2xl font-bold font-code">{{ solveCount }}</p>
              </div>
              <div
                class="stat-item relative bg-base-100 border-2 border-base-300 p-4 text-center flex flex-col justify-center items-center rounded-sm"
                :style="{ backgroundImage: `url(${pointsImg})`, backgroundSize: 'cover', backgroundPosition: 'center', backgroundColor: 'rgba(0,0,0,0.50)', backgroundBlendMode: 'multiply' }">
                <span
                  class="group info-icon absolute top-2 right-2 w-[18px] h-[18px] bg-[#444444] border border-[#666666] rounded-full flex items-center justify-center text-[10px] text-gray-400 cursor-help font-bold transition-colors hover:bg-gray-600 hover:text-white">
                  ?

                  <div
                    class="absolute bottom-full right-[-4px] mb-2 hidden group-hover:flex flex-col items-end z-50 w-48 pointer-events-none">
                    <div class="bg-base-300 border border-gray-600 p-2.5 rounded-md shadow-xl text-left w-full">
                      <p class="font-titre text-[#d4a500] text-xs font-bold uppercase tracking-wider mb-1">Rank Global
                      </p>
                      <p
                        class="text-gray-300 text-[11px] font-text font-normal leading-relaxed normal-case tracking-normal">
                        Votre positionnement actuel au classement général par rapport à l'ensemble des joueurs.
                      </p>
                    </div>
                    <div class="w-2 h-2 bg-base-300 border-r border-b border-gray-600 transform rotate-45 -mt-1 mr-2">
                    </div>
                  </div>
                </span>
                <p class="stat-label text-xs text-white uppercase tracking-wider mb-1 font-bold font-stitre">Points</p>
                <p class="stat-value text-2xl font-bold font-mono">{{ profile.global_score }}</p>
              </div>
              <div
                class="stat-item relative bg-base-100 border-2 border-base-300 p-4 text-center flex flex-col justify-center items-center rounded-sm"
                :style="{ backgroundImage: `url(${machineImg})`, backgroundSize: 'cover', backgroundPosition: 'center', backgroundColor: 'rgba(0,0,0,0.50)', backgroundBlendMode: 'multiply' }">
                <span
                  class="group info-icon absolute top-2 right-2 w-[18px] h-[18px] bg-[#444444] border border-[#666666] rounded-full flex items-center justify-center text-[10px] text-gray-400 cursor-help font-bold transition-colors hover:bg-gray-600 hover:text-white">
                  ?

                  <div
                    class="absolute bottom-full right-[-4px] mb-2 hidden group-hover:flex flex-col items-end z-50 w-48 pointer-events-none">
                    <div class="bg-base-300 border border-gray-600 p-2.5 rounded-md shadow-xl text-left w-full">
                      <p class="font-mono text-[#d4a500] text-xs font-bold uppercase tracking-wider mb-1">Machines
                        Complétées
                      </p>
                      <p
                        class="text-gray-300 text-[11px] font-sans font-normal leading-relaxed normal-case tracking-normal">
                        Nombre total de machines de CTF/pentesting que vous avez réussi à pwner sur la plateforme.
                      </p>
                    </div>
                    <div class="w-2 h-2 bg-base-300 border-r border-b border-gray-600 transform rotate-45 -mt-1 mr-2">
                    </div>
                  </div>
                </span>
                <p class="stat-label text-xs text-white uppercase tracking-wider mb-1 font-bold font-stitre">Machines
                </p>
                <p class="stat-value text-2xl font-bold font-mono">{{ machineCount }}</p>
              </div>
              <div
                class="stat-item relative bg-base-100 border-2 border-base-300 p-4 text-center flex flex-col justify-center items-center rounded-sm"
                :style="{ backgroundImage: `url(${badgesImg})`, backgroundSize: 'cover', backgroundPosition: 'center', backgroundColor: 'rgba(0,0,0,0.50)', backgroundBlendMode: 'multiply' }">
                <span
                  class="group info-icon absolute top-2 right-2 w-[18px] h-[18px] bg-[#444444] border border-[#666666] rounded-full flex items-center justify-center text-[10px] text-gray-400 cursor-help font-bold transition-colors hover:bg-gray-600 hover:text-white">
                  ?

                  <div
                    class="absolute bottom-full right-[-4px] mb-2 hidden group-hover:flex flex-col items-end z-50 w-48 pointer-events-none">
                    <div class="bg-base-300 border border-gray-600 p-2.5 rounded-md shadow-xl text-left w-full">
                      <p class="font-mono text-[#d4a500] text-xs font-bold uppercase tracking-wider mb-1">Rank Global
                      </p>
                      <p
                        class="text-gray-300 text-[11px] font-sans font-normal leading-relaxed normal-case tracking-normal">
                        Votre positionnement actuel au classement général par rapport à l'ensemble des joueurs.
                      </p>
                    </div>
                    <div class="w-2 h-2 bg-base-300 border-r border-b border-gray-600 transform rotate-45 -mt-1 mr-2">
                    </div>
                  </div>
                </span>
                <p class="stat-label text-xs text-white uppercase tracking-wider mb-1 font-bold font-stitre">Badges</p>
                <p class="stat-value text-2xl font-bold font-mono">{{ badges.length }}</p>
              </div>
              <div
                class="stat-item relative bg-base-100 border-2 border-base-300 p-4 text-center flex flex-col justify-center items-center rounded-sm"
                :style="{ backgroundImage: `url(${streakImg})`, backgroundSize: 'cover', backgroundPosition: 'center', backgroundColor: 'rgba(0,0,0,0.50)', backgroundBlendMode: 'multiply' }">
                <span
                  class="group info-icon absolute top-2 right-2 w-[18px] h-[18px] bg-[#444444] border border-[#666666] rounded-full flex items-center justify-center text-[10px] text-gray-400 cursor-help font-bold transition-colors hover:bg-gray-600 hover:text-white">
                  ?

                  <div
                    class="absolute bottom-full right-[-4px] mb-2 hidden group-hover:flex flex-col items-end z-50 w-48 pointer-events-none">
                    <div class="bg-base-300 border border-gray-600 p-2.5 rounded-md shadow-xl text-left w-full">
                      <p class="font-mono text-[#d4a500] text-xs font-bold uppercase tracking-wider mb-1">Rank Global
                      </p>
                      <p
                        class="text-gray-300 text-[11px] font-sans font-normal leading-relaxed normal-case tracking-normal">
                        Votre positionnement actuel au classement général par rapport à l'ensemble des joueurs.
                      </p>
                    </div>
                    <div class="w-2 h-2 bg-base-300 border-r border-b border-gray-600 transform rotate-45 -mt-1 mr-2">
                    </div>
                  </div>
                </span>
                <p class="stat-label text-xs text-white uppercase tracking-wider mb-1 font-bold font-stitre">Streak</p>
                <p class="stat-value text-2xl font-bold font-mono">{{ currentStreak }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Badges -->
      <div class="grid grid-cols-1 lg:grid-cols-10 gap-6">
        <div class="lg:col-span-6 bg-base-300 backdrop-blur-md border-[2px] border-base-200 p-6 flex flex-col h-full">

          <div class="flex items-center justify-between mb-4">
            <h3 class="text-xl font-bold font-titre">Badges</h3>
            <button @click="openAllBadgesModal"
              class="w-6 h-6 flex items-center justify-center rounded-full border border-primary text-primary hover:bg-secondary hover:text-base-300 transition-colors cursor-pointer"
              title="Voir tous les badges disponibles">
              ?
            </button>
          </div>

          <div class="badges-container flex flex-col flex-1 gap-4">
            <div v-if="badges.length === 0" class="border-2 border-base-300 p-8 rounded-sm text-center my-auto">
              <p class="text-gray-400 font-text">Aucun badge</p>
            </div>

            <template v-else>
              <div class="badges-grid grid grid-cols-5 gap-10 bg-base-100/50 p-8 rounded-sm">
                <div v-for="(badge, index) in paginatedBadges" :key="index"
                  class="relative group mx-auto flex flex-col items-center">

                  <!-- BOX CARRÉE INVISIBLE (Modifiée pour afficher la vraie forme) -->
                  <div
                    class="badge-box w-[60px] h-[60px] bg-transparent overflow-hidden flex items-center justify-center group-hover:scale-110 transition-transform duration-200 cursor-help">
                    <img v-if="badge.icon_url" :src="getAssetUrl(badge.icon_url)" :alt="badge.name"
                      class="max-w-full max-h-full object-contain" />
                    <span v-else class="text-white font-bold text-center text-[10px] bg-neutral p-2 rounded-md">
                      {{ badge.name.substring(0, 2).toUpperCase() }}
                    </span>
                  </div>

                  <!-- Tooltip -->
                  <div
                    class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-3 hidden group-hover:flex flex-col items-center z-50 w-48 pointer-events-none">
                    <div
                      class="bg-base-200 border border-primary p-2.5 rounded-md shadow-[0_0_15px_rgba(212,165,0,0.2)] text-center">
                      <p class="font-mono font-bold text-primary text-xs uppercase tracking-wider mb-1">
                        {{ badge.name }}
                      </p>
                      <p class="text-gray-300 text-[11px] leading-relaxed font-sans">
                        {{ badge.description || 'Aucune description disponible pour ce badge.' }}
                      </p>
                    </div>
                    <div class="w-2 h-2 bg-base-200 border-r border-b border-primary transform rotate-45 -mt-1"></div>
                  </div>
                </div>
              </div>

              <div v-if="totalBadgePages > 1" class="pagination flex gap-2 justify-center mt-auto pt-2">
                <span v-for="page in totalBadgePages" :key="page"
                  class="page-number w-7 h-7 flex items-center justify-center cursor-pointer text-sm rounded-sm transition-colors"
                  :class="currentBadgePage === page ? 'bg-primary text-[#1a1a1a] font-bold' : 'bg-primary/25 border border-base-300 text-base-content hover:text-white'"
                  @click="currentBadgePage = page">{{ page }}</span>
              </div>
            </template>
          </div>
        </div>

        <dialog class="modal" :class="{ 'modal-open': isAllBadgesModalOpen }">
          <div class="modal-box w-11/12 max-w-4xl bg-base-300 border-2 border-base-200 rounded-none p-8">
            <button class="btn btn-sm btn-circle btn-ghost absolute right-4 top-4"
              @click="isAllBadgesModalOpen = false">✕</button>
            <h3 class="font-titre text-2xl mb-6 text-white border-b border-base-100 pb-4">Tous les badges</h3>

            <div v-if="isLoadingAllBadges" class="text-center py-10">
              <span class="loading loading-spinner text-primary loading-lg"></span>
            </div>

            <div v-else
              class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-6 max-h-[60vh] overflow-y-auto no-scrollbar pr-2">
              <div v-for="badge in allGlobalBadges" :key="badge.id"
                class="flex flex-col items-center p-4 rounded-xs transition-all text-center"
                :class="userHasBadge(badge) ? 'opacity-100' : 'opacity-50 grayscale'">

                <div class="w-[60px] h-[60px] flex items-center justify-center overflow-hidden mb-3"
                  :class="userHasBadge(badge) ? 'bg-transparent' : 'bg-base-300'">
                  <img v-if="badge.icon_url" :src="getAssetUrl(badge.icon_url)" :alt="badge.name"
                    class="w-full h-full object-cover" />
                  <span v-else class="text-white font-bold text-center text-[10px]">
                    {{ badge.name.substring(0, 2).toUpperCase() }}
                  </span>
                </div>

                <h4 class="font-bold text-xs uppercase tracking-wide mb-2"
                  :class="userHasBadge(badge) ? 'text-primary' : 'text-gray-400'">
                  {{ badge.name }}
                </h4>
                <p class="text-[10px] text-gray-500 leading-tight">
                  {{ badge.description || 'Aucune description' }}
                </p>
              </div>
            </div>
          </div>
          <form method="dialog" class="modal-backdrop" @click="isAllBadgesModalOpen = false">
            <button>Fermer</button>
          </form>
        </dialog>
        <div
          class="lg:col-span-4 bg-base-300 backdrop-blur-md border-[2px] border-base-200 p-6 flex flex-col rounded-sm">
          <h3 class="text-xl font-bold mb-4 font-titre">Activité récente</h3>
          <div class="activity-container flex flex-col gap-3 flex-1 justify-between">
            <div v-if="recentActivities.length === 0"
              class="bg-base-100 border border-base-300 p-4 rounded-sm text-center">
              <p class="text-gray-400 text-sm font-mono">Aucune activité récente</p>
            </div>

            <template v-else>
              <div v-for="(activity, index) in recentActivities" :key="index"
                class="activity-item bg-base-100 border border-base-300 p-3 min-h-[45px] flex items-center justify-between hover:border-[#d4a500] transition-colors">
                <div class="flex-1">
                  <p class="activity-title text-white font-bold text-sm">{{ activity.reason }}</p>
                  <p class="text-xs text-gray-500 font-mono">{{ formatRelativeDate(activity.timestamp) }}</p>
                </div>
                <span v-if="activity.change" class="text-accent font-bold">+{{ activity.change }} pts</span>
              </div>
            </template>
          </div>
        </div>
      </div>

      <!-- heatmap contribution -->
      <div class="bg-base-300 backdrop-blur-md border-[2px] border-base-200 p-6">
        <h3 class="text-xl font-bold mb-4 font-titre">Activité annuelle</h3>
        <div class="contribution-container overflow-x-auto bg-base-100 border-2 border-base-300 p-4 rounded-sm"
          style="scrollbar-width: none;">
          <div id="heatmap" style="width: 100%; min-height: 280px;"></div>
        </div>
      </div>
      <!-- heatmap contribution -->

      <!-- PERFORMANCETEST -->
      <div class="bg-base-300 backdrop-blur-md border-[2px] border-base-200 p-6 flex flex-col gap-6">
        <h3 class="text-xl font-bold font-titre">Performance</h3>
        <div class="bg-base-100 border-2 border-base-300 p-4 rounded-sm w-full">
          <p class="text-sm font-bold text-gray-400 mb-4 uppercase tracking-wider font-mono">Progression (Points)</p>
          <div class="h-[260px] relative w-full">
            <div id="chart-scroll-area" class="w-full h-full">
              <canvas id="progressionChart"></canvas>
            </div>
          </div>
        </div>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 w-full">
          <div class="bg-base-100 border-2 border-base-300 p-4 rounded-sm flex flex-col items-center">
            <p class="text-sm font-bold text-gray-400 mb-4 uppercase tracking-wider font-mono self-start">Résolutions
              par
              Catégorie</p>
            <div class="h-[280px] w-full max-w-[340px] relative flex items-center justify-center">
              <canvas id="categoryChart"></canvas>
            </div>
          </div>
          <div class="bg-base-100 border-2 border-base-300 p-4 rounded-sm">
            <p class="text-sm font-bold text-gray-400 mb-4 uppercase tracking-wider font-mono">Challenges par Difficulté
            </p>
            <div class="h-[280px] relative w-full">
              <canvas id="difficultyChart"></canvas>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ==================== MODALE COSMÉTIQUES AGRANDIE ==================== -->
  <Teleport to="body">
    <Transition enter-active-class="transition duration-100 ease-out" enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100" leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100 scale-100" leave-to-class="opacity-0 scale-95">
      <div v-if="cosmeticModal"
        class="fixed inset-0 z-[200] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
        @click.self="cosmeticModal = false">

        <!-- Changement de taille ici : max-w-3xl -->
        <div class="bg-base-200 shadow-2xl w-full max-w-3xl max-h-[92vh] flex flex-col overflow-hidden">

          <!-- Header -->
          <div class="flex items-center justify-between px-6 py-4 border-b border-base-300 flex-shrink-0">
            <h2 class="font-bold text-lg font-titre tracking-wide">Personnalisation du profil</h2>
            <button @click="cosmeticModal = false" class="btn btn-sm btn-circle btn-ghost text-lg">✕</button>
          </div>

          <!-- Zone de Body Scrollable -->
          <div class="flex-1 overflow-y-auto px-6 py-6 space-y-6">

            <!-- APERÇU EN DIRECT DU COMPOSANT (Inspiré de la Capture d’écran 2026-06-10 à 14.17.01.jpg) -->
            <div>
              <p class="text-xs font-bold font-text uppercase tracking-wider opacity-50 mb-2">Aperçu</p>
              <div
                class="w-full rounded-lg p-6 flex flex-col items-center justify-between relative overflow-hidden min-h-[280px] transition duration-300"
                :style="{
                  backgroundImage: bannerPreview ? `url(${getAssetUrl(bannerPreview.icon_url)})` : (profile.banner_url ? `url(${getAssetUrl(profile.banner_url)})` : 'none'),
                  backgroundSize: 'cover',
                  backgroundPosition: 'center center',
                  backgroundColor: 'rgba(0, 0, 0, 0.6)',
                  backgroundBlendMode: 'multiply'
                }">
                <!-- Avatar Preview (Box carrée invisible) -->
                <div class="mb-3">
                  <div class="w-[110px] h-[110px] flex items-center justify-center bg-transparent overflow-hidden">
                    <img v-if="avatarPreview" :src="getAssetUrl(avatarPreview.icon_url)"
                      class="max-w-full max-h-full object-contain" alt="Preview avatar" />
                    <img v-else-if="profile.avatar_url" :src="getAssetUrl(profile.avatar_url)"
                      class="max-w-full max-h-full object-contain" alt="Current avatar" />
                    <img v-else src="http://127.0.0.1:9414/static/hero.png"
                      class="max-w-full max-h-full object-contain" />
                  </div>
                </div>

                <!-- Infos Preview -->
                <div class="text-center mb-3 w-full text-white">
                  <p class="text-lg font-bold font-text mb-1">{{ profile.first_name || 'Abonga' }} {{ profile.last_name
                    ||
                    'AJAX' }}</p>
                  <span
                    class="bg-blue-700 inline-block text-white px-3 py-0.5 rounded text-xs font-bold font-stitre mb-1">PARIS</span>
                  <p class="text-xs font-text text-gray-300">GCS3 - classe 1</p>
                </div>

                <!-- Barre XP Vert Flashy (Identique à la capture) -->
                <div class="w-full text-white px-4">
                  <p class="text-center text-[10px] text-gray-300 mb-1 font-code">XP: {{ profile.xp || 0 }} / 251</p>
                  <div class="flex items-center gap-3">
                    <span class="font-bold font-code text-xs">1</span>
                    <div class="flex-1 h-4 bg-black/40 rounded overflow-hidden relative border border-white/10">
                      <div class="h-full bg-[#00ff1a]" style="width: 100%;"></div>
                    </div>
                    <span class="font-bold font-code text-xs">2</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Navigation Onglets Onglets -->
            <div class="flex gap-1 bg-base-300 p-1 rounded-sm flex-shrink-0">
              <button @click="cosmeticTab = 'avatar'" class="flex-1 py-2.5 rounded-sm text-sm font-bold transition-all"
                :class="cosmeticTab === 'avatar' ? 'bg-primary text-base-100 shadow' : 'text-base-content/60 hover:text-base-content'">
                Avatars
              </button>
              <button @click="cosmeticTab = 'banner'" class="flex-1 py-2.5 rounded-sm text-sm font-bold transition-all"
                :class="cosmeticTab === 'banner' ? 'bg-primary text-base-100 shadow' : 'text-base-content/60 hover:text-base-content'">
                Bannières
              </button>
            </div>

            <!-- ===== SECTION GALERIE : AVATARS ===== -->
            <div v-if="cosmeticTab === 'avatar'">
              <p class="text-xs font-bold font-text uppercase tracking-wider opacity-50 mb-3">Mes avatars</p>
              <div v-if="avatarsLoading" class="flex justify-center py-8"><span
                  class="loading loading-spinner text-primary"></span></div>
              <div v-else-if="availableAvatars.length === 0"
                class="text-center text-sm opacity-40 py-8 bg-base-300/40 rounded-lg">Aucun avatar</div>

              <!-- Grid avec Box Carrées Invisibles -->
              <div v-else class="grid grid-cols-4 sm:grid-cols-5 gap-4">
                <button v-for="cosmetic in availableAvatars" :key="cosmetic.id" @click="selectGalleryAvatar(cosmetic)"
                  class="relative w-full aspect-square bg-base-300/20 hover:bg-base-300/40 rounded-xl border-2 transition-all hover:scale-105 flex items-center justify-center p-3"
                  :class="selectedAvatar?.id === cosmetic.id ? 'border-primary shadow-lg shadow-primary/20' : 'border-transparent'">
                  <img :src="getAssetUrl(cosmetic.icon_url)" class="max-w-full max-h-full object-contain"
                    :alt="cosmetic.name" />
                  <div v-if="selectedAvatar?.id === cosmetic.id"
                    class="absolute top-1 right-1 bg-primary text-white rounded-full p-0.5 shadow">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24"
                      stroke="currentColor" stroke-width="3">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                </button>
              </div>
            </div>

            <!-- ===== SECTION GALERIE : BANNIÈRES ===== -->
            <div v-if="cosmeticTab === 'banner'">
              <p class="text-xs font-bold uppercase tracking-wider opacity-50 mb-3">Mes bannières</p>
              <div v-if="bannersLoading" class="flex justify-center py-8"><span
                  class="loading loading-spinner text-primary"></span></div>
              <div v-else-if="availableBanners.length === 0"
                class="text-center text-sm opacity-40 py-8 bg-base-300/40 rounded-lg">Aucune bannière</div>

              <div v-else class="grid grid-cols-2 gap-4">
                <button v-for="cosmetic in availableBanners" :key="cosmetic.id" @click="selectGalleryBanner(cosmetic)"
                  class="relative w-full h-24 overflow-hidden border-2 transition-all hover:scale-[1.02]"
                  :class="selectedBanner?.id === cosmetic.id ? 'border-primary shadow-lg' : 'border-base-300'">
                  <img :src="getAssetUrl(cosmetic.icon_url)" class="w-full h-full object-cover" :alt="cosmetic.name" />
                  <div v-if="selectedBanner?.id === cosmetic.id"
                    class="absolute inset-0 bg-primary/10 flex items-center justify-center">
                    <div class="bg-primary text-white rounded-full p-1 shadow">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-1 w-1" fill="none" viewBox="0 0 24 24"
                        stroke="currentColor" stroke-width="4">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                  </div>
                </button>
              </div>
            </div>

          </div>

          <!-- Footer -->
          <div class="flex gap-3 px-6 py-4 border-t border-base-300 bg-base-300/30 flex-shrink-0">
            <button @click="cosmeticModal = false" class="btn btn-sm btn-ghost flex-1">Annuler</button>

            <!-- Bouton dynamique avec '!' pour forcer le vert sur le fond et la bordure -->
            <button @click="saveCosmetics" class="btn btn-sm flex-1 transition-all duration-300 select-none" :class="cosmeticSuccess
              ? '!bg-green-600 !border-green-600 text-white font-bold'
              : 'btn-primary'" :disabled="cosmeticSaving || cosmeticSuccess">
              <!-- État : En cours de chargement -->
              <span v-if="cosmeticSaving" class="loading loading-spinner loading-xs"></span>

              <!-- État : Sauvegardé avec succès (Nettoyé du bg-green inutile) -->
              <span v-if="cosmeticSuccess"
                class="flex items-center gap-1.5 text-white justify-center cursor-not-allowed">
                ✓ Modification sauvegardée !
              </span>

              <!-- État : Par défaut -->
              <span v-else-if="!cosmeticSaving">
                Appliquer les changements
              </span>
            </button>
          </div>

        </div>
      </div>
    </Transition>
  </Teleport>

</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import axios from 'axios';
import { getAssetUrl } from '../../utils/assets'
import { useRoute, useRouter } from 'vue-router';
import Chart from 'chart.js/auto';
import zoomPlugin from 'chartjs-plugin-zoom';
import ApexCharts from 'apexcharts';
import 'chartjs-adapter-date-fns';

import rankImg from '../../assets/rank.png';
import challImg from '../../assets/chall.png';
import pointsImg from '../../assets/points.png';
import machineImg from '../../assets/machine.png';
import badgesImg from '../../assets/badges.png';
import streakImg from '../../assets/streak.png';
import profileImg from '../../assets/profilefond.jpg';

const route = useRoute()
const router = useRouter();
Chart.register(zoomPlugin);

const currentUsername = ref('');
// État pour savoir si c'est le profil de l'utilisateur connecté ou non
const isOwnProfile = computed(() => !route.params.username);
const targetUsername = computed(() => route.params.username);

// -- ÉTATS --
const loading = ref(true);
const error = ref(null);
const profile = ref({
  username: '',
  first_name: '',
  last_name: '',
  affiliation: '',
  niveau: '',
  classe: '',
  type: 'user',
  global_score: 0,
  xp: 0,
  level: 0,
  xp_level: 0,
  next_xp_level: 0,
  avatar: null
});

const affiliationColors = ref('bg-neutral');

const badges = ref([]);
const recentActivities = ref([]);
const currentBadgePage = ref(1);
const solveCount = ref(0);
const machineCount = ref(0);
const userRank = ref(0);
const currentStreak = ref(0);

const categoryStats = ref({})
const globalCategories = ref([])
const difficultyStats = ref({})

let progressionChart = null;
let categoryChart = null;
let difficultyChart = null;

const filterTypeMap = ['YEAR', 'MONTH', 'DAY'];

const badgesPerPage = 10;
const totalBadgePages = computed(() => Math.ceil(badges.value.length / badgesPerPage));
const paginatedBadges = computed(() => {
  const start = (currentBadgePage.value - 1) * badgesPerPage;
  return badges.value.slice(start, start + badgesPerPage);
});

// --- GESTION DU LEXIQUE DES BADGES GLOBALS ---
const isAllBadgesModalOpen = ref(false);
const isLoadingAllBadges = ref(false);
const allGlobalBadges = ref([]);

const openAllBadgesModal = async () => {
  isAllBadgesModalOpen.value = true;
  if (allGlobalBadges.value.length > 0) return;
  isLoadingAllBadges.value = true;
  try {
    const response = await axios.get('/api/user/badge/list');
    allGlobalBadges.value = response.data.badges || response.data || [];
  } catch (error) {
    console.error("Erreur lors de la récupération des badges globaux :", error);
  } finally {
    isLoadingAllBadges.value = false;
  }
};

// Fonction qui compare l'ID (ou le nom) du badge global avec tes badges possédés
const userHasBadge = (globalBadge) => {
  // Assure-toi que "badges.value" est bien le tableau contenant les badges de l'utilisateur
  return badges.value.some(userBadge =>
    userBadge.id === globalBadge.id || userBadge.name === globalBadge.name
  );
};

const scorePercentage = computed(() => {
  if (!profile.value.next_xp_level) return 0;
  return Math.min(Math.max((profile.value.xp / profile.value.next_xp_level) * 100, 0), 100);
});

const parseTimestamp = (timestampStr) => {
  if (!timestampStr) return new Date();

  if (timestampStr.includes(':')) {
    const [hours] = timestampStr.split(':');
    const date = new Date();
    date.setHours(parseInt(hours), 0, 0, 0);
    return date;
  } else if (timestampStr.split('/').length === 2) {
    const [day, month] = timestampStr.split('/');
    const now = new Date();
    return new Date(now.getFullYear(), parseInt(month) - 1, parseInt(day));
  } else if (timestampStr.split('/').length === 3) {
    const [day, month, year] = timestampStr.split('/');
    return new Date(year, parseInt(month) - 1, parseInt(day));
  } else if (timestampStr.includes('-') && !timestampStr.includes(' ')) {
    const [year, month, day] = timestampStr.split('-');
    return new Date(year, parseInt(month) - 1, parseInt(day));
  } else if (timestampStr.includes('-') && timestampStr.includes(' ')) {
    return new Date(timestampStr);
  }

  return new Date(timestampStr);
};

const formatRelativeDate = (timestampStr) => {
  if (!timestampStr) return '';
  const activityDate = parseTimestamp(timestampStr);
  const now = new Date();
  const diffInSeconds = Math.floor((now - activityDate) / 1000);

  if (diffInSeconds < 60) return "À l'instant";

  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) return `Il y a ${diffInMinutes} minute${diffInMinutes > 1 ? 's' : ''}`;

  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) return `Il y a ${diffInHours} heure${diffInHours > 1 ? 's' : ''}`;

  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 7) return `Il y a ${diffInDays} jour${diffInDays > 1 ? 's' : ''}`;

  return `Le ${activityDate.toLocaleDateString('fr-FR', { day: 'numeric', month: 'long' })}`;
};

const currentZoomLevel = ref(0);
let lastChartHistory = [];
let isLoadingZoom = false;

const handleWheelZoomSteps = (chart, isZoomIn) => {
  if (isLoadingZoom) return;

  if (isZoomIn) {
    if (currentZoomLevel.value < 2) currentZoomLevel.value++;
    else return;
  } else {
    if (currentZoomLevel.value > 0) currentZoomLevel.value--;
    else return;
  }

  isLoadingZoom = true;
  const filterType = filterTypeMap[currentZoomLevel.value];

  axios.get(`/api/user/${currentUsername.value}/score/history`).then(response => {
    if (response.data?.status === 'success' && response.data?.history) {
      updateProgressionChart(response.data.history);
    }
    isLoadingZoom = false;
  }).catch(err => {
    console.warn('Erreur lors du chargement du zoom:', err);
    isLoadingZoom = false;
  });
};

const updateProgressionChart = (history) => {
  if (!history || history.length === 0) return;

  lastChartHistory = history;

  let chartPoints = history.map(h => {
    return {
      x: parseTimestamp(h.timestamp),
      y: h.score_total,
      reason: h.reason,
      change: h.change
    };
  });

  chartPoints.sort((a, b) => a.x - b.x);

  // FILTRAGE : Conserve uniquement le 1er point, le dernier point, ou les changements réels.
  chartPoints = chartPoints.filter((point, i, arr) => {
    if (i === 0) return true;
    if (i === arr.length - 1) return true;
    return point.y !== arr[i - 1].y;
  });

  const applyUpdate = () => {
    if (progressionChart) {
      progressionChart.data.datasets[0].data = chartPoints;

      const now = new Date();
      if (currentZoomLevel.value === 0) {
        if (now.getMonth() >= 8) {
          progressionChart.options.scales.x.min = new Date(`${now.getFullYear()}-09-01T00:00:00`);
          progressionChart.options.scales.x.max = new Date(`${now.getFullYear() + 1}-08-31T23:59:59`);
        } else {
          progressionChart.options.scales.x.min = new Date(`${now.getFullYear() - 1}-09-01T00:00:00`);
          progressionChart.options.scales.x.max = new Date(`${now.getFullYear()}-08-31T23:59:59`);
        }
      } else if (currentZoomLevel.value === 1) {
        progressionChart.options.scales.x.min = new Date(now.getTime() - (30 * 24 * 60 * 60 * 1000));
        progressionChart.options.scales.x.max = now;
      } else if (currentZoomLevel.value === 2) {
        progressionChart.options.scales.x.min = new Date(now.getTime() - (24 * 60 * 60 * 1000));
        progressionChart.options.scales.x.max = now;
      }

      progressionChart.update();
    } else {
      setTimeout(applyUpdate, 50);
    }
  };

  applyUpdate();
};

const loadProfile = async () => {
  loading.value = true;
  error.value = null;

  const profileEndpoint = isOwnProfile.value
    ? '/api/user/me/profile'
    : `/api/user/${targetUsername.value}/profile`;

  try {
    const profileRes = await axios.get(profileEndpoint);
    const fallbackProfile = profileRes.data?.profile || profileRes.data?.user || profileRes.data?.type;

    if (profileRes.data?.status === 'success' && fallbackProfile) {
      profile.value = {
        ...fallbackProfile,
        type: fallbackProfile.type || 'user',
        global_score: fallbackProfile.global_score || 0,
        currentStreak: fallbackProfile.current_streak || 0,
      };
      currentUsername.value = fallbackProfile.username;

      profile.value.avatar_url = fallbackProfile.avatar || fallbackProfile.avatar;
      profile.value.banner_url = fallbackProfile.banner || fallbackProfile.banner;

      if (fallbackProfile.affiliation === 'PARIS') {
        affiliationColors.value = 'bg-paris';
      } else if (fallbackProfile.affiliation === 'BORDEAUX') {
        affiliationColors.value = 'bg-bordeaux';
      } else if (fallbackProfile.affiliation === 'LYON') {
        affiliationColors.value = 'bg-lyon';
      } else {
        affiliationColors.value = 'bg-white';
      }

    } else {
      error.value = profileRes.data?.message || 'Impossible de charger le profil.';
      loading.value = false;
      return;
    }

    try {
      const rankRes = await axios.get(`/api/user/${currentUsername.value}/score/rank`);
      if (rankRes.data?.status === 'success') {
        userRank.value = rankRes.data.rank || 0;
      }
    } catch (err) {
      console.warn('Erreur lors du chargement du rank:', err);
    }

    try {
      const badgesRes = await axios.get(`/api/user/${currentUsername.value}/badge`);
      if (badgesRes.data?.status === 'success') {
        badges.value = badgesRes.data.badges || [];
      }
    } catch (err) {
      console.warn('Erreur lors du chargement des badges:', err);
    }

    try {
      const activitiesRes = await axios.get(`/api/user/${currentUsername.value}/score/recent`);
      if (activitiesRes.data?.status === 'success') {
        recentActivities.value = activitiesRes.data.history || [];
      }
    } catch (err) {
      console.warn('Erreur lors du chargement des activités récentes:', err);
    }

    let historyData = [];
    try {
      const HistoryRes = await axios.get(`/api/user/${currentUsername.value}/score/history`);
      if (HistoryRes.data?.status === 'success' && HistoryRes.data?.history) {
        historyData = HistoryRes.data.history;
        updateProgressionChart(historyData);
      }

      // 1. Récupération dynamique de toutes les catégories du système
      try {
        const catListRes = await axios.get('/api/user/challenge/category/list');
        if (catListRes.data?.status === 'success') {
          globalCategories.value = catListRes.data.categories || [];
        }
      } catch (catErr) {
        console.warn('Erreur lors du chargement des catégories système:', catErr);
      }

      // 2. Récupération de tes statistiques personnelles
      const statsRes = await axios.get(`/api/user/${currentUsername.value}/challenge/statistics`);
      if (statsRes.data?.status === 'success' && statsRes.data?.statistics) {
        categoryStats.value = statsRes.data.statistics.category_stats || {};
        difficultyStats.value = statsRes.data.statistics.difficulty_stats || {};

        // Calcul automatique et dynamique du nombre total de challenges résolus
        solveCount.value = Object.values(categoryStats.value).reduce((sum, val) => sum + Number(val), 0);
      }

      // Conserve la simulation des machines
      machineCount.value = Math.floor(Math.random() * 20) + 3;

    } catch (err) {
      console.warn('Erreur lors du chargement des stats:', err);
    }

    setTimeout(() => {
      initializeCharts();
      // On passe l'historique complet pour calculer les points de la heatmap
      initializeHeatmap(historyData);
    }, 100);

  } catch (err) {
    console.error('Erreur lors du chargement du profil:', err);

    if (err.response?.status === 401) {
      error.value = 'Vous devez être connecté pour voir votre profil.';
      setTimeout(() => router.push('/login'), 2000);
      return;
    }

    error.value = err.response?.data?.message || err.message || 'Erreur lors du chargement du profil.';
  } finally {
    loading.value = false;
  }
};

// -- INITIALIZE CHARTS --
const initializeCharts = () => {
  Chart.defaults.color = '#9ca3af';
  Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.08)';
  Chart.defaults.font.family = 'monospace';

  // 1. Progression Chart
  const ctxLine = document.getElementById('progressionChart');
  if (ctxLine) {
    if (progressionChart && typeof progressionChart.destroy === 'function') {
      progressionChart.destroy();
    }
    progressionChart = new Chart(ctxLine, {
      type: 'line',
      data: {
        datasets: [{
          label: 'Score global',
          data: [],
          borderColor: '#ff4444',
          backgroundColor: 'rgba(255, 68, 68, 0.06)',
          borderWidth: 3,
          fill: true,
          tension: 0.1,
          pointBackgroundColor: '#ffffff',
          pointHoverRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          zoom: {
            zoom: { wheel: { enabled: false }, pinch: { enabled: false } },
            pan: { enabled: false }
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            borderColor: '#d4a500',
            borderWidth: 1,
            padding: 10,
            titleColor: '#d4a500',
            bodyColor: '#ffffff',
            callbacks: {
              title: function (context) {
                if (context.length > 0) {
                  const date = context[0].raw.x;
                  return date.toLocaleDateString('fr-FR', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  });
                }
                return '';
              },
              label: function (context) {
                return `Score: ${context.raw.y}`;
              },
              afterLabel: function (context) {
                let text = `Raison: ${context.raw.reason}`;
                if (context.raw.change !== null && context.raw.change !== undefined) {
                  text += `\n+${context.raw.change} pts`;
                }
                return text;
              }
            }
          }
        },
        scales: {
          y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, beginAtZero: true },
          x: {
            type: 'time',
            time: {
              isoWeekday: true,
              displayFormats: {
                hour: 'HH:mm',
                day: 'dd MMM',
                month: 'MMM yyyy'
              }
            },
            grid: { display: false },
            ticks: { color: 'rgba(255, 255, 255, 0.6)', font: { family: 'monospace' } }
          }
        }
      }
    });

    const scrollArea = document.getElementById('chart-scroll-area');
    if (scrollArea) {
      scrollArea.addEventListener('wheel', (event) => {
        event.preventDefault();
        if (progressionChart) {
          const isZoomIn = event.deltaY < 0;
          handleWheelZoomSteps(progressionChart, isZoomIn);
        }
      }, { passive: false });
    }
  }

  // 2. Category Chart (Radar)
  // 2. Category Chart (Radar) - VERSION TOILE D'ARAIGNÉE 100% DYNAMIQUE
  const ctxRadar = document.getElementById('categoryChart');
  if (ctxRadar) {
    if (categoryChart && typeof categoryChart.destroy === 'function') {
      categoryChart.destroy();
    }

    // Extraction dynamique des noms des catégories depuis l'API globale
    // Si l'API est vide, on garde tes catégories de base en secours (fallback)
    const categoriesToUse = globalCategories.value.length > 0
      ? globalCategories.value.map(c => c.name)
      : ['WEB', 'REVERSE', 'FORENSIC', 'CRYPTO', 'PWN', 'OSINT'];

    // Association de tes scores utilisateur à chaque catégorie existante
    const catData = categoriesToUse.map(catName => {
      const matchKey = Object.keys(categoryStats.value).find(k => k.toUpperCase() === catName.toUpperCase());
      return matchKey ? Number(categoryStats.value[matchKey]) : 0;
    });

    // Formatage propre pour l'affichage (ex: OSINT -> Osint, WEB -> Web)
    const catLabels = categoriesToUse.map(catName => catName.charAt(0).toUpperCase() + catName.slice(1).toLowerCase());

    // CALCUL DU MAX : Trouve le score le plus élevé parmi toutes tes catégories
    const maxSolved = Math.max(...catData, 0);
    const dynamicSuggestedMax = maxSolved > 0 ? maxSolved : 5; // Si 0 challenge fait, met un plafond à 5 par défaut

    categoryChart = new Chart(ctxRadar, {
      type: 'radar',
      data: {
        labels: catLabels,
        datasets: [{
          data: catData,
          backgroundColor: 'rgba(212, 165, 0, 0.15)',
          borderColor: '#d4a500',
          borderWidth: 2,
          pointBackgroundColor: '#d4a500',
          pointBorderColor: '#fff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          r: {
            angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
            grid: { color: 'rgba(255, 255, 255, 0.1)' },
            pointLabels: { color: '#ffffff', font: { size: 11, weight: 'bold' } },
            ticks: { display: false },
            suggestedMin: 0,
            suggestedMax: dynamicSuggestedMax // <--- S'ADAPTE PARFAITEMENT AU MAX DU JOUEUR !
          }
        }
      }
    });
  }

  // 3. Difficulty Chart (Bar)
  const ctxBar = document.getElementById('difficultyChart');
  if (ctxBar) {
    if (difficultyChart && typeof difficultyChart.destroy === 'function') {
      difficultyChart.destroy();
    }

    // Mapping des clés de l'API avec l'ordre d'affichage du graphique
    const diffMapping = { 'INTRO': 0, 'EASY': 1, 'MEDIUM': 2, 'HARD': 3, 'INSANE': 4 };
    const diffData = [0, 0, 0, 0, 0]; // Correspond à [intro, Facile, Moyen, Difficile, Insane]

    Object.entries(difficultyStats.value).forEach(([key, val]) => {
      const upperKey = key.toUpperCase();
      if (diffMapping[upperKey] !== undefined) {
        diffData[diffMapping[upperKey]] = Number(val);
      }
    });

    difficultyChart = new Chart(ctxBar, {
      type: 'bar',
      data: {
        labels: ['intro', 'Facile', 'Moyen', 'Difficile', 'Insane'],
        datasets: [{
          data: diffData, // Utilise les vraies valeurs triées
          backgroundColor: [
            'rgba(255, 255, 255, 0.75)',
            'rgba(0, 255, 27, 0.75)',
            'rgba(255, 138, 0, 0.75)',
            'rgba(255, 0, 0, 0.75)',
            'rgba(239, 0, 255, 0.75)'
          ],
          borderColor: ['#ffffff', '#00ff14', '#ff8a00', '#ff0000', '#ef00ff'],
          borderWidth: 1,
          borderRadius: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, beginAtZero: true },
          x: { grid: { display: false } }
        }
      }
    });
  }
};

// -- INITIALIZE HEATMAP (APEXCHARTS - SÉCURITÉ MAXIMALE & SANS BUG) --
const initializeHeatmap = (history = []) => {

  const renderChart = () => {
    const heatmapContainer = document.getElementById('heatmap');

    // Si la page charge encore, on attend un peu pour éviter le "Nœud introuvable"
    if (!heatmapContainer) {
      setTimeout(renderChart, 50);
      return;
    }

    // 1. TRI CHRONOLOGIQUE SÉCURISÉ
    const safeHistory = Array.isArray(history) ? [...history] : [];

    const getSafeDate = (rawDate) => {
      if (!rawDate) return new Date();
      let d = parseTimestamp(rawDate);
      if (isNaN(d.getTime()) && typeof rawDate === 'string') {
        d = new Date(rawDate.replace(' ', 'T'));
      }
      return isNaN(d.getTime()) ? new Date() : d;
    };

    safeHistory.sort((a, b) => {
      const rawA = a.timestamp || a.submitted_at || a.date;
      const rawB = b.timestamp || b.submitted_at || b.date;
      return getSafeDate(rawA) - getSafeDate(rawB);
    });

    const getLocalYYYYMMDD = (dateObj) => {
      const y = dateObj.getFullYear();
      const m = String(dateObj.getMonth() + 1).padStart(2, '0');
      const d = String(dateObj.getDate()).padStart(2, '0');
      return `${y}-${m}-${d}`;
    };

    // 2. CALCUL DES POINTS (100% NOMBRES)
    const dailyContributions = {};
    let previousScore = null;

    safeHistory.forEach((event) => {
      const rawDate = event.timestamp || event.submitted_at || event.date;
      if (!rawDate) return;

      const dateObj = getSafeDate(rawDate);
      const dateKey = getLocalYYYYMMDD(dateObj);
      let pointsGained = 0;

      const currentScore = Number(event.score_total);
      const changeScore = Number(event.change);

      if (previousScore === null) {
        if (!isNaN(changeScore) && changeScore > 0) pointsGained = changeScore;
        previousScore = isNaN(currentScore) ? 0 : currentScore;
      } else {
        if (!isNaN(currentScore)) {
          pointsGained = Math.max(0, currentScore - previousScore);
          previousScore = currentScore;
        } else if (!isNaN(changeScore)) {
          pointsGained = changeScore;
        }
      }

      if (pointsGained > 0) {
        dailyContributions[dateKey] = (dailyContributions[dateKey] || 0) + pointsGained;
      }
      if (dailyContributions[dateKey] >= 750) {
      }
    });

    // 3. GRILLE DE 371 JOURS
    const today = new Date();
    const dow = today.getDay();
    const daysToSunday = dow === 0 ? 0 : 7 - dow;

    const endDate = new Date(today);
    endDate.setDate(today.getDate() + daysToSunday);

    const startDate = new Date(endDate);
    startDate.setDate(endDate.getDate() - 370);

    const allDays = [];
    let cursor = new Date(startDate);

    while (cursor <= endDate) {
      const dateKey = getLocalYYYYMMDD(cursor);
      const finalValue = Number(dailyContributions[dateKey]) || 0;
      allDays.push({
        date: new Date(cursor),
        value: isNaN(finalValue) ? 0 : finalValue
      });
      cursor.setDate(cursor.getDate() + 1);
    }

    // 4. REGROUPEMENT PAR SEMAINES
    const weeks = [];
    for (let i = 0; i < allDays.length; i += 7) {
      weeks.push(allDays.slice(i, i + 7));
    }

    const dayLabelsOrdered = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'];
    const dayLabelsDisplay = [...dayLabelsOrdered].reverse();

    const series = dayLabelsDisplay.map((dayName) => {
      const physicalIndex = dayLabelsOrdered.indexOf(dayName);
      return {
        name: dayName,
        data: weeks.map((week, weekIndex) => {
          const entry = week[physicalIndex];
          const safeY = (entry && !isNaN(Number(entry.value))) ? Number(entry.value) : 0;
          if (safeY >= 750) {
          }
          return { x: `w${weekIndex}`, y: safeY, date: entry ? entry.date : null };
        })
      };
    });

    const monthLabels = [];
    weeks.forEach((week, weekIndex) => {
      const firstDay = week[0]?.date;
      if (!firstDay) return;
      const monthName = firstDay.toLocaleDateString('fr-FR', { month: 'short' });
      const prevFirstDay = weeks[weekIndex - 1]?.[0]?.date;
      const prevMonthName = prevFirstDay ? prevFirstDay.toLocaleDateString('fr-FR', { month: 'short' }) : null;
      if (monthName !== prevMonthName) {
        const daysInNewMonth = week.filter(d => d && d.date.toLocaleDateString('fr-FR', { month: 'short' }) === monthName).length;
        const targetIndex = daysInNewMonth < 4 ? weekIndex + 1 : weekIndex;
        monthLabels.push({ index: targetIndex, label: monthName });
      }
    });

    if (heatmapContainer._apexchart) {
      heatmapContainer._apexchart.destroy();
    }

    const currentTheme = document.documentElement.getAttribute('data-theme') || '';
    const isDark = !['light', 'cupcake', 'bumblebee', 'emerald', 'corporate', 'retro', 'cyberpunk', 'valentine', 'garden', 'lofi', 'pastel', 'fantasy', 'wireframe', 'cmyk', 'autumn', 'acid', 'lemonade'].includes(currentTheme);
    const textColor = isDark ? '#af9caaff' : '#57606a';

    // COULEURS HEXADÉCIMALES (Interdit d'utiliser rgba sinon ApexCharts affiche du noir)
    const emptyColor = isDark ? '#2a2a2a' : '#ebedf0';
    const level1Color = '#806400';
    const level2Color = '#d4a500';
    const level3Color = '#ff8c00';
    const level4Color = '#ff4444';

    const options = {
      chart: { type: 'heatmap', height: 230, toolbar: { show: false }, animations: { enabled: false }, background: 'transparent' },
      grid: { show: false, padding: { top: 0, right: 10, bottom: 0, left: 42 } },

      // --- C'EST ICI QUE TOUT SE JOUE ---
      plotOptions: {
        heatmap: {
          enableShades: false, // Désactive les ombres noires automatiques d'ApexCharts
          radius: 2,
          useFillColorAsStroke: false,
          colorScale: {
            ranges: [
              { from: -1, to: 0, name: 'Aucune activité', color: emptyColor },
              { from: 1, to: 149, name: 'Peu', color: level1Color },
              { from: 150, to: 449, name: 'Modéré', color: level2Color }, // CORRIGÉ : Évite le chevauchement avec 450
              { from: 450, to: 749, name: 'Actif', color: level3Color },
              { from: 750, to: 9999999, name: 'Très actif', color: level4Color },
            ]
          }
        }
      },
      // ----------------------------------

      dataLabels: { enabled: false },
      stroke: { width: 2, colors: [isDark ? '#1d232a' : '#ffffff'] },
      xaxis: {
        type: 'category', position: 'top', categories: weeks.map((_, i) => `w${i}`),
        labels: {
          rotate: 0, style: { fontSize: '12px', colors: textColor, fontFamily: 'monospace' },
          formatter: (val) => {
            if (val === undefined || val === null) return '\u200B';
            const strVal = String(val);
            if (!strVal.startsWith('w')) return '\u200B';
            const weekIndex = parseInt(strVal.replace('w', ''), 10);
            if (isNaN(weekIndex)) return '\u200B';

            const found = monthLabels.find(m => m.index === weekIndex);
            return found ? found.label : '\u200B';
          }
        },
        axisBorder: { show: false }, axisTicks: { show: false }, tooltip: { enabled: false },
      },
      yaxis: { labels: { show: true, style: { fontSize: '13px', colors: textColor, fontFamily: 'monospace' }, minWidth: 42, maxWidth: 48 } },
      tooltip: {
        theme: isDark ? 'dark' : 'light',
        x: { show: false },
        y: {
          formatter: (val, { dataPointIndex, seriesIndex, w }) => {
            const point = w.config.series[seriesIndex]?.data[dataPointIndex];
            if (!point?.date) return `${val} points`;
            const dateStr = point.date.toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
            return val === 0 ? `Aucun point gagné — ${dateStr}` : `${val} points gagnés — ${dateStr}`;
          }
        }
      },
      legend: {
        show: true, position: 'bottom', horizontalAlign: 'right', markers: { size: 10, strokeWidth: 0, radius: 2 },
        labels: { colors: textColor },
        formatter: (name) => {
          if (name === 'Aucune activité') return 'Moins';
          if (name === 'Très actif') return 'Plus';
          return '\u200B';
        }
      },
      states: { hover: { filter: { type: 'darken', value: 0.15 } } },
      theme: { mode: isDark ? 'dark' : 'light' },
      series: series,
    };
    const chart = new ApexCharts(heatmapContainer, options);
    chart.render();
    heatmapContainer._apexchart = chart;

    // J'AI SUPPRIMÉ isLoadingHeatmap.value = false; ICI !
  };

  renderChart();
};


// ==================== LOGIQUE MODALE COSMÉTIQUES ====================
const cosmeticModal = ref(false)
const cosmeticTab = ref('avatar')

// Previews
const avatarPreview = ref(null)
const bannerPreview = ref(null)

// Galerie disponible
const availableAvatars = ref([])
const availableBanners = ref([])
const avatarsLoading = ref(false)
const bannersLoading = ref(false)

// Sélection en cours
const selectedAvatar = ref(null)
const selectedBanner = ref(null)

const cosmeticSuccess = ref(false)
const cosmeticSaving = ref(false)

const openCosmeticModal = async () => {
  cosmeticModal.value = true
  cosmeticTab.value = 'avatar'

  await fetchAvailableCosmetics()

  // On pré-sélectionne ce que l'utilisateur a déjà
  const currentAvatar = availableAvatars.value.find(c => c.id === profile.value.avatar_id)
  const currentBanner = availableBanners.value.find(c => c.id === profile.value.banner_id)

  selectedAvatar.value = currentAvatar || null
  avatarPreview.value = currentAvatar || null

  selectedBanner.value = currentBanner || null
  bannerPreview.value = currentBanner || null
}

const fetchAvailableCosmetics = async () => {
  avatarsLoading.value = true
  bannersLoading.value = true
  try {
    const [resCosmetics] = await Promise.all([
      axios.get('/api/user/cosmetic/list').catch(() => ({ data: { cosmetics: [] } }))
    ])
    availableAvatars.value = resCosmetics.data?.cosmetics.avatar_list || []
    availableBanners.value = resCosmetics.data?.cosmetics.banner_list || []
  } catch (error) {
    console.error("Erreur lors de la récupération des cosmétiques:", error)
    availableAvatars.value = []
    availableBanners.value = []
  } finally {
    avatarsLoading.value = false
    bannersLoading.value = false
  }
}

const selectGalleryAvatar = (cosmetic) => {
  selectedAvatar.value = cosmetic
  avatarPreview.value = cosmetic
}

const selectGalleryBanner = (cosmetic) => {
  selectedBanner.value = cosmetic
  bannerPreview.value = cosmetic
}


const saveCosmetics = async () => {
  cosmeticSaving.value = true
  try {
    if (selectedAvatar.value && selectedAvatar.value.id !== profile.value.avatar) {
      await axios.post('/api/user/update/cosmetic', { new_cosmetic_id: selectedAvatar.value.id })
      profile.value.avatar = selectedAvatar.value.id
      profile.value.avatar_url = selectedAvatar.value.icon_url
      profile.value.avatar_id = selectedAvatar.value.id
    }
    if (selectedBanner.value && selectedBanner.value.id !== profile.value.banner) {
      await axios.post('/api/user/update/cosmetic', { new_cosmetic_id: selectedBanner.value.id })
      profile.value.banner = selectedBanner.value.id
      profile.value.banner_url = selectedBanner.value.icon_url
      profile.value.banner_id = selectedBanner.value.id
    }
    if (window.refreshGlobalAvatar) {
      window.refreshGlobalAvatar()
    }
    cosmeticSuccess.value = true
    setTimeout(() => {
      cosmeticSuccess.value = false
    }, 1500)
  } catch (e) {
    console.error("Erreur lors de la sauvegarde des cosmétiques:", e)
    alert(e.response?.data?.message || 'Erreur lors de la sauvegarde. Veuillez réessayer.')
  } finally {
    cosmeticSaving.value = false
  }
}

// -- LIFECYCLE --
onMounted(async () => {
  await loadProfile();
});

watch(() => route.params.username, () => {
  loadProfile()
});

</script>

<style scoped>
/* Configuration des variables de couleur pour la Heatmap */
:root {
  /* Modifie ces variables si tu utilises des couleurs DaisyUI (ex: var(--b1), var(--su)) */
  --heatmap-empty: #2a2a2a;
  --heatmap-level1: rgba(212, 165, 0, 0.4);
  /* Peu - Or avec opacité */
  --heatmap-level2: #d4a500;
  /* Modéré - Or plein */
  --heatmap-level3: #ff8c00;
  /* Actif - Orange */
  --heatmap-level4: #ff4444;
  /* Très actif - Rouge */
  --heatmap-text: #9ca3af;
  /* Texte (Mois/Jours) */
  --heatmap-stroke: transparent;
  /* Contour des blocs */
}

/* Masquer la barre de défilement pour la heatmap */
.no-scrollbar::-webkit-scrollbar {
  display: none;
}

.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

:deep(.apexcharts-svg) {
  background: transparent !important;
}

:deep(.apexcharts-series.apexcharts-heatmap-series rect) {
  stroke: var(--heatmap-stroke) !important;
  stroke-width: 2 !important;
}

.binary-scroll {
  /* Fait défiler le texte en continu de manière fluide */
  animation: scrollBinary 200s linear infinite;
}

@keyframes scrollBinary {
  0% {
    transform: translateX(0);
  }

  100% {
    /* Le texte est tellement long grâce au .repeat(30) qu'on peut le décaler sans voir la fin */
    transform: translateX(-30%);
  }
}
</style>