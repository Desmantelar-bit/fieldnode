import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Relatórios | FieldNode',
  description: 'Gere relatórios de telemetria e cobertura operacional da frota FieldNode.',
};

export default function RelatoriosLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return children;
}
