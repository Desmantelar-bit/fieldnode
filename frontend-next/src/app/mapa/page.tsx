import { AppShell } from '@/components/AppShell';
import { FleetMap } from '@/components/FleetMap';

export default function MapaPage() {
  return (
    <AppShell active="/mapa" eyebrow="FieldNode" title="Mapa de Frota">
      <FleetMap />
    </AppShell>
  );
}
