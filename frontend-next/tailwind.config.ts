import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        field: {
          bg: '#090d0b',
          panel: '#101714',
          panel2: '#17211d',
          border: 'rgba(219, 255, 233, 0.10)',
          muted: '#7f9488',
          text: '#edf7f1',
          green: '#64d98c',
          amber: '#f2c15f',
          red: '#f07878',
        },
      },
      boxShadow: {
        glass: '0 20px 60px rgba(0, 0, 0, 0.32)',
      },
    },
  },
  plugins: [],
};

export default config;
