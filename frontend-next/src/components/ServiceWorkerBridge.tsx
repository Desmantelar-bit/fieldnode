'use client';

import { useEffect } from 'react';
import { resolveApiUrl } from "@/services/telemetryService";

const API_URL = resolveApiUrl();
const API_KEY = process.env.NEXT_PUBLIC_FIELDNODE_API_KEY || '';

export function ServiceWorkerBridge() {
  useEffect(() => {
    if (!('serviceWorker' in navigator)) return;

    if (process.env.NODE_ENV !== 'production') {
      navigator.serviceWorker.getRegistrations().then((registrations) => {
        registrations.forEach((registration) => registration.unregister());
      });
      if ('caches' in window) {
        caches.keys().then((cacheNames) => {
          cacheNames
            .filter((cacheName) => cacheName.startsWith('fieldnode-'))
            .forEach((cacheName) => caches.delete(cacheName));
        });
      }
      return;
    }

    let active = true;

    navigator.serviceWorker
      .register('/sw.js')
      .then(async (registration) => {
        await navigator.serviceWorker.ready;
        if (!active) return;

        const worker =
          registration.active ||
          registration.waiting ||
          registration.installing ||
          navigator.serviceWorker.controller;

        worker?.postMessage({
          type: 'FIELDNODE_CONFIG',
          apiUrl: API_URL,
          apiKey: API_KEY,
        });
      })
      .catch((error) => {
        console.warn('[FieldNode] Service Worker indisponivel:', error);
      });

    return () => {
      active = false;
    };
  }, []);

  return null;
}
