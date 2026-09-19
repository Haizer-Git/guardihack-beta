export function getAssetUrl(iconUrl) {
  if (!iconUrl) return '';
  if (typeof iconUrl !== 'string') {
    iconUrl = String(iconUrl);
  }
  if (iconUrl.startsWith('http://') || iconUrl.startsWith('https://')) {
    return iconUrl;
  }
  const cleanUrl = iconUrl.replace(/^app\//, '').replace(/^\//, '');
  const backendBaseUrl = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:9414';
  return `${backendBaseUrl}/${cleanUrl}`;
}