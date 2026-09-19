<script setup>
import { useRouter } from 'vue-router'
import PageTitle from '../../components/PageTitle.vue'

const router = useRouter()

// Fonction pour gérer la navigation
const selectProfile = (routeName) => {
    router.push(routeName)
}
</script>

<template>
    <PageTitle text="Changer de profil" />
    <div class="flex flex-col items-center p-6 overflow-hidden font-text text-base-content">

        <div class="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/5 via-base-300 to-base-300 pointer-events-none"></div>

        <div class="relative z-10 w-full max-w-4xl animate-fade-in">

            <!-- En-tête -->
            <div class="text-center mb-16">
                <h1 class="text-3xl md:text-5xl font-titre mb-4 text-primary">
                    Sélectionner le profil
                </h1>
                <p class="text-base-content/60 font-text text-sl md:text-base mx-auto">
                    <!-- text-base-content/60 font-text text-sm md:text-base max-w-lg mx-auto -->
                    Choisissez la plateforme à laquelle vous souhaitez accéder avec votre compte Guardia.
                </p>
            </div>

            <!-- Grille des profils -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <!-- grid grid-cols-1 md:grid-cols-2 gap-8 -->

                <!-- Box 1 : GuardiHack -->
                <div @click="selectProfile('/')" class="bg-base-100 backdrop-blur-sm rounded-xl p-8 border border-base-content/10 shadow-lg cursor-pointer transition-all duration-300 hover:-translate-y-1 hover:border-primary/50 hover:shadow-[0_0_20px_rgba(var(--p),0.15)] group relative overflow-hidden">
                    <!-- Décoration d'angle -->
                    <div class="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-bl-full -z-10 group-hover:bg-primary/10">
                    </div>
                    <!-- transition-colors duration-500 -->

                    <!-- Icône -->
                    <!-- Icône / Logo GuardiHack -->
                    <div
                        class="w-14 h-14 rounded-lg bg-base-200 border border-base-content/10 flex items-center justify-center mb-6 group-hover:border-primary/30 transition-all p-2">
                        <img src="../../assets/Logo Guardihack2.png" alt="Logo GuardiHack"
                            class="w-full h-full object-contain opacity-80 group-hover:opacity-100 group-hover:scale-110 transition-all duration-300" />
                    </div>

                    <h2 class="text-2xl font-bold mb-2 font-titre tracking-wide">GuardiHack</h2>
                    <!-- text-2xl font-bold mb-2 font-titre tracking-wide -->

                    <p class="text-base-content/60 text-sm font-text mb-8 min-h-[60px]">
                        <!-- text-base-content/60 text-sm font-text mb-8 min-h-[60px] -->
                        L'environnement principal de CTF et de Cyber Challenges. Validez vos flags et grimpez dans le
                        classement.
                    </p>

                    <div
                        class="flex items-center text-primary font-code text-sm font-bold group-hover:translate-x-2 transition-transform">
                        <span>Accéder à la plateforme</span>
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-2" fill="none" viewBox="0 0 24 24"
                            stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M14 5l7 7m0 0l-7 7m7-7H3" />
                        </svg>
                    </div>
                </div>

                <!-- Box 2 : GuardiHack Pool -->
                <div @click="selectProfile('/pool')"
                    class="bg-base-100 backdrop-blur-sm rounded-xl p-8 border border-base-content/10 shadow-lg cursor-pointer transition-all duration-300 hover:-translate-y-1 hover:border-secondary/50 hover:shadow-[0_0_20px_rgba(var(--s),0.15)] group relative overflow-hidden">
                    <!-- bg-base-100 backdrop-blur-sm rounded-xl p-8 border border-base-content/10 shadow-lg cursor-pointer transition-all duration-300 hover:-translate-y-1 hover:border-secondary/50 hover:shadow-[0_0_20px_rgba(var(--s),0.15)] group relative overflow-hidden -->
                    <!-- Décoration d'angle -->
                    <div
                        class="absolute top-0 right-0 w-32 h-32 bg-secondary/5 rounded-bl-full -z-10 group-hover:bg-secondary/10 transition-colors duration-500">
                    </div>

                    <!-- Icône -->
                    <div
                        class="w-14 h-14 rounded-lg bg-base-200 border border-base-content/10 flex items-center justify-center mb-6 group-hover:border-primary/30 transition-all p-2">
                        <img src=".../../assets/Logo Guardihack2.png" alt="Logo GuardiHack"
                            class="w-full h-full object-contain opacity-80 group-hover:opacity-100 group-hover:scale-110 transition-all duration-300" />
                    </div>

                    <h2 class="text-2xl font-bold mb-2 font-titre tracking-wide">
                        GuardiHack Pool
                        <span
                            class="text-[10px] font-code bg-base-200 text-base-content/50 border border-base-content/10 px-2 py-0.5 rounded uppercase tracking-wider">
                            En dev
                        </span>
                    </h2>

                    <p class="text-base-content/60 text-sm font-text mb-8 min-h-[60px]">
                        <!-- text-base-content/60 text-sm font-text mb-8 min-h-[60px] -->
                        L'environnement d'entraînement intensif. Plongez dans les fondamentaux lors des sessions
                        piscines.
                    </p>

                    <div
                        class="flex items-center text-secondary font-code text-sm font-bold group-hover:translate-x-2 transition-transform">
                        <!-- flex items-center text-secondary font-code text-sm font-bold group-hover:translate-x-2 transition-transform -->
                        <span>Plonger dans le code</span>
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-2" fill="none" viewBox="0 0 24 24"
                            stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M14 5l7 7m0 0l-7 7m7-7H3" />
                        </svg>
                    </div>
                </div>

            </div>
        </div>
    </div>
</template>