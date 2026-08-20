import { AppShell } from '@/components/AppShell';
import { MapaFrotaDynamic } from './MapaFrotaDynamic';

export default function MapaPage() {
  return (
    <AppShell active="/mapa" eyebrow="FieldNode" title="Mapa de Frota">
      <MapaFrotaDynamic />
    </AppShell>
  );
}
