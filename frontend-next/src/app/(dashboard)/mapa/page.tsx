"use client";

import dynamic from 'next/dynamic';
import { useEffect, useState } from 'react';


// Define the type for the machine position data from the API
type MachinePosition = {
  id: number;
  modelo: string;
  lat: number;
  lng: number;
  status: string; // 'operando', 'parada', 'offline'
  telemetria: {
    temperatura: number;
    rpm: number;
    timestamp: string;
  };
};

const MapClient = dynamic(() => import("@/components/MapClient"), {
  ssr: false,
  loading: () => (
    <div className="min-h-[24rem] w-full rounded-2xl bg-white/5 p-6 text-slate-300">
      Carregando mapa...
    </div>
  ),
});

const MapPage = () => {
  const [machinePositions, setMachinePositions] = useState<MachinePosition[]>(
    [],
  );
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch("/api/maquinas/posicao/");
        if (!response.ok) {
          throw new Error("Failed to fetch machine positions");
        }
        const data: MachinePosition[] = await response.json();
        setMachinePositions(data);
      } catch (error) {
        console.error("Error fetching machine positions:", error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000); // Fetch every 5 seconds
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const mq = window.matchMedia("(pointer: coarse), (max-width: 768px)");
    const update = () => setIsMobile(Boolean(mq.matches));
    update();
    mq.addEventListener?.("change", update);
    return () => mq.removeEventListener?.("change", update);
  }, []);

  return (
    <div className="min-h-[50vh] h-[calc(100vh-6rem)] w-full">
      <MapClient positions={machinePositions} isMobile={isMobile} />
    </div>
  );
};

export default MapPage;