/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        herb: {
          50: "#f0f9f1",
          100: "#dbf0dd",
          200: "#b9e1bf",
          300: "#8aca95",
          400: "#54ab65",
          500: "#2f8f45",
          600: "#1f7235",
          700: "#1a5b2d",
          800: "#184827",
          900: "#153b22",
        },
        marigold: {
          50: "#fff7ed",
          100: "#ffedd5",
          200: "#fed7aa",
          300: "#fdba74",
          400: "#fb923c",
          500: "#ef7c1a",
          600: "#e8791a",
          700: "#c2540d",
          800: "#9a4210",
          900: "#7c3812",
        },
      },
      fontFamily: {
        display: ["Poppins", "system-ui", "sans-serif"],
        body: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
