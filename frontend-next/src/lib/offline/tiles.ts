export type TileBounds = { west: number; south: number; east: number; north: number };

export function tileUrl(z: number, x: number, y: number, subdomain = 'a') {
  return `https://${subdomain}.tile.openstreetmap.org/${z}/${x}/${y}.png`;
}

export function tilesForBounds(bounds: TileBounds, zooms: number[]) {
  const result: string[] = [];
  for (const z of zooms) {
    const n = 2 ** z;
    const x = (longitude: number) => Math.floor(((longitude + 180) / 360) * n);
    const y = (latitude: number) => Math.floor((1 - Math.asinh(Math.tan((latitude * Math.PI) / 180)) / Math.PI) / 2 * n);
    for (let tx = x(bounds.west); tx <= x(bounds.east); tx += 1) {
      for (let ty = y(bounds.north); ty <= y(bounds.south); ty += 1) result.push(tileUrl(z, tx, ty));
    }
  }
  return result;
}

export async function preloadTiles(bounds: TileBounds, zooms: number[]) {
  if (!('caches' in window)) return 0;
  const cache = await caches.open('fieldnode-map-tiles-v1');
  let saved = 0;
  for (const url of tilesForBounds(bounds, zooms)) {
    try { const response = await fetch(url); if (response.ok) { await cache.put(url, response.clone()); saved += 1; } } catch { /* offline tile preload is best effort */ }
  }
  return saved;
}
