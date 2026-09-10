/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0fdfa',
          100: '#ccfbf1',
          500: '#14b8a6',
          600: '#0d9488',
          900: '#134e4a',
        },
        heat: {
          low: '#22c55e',
          medium: '#eab308',
          high: '#f97316',
          extreme: '#ef4444',
        },
        dark: {
          bg: '#0a0f1d',
          card: '#111827',
          border: '#1f2937',
          muted: '#374151'
        }
      },
      fontFamily: {
        sans: ['var(--font-inter)', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
