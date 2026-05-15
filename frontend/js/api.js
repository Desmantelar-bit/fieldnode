/**
 * frontend/js/api.js
 *
 * Camada de comunicação com a API Django.
 * Usa SEMPRE a variável API do config.js.
 * Sem autodescoberta, sem lógica esperta, sem surpresa.
 */

async function apiFetch(endpoint, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers
  };
  
  if (options.requiresAuth || options.method === 'POST' || options.method === 'PUT' || options.method === 'DELETE') {
    headers['X-API-Key'] = API_KEY;
  }
  
  const fetchOptions = {
    method: options.method || 'GET',
    headers,
    ...options
  };
  
  if (options.body) {
    fetchOptions.body = options.body;
  }
  
  const r = await fetch(API + endpoint, fetchOptions);
  if (!r.ok) {
    const err = await r.json().catch(() => ({ detail: `HTTP ${r.status}` }));
    throw new Error(err.detail || JSON.stringify(err));
  }
  return r.json();
}

async function apiPost(endpoint, body) {
  return apiFetch(endpoint, {
    method: 'POST',
    body: JSON.stringify(body)
  });
}
