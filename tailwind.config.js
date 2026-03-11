/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.html", "./static/js/**/*.js"],
  theme: {
    extend: {
      colors: {
        ink: "#0f172a",
        mist: "#f5f8fc",
      },
    },
  },
  plugins: [],
};
