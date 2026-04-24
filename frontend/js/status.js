/**
 * frontend/js/status.js
 * 
 * Gerencia a tabela de status em tempo real e o carrossel de máquinas.
 * 
 * Estado centralizado em um único objeto `tabelaState` em vez de
 * variáveis globais espalhadas — isso foi a causa raiz de vários bugs:
 * - Carrossel voltando ao início no polling (currentTableIndex não sobrevivia)
 * - Filtro de busca interferindo com o índice do carrossel
 * - Total de máquinas ficando desatualizado após reconexão da API
 * 
 * Contrato de atualização:
 * - Fonte de dados: GET /api/leituras/ultimas/
 * - Intervalo: 3 segundos
 * - Se API falhar: mantém últimos dados na tela, mostra indicador de erro
 * - Se não há dados: mostra mensagem de "aguardando leituras"
 * - Índice do carrossel: preservado entre polls (usuário não perde a posição)
 */

const tabelaState = {
  dados:        [],    // todos os dados da frota atual
  indiceGrupo:  0,     // grupo atual do carrossel (0 = primeiras 3 máquinas)
  totalMaquinas: 0,
};

const MAQUINAS_POR_GRUPO = 3;

/**
 * Atualiza os dados e re-renderiza a tabela.
 * Preserva a posição do carrossel a menos que o número de máquinas mude.
 */
async function atualizarStatusMaquinas() {
  try {
    const maquinas = await apiFetch('/api/leituras/ultimas/');

    if (!maquinas.length) {
      _mostrarMensagemTabela('Nenhuma leitura recebida do ESP32 ainda.');
      return;
    }

    // Reseta o carrossel apenas se o número de máquinas mudou
    // (evita que o polling derrube o usuário de volta à página 1)
    if (tabelaState.totalMaquinas !== maquinas.length) {
      tabelaState.totalMaquinas = maquinas.length;
      tabelaState.indiceGrupo = 0;
    }

    tabelaState.dados = maquinas;
    renderStatusTable(maquinas, tabelaState.indiceGrupo);
    _atualizarControlesCarrossel();

    const upEl = document.getElementById('ultimo-update');
    if (upEl) upEl.textContent = 'atualizado às ' + new Date().toLocaleTimeString('pt-BR');

  } catch (err) {
    console.error('[status] Erro ao buscar status de máquinas:', err);
    const tbody = document.getElementById('status-table-body');
    if (tbody && !tabelaState.dados.length) {
      // Só mostra erro se não há dados anteriores para manter na tela
      tbody.innerHTML = '<tr><td colspan="100%" class="state-msg err-red">Erro ao buscar dados. Verificando reconexão...</td></tr>';
    }
  }
}

/**
 * Navega entre grupos de máquinas no carrossel.
 * @param {number} direcao - +1 (próximo) ou -1 (anterior)
 */
function scrollMaquinasTabela(direcao) {
  const maxGrupo = Math.ceil(tabelaState.totalMaquinas / MAQUINAS_POR_GRUPO) - 1;
  tabelaState.indiceGrupo = Math.max(0, Math.min(maxGrupo, tabelaState.indiceGrupo + direcao));
  renderStatusTable(tabelaState.dados, tabelaState.indiceGrupo);
  _atualizarControlesCarrossel();
}

function _atualizarControlesCarrossel() {
  const maxGrupo = Math.ceil(tabelaState.totalMaquinas / MAQUINAS_POR_GRUPO) - 1;
  const btnPrev = document.getElementById('carousel-prev');
  const btnNext = document.getElementById('carousel-next');
  if (btnPrev) btnPrev.disabled = tabelaState.indiceGrupo === 0;
  if (btnNext) btnNext.disabled = tabelaState.indiceGrupo >= maxGrupo || tabelaState.totalMaquinas <= MAQUINAS_POR_GRUPO;
}

function _mostrarMensagemTabela(mensagem) {
  const tbody = document.getElementById('status-table-body');
  if (tbody) tbody.innerHTML = `<tr><td colspan="100%" class="state-msg">${mensagem}</td></tr>`;
  const thead = document.getElementById('status-table-head');
  if (thead) thead.innerHTML = '<tr></tr>';
}

/**
 * Renderiza um grupo de máquinas na tabela.
 */
function renderStatusTable(maquinas, grupoIndex = 0) {
  const thead = document.getElementById('status-table-head');
  const tbody = document.getElementById('status-table-body');
  if (!thead || !tbody) return;

  if (!maquinas.length) {
    _mostrarMensagemTabela('Nenhuma máquina ativa.');
    return;
  }

  const inicio = grupoIndex * MAQUINAS_POR_GRUPO;
  const grupo = maquinas.slice(inicio, inicio + MAQUINAS_POR_GRUPO);

  // Headers
  const headerCells = grupo.map(m => {
    const cores = getMachineColor(m.maquina_id, maquinas);
    const cor = nivelCor(m.nivel_risco || 'NORMAL');
    const bg = nivelBg(m.nivel_risco || 'NORMAL');
    const bordaStyle = cores.isBicolor
      ? `border-image: linear-gradient(90deg, ${cores.primary}, ${cores.secondary}) 1;`
      : `border-color: ${cores.primary};`;
    const nomeStyle = cores.isBicolor
      ? `background: linear-gradient(135deg, ${cores.primary}, ${cores.secondary}); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-weight: 600;`
      : `color: ${cores.primary};`;

    return `<th class="machine-header" style="border-top: 4px solid; ${bordaStyle}" onclick="abrirPopupMaquina('${m.maquina_id}')">
      <div class="machine-name" style="${nomeStyle}">${m.maquina_id}</div>
      <div class="machine-status-badge" style="background:${bg}; color:${cor}; border:1px solid ${cor}33;" title="${rotuloRisco(m.nivel_risco || 'NORMAL')}">${m.nivel_risco || 'NORMAL'}</div>
    </th>`;
  }).join('');

  thead.innerHTML = `<tr><th class="info-label-header"><div class="diagonal-header"><span class="diagonal-top">Info</span><span class="diagonal-bottom">Máquinas</span></div></th>${headerCells}</tr>`;

  // Linhas de dados
  const linhas = [
    { label: 'Temperatura', fn: m => {
      const cor = m.temperatura > 85 ? '#f87171' : m.temperatura > 75 ? '#fbbf24' : '#4ade80';
      return `<span class="status-value" style="color:${cor}">${m.temperatura}<span class="status-unit">°C</span></span>`;
    }},
    { label: 'Vibração', fn: m => {
      const cor = m.vibracao > 0.8 ? '#f87171' : m.vibracao > 0.5 ? '#fbbf24' : 'var(--text)';
      return `<span class="status-value" style="color:${cor}">${m.vibracao}<span class="status-unit">g</span></span>`;
    }},
    { label: 'RPM', fn: m => {
      const cor = m.rpm < 1300 ? '#fbbf24' : 'var(--text)';
      return `<span class="status-value" style="color:${cor}">${m.rpm}</span>`;
    }},
    { label: 'Última leitura', fn: m => `<span class="status-timestamp">${formatTimestamp(m.timestamp)}</span>` },
  ];

  tbody.innerHTML = linhas.map(({ label, fn }) =>
    `<tr class="status-row"><td class="info-label">${label}</td>${grupo.map(m => `<td>${fn(m)}</td>`).join('')}</tr>`
  ).join('');
}

/**
 * Busca uma máquina pelo nome e abre o popup de detalhes.
 */
function buscarMaquina() {
  const input = document.getElementById('machine-search');
  const termo = (input?.value ?? '').trim().toUpperCase();
  if (!termo) return;

  const encontrada = tabelaState.dados.find(m =>
    m.maquina_id.toUpperCase().includes(termo)
  );

  if (encontrada) {
    abrirPopupMaquina(encontrada.maquina_id);
    if (input) input.value = '';
  } else {
    alert(`Máquina "${termo}" não encontrada`);
  }
}
