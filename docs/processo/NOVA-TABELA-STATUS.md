# Nova Tabela de Status em Tempo Real 📊

## Visão Geral das Melhorias

A tabela de status em tempo real foi completamente reformulada para oferecer uma experiência mais intuitiva e funcional, seguindo as especificações solicitadas.

## 🔄 Mudanças Estruturais

### Antes
- Estrutura confusa: `id` e `maquina_id` como campos
- Máquinas como linhas, métricas espalhadas
- Navegação limitada

### Depois
- **Máquinas como colunas**: Cada coluna representa uma máquina específica
- **Métricas como linhas**: 4 métricas principais organizadas verticalmente
- **Estrutura clara**: Fácil comparação entre máquinas

## 🎠 Sistema de Carrossel Inteligente

### Funcionamento
- **Grupos de 3**: Mostra 3 máquinas por vez
- **Navegação inteligente**: Botões habilitados apenas quando necessário
- **Estados dos botões**:
  - ← **Desabilitado** no primeiro grupo
  - → **Desabilitado** no último grupo
  - → **Desabilitado** se ≤ 3 máquinas total

### Exemplos de Navegação
```
Cenário 1: 5 máquinas
Grupo 1: [M1, M2, M3] ← desabilitado | → habilitado
Grupo 2: [M4, M5]     ← habilitado   | → desabilitado

Cenário 2: 2 máquinas  
Grupo 1: [M1, M2]     ← desabilitado | → desabilitado
```

## 🔍 Sistema de Busca com Popup

### Campo de Busca
- **Localização**: Ao lado dos controles do carrossel
- **Funcionalidade**: Busca por nome da máquina (case-insensitive)
- **Atalho**: Pressionar `Enter` executa a busca
- **Feedback**: Alerta se máquina não encontrada

### Popup de Detalhes
- **Ativação**: 
  - Via busca (digitando nome da máquina)
  - Clicando no cabeçalho da máquina na tabela
- **Conteúdo**:
  - Status atual da máquina
  - Métricas atuais (Temperatura, Vibração, RPM)
  - **Histórico das últimas 20 leituras** (ou todas se < 20)
  - Tabela scrollável com timestamps completos
- **Fechamento**:
  - Botão `×` no canto superior direito
  - Clicando fora do popup
  - Pressionando `ESC`

## 📋 Estrutura da Nova Tabela

### Cabeçalho
```
| Métrica     | CASE-TC5000-01 | CASE-TC5000-02 | NH-CR9000-01 |
```

### Linhas de Dados
```
| TEMPERATURA | 72°C           | 78°C           | 69°C         |
| VIBRAÇÃO    | 0.3g           | 0.6g           | 0.2g         |
| RPM         | 2100           | 2350           | 1950         |
| ÚLTIMA      | 14:32          | 14:31          | 14:33        |
```

## 🎨 Sistema de Cores Integrado

### Aplicação nas Colunas
- **Máquinas únicas**: Cor primária da marca
- **Máquinas duplicadas**: Sistema bicolor automático
- **Headers clicáveis**: Hover effect para indicar interatividade

### Cores por Status
- **Temperatura**: Verde (≤75°C) | Amarelo (76-85°C) | Vermelho (>85°C)
- **Vibração**: Verde (≤0.5g) | Amarelo (0.6-0.8g) | Vermelho (>0.8g)
- **RPM**: Amarelo (<1300) | Branco (≥1300)

## 💻 Implementação Técnica

### Variáveis Globais
```javascript
let currentTableIndex = 0;     // Índice do grupo atual
let totalMachines = 0;         // Total de máquinas
let allMachinesData = [];      // Dados de todas as máquinas
```

### Funções Principais
```javascript
renderStatusTable(maquinas, groupIndex)  // Renderiza grupo específico
scrollMaquinasTabela(direction)          // Navega entre grupos
buscarMaquina()                          // Executa busca
abrirPopupMaquina(maquinaId)            // Abre popup com detalhes
```

### Fluxo de Atualização
1. `atualizarStatusMaquinas()` busca dados da API
2. Armazena em `allMachinesData`
3. Renderiza primeiro grupo via `renderStatusTable()`
4. Atualiza controles do carrossel
5. Repete a cada 3 segundos

## 📱 Responsividade

### Desktop
- Tabela completa com 3 colunas de máquinas
- Popup centralizado (800px max-width)

### Mobile
- Tabela adaptável
- Popup ocupa 90% da largura
- Scroll vertical no histórico

## 🚀 Melhorias de UX

### Feedback Visual
- **Loading states**: "Carregando..." durante fetch
- **Empty states**: Mensagem quando sem dados
- **Error states**: Mensagem de erro em vermelho
- **Hover effects**: Indicação de elementos clicáveis

### Acessibilidade
- **Keyboard navigation**: Enter para buscar, ESC para fechar
- **Click outside**: Fecha popup clicando fora
- **Visual hierarchy**: Cores e tamanhos consistentes

## 📁 Arquivos Modificados

### `frontend/index.html`
- ✅ Campo de busca adicionado
- ✅ Estrutura do popup implementada
- ✅ Funções de busca e popup
- ✅ Nova lógica do carrossel
- ✅ Renderização reformulada

### `frontend/styles.css`
- ✅ Estilos do campo de busca
- ✅ Estilos do popup completo
- ✅ Headers clicáveis
- ✅ Responsividade do popup

### `frontend/demo-tabela.html`
- ✅ Demonstração interativa
- ✅ Dados simulados
- ✅ Todas as funcionalidades testáveis

## 🎯 Resultados Alcançados

### ✅ Requisitos Atendidos
- [x] Máquinas como colunas, métricas como linhas
- [x] Carrossel de grupos de 3 máquinas
- [x] Botões habilitados apenas quando necessário
- [x] Sistema de busca por nome
- [x] Popup centralizado com histórico
- [x] Últimas 20 leituras scrolláveis
- [x] Fechamento via X, clique fora ou ESC
- [x] Sistema bicolor integrado

### 🚀 Benefícios Adicionais
- **Performance**: Renderização otimizada por grupos
- **Usabilidade**: Interface mais intuitiva
- **Escalabilidade**: Funciona com qualquer quantidade de máquinas
- **Manutenibilidade**: Código modular e documentado

## 🧪 Como Testar

1. **Abrir `demo-tabela.html`** para ver funcionamento simulado
2. **Testar busca**: Digite "CASE-TC5000-02" e clique na lupa
3. **Testar popup**: Clique em qualquer cabeçalho de máquina
4. **Testar carrossel**: Use as setas ← → (simulado com alert)
5. **Testar fechamento**: ESC, clique fora, ou botão X

---

**Desenvolvido para o TCC FieldNode - SENAI 2024**  
*Sistema de telemetria offline-first para colheitadeiras agrícolas*