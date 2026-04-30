/**
 * frontend/js/api.js
 *
 * Camada de comunicação com a API Django.
 * Usa SEMPRE a variável API do config.js.
 * Sem autodescoberta, sem lógica esperta, sem surpresa.
 */

async function apiFetch(endpoint) {
  const r = await fetch(API + endpoint);
  if (!r.ok) throw new Error(`HTTP ${r.status} em ${endpoint}`);
  return r.json();
}

async function apiPost(endpoint, body) {
  const r = await fetch(API + endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!r.ok) {
    const err = await r.json().catch(() => ({}));
    throw new Error(JSON.stringify(err));
  }
  return r.json();
}
