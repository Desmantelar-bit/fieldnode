/**
 * frontend/js/status.js - VERSÃO REFATORADA
 * 
 * Motor limpo do dashboard:
 * - Carrega métricas a cada 3 segundos
 * - Carrega tabela de máquinas a cada 3 segundos
 * - Abre popup com dados de IA quando clica em "Detalhes"
 * - Sem inventações CSS, sem estado complexo
 */

const state = {
  dados: [],
  ultimaPoll: null
};

/**
 * Carrega os 3 cards de métricas
 */
async function carregarMetricas() {
  try {
    const data = await apiFetch('/api/metricas/');
    
    document.getElementById('metric-validas').textContent = 
      (data.leituras_validas || 0).toLocaleString('pt-BR');
    
    document.getElementById('metric-ativas').textContent = 
      (data.maquinas_ativas || 0);
    
    document.getElementById('metric-rejeicao').textContent = 
      ((data.taxa_rejeicao || 0).toFixed(1)) + '%';
      
  } catch (e) {
    console.error('[carregarMetricas] Erro:', e.message);
    document.getElementById('metric-validas').textContent = '—';
    document.getElementById('metric-ativas').textContent = '—';
    document.getElementById('metric-rejeicao').textContent = '—';
  }
}

/**
 * Carrega as máquinas e renderiza a tabela
 */
async function carregarTabela() {
  try {
    const maquinas = await apiFetch('/api/leituras/ultimas/');
    
    if (!maquinas || maquinas.length === 0) {
      document.getElementById('status-table-body').innerHTML = 
        '<tr><td colspan="7" class="text-center text-muted py-4">Nenhuma máquina com leitura recente</td></tr>';
      state.dados = [];
      return;
    }

    state.dados = maquinas;

    const html = maquinas.map(m => {
      const statusColor = m.nivel_risco === 'CRITICO' ? 'danger' : 
                          m.nivel_risco === 'ATENCAO' ? 'warning' : 'success';
      const timestamp = new Date(m.timestamp).toLocaleTimeString('pt-BR');

      return `
        <tr>
          <td><strong>${m.maquina_id}</strong></td>
          <td>${m.temperatura}°C</td>
          <td>${m.vibracao}g</td>
          <td>${m.rpm} RPM</td>
          <td><span class="badge bg-${statusColor}">${m.nivel_risco || 'NORMAL'}</span></td>
          <td>${timestamp}</td>
          <td><button class="btn btn-sm btn-outline-primary btn-detalhe" onclick="abrirPopupMaquina('${m.maquina_id}')">Detalhes</button></td>
        </tr>
      `;
    }).join('');

    document.getElementById('status-table-body').innerHTML = html;

  } catch (e) {
    console.error('[carregarTabela] Erro:', e.message);
    document.getElementById('status-table-body').innerHTML = 
      '<tr><td colspan="7" class="text-center text-danger py-4">Erro ao carregar máquinas</td></tr>';
  }
}

/**
 * Abre o popup com detalhes da máquina
 */
async function abrirPopupMaquina(maquinaId) {
  const modal = new bootstrap.Modal(document.getElementById('machine-popup'));
  
  // Mostra loading
  document.getElementById('popup-title').textContent = `Detalhes — ${maquinaId}`;
  document.getElementById('popup-id').textContent = maquinaId;
  document.getElementById('popup-temp').textContent = '—';
  document.getElementById('popup-vib').textContent = '—';
  document.getElementById('popup-rpm').textContent = '—';
  document.getElementById('popup-status').textContent = '—';
  document.getElementById('popup-ia').innerHTML = '<p class="text-muted">⌛ Carregando análise...</p>';
  
  modal.show();

  try {
    // Busca dados da máquina no estado local
    const maquina = state.dados.find(m => m.maquina_id === maquinaId);
    if (maquina) {
      document.getElementById('popup-temp').textContent = `${maquina.temperatura}°C`;
      document.getElementById('popup-vib').textContent = `${maquina.vibracao}g`;
      document.getElementById('popup-rpm').textContent = `${maquina.rpm}`;
      document.getElementById('popup-status').textContent = maquina.nivel_risco || 'NORMAL';
    }

    // Carrega IA em paralelo
    const [anomalias, manutencao] = await Promise.all([
      apiFetch(`/api/anomalias/?maquina_id=${maquinaId}`).catch(() => ({})),
      apiFetch(`/api/manutencao/?maquina_id=${maquinaId}`).catch(() => ({}))
    ]);

    let iaHtml = '';

    if (anomalias.status === 'ok') {
      iaHtml += `<p><strong>Anomalias:</strong> ${anomalias.total || 0} detectadas</p>`;
    } else {
      iaHtml += `<p><strong>Anomalias:</strong> ${anomalias.status || 'Indisponível'}</p>`;
    }

    if (manutencao.status === 'ok') {
      const prob = Math.round((manutencao.prob_risco || 0) * 100);
      iaHtml += `<p><strong>Risco de Manutenção:</strong> ${manutencao.nivel || '—'} (${prob}%)</p>`;
    } else {
      iaHtml += `<p><strong>Risco de Manutenção:</strong> ${manutencao.status || 'Indisponível'}</p>`;
    }

    document.getElementById('popup-ia').innerHTML = iaHtml;

  } catch (e) {
    console.error('[abrirPopupMaquina] Erro ao carregar IA:', e.message);
    document.getElementById('popup-ia').innerHTML = '<p class="text-danger">Erro ao carregar análise</p>';
  }
}

/**
 * Polling recursivo: carrega métricas + tabela a cada 3 segundos
 */
async function pollStatus() {
  await Promise.all([
    carregarMetricas(),
    carregarTabela()
  ]);

  setTimeout(pollStatus, 3000);
}

/**
 * Inicializa no load
 */
window.addEventListener('DOMContentLoaded', () => {
  console.log('[status.js] Iniciando polling...');
  pollStatus();
});
