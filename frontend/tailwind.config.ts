import type { Config } from 'tailwindcss'

export default <Config>{
  content: [
    './components/**/*.{vue,js,ts}',
    './layouts/**/*.vue',
    './pages/**/*.vue',
    './app.vue',
  ],
  theme: {
    extend: {
      colors: {
        ink: '#23222B',
        primary: {
          DEFAULT: '#2F3B6B',
          dark: '#212a4d',
          light: '#4c5990',
        },
        accent: {
          DEFAULT: '#C99A3E',
          dark: '#a87f2f',
          light: '#dab868',
        },
        bg: '#F5F4F1',
        surface: '#FDFCFA',
        muted: '#6B7280',
      },
      fontFamily: {
        display: ['Fraunces', 'serif'],
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}