export const OFFLINE_DB_NAME = 'fieldnode-offline';
export const OFFLINE_DB_VERSION = 3;

export type QueuedAction = {
  localId: string;
  type: 'decision.approve' | 'decision.reject' | 'wo.update';
  id: string;
  body: unknown;
  key: string;
  state: 'pending' | 'retrying' | 'rejected';
  attempts: number;
  createdAt: number;
  lastError?: string | null;
};

export type RecentData = { url: string; body: unknown; savedAt: number };

export function openOfflineDb(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(OFFLINE_DB_NAME, OFFLINE_DB_VERSION);
    req.onupgradeneeded = () => {
      const db = req.result;
      if (!db.objectStoreNames.contains('telemetria-pendente')) db.createObjectStore('telemetria-pendente', { keyPath: 'localId' });
      if (!db.objectStoreNames.contains('actions')) db.createObjectStore('actions', { keyPath: 'localId' });
      if (!db.objectStoreNames.contains('dados-recentes')) db.createObjectStore('dados-recentes', { keyPath: 'url' });
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error ?? new Error('offline database unavailable'));
  });
}

export function put<T extends { localId?: string; url?: string }>(storeName: string, value: T) {
  return openOfflineDb().then((db) => new Promise<void>((resolve, reject) => {
    const tx = db.transaction(storeName, 'readwrite');
    tx.objectStore(storeName).put(value);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error ?? new Error('offline database write failed'));
  }));
}

export function getAll<T>(storeName: string): Promise<T[]> {
  return openOfflineDb().then((db) => new Promise<T[]>((resolve, reject) => {
    const req = db.transaction(storeName, 'readonly').objectStore(storeName).getAll();
    req.onsuccess = () => resolve(req.result as T[]);
    req.onerror = () => reject(req.error ?? new Error('offline database read failed'));
  }));
}

export function get<T>(storeName: string, key: IDBValidKey): Promise<T | undefined> {
  return openOfflineDb().then((db) => new Promise<T | undefined>((resolve, reject) => {
    const req = db.transaction(storeName, 'readonly').objectStore(storeName).get(key);
    req.onsuccess = () => resolve(req.result as T | undefined);
    req.onerror = () => reject(req.error ?? new Error('offline database read failed'));
  }));
}

export function remove(storeName: string, key: IDBValidKey) {
  return openOfflineDb().then((db) => new Promise<void>((resolve, reject) => {
    const tx = db.transaction(storeName, 'readwrite');
    tx.objectStore(storeName).delete(key);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error ?? new Error('offline database delete failed'));
  }));
}
