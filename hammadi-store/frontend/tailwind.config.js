module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#3b82f6',
          dark: '#1e40af',
        },
        dark: {
          bg: '#0f172a',
          card: '#1e293b',
          hover: '#334155',
        }
      }
    },
  },
  plugins: [],
}
