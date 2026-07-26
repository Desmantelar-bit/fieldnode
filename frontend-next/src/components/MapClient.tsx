'use client';

import 'leaflet/dist/leaflet.css';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import L from "leaflet";
import React, { useEffect, useState } from "react";
import { MachinePositionSchema, type MachinePosition } from "@/types/telemetry";

const API_URL =
  typeof window !== 'undefined'
    ? (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api')
    : 'http://localhost:8000/api';

const DEMO_WAYPOINTS: Array<{ lat: number; lng: number }> = [
  { lat: -15.793889, lng: -47.882778 },
  { lat: -15.795500, lng: -47.885000 },
  { lat: -15.798000, lng: -47.888500 },
  { lat: -15.801000, lng: -47.892000 },
  { lat: -15.803500, lng: -47.889500 },
  { lat: -15.802000, lng: -47.885000 },
  { lat: -15.799000, lng: -47.881500 },
  { lat: -15.796000, lng: -47.879000 },
  { lat: -15.794000, lng: -47.881000 },
  { lat: -15.793889, lng: -47.882778 },
];

const MODELS = ['TC5000', 'CR9000', 'BC8800', 'TX7000', 'AF9000', 'W5000', 'MX3000', 'FH7800'];

function buildDemoPositions(timestamp: string): MachinePosition[] {
  return DEMO_WAYPOINTS.map((wp, idx) => ({
    id: idx + 1,
    maquina_id: `COLH-${String(idx + 1).padStart(2, '0')}`,
    modelo: MODELS[idx] || 'TC5000',
    lat: wp.lat + (Math.random() - 0.5) * 0.0001,
    lng: wp.lng + (Math.random() - 0.5) * 0.0001,
    status: idx % 3 === 0 ? 'operando' : idx % 3 === 1 ? 'parada' : 'offline',
    telemetria: {
      temperatura: Number((68 + Math.random() * 20).toFixed(1)),
      rpm: Number(Math.round(1500 + Math.random() * 500)),
      timestamp,
    },
  }));
}

const getIconByStatus = (status: string) => {
  const color =
    status === 'operando'
      ? '#10b981'
      : status === 'parada'
        ? '#f59e0b'
        : '#ef4444';

  const svg = `<?xml version="1.0" encoding="UTF-8"?><svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' width='28' height='28'><path d='M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z' fill='${color}' stroke='%23000000' stroke-opacity='0.15' stroke-width='1'/><circle cx='12' cy='9' r='3' fill='%23fff' opacity='0.9'/></svg>`;

  const dataUrl = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;

  return new L.Icon({
    iconUrl: dataUrl,
    iconSize: [28, 36],
    iconAnchor: [14, 36],
    popupAnchor: [0, -34],
  });
};

export default function MapClient({
  externalPositions,
}: {
  externalPositions?: MachinePosition[];
}) {
  const [positions, setPositions] = useState<MachinePosition[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [demo, setDemo] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const mq = window.matchMedia('(max-width: 1023px)');
    setIsMobile(mq.matches);
    const handler = (e: MediaQueryListEvent) => setIsMobile(e.matches);
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      if (externalPositions?.length) {
        try {
          const parsed = MachinePositionSchema.array().parse(externalPositions);
          if (!cancelled) {
            setPositions(parsed);
            setDemo(false);
            setError(null);
            setLoading(false);
          }
          return;
        } catch {
          if (!cancelled) {
            setError('Dados de GPS invalidos');
          }
        }
      }

      try {
        const response = await fetch(`${API_URL}/maquinas/posicao/`, {
          cache: 'no-store',
          headers: { Accept: 'application/json' },
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        const parsed = MachinePositionSchema.array().parse(data);
        if (!cancelled) {
          setPositions(parsed);
          setDemo(false);
          setError(null);
          setLoading(false);
        }
      } catch {
        if (!cancelled) {
          const fallback = buildDemoPositions(new Date().toISOString());
          setPositions(fallback);
          setDemo(true);
          setError(null);
          setLoading(false);
        }
      }
    }

    load();
    const interval = window.setInterval(load, 30000);
    return () => {
      cancelled = true;
      window.clearInterval(interval);
    };
  }, [externalPositions]);

  if (loading) {
    return (
      <div className="min-h-[50vh] h-[calc(100vh-5.5rem)] w-full sm:h-[calc(100vh-5rem)] flex items-center justify-center">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-emerald-300 border-t-transparent" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-[50vh] h-[calc(100vh-5.5rem)] w-full sm:h-[calc(100vh-5rem)] flex items-center justify-center">
        <div className="glass-panel border border-white/10 bg-white/[0.02] p-6 text-center">
          <p className="text-xs text-red-300">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-[50vh] h-[calc(100vh-5.5rem)] w-full sm:h-[calc(100vh-5rem)]">
      <MapContainer
        center={
          positions.length
            ? [positions[0].lat, positions[0].lng]
            : [-15.793889, -47.882778]
        }
        zoom={positions.length ? 13 : 4}
        scrollWheelZoom={!isMobile}
        dragging={!isMobile}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {demo && positions.length > 1 && (
          <Polyline
            positions={positions.map((machine) => [machine.lat, machine.lng])}
            pathOptions={{ color: '#10b981', weight: 2, opacity: 0.5, dashArray: '6, 10' }}
          />
        )}
        {demo && (
          <div className="leaflet-top leaflet-left" style={{ position: 'absolute', top: '10px', left: '10px', zIndex: 1000 }}>
            <div className="rounded-lg border border-amber-300/30 bg-amber-300/15 px-3 py-2 text-[11px] font-semibold uppercase tracking-[0.16em] text-amber-100 backdrop-blur-md">
              Modo Demo - Rota Simulada
            </div>
          </div>
        )}
        {positions.map((machine) => (
          <Marker
            key={machine.id}
            position={[machine.lat, machine.lng]}
            icon={getIconByStatus(machine.status)}
          >
            <Popup>
              <strong>Máquina: {machine.maquina_id ?? machine.modelo}</strong>
              {machine.maquina_id && <> ({machine.modelo})</>}
              <br />
              <strong>Status:</strong>{' '}
              {machine.status === 'operando'
                ? 'Operando'
                : machine.status === 'parada'
                  ? 'Parada'
                  : 'Offline'}
              <br />
              <strong>Temperatura:</strong> {machine.telemetria.temperatura}°C
              <br />
              <strong>RPM:</strong> {machine.telemetria.rpm}
              <br />
              <strong>Última atualização:</strong>{' '}
              {new Date(machine.telemetria.timestamp).toLocaleString()}
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
