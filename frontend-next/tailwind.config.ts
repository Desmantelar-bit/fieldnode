import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: 'class',
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
    './src/lib/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        base: {
          950: 'var(--background)',
        },
        field: {
          bg: 'var(--background)',
          panel: 'var(--panel)',
          panel2: 'var(--panel-2)',
          glass: 'var(--panel-glass)',
          'glass-mid': 'var(--panel-glass-mid)',
          'glass-strong': 'var(--panel-glass-strong)',
          border: 'var(--line)',
          muted: 'var(--muted)',
          text: 'var(--foreground)',
          text1: 'var(--text-1)',
          text2: 'var(--text-2)',
          text3: 'var(--text-3)',
        },
        status: {
          normal: 'var(--status-normal)',
          atencao: 'var(--status-atencao)',
          critico: 'var(--status-critico)',
          neutro: 'var(--status-neutro)',
        },
        accent: {
          DEFAULT: 'var(--ui-accent)',
          dim: 'var(--panel-glass-strong)',
          text: 'var(--text-1)',
        },
      },
      backdropBlur: {
        xs: '2px',
      },
      borderRadius: {
        none: '0',
        sm: '6px',
        DEFAULT: '8px',
        md: '10px',
        lg: '12px',
        xl: '16px',
        '2xl': '20px',
        '3xl': '24px',
        '4xl': '32px',
        full: '9999px',
      },
      boxShadow: {
        glass: 'var(--shadow-glass)',
        card: '0 1px 3px rgba(0,0,0,0.12), 0 4px 16px rgba(0,0,0,0.08)',
        'card-hover': '0 4px 24px rgba(0,0,0,0.18)',
      },
      fontFamily: {
        display: ['var(--font-display)', 'sans-serif'],
        body: ['var(--font-body)', 'sans-serif'],
        sans: ['var(--font-body)', 'sans-serif'],
        mono: ['ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      letterSpacing: {
        label: '0.06em',
        title: '-0.01em',
        tightest: '-0.04em',
      },
      transitionDuration: {
        DEFAULT: '150ms',
      },
    },
  },
  plugins: [],
};

export default config;
