/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        cyber: {
          bg: "#070B17",
          card: "#0F1629",
          border: "#1E2D4A",
          primary: "#00D9FF", // Neon Cyan
          secondary: "#7C4DFF", // Electric Purple
          accent: "#00FFA3", // Neon Green
          danger: "#FF3B5C", // Neon Red
          warning: "#FFC400", // Neon Yellow
          text: "#E8EDF5",
          muted: "#8FA3C0",
          dim: "#4D6380"
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      borderRadius: {
        'xl': '14px',
        '2xl': '18px',
      },
      boxShadow: {
        'glow-primary': '0 0 15px rgba(0, 217, 255, 0.25)',
        'glow-secondary': '0 0 15px rgba(124, 77, 255, 0.25)',
        'glow-accent': '0 0 15px rgba(0, 255, 163, 0.25)',
        'glow-danger': '0 0 15px rgba(255, 59, 92, 0.25)',
      }
    },
  },
  plugins: [],
}
