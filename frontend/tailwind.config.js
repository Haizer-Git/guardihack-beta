/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        titre: ["Special Gothic Expanded One", 'sans-serif'],
        stitre: ["Stack Sans Notch", 'sans-serif'],
        text: ["Inter", 'sans-serif'],
        code: ["Google Sans Code", 'monospace'],
        nbr: ["Bebas Neue", 'sans-serif'],
        pool: ["Press Start 2P", 'sans-serif']
      },
      colors: {
        'ctf-dark': '#0B0E14',
        'ctf-surface': '#161B22',
        'ctf-primary': '#00F5FF',
        'ctf-accent': '#7000FF',
        paris: "#002395",
        bordeaux: "#6d071a",
        lyon: "#D49F45",
      },
      keyframes: {
        'fade-in': {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        }
      },
      animation: {
        'fade-in': 'fade-in 0.5s ease-out forwards',
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
          "primary": "#00CFF6",
          "secondary": "#D6BE91",
          "accent": "#B1B1B1",

          "neutral": "#474D57",

          "base-100": "#212529",
          "base-200": "#2C3034",
          "base-300": "#0A0A0A",

          "base-content": "#FFFFFF",
          "info": "#147FFE",
          "success": "#21EB0F",
          "warning": "#ff5724",
          "error": "#FF0000",
        },
      },
      {
        'piscine-light': {
          "primary": "#007B91",
          "secondary": "#8A744E",
          "accent": "#474D57",

          "neutral": "#E5E7EB",

          "base-100": "#B1B1B1",
          "base-200": "#FFFFFF",
          "base-300": "#EAEAEA",

          "base-content": "#0A0A0A",
          "info": "#0CA5E9",
          "success": "#21EB0F",
          "warning": "#ff5724",
          "error": "#DF0000",
        },
      },

      {
        'pool-theme': {
          "primary": "#6CC5AA",     // Vert Matrix (Terminal)
          "secondary": "#FDD800",   // Cyan néon
          "accent": "#FEFEFF",      // Rouge cyber punk
          "neutral": "#252728",     
          "base-100": "#1C6597",    // Fond principal 
          "base-200": "#3855BA",    // Fond secondaire
          "base-300": "#EDEDED",    // Fond profond
          "base-content": "#FFFFFF",// Texte vert terminal
          "info": "#147FFE",
          "success": "#21EB0F",
          "warning": "#EAB308",
          "error": "#FF003C",
        }
      }
    ],
  },
}