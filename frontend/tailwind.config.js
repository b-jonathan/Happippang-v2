/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}", // Next.js App Router
    "./pages/**/*.{js,ts,jsx,tsx,mdx}", // traditional pages/
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/**/*.{js,ts,jsx,tsx,mdx}", // if you keep code under src/
  ],

  theme: {
    extend: {
      // example: extend colors or fonts here
    },
  },

  plugins: [
    require("@tailwindcss/forms"),
    require("tailwind-scrollbar")({ nocompatible: true }),
  ],
};
