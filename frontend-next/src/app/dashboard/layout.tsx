import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Dashboard | FieldNode',
  description: 'Acompanhe a telemetria, os alertas e o estado operacional da frota FieldNode.',
};

export default function DashboardLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return children;
}
