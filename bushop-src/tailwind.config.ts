import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        // BusHop design tokens — Warm Kem & Sakura palette
        busBlue: "#1A3660",
        busBlueHover: "#243E72",
        busPink: "#D4607A",
        busPinkMuted: "#C67B5C",
        busCream: "#FEF9F0",
        busSurface: "#FFFFFF",
        busBorder: "#F0E8D8",
        busBorderFocus: "#D4607A",
        busBorderHover: "#E8C8A0",
        busTextPrimary: "#1A1008",
        busTextSecondary: "#78604A",
        busTextMuted: "#A08060",
        busTextPlaceholder: "#C4B09A",
        busSuccess: "#0D9488",
        busWarning: "#F57C3A",
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
        // BusHop border radius tokens
        card: "20px",
        input: "12px",
        btn: "14px",
        "btn-sm": "10px",
        sort: "12px",
        "sort-pill": "9px",
      },
      boxShadow: {
        // BusHop shadow tokens
        card: "0 4px 24px rgba(180,120,60,0.10), 0 1px 4px rgba(180,120,60,0.06)",
        "card-hover": "0 8px 24px rgba(180,120,60,0.12)",
      },
      fontSize: {
        display: ["28px", { lineHeight: "1.2", letterSpacing: "-0.03em", fontWeight: "700" }],
        h1: ["24px", { lineHeight: "1.2", letterSpacing: "-0.03em", fontWeight: "700" }],
        price: ["26px", { lineHeight: "1.0", letterSpacing: "-0.03em", fontWeight: "800" }],
        time: ["24px", { lineHeight: "1.0", letterSpacing: "-0.03em", fontWeight: "800" }],
        h3: ["18px", { lineHeight: "1.3", fontWeight: "600" }],
      },
      spacing: {
        "4.5": "18px",
      },
      maxWidth: {
        content: "640px",
      },
      fontFamily: {
        sans: ["var(--font-be-vietnam-pro)", "Noto Sans", "sans-serif"],
      },
    },
  },
  plugins: [],
};
export default config;
