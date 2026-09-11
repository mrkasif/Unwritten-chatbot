import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#0E1117",
        surface: "#161B22",
        borderline: "#30363D",
        userbubble: "#1F2B38",
        accent: "#58A6FF",
        muted: "#8B949E",
      },
    },
  },
  plugins: [],
};

export default config;