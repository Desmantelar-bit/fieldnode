import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        field: {
          bg: '#0a0d0b',
          panel: '#121715',
          panel2: '#1a201d',
          border: 'rgba(200, 210, 205, 0.12)',
          muted: '#8a9189',
          text: '#e6efe9',
          green: '#5cb870',
          amber: '#d49a3a',
          red: '#b54d4d',
        },
      },
      borderRadius: {
        none: '0',
        sm: '0',
        DEFAULT: '0',
        md: '0',
        lg: '0',
        xl: '0',
        '2xl': '0',
        '3xl': '0',
      },
      boxShadow: {
        glass: '0 20px 60px rgba(0, 0, 0, 0.32)',
      },
    },
  },
  plugins: [],
};

export default config;
