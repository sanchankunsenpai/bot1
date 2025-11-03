/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f8fbff',
          100: '#eef4ff',
          200: '#dbe7ff',
          300: '#bed3ff',
          400: '#8bb2ff',
          500: '#5e91ff',
          600: '#3c6ef5',
          700: '#2d55d9',
          800: '#2646af',
          900: '#203d8a'
        }
      }
    }
  },
  plugins: [require('@tailwindcss/forms')]
};
