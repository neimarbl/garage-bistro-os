/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}", // Varre recursivamente todas as nossas telas e contextos
  ],
  theme: {
    extend: {
      // Configuração de animações nativas para os pop-ups de KDS e SOS de salão
      animation: {
        'fade-in-up': 'fadeInUp 0.3s ease-out forwards',
        'shake': 'shake 0.4s ease-in-out',
      },
      keyframes: {
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        shake: {
          '0%, 100%': { transform: 'translateX(0)' },
          '25%': { transform: 'translateX(-4px)' },
          '75%': { transform: 'translateX(4px)' },
        },
      },
    },
  },
  plugins: [],
}
