import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Máquinas | FieldNode',
  description: 'Consulte máquinas, estado operacional e telemetria da frota FieldNode.',
};

export default function MaquinasLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return children;
}
