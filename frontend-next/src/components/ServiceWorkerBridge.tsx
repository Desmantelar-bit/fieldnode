'use client';

import { useEffect } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api';
const API_KEY = process.env.NEXT_PUBLIC_FIELDNODE_API_KEY || '';

export function ServiceWorkerBridge() {
  useEffect(() => {
    if (!('serviceWorker' in navigator)) return;

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
