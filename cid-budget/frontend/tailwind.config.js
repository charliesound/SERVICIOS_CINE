/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        dark: { 300: '#0f0f14', 400: '#16161e', 500: '#1c1c26', 600: '#242430', 700: '#2e2e3a' },
        cine: { 300: '#a0a0b0', 400: '#787890', 500: '#5c5c6e', 600: '#45455a', 700: '#35354a' },
        amber: { 400: '#f59e0b', 500: '#d97706', 600: '#b45309' },
        legal: { red: '#ef4444', green: '#22c55e', blue: '#3b82f6' },
      },
    },
  },
  plugins: [],
}
