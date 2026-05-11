/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        cyber: ['"Press Start 2P"', 'cursive'],
        sans: ['Poppins', 'sans-serif'],
        mono: ['"Roboto Mono"', 'monospace'],
      },
      colors: {
        'ctf-dark': '#0B0E14',
        'ctf-surface': '#161B22',
        'ctf-primary': '#00F5FF',
        'ctf-accent': '#7000FF',
      }
    }, // Fin de extend
  }, // Fin de theme
  plugins: [
    require('daisyui'),
  ],
  daisyui: {
    themes: [
      {
        'piscine-dark': {
          "primary": "#147FFE",
          "secondary": "#e1ff51",
          "accent": "#FFF2BD",
          "neutral": "#2a2a2a",
          "base-100": "#000000",
          "base-200": "#111111",
          "base-300": "#1c1c1c",
          "base-content": "#FFFFFF",
          "info": "#147FFE",
          "success": "#21EB0F",
          "warning": "#ff5724",
          "error": "#FF0000",
        },
      },
      {
        'piscine-light': {
          "primary": "#147FFE",
          "secondary": "#E1FF51",
          "accent": "#FFF2BD",
          "neutral": "#e0e0e0",
          "base-100": "#FFFFFF",
          "base-200": "#f5f5f5",
          "base-300": "#ebebeb",
          "base-content": "#000000",
          "info": "#0CA5E9",
          "success": "#21EB0F",
          "warning": "#ff5724",
          "error": "#FF0000",
        },
      }
    ],
  },
}