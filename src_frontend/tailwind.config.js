/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        amber: {
          50: '#fef9e7',
          100: '#fdf0c7',
          200: '#fae18e',
          300: '#f6d04d',
          400: '#f3c418',
          500: '#d4a212',
          600: '#b8860b',
          700: '#9a6d0a',
          800: '#7d5609',
          900: '#614208',
        },
        dark: {
          50: '#f8fafc',
          100: '#e2e8f0',
          200: '#1e293b',
          300: '#0f172a',
          400: '#020617',
        }
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
      },
      boxShadow: {
        'soft': '0 2px 15px rgba(0,0,0,0.3)',
        'card': '0 4px 25px rgba(0,0,0,0.4)',
        'glow': '0 0 30px rgba(245,197,24,0.15)',
      },
    },
  },
  plugins: [],
}