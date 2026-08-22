import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
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
        sans: 'var(--font-primary)',
        mono: 'var(--font-code)',
      },
      letterSpacing: {
        label: 'var(--tracking-label)',
        title: 'var(--tracking-title)',
      },
    },
  },
  plugins: [],
};

export default config;
