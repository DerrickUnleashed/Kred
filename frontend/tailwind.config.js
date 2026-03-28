/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: '#0F172A',
        secondary: '#1E293B',
        cta: '#3B82F6',
        background: '#020617',
        surface: '#0F172A',
        'text-primary': '#FFFFFF',
        'text-secondary': '#93C5FD',
        'text-muted': '#60A5FA',
        accent: '#3B82F6',
        'accent-glow': 'rgba(59, 130, 246, 0.3)',
        blue: {
          400: '#60A5FA',
          500: '#3B82F6',
        },
      },
      fontFamily: {
        sans: ['IBM Plex Sans', 'system-ui', 'sans-serif'],
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        'slide-up': 'slide-up 0.5s ease-out',
        'fade-in': 'fade-in 0.6s ease-out',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        'pulse-glow': {
          '0%, 100%': { 
            boxShadow: '0 0 20px rgba(59, 130, 246, 0.4)', // Increased opacity
            filter: 'brightness(100%)' 
          },
          '50%': { 
            boxShadow: '0 0 40px rgba(37, 99, 235, 0.7)', // Shifted to a deeper blue (blue-600)
            filter: 'brightness(120%)' 
          },
        },
        'slide-up': {
          '0%': { opacity: '0', transform: 'translateY(30px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
