/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Indian Railways inspired color palette
        primary: {
          50: '#fef3e2',
          100: '#fde4b9',
          200: '#fcd38c',
          300: '#fbc15f',
          400: '#fab43d',
          500: '#f9a825', // Railway yellow
          600: '#f49200',
          700: '#ed7d00',
          800: '#e66900',
          900: '#db4700',
        },
        railway: {
          blue: '#1a237e',
          red: '#c62828',
          green: '#2e7d32',
          orange: '#ef6c00',
        },
        berth: {
          lower: '#4caf50',
          middle: '#ff9800',
          upper: '#f44336',
          side: '#9c27b0',
        }
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'system-ui', 'sans-serif'],
        display: ['Outfit', 'system-ui', 'sans-serif'],
      },
      animation: {
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'fade-in': 'fadeIn 0.2s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: 0 },
          '100%': { transform: 'translateY(0)', opacity: 1 },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: 0 },
          '100%': { transform: 'translateY(0)', opacity: 1 },
        },
        fadeIn: {
          '0%': { opacity: 0 },
          '100%': { opacity: 1 },
        },
      },
    },
  },
  plugins: [],
}

