'use client';

import { useEffect } from 'react';

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

    navigator.serviceWorker
      .register('/sw.js')
      .catch((error) => {
        console.warn('[FieldNode] Service Worker indisponivel:', error);
      });
  }, []);

  return null;
}
