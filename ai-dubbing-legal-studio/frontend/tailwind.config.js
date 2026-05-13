/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        cine: {
          900: '#0a0e17',
          800: '#111827',
          700: '#1a2332',
          600: '#253044',
          500: '#334155',
          400: '#64748b',
          300: '#94a3b8',
          200: '#cbd5e1',
          100: '#e2e8f0',
        },
        amber: {
          400: '#f59e0b',
          500: '#d97706',
        },
        legal: {
          red: '#dc2626',
          green: '#16a34a',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
