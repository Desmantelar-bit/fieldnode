'use client';

import { useEffect } from 'react';
import { resolveApiUrl } from "@/services/telemetryService";

const API_URL = resolveApiUrl();

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
    const handleMessage = (event: MessageEvent) => {
      const message = event.data;
      if (message?.type === 'AUTH_REQUIRED') {
        window.dispatchEvent(new CustomEvent('fieldnode-auth-required'));
      }
      if (message?.type === 'AUTH_RECOVERED') {
        window.dispatchEvent(new CustomEvent('fieldnode-auth-recovered'));
      }
      if (message?.type === 'TELEMETRY_QUEUE_STATUS' || message?.type === 'TELEMETRY_SYNC_RESULT') {
        window.dispatchEvent(new CustomEvent('fieldnode-queue-status', { detail: message }));
      }
      if (message?.type === 'TELEMETRY_QUEUE_ERROR') {
        window.dispatchEvent(new CustomEvent('fieldnode-queue-error'));
      }
    };
    navigator.serviceWorker.addEventListener('message', handleMessage);

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
        });
        worker?.postMessage({ type: 'GET_TELEMETRY_STATUS' });
        if (localStorage.getItem('fn-auth-user')) worker?.postMessage({ type: 'AUTH_RECOVERED' });
      })
      .catch((error) => {
        console.warn('[FieldNode] Service Worker indisponivel:', error);
      });

    return () => {
      active = false;
      navigator.serviceWorker.removeEventListener('message', handleMessage);
    };
  }, []);

  return null;
}
