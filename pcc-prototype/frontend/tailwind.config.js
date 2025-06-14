/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'hospital-blue': '#0066CC',
        'hospital-dark': '#004499',
        'alert-red': '#DC2626',
        'ready-green': '#059669',
        'warning-yellow': '#F59E0B',
        border: 'hsl(var(--border))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'pulse-subtle': 'pulse-subtle 2s ease-in-out infinite',
        'bounce-gentle': 'bounce-gentle 1s ease-in-out infinite',
        'sparkle': 'sparkle 2s ease-in-out infinite',
        'fade-in': 'fade-in 0.5s ease-out',
        'slide-up': 'slide-up 0.3s ease-out',
        'slide-in-right': 'slide-in-right 0.3s ease-out',
      },
      keyframes: {
        'glow': {
          '0%': { boxShadow: '0 0 10px rgba(96, 165, 250, 0.5)' },
          '100%': { boxShadow: '0 0 20px rgba(96, 165, 250, 0.8)' }
        },
        'pulse-subtle': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.8' }
        },
        'bounce-gentle': {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-4px)' }
        },
        'sparkle': {
          '0%, 100%': { opacity: '1', transform: 'scale(1) rotate(0deg)' },
          '50%': { opacity: '0.7', transform: 'scale(1.1) rotate(180deg)' }
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' }
        },
        'slide-up': {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' }
        },
        'slide-in-right': {
          '0%': { transform: 'translateX(-10px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' }
        }
      }
    },
  },
  plugins: [],
}