/**
 * frontend/js/api.js
 * 
 * Camada de comunicação com a API Django.
 * Todas as requisições HTTP passam por aqui — nenhuma outra parte do frontend
 * usa fetch() diretamente.
 * 
 * IMPORTANTE: Usa a variável API do config.js (sempre http://127.0.0.1:8000)
 */

// Usa a variável API definida em config.js
// NÃO redefine aqui para evitar conflitos
const API_BASE_URL = typeof API !== 'undefined' ? API : 'http://127.0.0.1:8000';

/**
 * GET genérico com tratamento de erro padronizado.
 * Lança Error com mensagem legível em vez de retornar null silenciosamente.
 */
async function apiFetch(endpoint) {
  const url = API_BASE_URL + endpoint;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`API retornou HTTP ${response.status} em ${endpoint}`);
  }
  return response.json();
}

/**
 * POST com body JSON.
 * Lança Error com detalhes da resposta em caso de falha.
 */
async function apiPost(endpoint, body) {
  const response = await fetch(API_BASE_URL + endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(JSON.stringify(err));
  }
  return response.json();
}

// Exporta para uso nos outros módulos
// (em projeto sem bundler, estas funções ficam no escopo global do browser)
