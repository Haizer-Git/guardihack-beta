export function getAssetUrl(iconUrl) {
  // 1. Si la valeur est absente (null, undefined, vide), on s'arrête proprement
  if (!iconUrl) return '';
  
  // 2. SÉCURITÉ CRITIQUE : Si le backend renvoie un nombre (ex: un ID comme 12) ou un objet,
  // on le convertit de force en chaîne de caractères pour éviter de faire crasher .replace()
  if (typeof iconUrl !== 'string') {
    iconUrl = String(iconUrl);
  }
  
  // 3. Si c'est déjà une URL absolue (ex: commence par http:// ou https://), on la renvoie telle quelle
  if (iconUrl.startsWith('http://') || iconUrl.startsWith('https://')) {
    return iconUrl;
  }
  
  // 4. Nettoyage classique du chemin
  const cleanUrl = iconUrl.replace(/^app\//, '').replace(/^\//, '');
  
  // 5. Récupération de l'URL du backend depuis le .env
  const backendBaseUrl = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:9414';
  
  return `${backendBaseUrl}/${cleanUrl}`;
}