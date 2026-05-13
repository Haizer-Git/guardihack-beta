<script setup>
</script>

<template>
  <div class="w-full animate-fade-in pb-20 px-4 max-w-4xl mx-auto">

    <div class="mb-10">
      <h1 class="block w-full text-center text-3xl font-cyber font-bold bg-primary text-base-100 py-3 uppercase tracking-widest shadow-sm">
        Règles et Conditions
      </h1>
    </div>

    <div class="space-y-8">

      <!-- SECTION 1 -->
      <div class="card bg-base-200/50 border border-base-300">
        <div class="card-body">
          <h2 class="card-title text-2xl font-cyber">🎯 Objectif</h2>
          <p class="text-base-content/80 leading-relaxed">
            GuardiHack est une compétition de capture de drapeaux (CTF) dédiée à l'apprentissage de la cybersécurité. 
            Les participants doivent résoudre des défis de sécurité pour obtenir des points et grimper au classement.
          </p>
        </div>
      </div>

      <!-- SECTION 2 -->
      <div class="card bg-base-200/50 border border-base-300">
        <div class="card-body">
          <h2 class="card-title text-2xl font-cyber">✅ Conduites Autorisées</h2>
          <ul class="list-disc list-inside space-y-2 text-base-content/80">
            <li>Utiliser des outils de pentesting (nmap, metasploit, burp suite, etc.)</li>
            <li>Partager des techniques avec votre équipe</li>
            <li>Consulter des ressources externes et des tutoriels</li>
            <li>Demander de l'aide aux modérateurs pour les questions techniques</li>
            <li>Participer à des sessions de formation en direct</li>
          </ul>
        </div>
      </div>

      <!-- SECTION 3 -->
      <div class="card bg-base-200/50 border border-error/30">
        <div class="card-body">
          <h2 class="card-title text-2xl font-cyber text-error">❌ Conduites Interdites</h2>
          <ul class="list-disc list-inside space-y-2 text-base-content/80">
            <li><strong>Brute force excessif</strong> : Attaques DOS sur les serveurs</li>
            <li><strong>Cheating</strong> : Utiliser des solutions d'autres équipes</li>
            <li><strong>Langage abusif</strong> : Harcèlement ou insultes envers d'autres participants</li>
            <li><strong>Modification de l'infrastructure</strong> : Tentatives d'accès à d'autres serveurs</li>
            <li><strong>Partage de flags</strong> : Les solutions ne doivent pas être publiées pendant la compétition</li>
            <li><strong>Utilisation d'outils automatisés excessifs</strong> : SQLmap en mode agressif, par exemple</li>
          </ul>
        </div>
      </div>

      <!-- SECTION 4 -->
      <div class="card bg-base-200/50 border border-base-300">
        <div class="card-body">
          <h2 class="card-title text-2xl font-cyber">🏆 Système de Points</h2>
          <div class="overflow-x-auto">
            <table class="table w-full">
              <thead>
                <tr>
                  <th>Type de Challenge</th>
                  <th>Points</th>
                  <th>Ajustement</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>Route (Questions)</strong></td>
                  <td>1-5 pts</td>
                  <td>Fixe</td>
                </tr>
                <tr>
                  <td><strong>Jeopardy</strong></td>
                  <td>Var. (100-500)</td>
                  <td>Diminue avec les résolutions</td>
                </tr>
                <tr>
                  <td><strong>Machine</strong></td>
                  <td>Variable</td>
                  <td>Basé sur la complexité</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- SECTION 5 -->
      <div class="card bg-base-200/50 border border-base-300">
        <div class="card-body">
          <h2 class="card-title text-2xl font-cyber">⏱️ Horaires et Durée</h2>
          <ul class="list-disc list-inside space-y-2 text-base-content/80">
            <li><strong>Durée totale</strong> : 24 heures</li>
            <li><strong>Début</strong> : 2026-04-21 à 09:00</li>
            <li><strong>Fin</strong> : 2026-04-22 à 09:00</li>
            <li><strong>Ouverture des flags</strong> : 48h après fermeture pour post-mortem</li>
          </ul>
        </div>
      </div>

      <!-- SECTION 6 -->
      <div class="card bg-base-200/50 border border-base-300">
        <div class="card-body">
          <h2 class="card-title text-2xl font-cyber">🚨 Sanctions</h2>
          <div class="space-y-3 text-base-content/80">
            <p><strong>Avertissement</strong> : Pour les violations mineures (brute force léger, langage inapproprié)</p>
            <p><strong>Disqualification temporaire</strong> : 24h pour cheating confirmé</p>
            <p><strong>Disqualification permanente</strong> : Pour harcèlement ou modifications d'infrastructure</p>
            <p><strong>Perte de points</strong> : Déduction de 50% des points si collaborations non autorisées détectées</p>
          </div>
        </div>
      </div>

      <!-- SECTION 7 -->
      <div class="card bg-base-200/50 border border-base-300">
        <div class="card-body">
          <h2 class="card-title text-2xl font-cyber">📞 Support et Modération</h2>
          <ul class="list-disc list-inside space-y-2 text-base-content/80">
            <li>Une équipe de modérateurs est disponible 24/7</li>
            <li>Utilisez le chat de support pour signaler des problèmes techniques</li>
            <li>Signaler les comportements suspects via la page "Report"</li>
            <li>Les décisions d'arbitrage sont finales mais peuvent être contestées par email</li>
          </ul>
        </div>
      </div>

      <!-- ACCEPTATION -->
      <div class="card bg-primary/10 border-2 border-primary">
        <div class="card-body items-center text-center">
          <p class="text-lg font-bold">
            En participant à GuardiHack, vous acceptez ces règles et conditions.
          </p>
          <p class="text-sm opacity-70 mt-2">
            Amusez-vous bien et apprenez beaucoup! 🎮🔐
          </p>
          <router-link to="/" class="btn btn-primary btn-sm mt-6 font-cyber">
            Retour à l'Accueil
          </router-link>
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
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
