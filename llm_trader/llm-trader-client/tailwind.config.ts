import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        perspectiv: {
          dark: "#0b0d12",
          mid: "#1a1d27",
          border: "#2a2f3f",
          accent: "#5bc0ff",
          violet: "#7a6fff",
          text: "#e4e8f0",
          muted: "#9aa0b4",
          panel: "#1a1d27",
          success: "#16a34a",
          danger: "#dc2626",
        },
      },
    },
  },
  plugins: [],
};

export default config;
