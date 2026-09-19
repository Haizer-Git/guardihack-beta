<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
</script>
<template>
  <svg style="position: absolute; width: 0; height: 0;">
    <filter width="3000%" x="-1000%" height="3000%" y="-1000%" id="unopaq">
      <feColorMatrix values="1 0 0 0 0 
                0 1 0 0 0 
                0 0 1 0 0 
                0 0 0 3 0"></feColorMatrix>
    </filter>
  </svg>
  <div class="w-full animate-fade-in z-10">
    <section class="min-h-[75vh] flex flex-col items-center justify-center overflow-hidden px-4">
      <div class="relative z-10 flex flex-col items-center gap-6 text-center max-w-3xl">
        <img src="../../assets/V2.2-Sombre.png" alt="Logo GuardiHack"
          class=" h-auto w-auto object-contain mix-blend-screen drop-shadow-[0_0_35px_rgba(var(--p),0.3)]"
          style="animation-duration: 4s;" />
        <h1 class="text-6xl md:text-8xl font-black tracking-tighter font-titre uppercase">
          GuardiHack
        </h1>
        <div
          class="flex flex-wrap justify-center gap-2 text-xs font-stitre px-3 py-1.5 border border-primary/20 bg-primary/5 text-primary tracking-widest uppercase">
          <span>📍 Paris</span> • <span>📍 Lyon</span> • <span>📍 Bordeaux</span>
        </div>
        <p class="text-base md:text-lg text-base-content/70 font-text leading-relaxed">
          La plateforme d'entraînement de type <span class="text-primary font-bold">CTF & Cyber Challenges</span>
          exclusive et réservée aux étudiants de la <span class="text-white font-semibold">Guardia Cybersecurity
            School</span>.
        </p>
        <div class="mt-8 relative group">
          <button @click="router.push('/rules')" class="custom-cyber-btn">
            <div class="a l"></div>
            <div class="a r"></div>
            <div class="a t"></div>
            <div class="a b"></div>
            <span class="text font-titre tracking-[0.2em] uppercase font-bold text-xs">Explorer</span>
          </button>
        </div>
      </div>
    </section>
    <section class="py-20 px-6 bg-base-200/40 backdrop-blur-md border border-base-300">
      <div class="max-w-6xl mx-auto">
        <div class="text-center mb-16">
          <h2
            class="inline-block bg-primary text-base-100 text-2xl md:text-3xl font-black uppercase tracking-widest font-titre px-8 py-2">
            <span class="inline-block">À propos</span>
          </h2>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div
            class="bg-base-300/70 backdrop-blur-sm rounded-xl p-8 border border-base-100 shadow-xl transition-all duration-300 hover:-translate-y-1 hover:border-primary/30 group">
            <div
              class="w-10 h-10 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center mb-5 text-primary group-hover:bg-primary group-hover:text-base-100 transition-colors">
              <span class="font-code font-bold text-sm">01</span>
            </div>
            <h3 class="text-xl font-bold text-white mb-3">Entraînement Non-Stop</h3>
            <p class="text-base-content/60 text-sm leading-relaxed font-text">
              Résous des dizaines de challenges conçus pour tester tes limites. Du Forensic au Web, en passant par la
              Crypto et le Reverse engineering, affine tes compétences d'analyste et de hacker éthique.
            </p>
          </div>
          <div
            class="bg-base-300/70 backdrop-blur-sm rounded-xl p-8 border border-base-100 shadow-xl transition-all duration-300 hover:-translate-y-1 hover:border-primary/30 group">
            <div
              class="w-10 h-10 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center mb-5 text-primary group-hover:bg-primary group-hover:text-base-100 transition-colors">
              <span class="font-code font-bold text-sm">02</span>
            </div>
            <h3 class="text-xl font-bold text-white mb-3">Exclusivité Guardia</h3>
            <p class="text-base-content/60 text-sm leading-relaxed font-text">
              Un espace d'émulation unique dédié uniquement aux futurs experts de Guardia. Connecte-toi avec ton compte
              étudiant et mesure-toi aux talents des campus de Paris, Lyon et Bordeaux.
            </p>
          </div>
          <div
            class="bg-base-300/70 backdrop-blur-sm rounded-xl p-8 border border-base-100 shadow-xl transition-all duration-300 hover:-translate-y-1 hover:border-primary/30 group">
            <div
              class="w-10 h-10 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center mb-5 text-primary group-hover:bg-primary group-hover:text-base-100 transition-colors">
              <span class="font-code font-bold text-sm">03</span>
            </div>
            <h3 class="text-xl font-bold text-white mb-3">Gravis le Scoreboard</h3>
            <p class="text-base-content/60 text-sm leading-relaxed font-text">
              Chaque flag validé te rapporte des points. Suis ta progression en temps réel, grimpe dans le classement
              général de l'école et montre qui domine la matrice des campus.
            </p>
          </div>
        </div>
      </div>
    </section>

    <section class="py-20 px-6">
      <div class="max-w-6xl mx-auto">
        <div class="text-center mb-16">
          <h2
            class="inline-block bg-primary text-base-100 text-2xl md:text-3xl font-black uppercase tracking-widest font-titre px-8 py-2">
            <span class="inline-block">Les catégories</span>
          </h2>
        </div>
        <div class="grid grid-cols-2 lg:grid-cols-5 gap-4 text-center font-mono text-xs">
          <div class="p-6 bg-base-300/40 border border-base-200 hover:border-primary/20 transition-all">
            <div class="text-2xl mb-2">🌐</div>
            <div class="text-white font-bold font-text text-sm tracking-wider">WEB</div>
          </div>
          <div class="p-6 bg-base-300/40 border border-base-200 hover:border-primary/20 transition-all">
            <div class="text-2xl mb-2">🔎</div>
            <div class="text-white font-bold font-text text-sm tracking-wider">FORENSICS</div>
          </div>
          <div class="p-6 bg-base-300/40 border border-base-200 hover:border-primary/20 transition-all">
            <div class="text-2xl mb-2">🔐</div>
            <div class="text-white font-bold font-text text-sm tracking-wider">CRYPTOGRAPHY</div>
          </div>
          <div class="p-6 bg-base-300/40 border border-base-200 hover:border-primary/20 transition-all">
            <div class="text-2xl mb-2">⚙️</div>
            <div class="text-white font-bold font-text text-sm tracking-wider">REVERSE</div>
          </div>
          <div
            class="p-6 bg-base-300/40 border border-base-200 hover:border-primary/20 transition-all col-span-2 lg:col-span-1">
            <div class="text-2xl mb-2">💣</div>
            <div class="text-white font-bold font-text text-sm tracking-wider">PWN</div>
          </div>
        </div>
      </div>
    </section>
    <section class="py-20 px-6 bg-base-200/40 backdrop-blur-md border-y border-base-300">
      <div class="max-w-6xl mx-auto flex flex-col gap-20">
        <div>
          <h2 class="text-2xl md:text-3xl font-bold uppercase tracking-widest font-stitre text-white text-center mb-12">
            Avec le soutien de</h2>
          <div class="flex items-center justify-center gap-10 flex-wrap">
            <div
              class="w-32 h-16 bg-base-300/80 border border-base-100 rounded-xl flex items-center justify-center text-base-content/30 text-xs font-mono tracking-widest uppercase shadow-md grayscale hover:grayscale-0 hover:border-primary/30 transition-all duration-200">
              Guardia</div>
            <div
              class="w-32 h-16 bg-base-300/80 border border-base-100 rounded-xl flex items-center justify-center text-base-content/30 text-xs font-mono tracking-widest uppercase shadow-md grayscale hover:grayscale-0 hover:border-primary/30 transition-all duration-200">
              BDE Cyber</div>
          </div>
        </div>
        <div>
          <h2 class="text-2xl md:text-3xl font-bold uppercase tracking-widest font-stitre text-white text-center mb-12">
            Nos partenaires</h2>
          <div class="flex items-center justify-center gap-8 flex-wrap">
            <div
              class="w-28 h-14 bg-base-300/60 border border-base-200 rounded-xl flex items-center justify-center text-base-content/20 text-xs font-mono tracking-wider shadow-sm">
              Partenaire A</div>
            <div
              class="w-28 h-14 bg-base-300/60 border border-base-200 rounded-xl flex items-center justify-center text-base-content/20 text-xs font-mono tracking-wider shadow-sm">
              Partenaire B</div>
            <div
              class="w-28 h-14 bg-base-300/60 border border-base-200 rounded-xl flex items-center justify-center text-base-content/20 text-xs font-mono tracking-wider shadow-sm">
              Partenaire C</div>
          </div>
        </div>
      </div>
    </section>
    <section class="py-20 px-6">
      <div class="max-w-5xl mx-auto">
        <div class="text-center mb-16">
          <h2
            class="inline-block bg-primary text-base-100 text-2xl md:text-3xl font-black uppercase tracking-widest font-titre px-8 py-2">
            <span class="inline-block">L'équipe</span>
          </h2>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div
            class="flex items-center gap-5 bg-base-300/60 backdrop-blur-sm rounded-xl p-6 border border-base-200 shadow-lg transition-all duration-200 hover:-translate-y-0.5 hover:border-primary/30">
            <div
              class="w-16 h-16 rounded-lg bg-primary/10 border border-primary/30 flex items-center justify-center font-mono font-bold text-primary text-xl shadow-inner">
              HZ
            </div>
            <div class="flex flex-col gap-0.5">
              <p class="text-white font-bold text-base font-text tracking-wide">Haizer</p>
              <p class="text-primary font-mono text-xs uppercase tracking-widest">Core Developer</p>
            </div>
          </div>
          <div
            class="flex items-center gap-5 bg-base-300/60 backdrop-blur-sm rounded-xl p-6 border border-base-200 shadow-lg transition-all duration-200 hover:-translate-y-0.5 hover:border-primary/30">
            <div
              class="w-16 h-16 rounded-lg bg-primary/10 border border-primary/30 flex items-center justify-center font-mono font-bold text-primary text-xl shadow-inner">
              VX
            </div>
            <div class="flex flex-col gap-0.5">
              <p class="text-white font-bold text-base font-text tracking-wide">0xVexx</p>
              <p class="text-primary font-mono text-xs uppercase tracking-widest">Core Developer</p>
            </div>
          </div>
          <div
            class="flex items-center gap-5 bg-base-300/60 backdrop-blur-sm rounded-xl p-6 border border-base-200 shadow-lg transition-all duration-200 hover:-translate-y-0.5 hover:border-primary/30">
            <div
              class="w-16 h-16 rounded-lg bg-primary/10 border border-primary/30 flex items-center justify-center font-mono font-bold text-primary text-xl shadow-inner">
              DV
            </div>
            <div class="flex flex-col gap-0.5">
              <p class="text-white font-bold text-base font-text tracking-wide">David</p>
              <p class="text-primary font-mono text-xs uppercase tracking-widest">Core Developer</p>
            </div>
          </div>
        </div>
      </div>
    </section>
    <section class="py-20 px-6 bg-base-200/40 backdrop-blur-md border-t border-base-300">
      <div class="max-w-2xl mx-auto">
        <div class="text-center mb-16">
          <h2
            class="inline-block bg-primary text-base-100 text-2xl md:text-3xl font-black uppercase tracking-widest font-titre px-8 py-2">
            <span class="inline-block">Nous contacter</span>
          </h2>
        </div>
        <div
          class="bg-gradient-to-br from-base-300 via-base-300 to-base-200/40 rounded-xl border border-base-100 shadow-2xl p-1">
          <form @submit.prevent class="flex flex-col gap-4 bg-base-300/90 rounded-xl p-6 md:p-8">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <input type="text" placeholder="Nom / Pseudo"
                class="bg-base-100 border border-base-200 outline-none text-white px-4 py-3 text-sm font-mono rounded-lg transition-all duration-200 focus:border-primary/50 placeholder:text-neutral-500" />
              <input type="email" placeholder="Email étudiant"
                class="bg-base-100 border border-base-200 outline-none text-white px-4 py-3 text-sm font-mono rounded-lg transition-all duration-200 focus:border-primary/50 placeholder:text-neutral-500" />
            </div>
            <textarea rows="4" placeholder="Un bug ? Une suggestion de challenge ? Un flag cassé ?..."
              class="bg-base-100 border border-base-200 outline-none text-white px-4 py-3 text-sm font-mono rounded-lg resize-none transition-all duration-200 focus:border-primary/50 placeholder:text-neutral-500"></textarea>
            <button type="submit"
              class="self-end px-6 py-2.5 bg-primary text-base-100 font-mono text-xs tracking-widest uppercase font-bold rounded-md shadow-md transition-all duration-200 hover:opacity-90 hover:scale-[1.02] active:scale-[0.98]">
              🚀 Émettre le signal
            </button>
          </form>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.custom-cyber-btn {
  position: relative;
  cursor: pointer;
  border: none;
  width: 170px;
  height: 48px;
  background: #111111;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}
.text {
  position: relative;
  z-index: 1;
  transition: color 0.3s;
}
.custom-cyber-btn:hover .text {
  color: theme('colors.primary');
}
.custom-cyber-btn::before {
  content: "";
  position: absolute;
  inset: 0;
  opacity: 0;
  background: radial-gradient(circle at 50% 50%,
      #0000 0,
      #0000 20%,
      #111111aa 50%),
    radial-gradient(ellipse 100% 100%, #fff, #fff0);
  background-size: 3px 3px, auto auto;
  transition: 0.3s;
}
.custom-cyber-btn:hover::before {
  opacity: 0.2;
}
.a {
  pointer-events: none;
  position: absolute;
  --w: 2px;
  --t: -48px;
  --s: calc(var(--t) * -1);
  --e: calc(100% + var(--t));
  --g: #fff0, #fff3 var(--s), #fffa var(--s), #fff, #fffa var(--e),
    #fff3 var(--e), #fff0;
}
.a::before {
  content: "";
  position: absolute;
  inset: 0;
  background: inherit;
  filter: blur(4px) url(#unopaq);
  z-index: -2;
}
.a::after {
  content: "";
  position: absolute;
  inset: 0;
  background: inherit;
  filter: blur(10px) url(#unopaq);
  opacity: 0;
  z-index: -2;
  transition: 0.3s;
}
.custom-cyber-btn:hover .a::after {
  opacity: 1;
}
.l {
  left: -2px;
}
.r {
  background: linear-gradient(var(--g));
  top: var(--t);
  bottom: var(--t);
  width: var(--w);
  right: -2px;
}
.t {
  top: -2px;
}
.b {
  background: linear-gradient(90deg, var(--g));
  left: var(--t);
  right: var(--t);
  height: var(--w);
    bottom: -2px;
}
</style>