/**
 * frontend/js/colors.js
 * 
 * Fonte única de verdade para cores de máquinas no dashboard.
 * 
 * Problema resolvido: a função getMachineColor estava duplicada em
 * index.html, maquina.html e demo-cores.html com variações sutis.
 * Isso gerava inconsistência: a mesma máquina aparecia com cores
 * diferentes em seções distintas do mesmo dashboard.
 * 
 * Regra de negócio das cores:
 * - Cada modelo de colheitadeira tem uma cor primária (por fabricante)
 * - Quando há múltiplas máquinas do mesmo modelo, a 1ª usa cor pura
 *   e as demais recebem gradiente bicolor para diferenciação visual
 * - A lógica de "modelo base" extrai o prefixo antes do número de série
 *   (ex: CASE-TC5000-01 → modelo CASE-TC5000)
 */

// Paleta de cores por posição — atribuída por ordem de chegada dos modelos
// (em vez de por marca, que era frágil para modelos não mapeados)
const CORES_PRIMARIAS = [
  '#f87171', // Vermelho    — modelo 0
  '#fbbf24', // Amarelo     — modelo 1
  '#4ade80', // Verde       — modelo 2
  '#60a5fa', // Azul        — modelo 3
  '#a78bfa', // Roxo        — modelo 4
  '#f59e0b', // Laranja     — modelo 5
  '#10b981', // Esmeralda   — modelo 6
  '#ef4444', // Vermelho escuro — modelo 7
  '#3b82f6', // Azul escuro — modelo 8
  '#8b5cf6', // Roxo escuro — modelo 9
  '#06b6d4', // Ciano       — modelo 10
  '#84cc16', // Verde lima  — modelo 11
];

// Cores secundárias distintas das primárias para o efeito bicolor
const CORES_SECUNDARIAS = [
  '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#06b6d4',
  '#8b5cf6', '#84cc16', '#a78bfa', '#fbbf24', '#4ade80',
  '#f87171', '#60a5fa',
];

/**
 * Extrai o modelo base de um ID de máquina.
 * "CASE-TC5000-01" → "CASE-TC5000"
 * "NH-CR9000-02"   → "NH-CR9000"
 * "COLH-01"        → "COLH" (sem número de modelo — usa o ID inteiro)
 */
function _extrairModeloBase(maquinaId) {
  const match = maquinaId.match(/^([A-Z][-A-Z0-9]+[A-Z0-9])(?:-\d+)?$/);
  return match ? match[1] : maquinaId;
}

/**
 * Retorna informação de cor para uma máquina dado o contexto da frota.
 * 
 * @param {string} maquinaId - ID da máquina (ex: "CASE-TC5000-01")
 * @param {Array}  allMachines - lista de objetos com campo maquina_id
 * @returns {{ primary: string, secondary: string|null, isBicolor: boolean }}
 */
function getMachineColor(maquinaId, allMachines = []) {
  if (!allMachines.length) {
    return { primary: CORES_PRIMARIAS[0], secondary: null, isBicolor: false };
  }

  // Ordena para garantir atribuição de cores determinística (não depende da ordem de chegada)
  const ordenadas = [...allMachines].sort((a, b) =>
    a.maquina_id.localeCompare(b.maquina_id)
  );

  // Agrupa por modelo base
  const porModelo = {};
  const modelosOrdem = []; // mantém ordem de primeiro aparecimento

  ordenadas.forEach(m => {
    const modelo = _extrairModeloBase(m.maquina_id);
    if (!porModelo[modelo]) {
      porModelo[modelo] = [];
      modelosOrdem.push(modelo);
    }
    porModelo[modelo].push(m);
  });

  const modeloAtual = _extrairModeloBase(maquinaId);
  const indiceModelo = modelosOrdem.indexOf(modeloAtual);
  const corPrimaria = CORES_PRIMARIAS[indiceModelo % CORES_PRIMARIAS.length];

  const maquinasDoModelo = porModelo[modeloAtual] || [];
  const indiceDentroModelo = maquinasDoModelo.findIndex(m => m.maquina_id === maquinaId);
  const indiceGlobal = ordenadas.findIndex(m => m.maquina_id === maquinaId);

  if (indiceDentroModelo <= 0) {
    // Primeira (ou única) máquina do modelo — cor pura
    return { primary: corPrimaria, secondary: null, isBicolor: false };
  }

  // Demais máquinas do mesmo modelo — bicolor
  const corSecundaria = CORES_SECUNDARIAS[indiceGlobal % CORES_SECUNDARIAS.length];
  return { primary: corPrimaria, secondary: corSecundaria, isBicolor: true };
}

/**
 * Retorna a cor CSS para um nível de risco.
 * Centralizado aqui para garantir consistência entre tabela, alertas e IA.
 */
function nivelCor(nivel) {
  const mapa = { CRITICO: '#f87171', ATENCAO: '#fbbf24', NORMAL: '#4ade80' };
  return mapa[nivel] ?? '#4a6055';
}

function nivelBg(nivel) {
  const mapa = { CRITICO: 'var(--red-dim)', ATENCAO: 'var(--amber-dim)', NORMAL: 'var(--green-dim)' };
  return mapa[nivel] ?? 'var(--bg3)';
}

/**
 * Formata timestamp para exibição.
 * Padrão único em todo o dashboard: HH:MM (hora local).
 * Para histórico detalhado (popup): usar formatTimestampDetalhado().
 */
function formatTimestamp(isoString) {
  return new Date(isoString).toLocaleTimeString('pt-BR', {
    hour: '2-digit', minute: '2-digit',
  });
}

function formatTimestampDetalhado(isoString) {
  return new Date(isoString).toLocaleString('pt-BR', {
    day: '2-digit', month: '2-digit', year: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
  });
}

/**
 * Rótulo amigável de risco — linguagem de campo, não de ciência de dados.
 * "CRITICO" → "Parar agora" faz mais sentido para um operador agrícola
 * do que "prob_risco: 0.87".
 */
function rotuloRisco(nivel) {
  const mapa = {
    CRITICO: 'Parar e verificar',
    ATENCAO: 'Monitorar de perto',
    NORMAL:  'Operando bem',
  };
  return mapa[nivel] ?? nivel;
}
