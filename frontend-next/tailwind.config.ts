import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
    './src/lib/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        base: {
          950: '#0B0E14',
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
        // accent: identidade visual de interface (navegacao, foco, botoes primarios)
        // semanticamente independente de --status-normal
        accent: {
          DEFAULT: 'var(--ui-accent)',
          dim: 'var(--panel-glass-strong)',
          text: 'var(--text-1)',
          lime: '#CCFF00',
          orange: '#FF5E00',
        },
      },
      backdropBlur: {
        xs: '2px',
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
        '4xl': '2rem',
      },
      boxShadow: {
        glass: 'var(--shadow-glass)',
      },
      spacing: {
        1: 'var(--space-1)',
        2: 'var(--space-2)',
        3: 'var(--space-3)',
        4: 'var(--space-4)',
        6: 'var(--space-6)',
        8: 'var(--space-8)',
      },
      fontFamily: {
        sans: ['Inter', 'SF Pro Display', 'sans-serif'],
        mono: 'var(--font-code)',
      },
      letterSpacing: {
        label: 'var(--tracking-label)',
        title: 'var(--tracking-title)',
        tightest: '-.04em',
      },
    },
  },
  plugins: [],
};

export default config;
