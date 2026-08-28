"use client";

import React, { useEffect, useMemo, useRef, useState } from "react";
import "leaflet/dist/leaflet.css";
import { resolveApiUrl } from "@/services/telemetryService";
import { ListaPosicoesMaquinasSchema } from "@/schemas";
import type { MachinePosition } from "@/types/telemetry";
import type { EstadoRequisicao } from "@/types/api";
import { LoadingState, EmptyState, ErrorState } from "@/components/ui/FeedbackStates";

type LeafletModule = typeof import("leaflet");
type LeafletMap = import("leaflet").Map;
type LeafletFeatureGroup = import("leaflet").FeatureGroup;

const DEFAULT_CENTER: [number, number] = [-15.793889, -47.882778];

const API_URL = resolveApiUrl();

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
    console.error("Contrato de API quebrado:", {
      endpoint: "MapClient.getMachinePositions",
      errors: parseResult.error.format(),
    });
    throw new Error("Formato de dados inesperado recebido do servidor.");
  }

  return parseResult.data;
}

function getPopupHtml(machine: MachinePosition) {
  const statusLabel =
    machine.status === "operando"
      ? "Operando"
      : machine.status === "parada"
        ? "Parada"
        : "Offline";

  return `
    <div style="font-size:0.9rem; line-height:1.35;">
      <strong>Máquina:</strong> ${escapeHtml(machine.maquina_id ?? machine.modelo)}<br />
      <strong>Status:</strong> ${statusLabel}<br />
      <strong>Temperatura:</strong> ${escapeHtml(String(machine.telemetria.temperatura))}°C<br />
      <strong>RPM:</strong> ${escapeHtml(String(machine.telemetria.rpm))}<br />
      <strong>Última atualização:</strong> ${escapeHtml(new Date(machine.telemetria.timestamp).toLocaleString())}
    </div>
  `;
}

function escapeHtml(value: string) {
  return value.replace(/[&<>'"]/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "'": "&#039;",
    '"': "&quot;",
  })[character] ?? character);
}

function getMarkerStatus(status: MachinePosition["status"]) {
  if (status === "operando") {
    return { label: "Operando", className: "bg-status-normal", indicator: "●" };
  }
  if (status === "parada") {
    return { label: "Atenção", className: "bg-status-atencao", indicator: "●" };
  }
  return { label: "Offline", className: "bg-status-critico", indicator: "●" };
}

function createMarkerIcon(L: LeafletModule, machine: MachinePosition) {
  const status = getMarkerStatus(machine.status);
  const machineId = escapeHtml(machine.maquina_id ?? machine.modelo);

  return L.divIcon({
    className: "leaflet-machine-pill-icon",
    html: `<div class="flex items-center gap-2 whitespace-nowrap rounded-full border border-white/20 bg-slate-950/90 px-3 py-2 text-xs font-semibold text-white shadow-xl backdrop-blur-md"><span aria-hidden="true">🚜</span><span>${machineId}</span><span class="h-1 w-1 rounded-full bg-white/30"></span><span class="flex items-center gap-1 text-slate-200"><span class="text-[10px] ${status.className}">${status.indicator}</span>${status.label}</span></div>`,
    iconSize: [190, 36],
    iconAnchor: [95, 18],
    popupAnchor: [0, -20],
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
  fullBleed = false,
}: {
  externalPositions?: MachinePosition[];
  fullBleed?: boolean;
}) {
  const [estado, setEstado] = useState<EstadoRequisicao<MachinePosition[]>>({ tipo: "carregando" });
  const [retryCount, setRetryCount] = useState(0);
  const [isMobile, setIsMobile] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [mapReady, setMapReady] = useState(false);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const leafletRef = useRef<LeafletModule | null>(null);
  const mapRef = useRef<LeafletMap | null>(null);
  const markersRef = useRef<LeafletFeatureGroup | null>(null);

  const positions = useMemo(() => estado.tipo === "sucesso" ? estado.dados : [], [estado]);
  const visiblePositionCount = positions.filter(isValidPosition).length;
  const shouldRenderMap = estado.tipo === "sucesso" && visiblePositionCount > 0;

  useEffect(() => {
    if (typeof window === "undefined") return;
    const mq = window.matchMedia("(max-width: 1023px)");
    setIsMobile(mq.matches);
    const listener = (event: MediaQueryListEvent) => setIsMobile(event.matches);
    mq.addEventListener("change", listener);
    return () => mq.removeEventListener("change", listener);
  }, []);

  useEffect(() => {
    setMounted(true);
    return () => setMounted(false);
  }, []);

  useEffect(() => {
    let active = true;

    async function createMap() {
      if (!shouldRenderMap) return;
      if (typeof window === "undefined") return;
      if (mapRef.current) return;
      const container = containerRef.current;
      if (!container) return;

      const imported = await import("leaflet");
      const leafletImport = imported as { default?: LeafletModule };
      const L = leafletImport.default ?? imported;
      leafletRef.current = L;

      cleanupLeafletContainer(container);

      const map = L.map(container, {
        center: DEFAULT_CENTER,
        zoom: 4,
      });

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors",
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
    if (!mapReady || !mapRef.current || !leafletRef.current) return;
    const L = leafletRef.current;
    const map = mapRef.current;
    const markers = markersRef.current ?? L.featureGroup().addTo(map);
    markersRef.current = markers;
    const validPositions = positions.filter(isValidPosition);

    markers.clearLayers();

    validPositions.forEach((machine) => {
      L.marker([machine.lat, machine.lng], {
        icon: createMarkerIcon(L, machine),
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

  useEffect(() => {
    let cancelled = false;

    async function loadPositions() {
      if (externalPositions?.length) {
        try {
          const parsed = parsePositions(externalPositions as unknown as UnknownRecord[]);
          if (!cancelled) {
            setEstado({ tipo: "sucesso", dados: parsed });
          }
          return;
        } catch {
          if (!cancelled) {
            setEstado({ tipo: "erro", mensagem: "Dados de GPS inválidos" });
          }
          return;
        }
      }

      try {
        const response = await fetch(`${API_URL}/maquinas/posicao/`, {
          cache: "no-store",
          headers: { Accept: "application/json" },
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        const normalized = Array.isArray(data) ? normalizeApiPositions(data) : [];
        const parsed = parsePositions(normalized);
        if (!cancelled) {
          setEstado(parsed.length === 0 ? { tipo: "vazio" } : { tipo: "sucesso", dados: parsed });
        }
      } catch (err) {
        if (!cancelled) {
          const mensagem = err instanceof Error ? err.message : "Falha ao carregar posições da frota.";
          setEstado({ tipo: "erro", mensagem });
        }
      }
    }

    loadPositions();
    const interval = window.setInterval(loadPositions, 30000);

    return () => {
      cancelled = true;
      window.clearInterval(interval);
    };
  }, [externalPositions, retryCount]);

  if (estado.tipo === "carregando") {
    return (
      <div className={`${fullBleed ? "h-full" : "min-h-[50vh] h-[calc(100vh-5.5rem)] sm:h-[calc(100vh-5rem)]"} flex w-full items-center justify-center`}>
        <LoadingState mensagem="Carregando posições..." />
      </div>
    );
  }

  if (estado.tipo === "erro") {
    return (
      <div className={`${fullBleed ? "h-full" : "min-h-[50vh] h-[calc(100vh-5.5rem)] sm:h-[calc(100vh-5rem)]"} flex w-full items-center justify-center`}>
        <ErrorState mensagem={estado.mensagem} onRetry={() => setRetryCount((c) => c + 1)} />
      </div>
    );
  }

  if (estado.tipo === "vazio") {
    return (
      <div className={`${fullBleed ? "h-full min-h-0" : "h-[calc(100vh-5.5rem)] min-h-[28rem] sm:h-[calc(100vh-5rem)]"} flex w-full items-center justify-center bg-black/20 px-6 text-center`}>
        <EmptyState mensagem="Nenhuma máquina veio com coordenadas válidas de GPS no momento." />
      </div>
    );
  }

  return (
    <div className={`${fullBleed ? "h-full min-h-0" : "h-[calc(100vh-5.5rem)] min-h-[28rem] sm:h-[calc(100vh-5rem)]"} relative w-full`}>
      {process.env.NODE_ENV !== "production" && (
        <div
          id="map-client-debug"
          style={{
            position: "absolute",
            top: 12,
            right: 12,
            zIndex: 9999,
            background: "var(--overlay-debug)",
            color: "var(--text-1)",
            padding: "6px 8px",
            borderRadius: 6,
            fontSize: 12,
          }}
        >
          MapClient: {mounted ? "mounted" : "not-mounted"} • positions: {positions.length}
        </div>
      )}

      <div ref={containerRef} className={`relative z-0 h-full w-full ${fullBleed ? "min-h-0" : "min-h-[28rem]"}`} />
    </div>
  );
}
