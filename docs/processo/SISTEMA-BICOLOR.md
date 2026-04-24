# Sistema Bicolor FieldNode 🎨

## Visão Geral

O Sistema Bicolor foi implementado para resolver o problema de diferenciação visual entre colheitadeiras do mesmo modelo mas com operadores diferentes, como **CASE-TC5000-01**, **CASE-TC5000-02** e **CASE-TC5000-03**.

## Como Funciona

### 1. Detecção de Duplicatas
O sistema analisa os IDs das máquinas e agrupa por modelo base:
- `CASE-TC5000-01` → modelo base: `CASE-TC5000`
- `CASE-TC5000-02` → modelo base: `CASE-TC5000`
- `CASE-TC5000-03` → modelo base: `CASE-TC5000`

### 2. Aplicação de Cores

#### Máquinas Únicas (Monocor)
- Se há apenas **1 máquina** de um modelo → usa **cor primária** da marca
- Exemplo: `JD-S700` → Verde puro (#4ade80)

#### Máquinas Duplicadas (Bicolor)
- **Primeira máquina** do modelo → **cor primária** pura
- **Demais máquinas** → **sistema bicolor** (primária + secundária)

### 3. Paleta de Cores por Marca

| Marca | Cor Primária | Cor Secundária | Exemplo |
|-------|-------------|----------------|---------|
| **CASE** | Vermelho (#f87171) | Vermelho Escuro (#ef4444) | CASE-TC5000 |
| **NH** | Amarelo (#fbbf24) | Laranja (#f59e0b) | NH-CR9000 |
| **JD** | Verde (#4ade80) | Verde Escuro (#22c55e) | JD-S700 |
| **MF** | Azul (#60a5fa) | Azul Escuro (#3b82f6) | MF-IDEAL9T |

## Implementação Técnica

### Função Principal
```javascript
function getMachineColor(maquinaId, allMachines = []) {
  // 1. Identifica marca da máquina
  // 2. Agrupa máquinas por modelo base
  // 3. Determina se usa monocor ou bicolor
  // 4. Retorna objeto com cores
}
```

### Retorno da Função
```javascript
// Máquina única
{ primary: '#f87171', secondary: null, isBicolor: false }

// Máquina duplicada
{ primary: '#f87171', secondary: '#ef4444', isBicolor: true }
```

### Aplicação Visual

#### Monocor
```css
.machine-id {
  color: #f87171; /* Cor primária */
  border-left: 4px solid #f87171;
}
```

#### Bicolor
```css
.machine-id {
  background: linear-gradient(135deg, #f87171 0%, #ef4444 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  border-left: 4px solid #f87171;
}

.machine-card {
  background: linear-gradient(135deg, #f8717108 0%, #ef444408 100%);
}
```

## Casos de Uso

### Cenário 1: Frota Diversificada
```
JD-S700        → Verde (monocor)
MF-IDEAL9T     → Azul (monocor)  
NH-CR8000      → Amarelo (monocor)
```

### Cenário 2: Múltiplas CASE-TC5000
```
CASE-TC5000-01 → Vermelho (monocor - primeira)
CASE-TC5000-02 → Vermelho + Vermelho Escuro (bicolor)
CASE-TC5000-03 → Vermelho + Vermelho Escuro (bicolor)
```

### Cenário 3: Múltiplas NH-CR9000
```
NH-CR9000-01   → Amarelo (monocor - primeira)
NH-CR9000-02   → Amarelo + Laranja (bicolor)
```

## Vantagens

✅ **Diferenciação Clara**: Operadores diferentes são visualmente distintos
✅ **Consistência de Marca**: Mantém identidade visual da marca
✅ **Escalabilidade**: Funciona com qualquer quantidade de duplicatas
✅ **Automático**: Não requer configuração manual
✅ **Responsivo**: Adapta-se dinamicamente à frota ativa

## Arquivos Modificados

- `frontend/index.html` → Função `getMachineColor()` atualizada
- `frontend/maquina.html` → Função `getMachineColor()` adicionada
- `frontend/styles.css` → Estilos bicolor adicionados
- `frontend/demo-cores.html` → Demonstração visual (novo)

## Demonstração

Abra `demo-cores.html` no navegador para ver o sistema em ação com dados simulados.

## Regex de Detecção

O sistema usa esta regex para extrair o modelo base:
```javascript
const modeloMatch = maquinaId.match(/^([A-Z-]+[A-Z0-9]+)(?:-\d+)?$/);
```

**Exemplos:**
- `CASE-TC5000-01` → `CASE-TC5000`
- `NH-CR9000-02` → `NH-CR9000`
- `JD-S700` → `JD-S700`

---

**Desenvolvido para o TCC FieldNode - SENAI 2024**