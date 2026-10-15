'use client';

import { useEffect, useState } from 'react';
import { Moon, Sun } from 'lucide-react';

export function ThemeToggle() {
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem('fn-theme') as 'dark' | 'light' | null;
    const preferred = saved ?? (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
    setTheme(preferred);
    applyTheme(preferred);
    setMounted(true);
  }, []);

  function applyTheme(t: 'dark' | 'light') {
    const root = document.documentElement;
    root.classList.remove('dark', 'light');
    root.classList.add(t);
  }

  function toggle() {
    const next = theme === 'dark' ? 'light' : 'dark';
    setTheme(next);
    applyTheme(next);
    localStorage.setItem('fn-theme', next);
  }

  if (!mounted) {
    return <div className="h-9 w-9" aria-hidden="true" />;
  }

  return (
    <button
      type="button"
      onClick={toggle}
      aria-label={theme === 'dark' ? 'Ativar modo claro' : 'Ativar modo escuro'}
      title={theme === 'dark' ? 'Modo claro' : 'Modo escuro'}
      className="icon-control flex h-9 w-9 items-center justify-center rounded-xl border text-[var(--text-3)] hover:text-[var(--text-1)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--ui-accent)] active:scale-95"
    >
      {theme === 'dark'
        ? <Sun size={16} strokeWidth={1.8} aria-hidden="true" />
        : <Moon size={16} strokeWidth={1.8} aria-hidden="true" />
      }
    </button>
  );
}
