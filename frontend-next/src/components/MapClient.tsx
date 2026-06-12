'use client';

import 'leaflet/dist/leaflet.css';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from "leaflet";
import React from "react";

type MachinePosition = {
  id: number;
  modelo: string;
  lat: number;
  lng: number;
  status: string;
  telemetria: {
    temperatura: number;
    rpm: number;
    timestamp: string;
  };
};

const getIconByStatus = (status: string) => {
  const color =
    status === "operando"
      ? "#10b981"
      : status === "parada"
        ? "#f59e0b"
        : "#ef4444";

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
  positions,
  isMobile,
}: {
  positions: MachinePosition[];
  isMobile: boolean;
}) {
  return (
    <div className="min-h-[50vh] h-[calc(100vh-5.5rem)] w-full sm:h-[calc(100vh-5rem)]">
      <MapContainer
        center={
          positions.length
            ? [positions[0].lat, positions[0].lng]
            : [-15.793889, -47.882778]
        }
        zoom={positions.length ? 8 : 4}
        scrollWheelZoom={!isMobile}
        dragging={!isMobile}
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {positions.map((machine) => (
          <Marker
            key={machine.id}
            position={[machine.lat, machine.lng]}
            icon={getIconByStatus(machine.status)}
          >
            <Popup>
              <strong>Máquina: {machine.modelo}</strong>
              <br />
              <strong>Status:</strong>{" "}
              {machine.status === "operando"
                ? "Operando"
                : machine.status === "parada"
                  ? "Parada"
                  : "Offline"}
              <br />
              <strong>Temperatura:</strong> {machine.telemetria.temperatura}°C
              <br />
              <strong>RPM:</strong> {machine.telemetria.rpm}
              <br />
              <strong>Última atualização:</strong>{" "}
              {new Date(machine.telemetria.timestamp).toLocaleString()}
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
