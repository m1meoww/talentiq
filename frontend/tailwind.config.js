/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        navy: {
          DEFAULT: "#0B1736",
          light: "#102A56",
        },
        accent: {
          blue: "#2563EB",
          teal: "#14B8A6",
        },
        surface: "#F5F7FB",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        display: ["Sora", "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(11, 23, 54, 0.06), 0 1px 3px rgba(11, 23, 54, 0.08)",
      },
    },
  },
  plugins: [],
};
