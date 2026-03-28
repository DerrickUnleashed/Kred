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
        cta: '#E5B74B',
        background: '#020617',
        surface: '#0F172A',
        'text-primary': '#FFFFFF',
        'text-secondary': '#E5B74B',
        'text-muted': '#D4A84A',
        accent: {
          DEFAULT: '#E5B74B',
          50: '#F5EDD4',
          100: '#F0E0B8',
          200: '#EBD49D',
          300: '#E5C881',
          400: '#E5B74B',
          500: '#D4A84A',
          600: '#C49A3D',
          700: '#A88134',
          800: '#8D6A2C',
          900: '#715524',
        },
        'accent-glow': 'rgba(229, 183, 75, 0.3)',
        blue: {
          400: '#E5B74B',
          500: '#D4A84A',
        },
      },
      textColor: {
        accent: '#E5B74B',
      },
      backgroundColor: {
        accent: '#E5B74B',
      },
      borderColor: {
        accent: '#E5B74B',
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
            boxShadow: '0 0 20px rgba(229, 183, 75, 0.4)',
            filter: 'brightness(100%)' 
          },
          '50%': { 
            boxShadow: '0 0 40px rgba(229, 183, 75, 0.7)',
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
