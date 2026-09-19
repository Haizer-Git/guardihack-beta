<template>
  <div class="w-full animate-fade-in pb-20 px-4 max-w-[1200px] mx-auto">
    <div class="reglement-container">
      
      <div class="reglement-header">
        <h1 class="reglement-title">RÈGLEMENT</h1>
        <p class="reglement-subtitle">GuardiHack 2026</p>
      </div>

      <div class="reglement-section">
        <h2 class="section-title">0. Éligibilité</h2>
        <div class="section-content">
          <ul>
            <li><strong>Campus :</strong> Ce CTF est réservé exclusivement aux étudiants des campus Guardia PARIS, LYON et BORDEAUX.</li>
            <li><strong>Promo :</strong> La compétition est accessible à tous les étudiants de la 1ère à la 5ème année.</li>
            <li><strong>Date :</strong> Du 12 au 14 mars 2026 (72 heures non-stop) <span class="hidden-flag">[sys.ping: .---- ... ..--.- .-..]</span> </li>
            <li><strong>Lieu :</strong> Paris, en présentiel. Bordeaux</li>
          </ul>
        </div>
      </div>

      <div class="reglement-section">
        <h2 class="section-title">1. Inscription & Comptes</h2>
        <div class="section-content">
          <ul>
            <li><strong>Inscription avec email école :</strong> Les participants doivent s'inscrire uniquement avec leur adresse email d'école <span class="code-inline">@guardiaschool.fr</span>. Tout autre email sera supprimé.</li>
            <li><strong>Format équipe :</strong> La participation se fait en équipes de <strong class="text-error">5 personnes</strong></li>
            <li><strong>Un compte par personne :</strong> Chaque participant ne peut créer qu'un seul compte. La création de comptes multiples entraînera une disqualification.</li>
            <li><strong>Pseudonyme approprié :</strong> Votre pseudonyme doit être respectueux. Sont interdits :
              <ul class="mt-2">
                <li>Les pseudonymes de troll</li>
                <li>Les symboles excessifs</li>
                <li>L'insertion de flags ou de parties de flags dans le pseudo</li>
              </ul>
              Tout manquement entraînera un bannissement.
            </li>
            <li><strong>Informations exactes :</strong> Les informations fournies lors de l'inscription doivent être exactes et complètes.</li>
          </ul>
        </div>
      </div>

      <div class="reglement-section">
        <h2 class="section-title">2. Format des Flags</h2>
        <div class="section-content">
          <ul>
            <li><strong>Format officiel :</strong> Le format standard des flags est <span class="code-inline">GH{FLAG}</span> (sensible à la casse), mais peut varier selon les challenges.</li>
            <li><strong>Soumission :</strong> Aucun bruteforce n'est nécessaire pour valider un flag. Si une tentative de bruteforce est détectée, elle pourra entraîner une disqualification.</li>
            <li><strong>Confidentialité :</strong> Ne pas partager ou divulguer de flags tant que l'événement est en cours.</li>
            <li><strong>Pas de flag hoarding :</strong> Le stockage ou la conservation de flags pour les soumettre en masse à la fin du CTF est interdit. Les flags doivent être soumis dès que le challenge est résolu.</li>
          </ul>
        </div>
      </div>

      <div class="warning-box">
        <h4>⚠ FLAG-SHARE = BANNISSEMENT IMMÉDIAT</h4>
        <p>Le partage de flags avec d'autres équipes est <strong>strictement interdit</strong> et sera puni d'un <strong>bannissement instantané sans possibilité de retour</strong>. Cette règle s'applique à tous les moyens de communication (Discord, messages privés, forums, etc.).</p>
        <p>Les organisateurs se réservent le droit de bannir toute équipe qui ne respecte pas le règlement.</p>
      </div>

      <div class="reglement-section">
        <h2 class="section-title">3. Conduite & Fair-Play</h2>
        <div class="section-content">
          <ul>
            <li><strong>Esprit sportif :</strong> Les participants sont tenus de maintenir un haut niveau d'esprit sportif et de fair-play tout au long de la compétition.</li>
            <li><strong>Interdictions strictes :</strong> Toute forme de tricherie est interdite, notamment :
              <ul class="mt-2">
                <li>Toute attaque sur l'infrastructure du CTF, la plateforme, ou d'autres participants</li>
                <li>Le plagiat (soumission d'une solution trouvée par une autre personne ou équipe)</li>
                <li>Le partage public de solutions ou d'indices détaillés</li>
                <li>Les attaques DoS/DDoS sur les challenges</li>
                <li>Le sabotage des autres participants</li>
              </ul>
            </li>
            <li><strong>Objectif :</strong> Restez courtois et dans l'esprit d'apprentissage. Le but est la montée en compétence collective.</li>
          </ul>
        </div>
      </div>

      <div class="reglement-section">
        <h2 class="section-title">4. Format du CTF & Notation</h2>
        <div class="section-content">
          <ul>
            <li><strong>Catégories :</strong> Les challenges sont répartis en plusieurs catégories (Web, Crypto, Forensics, Pwn, Reverse, Misc, etc.).</li>
            <li><strong>Difficulté :</strong> Chaque challenge sera étiqueté avec un niveau de difficulté estimé par ses auteurs.</li>
            <li><strong>Points :</strong> Le score est basé uniquement sur les validations réussies.</li>
            <li><strong>Scoring dynamique :</strong> La valeur des challenges pourra diminuer en fonction du nombre de validations (approche dynamique).</li>
            <li><strong>Classement :</strong> En cas d'égalité, le temps de soumission du dernier flag départage les équipes.</li>
          </ul>
        </div>
      </div>

      <div class="reglement-section">
        <h2 class="section-title">5. Support & Assistance</h2>
        <div class="section-content">
          <ul>
            <li><strong>Discord officiel :</strong> Pour tout problème, ouvrez un ticket sur le serveur Discord officiel : <a href="https://discord.gg/b35v8z4wdt" data-invite="M19TQQ==" class="hover:text-primary transition-colors"><span class="code-inline">GUARDIHACK 2026</span></a></li>
            <li><strong>Bugs :</strong> En cas de bug dans un challenge ou dysfonctionnement de la plateforme, contactez directement les organisateurs via Discord en ouvrant un ticket.</li>
            <li><strong>Vulnérabilités :</strong> Les participants qui découvrent des failles dans la plateforme doivent les signaler immédiatement aux organisateurs.</li>
            <li><strong>Pas de hints directs :</strong> L'équipe organisatrice ne donne pas de solutions ou hints détaillés sur les challenges.</li>
            <li><strong>Explications :</strong> L'équipe organisatrice se réserve le droit de demander des explications sur la méthode de résolution d'un challenge en cas de doute.</li>
          </ul>
        </div>
      </div>

      <div class="info-box">
        <h4>📧 Contact</h4>
        <p>Pour toute question concernant le règlement : Contactez la pédagogie ou l'équipe organisatrice via Discord.</p>
      </div>

      <div class="reglement-section">
        <h2 class="section-title">6. Récompenses</h2>
        <div class="section-content">
          <p class="mb-4">Les 3 premières équipes recevront des lots offerts par notre partenaire <strong>Root-Me PRO</strong> et plus encore...</p>
          <p class="mt-4">Tous les participants pourront télécharger un certificat de participation personnalisé à la fin du CTF.</p>
        </div>
      </div>

      <div class="reglement-section">
        <h2 class="section-title">7. Writeups</h2>
        <div class="section-content">
          <ul>
            <li>Les writeups ne doivent <strong>pas être publiés avant la fin du CTF sous risque de bannissement immédiat</strong>.</li>
            <li>Après l'événement, nous encourageons le partage de writeups pour l'apprentissage collectif.</li>
            <li>Les meilleurs writeups pourront être mis en avant par l'organisation.</li>
          </ul>
        </div>
      </div>

      <div class="reglement-section">
        <h2 class="section-title">8. Exigences Techniques</h2>
        <div class="section-content">
          <ul>
            <li>Les participants doivent disposer d'une <strong>connexion Internet stable</strong>.</li>
            <li>Il est conseillé de se connecter directement à la plateforme sans utiliser de proxy ou de VPN, sauf si le challenge l'exige explicitement.</li>
            <li>L'usurpation d'adresse matérielle pour contourner les restrictions réseau (<strong>hex</strong>emple: <span class="font-mono text-sm">49:52:33:21:7D</span>) est un motif de bannissement.</li>
            <li>Les équipes peuvent utiliser n'importe quel outil de leur choix pour résoudre les challenges.</li>
          </ul>
        </div>
      </div>

      <div class="reglement-section">
        <h2 class="section-title">9. Disqualification & Amendements</h2>
        <div class="section-content">
          <ul>
            <li><strong>Droit de réserve :</strong> Les organisateurs se réservent le droit de disqualifier tout participant pour violation du présent règlement ou engagement dans un comportement contraire à l'éthique.</li>
            <li><strong>Modifications :</strong> Les organisateurs peuvent amender le règlement à tout moment. Les participants seront informés de tout changement majeur via la plateforme et Discord.</li>
            <li><strong>Décisions finales :</strong> Les scores finaux seront validés après vérification par l'organisation.</li>
          </ul>
        </div>
      </div>

      <div class="reglement-section">
        <h2 class="section-title">10. Validation du Règlement</h2>
        <div class="section-content">
          <p>En vous inscrivant et en participant au GuardiHack CTF 2026, vous confirmez avoir pris connaissance de ce règlement et vous vous engagez à le respecter dans son intégralité.</p>
        </div>
      </div>

      <div class="success-box">
        <h4>✓ BON COURAGE À TOUS !</h4>
        <p>Que la meilleure équipe gagne ! Amusez-vous, apprenez ensemble et montrez vos compétences. 🚀</p>
      </div>

    </div>
  </div>
</template>

<script setup>
// Pas de logique nécessaire pour cette vue purement informative
</script>

<style scoped>
/* --- FLAG ? --- */
.reglement-container {
  --sys-bin: "01000111 01001000 01111011 01001010"; /* PARTIE 1 */
}
/* --- ?????? pas de commentaire pour les autres.... --- */

.reglement-container {
  /* Variables de couleurs adaptées (modifiables si besoin) */
  --accent-gold: #fbbf24;
  --accent-cyan: #00cff6;
  --glow-cyan: rgba(0, 207, 246, 0.5);
  --danger: #ff0055;
  --success: #00ff88;
  --text-primary: inherit;
  --bg-primary: rgba(0, 0, 0, 0.3);
  --muted: rgba(255, 255, 255, 0.2);

  padding: 2rem 0;
}

.animate-fade-in {
  animation: fadeIn 0.4s ease-out forwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.reglement-header {
  text-align: center;
  margin-bottom: 3rem;
  padding-bottom: 2rem;
  border-bottom: 2px solid var(--accent-gold);
}

.reglement-title {
  font-family: 'Jersey 10', sans-serif;
  font-size: 3.5rem;
  color: var(--accent-cyan);
  text-shadow: 0 0 20px var(--glow-cyan), 0 0 40px var(--glow-cyan);
  margin-bottom: 1rem;
  letter-spacing: 3px;
}

.reglement-subtitle {
  font-family: 'Fira Code', monospace;
  font-size: 1.1rem;
  color: var(--accent-gold);
  text-transform: uppercase;
  letter-spacing: 2px;
}

.reglement-section {
  margin-bottom: 3rem;
}

.section-title {
  font-family: 'Jersey 10', sans-serif;
  font-size: 2rem;
  color: var(--accent-cyan);
  text-shadow: 0 0 10px var(--glow-cyan);
  margin-bottom: 1.5rem;
  padding-left: 1rem;
  border-left: 4px solid var(--accent-cyan);
  background-color: rgba(0, 0, 0, 0.5);
}

.section-content {
  font-size: 1.05rem;
  color: var(--text-primary);
  line-height: 1.6;
  margin-left: 1.5rem;
}

.section-content ul {
  list-style: none;
  padding-left: 0;
}

.section-content li {
  margin-bottom: 0.5rem;
  padding-left: 2rem;
  position: relative;
}

.section-content li::before {
  content: '>';
  position: absolute;
  left: 0;
  color: var(--accent-cyan);
  font-family: 'Fira Code', monospace;
  font-weight: bold;
}

.warning-box {
  background: rgba(255, 0, 85, 0.1);
  border: 2px solid var(--danger);
  border-radius: 10px;
  padding: 1.5rem;
  margin: 2rem 0;
}

.warning-box h4 {
  font-family: 'Press Start 2P', cursive;
  font-size: 1rem;
  color: var(--danger);
  margin-bottom: 1rem;
  letter-spacing: 1px;
  line-height: 1.4;
}

.warning-box p {
  color: var(--text-primary);
  line-height: 1.4;
  margin: 0.5rem 0;
}

.info-box {
  background: rgba(0, 207, 246, 0.1);
  border: 2px solid var(--accent-cyan);
  border-radius: 10px;
  padding: 1.5rem;
  margin: 2rem 0;
}

.info-box h4 {
  font-family: 'Fira Code', monospace;
  font-size: 1rem;
  color: var(--accent-cyan);
  margin-bottom: 1rem;
  text-transform: uppercase;
}

.info-box p {
  color: var(--text-primary);
  line-height: 1.6;
  margin: 0;
}

.success-box {
  background: rgba(0, 255, 136, 0.05);
  border: 2px solid var(--success);
  border-radius: 10px;
  padding: 1.5rem;
  margin: 2rem 0;
}

.success-box h4 {
  font-family: 'Fira Code', monospace;
  font-size: 1.2rem;
  color: var(--success);
  margin-bottom: 1rem;
}

.code-inline {
  font-family: 'Fira Code', monospace;
  background: var(--bg-primary);
  color: var(--accent-gold);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  border: 1px solid var(--muted);
}

.hidden-flag {
  font-size: 0.7rem;
  opacity: 0.3;
  font-family: monospace;
  user-select: all;
}

@media (max-width: 768px) {
  .reglement-container {
    padding: 1rem;
  }
  
  .reglement-title {
    font-size: 2.5rem;
  }
  
  .section-title {
    font-size: 1.5rem;
  }
  
  .section-content {
    margin-left: 0.5rem;
  }
}
</style>