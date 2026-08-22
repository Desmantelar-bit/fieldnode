"use client";

import React, { useEffect, useRef, useState } from "react";
import "leaflet/dist/leaflet.css";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";
import { resolveApiUrl } from "@/services/telemetryService";
import { ListaPosicoesMaquinasSchema } from "@/schemas";
import type { MachinePosition } from "@/types/telemetry";
import { getStatusColor, readCssVar } from "@/lib/theme";

type LeafletModule = typeof import("leaflet");
type LeafletMap = import("leaflet").Map;
type LeafletFeatureGroup = import("leaflet").FeatureGroup;

const DEFAULT_CENTER: [number, number] = [-15.793889, -47.882778];

const API_URL = resolveApiUrl();

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

const MODELS = [
  'TC5000', 'CR9000', 'BC8800', 'TX7000', 'AF9000', 'W5000', 'MX3000', 'FH7800',
];

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

type UnknownRecord = Record<string, unknown>;

function normalizeApiPositions(data: UnknownRecord[]): UnknownRecord[] {
  return data.map((d) => ({
    ...d,
    lat: d.lat ?? d.latitude ?? d.latitude_deg ?? d.lat_deg,
    lng: d.lng ?? d.longitude ?? d.longitude_deg ?? d.lon,
    telemetria:
      d.telemetria || d.telemetry || d.leitura || d.leitura_atual || d.last_telemetry,
  }));
}

function hasUsableCoordinates(data: UnknownRecord) {
  if (data.lat == null || data.lng == null || data.lat === "" || data.lng === "") {
    return false;
  }

  const lat = Number(data.lat);
  const lng = Number(data.lng);

  return (
    Number.isFinite(lat) &&
    Number.isFinite(lng) &&
    Math.abs(lat) <= 90 &&
    Math.abs(lng) <= 180
  );
}

function parsePositions(data: UnknownRecord[]) {
  const parseResult = ListaPosicoesMaquinasSchema.safeParse(
    data.filter(hasUsableCoordinates),
  );

  if (!parseResult.success) {
    console.error('Contrato de API quebrado:', {
      endpoint: 'MapClient.getMachinePositions',
      errors: parseResult.error.format(),
    });
    throw new Error('Formato de dados inesperado recebido do servidor.');
  }

  return parseResult.data;
}

function getPopupHtml(machine: MachinePosition) {
  const statusLabel =
    machine.status === 'operando'
      ? 'Operando'
      : machine.status === 'parada'
        ? 'Parada'
        : 'Offline';

  return `
    <div style="font-size:0.9rem; line-height:1.35;">
      <strong>Máquina:</strong> ${machine.maquina_id ?? machine.modelo}<br />
      <strong>Status:</strong> ${statusLabel}<br />
      <strong>Temperatura:</strong> ${machine.telemetria.temperatura}°C<br />
      <strong>RPM:</strong> ${machine.telemetria.rpm}<br />
      <strong>Última atualização:</strong> ${new Date(machine.telemetria.timestamp).toLocaleString()}
    </div>
  `;
}

function createMarkerIcon(L: LeafletModule, status: string) {
  const color = getStatusColor(status);

  const svg = `<?xml version="1.0" encoding="UTF-8"?><svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' width='28' height='28'><path d='M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z' fill='${color}' stroke='${readCssVar('background')}' stroke-opacity='0.15' stroke-width='1'/><circle cx='12' cy='9' r='3' fill='${readCssVar('foreground')}' opacity='0.9'/></svg>`;
  const iconUrl = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;

  return L.icon({
    iconUrl,
    iconSize: [28, 36],
    iconAnchor: [14, 36],
    popupAnchor: [0, -34],
  });
}

function getStaticImageSrc(image: { src?: string } | string) {
  return typeof image === "string" ? image : image.src;
}

function configureDefaultLeafletIcons(L: LeafletModule) {
  delete (L.Icon.Default.prototype as { _getIconUrl?: unknown })._getIconUrl;
  L.Icon.Default.mergeOptions({
    iconUrl: getStaticImageSrc(markerIcon),
    shadowUrl: getStaticImageSrc(markerShadow),
  });
}

function isValidPosition(machine: MachinePosition) {
  return (
    Number.isFinite(machine.lat) &&
    Number.isFinite(machine.lng) &&
    Math.abs(machine.lat) <= 90 &&
    Math.abs(machine.lng) <= 180
  );
}

function cleanupLeafletContainer(container: HTMLElement | null) {
  if (!container) return;
  const typedContainer = container as HTMLElement & { _leaflet_id?: unknown };
  const existingId = typedContainer._leaflet_id;
  if (existingId != null) {
    try {
      delete typedContainer._leaflet_id;
    } catch {
      typedContainer._leaflet_id = undefined;
    }
  }
}

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
  const [mounted, setMounted] = useState(false);
  const [mapReady, setMapReady] = useState(false);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const leafletRef = useRef<LeafletModule | null>(null);
  const mapRef = useRef<LeafletMap | null>(null);
  const markersRef = useRef<LeafletFeatureGroup | null>(null);
  const visiblePositionCount = positions.filter(isValidPosition).length;
  const shouldRenderMap = !loading && !error && (demo || visiblePositionCount > 0);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const mq = window.matchMedia('(max-width: 1023px)');
    setIsMobile(mq.matches);
    const listener = (event: MediaQueryListEvent) => setIsMobile(event.matches);
    mq.addEventListener('change', listener);
    return () => mq.removeEventListener('change', listener);
  }, []);

  useEffect(() => {
    setMounted(true);
    return () => setMounted(false);
  }, []);

  useEffect(() => {
    let active = true;

    async function createMap() {
      if (!shouldRenderMap) return;
      if (typeof window === 'undefined') return;
      if (mapRef.current) return;
      const container = containerRef.current;
      if (!container) return;

      const imported = await import('leaflet');
      const leafletImport = imported as { default?: LeafletModule };
      const L = leafletImport.default ?? imported;
      configureDefaultLeafletIcons(L);
      leafletRef.current = L;

      cleanupLeafletContainer(container);

      const map = L.map(container, {
        center: DEFAULT_CENTER,
        zoom: 4,
      });

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      }).addTo(map);

      const layerGroup = L.featureGroup().addTo(map);
      markersRef.current = layerGroup;
      mapRef.current = map;
      setMapReady(true);
      map.invalidateSize();
      window.requestAnimationFrame(() => map.invalidateSize());
      window.setTimeout(() => map.invalidateSize(), 250);

      if (!active) {
        map.remove();
        mapRef.current = null;
        setMapReady(false);
      }
    }

    createMap();

    const container = containerRef.current;
    return () => {
      active = false;
      if (mapRef.current) {
        try {
          mapRef.current.remove();
        } catch {
          // ignore
        }
        cleanupLeafletContainer(container);
        mapRef.current = null;
        setMapReady(false);
      }
    };
  }, [shouldRenderMap]);

  useEffect(() => {
    if (!mapRef.current) return;
    const map = mapRef.current;

    if (isMobile) {
      map.scrollWheelZoom.disable();
      map.dragging.disable();
    } else {
      map.scrollWheelZoom.enable();
      map.dragging.enable();
    }
  }, [isMobile]);

  useEffect(() => {
    let cancelled = false;

    async function loadPositions() {
      if (externalPositions?.length) {
        try {
          const parsed = parsePositions(externalPositions as unknown as UnknownRecord[]);
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
            setLoading(false);
          }
          return;
        }
      }

      try {
        const response = await fetch(`${API_URL}/maquinas/posicao/`, {
          cache: 'no-store',
          headers: { Accept: 'application/json' },
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        const normalized = Array.isArray(data) ? normalizeApiPositions(data) : [];
        const parsed = parsePositions(normalized);
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

    loadPositions();
    const interval = window.setInterval(loadPositions, 30000);

    return () => {
      cancelled = true;
      window.clearInterval(interval);
    };
  }, [externalPositions]);

  useEffect(() => {
    if (!mapReady || !mapRef.current || !leafletRef.current) return;
    const L = leafletRef.current;
    const map = mapRef.current;
    const markers = markersRef.current ?? L.featureGroup().addTo(map);
    markersRef.current = markers;
    const validPositions = positions.filter(isValidPosition);

    markers.clearLayers();

    validPositions.forEach((machine) => {
      L.marker([machine.lat, machine.lng], {
        icon: createMarkerIcon(L, machine.status),
      })
        .bindPopup(getPopupHtml(machine))
        .addTo(markers);
    });

    if (validPositions.length === 1) {
      map.setView([validPositions[0].lat, validPositions[0].lng], 13);
    } else if (validPositions.length > 1) {
      const bounds = markers.getBounds();
      if (bounds.isValid()) {
        map.fitBounds(bounds.pad(0.2), { maxZoom: 13 });
      }
    } else {
      map.setView(DEFAULT_CENTER, 4);
    }

    setTimeout(() => map.invalidateSize(), 100);
  }, [mapReady, positions]);

  if (loading) {
    return (
      <div className="min-h-[50vh] h-[calc(100vh-5.5rem)] w-full sm:h-[calc(100vh-5rem)] flex items-center justify-center">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-accent border-t-transparent" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-[50vh] h-[calc(100vh-5.5rem)] w-full sm:h-[calc(100vh-5rem)] flex items-center justify-center">
        <div className="glass-panel p-6 text-center">
          <p className="text-xs text-status-critico">{error}</p>
        </div>
      </div>
    );
  }

  const hasVisiblePositions = visiblePositionCount > 0;

  if (!hasVisiblePositions && !demo) {
    return (
      <div className="flex h-[calc(100vh-5.5rem)] min-h-[28rem] w-full items-center justify-center bg-black/20 px-6 text-center sm:h-[calc(100vh-5rem)]">
        <div>
          <p className="text-sm font-semibold text-field-text2">
            Localizacao nao disponivel para esta frota.
          </p>
          <p className="mt-2 max-w-sm text-xs text-field-text3">
            Nenhuma maquina veio com coordenadas validas de GPS no momento.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative h-[calc(100vh-5.5rem)] min-h-[28rem] w-full sm:h-[calc(100vh-5rem)]">
      {process.env.NODE_ENV !== 'production' && (
        <div
          id="map-client-debug"
          style={{
            position: 'absolute',
            top: 12,
            right: 12,
            zIndex: 9999,
            background: 'var(--overlay-debug)',
            color: 'var(--text-1)',
            padding: '6px 8px',
            borderRadius: 6,
            fontSize: 12,
          }}
        >
          MapClient: {mounted ? 'mounted' : 'not-mounted'} • positions: {positions.length}
        </div>
      )}

      {demo && positions.length > 1 && (
        <div className="absolute left-4 top-4 z-20 rounded-lg border border-status-atencao/30 bg-status-atencao/15 px-3 py-2 text-[11px] font-semibold uppercase tracking-[0.16em] text-status-atencao backdrop-blur-md">
          Modo Demo - Rota Simulada
        </div>
      )}

      <div ref={containerRef} className="relative z-0 h-full min-h-[28rem] w-full" />
    </div>
  );
}
