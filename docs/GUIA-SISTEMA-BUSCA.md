# 🔍 Sistema de Busca e Autocompletar - FieldNode

## ✨ Novas Funcionalidades Implementadas

### 1. Autocompletar Inteligente
- **Digite e veja sugestões em tempo real**
- Busca por qualquer parte do nome da máquina
- Mostra temperatura, vibração e RPM de cada máquina
- Design moderno com dropdown estilizado

### 2. Popup de Detalhes
- **Clique em qualquer sugestão** para abrir popup com informações completas
- Mostra telemetria em tempo real
- Análise preditiva de IA (anomalias e manutenção)
- Botão para ver histórico completo

### 3. Novas Máquinas Cadastradas

#### New Holland (3 máquinas)
- `NH-CR9000-01` - Crítico (superaquecimento)
- `NH-CR8090-02` - Operação normal
- `NH-CR7090-03` - Atenção (temperatura elevada)

#### Valtra (3 máquinas)
- `VALTRA-BC8800-01` - Operação normal
- `VALTRA-BC6800-02` - Operação normal
- `VALTRA-BC5800-03` - Atenção (temperatura elevada)

#### CASE (2 máquinas - já existentes)
- `CASE-TC5000-01` - Operação normal
- `CASE-TC5070-01` - Atenção

**Total: 8 máquinas ativas**

---

## 🚀 Como Testar

### Passo 1: Iniciar o Sistema

```bash
# Terminal 1 - Django
python manage.py runserver

# Terminal 2 - MQTT Listener
python scripts/mqtt_listen.py

# Terminal 3 - Simulador (com novas máquinas)
python scripts/simular_mqtt.py
```

### Passo 2: Acessar o Dashboard

```
http://127.0.0.1:8000/frontend/dashboard.html
```

### Passo 3: Testar o Autocompletar

#### Teste 1: Buscar por fabricante
1. Clique no campo de busca
2. Digite: `CASE`
3. **Resultado esperado**: Dropdown mostra 2 máquinas CASE

#### Teste 2: Buscar New Holland
1. Digite: `NH`
2. **Resultado esperado**: Dropdown mostra 3 máquinas New Holland

#### Teste 3: Buscar Valtra
1. Digite: `VALTRA`
2. **Resultado esperado**: Dropdown mostra 3 máquinas Valtra

#### Teste 4: Buscar por modelo específico
1. Digite: `CR9000`
2. **Resultado esperado**: Mostra apenas NH-CR9000-01

#### Teste 5: Buscar parcial
1. Digite: `BC`
2. **Resultado esperado**: Mostra todas as 3 Valtras (BC8800, BC6800, BC5800)

### Passo 4: Testar o Popup

1. Digite qualquer termo de busca (ex: `NH`)
2. Clique em uma das sugestões no dropdown
3. **Resultado esperado**:
   - Popup abre automaticamente
   - Mostra ID e modelo da máquina
   - Exibe telemetria em tempo real
   - Mostra análise de IA (anomalias e risco de manutenção)
   - Barra de progresso colorida indica nível de risco

### Passo 5: Testar Navegação

1. No popup, clique em "📊 Ver Detalhes"
2. **Resultado esperado**: Redireciona para página de detalhes da máquina

---

## 🎯 Cenários de Demonstração para a Banca

### Cenário 1: Busca Rápida em Campo
**Situação**: Operador precisa verificar status de uma máquina específica

1. Digite `NH-CR9000` no campo de busca
2. Clique na sugestão
3. Popup mostra que está em estado CRÍTICO
4. Análise de IA indica alta probabilidade de manutenção

**Mensagem**: "Sistema permite localização instantânea de qualquer máquina da frota"

### Cenário 2: Monitoramento por Fabricante
**Situação**: Gestor quer ver todas as máquinas de um fabricante

1. Digite `VALTRA`
2. Veja as 3 máquinas listadas com status em tempo real
3. Compare temperatura e vibração entre elas

**Mensagem**: "Facilita gestão de frota heterogênea com múltiplos fabricantes"

### Cenário 3: Identificação de Anomalias
**Situação**: Buscar máquina com problema reportado

1. Digite `CR9000` (máquina crítica)
2. Popup mostra temperatura > 85°C
3. IA detecta anomalias e alto risco de manutenção

**Mensagem**: "Sistema integra busca com análise preditiva em tempo real"

---

## 🐛 Troubleshooting

### Problema: Dropdown não aparece
**Solução**: 
- Verifique se o simulador está rodando
- Aguarde 3 segundos para o polling atualizar
- Recarregue a página (F5)

### Problema: Máquinas não aparecem na busca
**Solução**:
```bash
# Reinicie o simulador
python scripts/simular_mqtt.py
```

### Problema: Popup não abre
**Solução**:
- Verifique console do navegador (F12)
- Confirme que a API está respondendo: http://127.0.0.1:8000/api/leituras/ultimas/

### Problema: Só aparecem 3 máquinas CASE
**Solução**:
- Pare o simulador antigo (Ctrl+C)
- Inicie o novo: `python scripts/simular_mqtt.py`
- Aguarde 5 segundos para as novas máquinas aparecerem

---

## 📊 Métricas Esperadas

Após iniciar o simulador, você deve ver:

- **Total de Leituras**: Aumentando continuamente
- **Máquinas Ativas**: 8 (ou quantas estiverem enviando dados)
- **Taxa de Rejeição**: < 1%

---

## 🎨 Detalhes Técnicos

### Autocompletar
- **Tecnologia**: JavaScript vanilla (sem dependências)
- **Latência**: < 50ms (busca local nos dados já carregados)
- **Atualização**: Sincronizada com polling de 3s

### Popup
- **Carregamento**: Assíncrono (mostra dados básicos imediatamente)
- **IA**: Carregada em paralelo (não bloqueia abertura)
- **Animação**: Fade-in suave com backdrop blur

### Simulador
- **Intervalo**: 2.5s por ciclo completo
- **Máquinas**: 8 simultâneas
- **Variação**: Temperatura, vibração e RPM realistas

---

## ✅ Checklist de Apresentação

- [ ] Sistema iniciado (Django + MQTT + Simulador)
- [ ] Dashboard carregado e atualizando
- [ ] Testado busca por "CASE" (2 resultados)
- [ ] Testado busca por "NH" (3 resultados)
- [ ] Testado busca por "VALTRA" (3 resultados)
- [ ] Popup abrindo corretamente
- [ ] IA mostrando análise preditiva
- [ ] Navegação para detalhes funcionando

---

## 🎤 Roteiro de Demonstração (30 segundos)

1. **Mostrar dashboard** com 8 máquinas ativas
2. **Digitar "NH"** no campo de busca
3. **Mostrar dropdown** com 3 sugestões New Holland
4. **Clicar em NH-CR9000-01** (máquina crítica)
5. **Mostrar popup** com temperatura 85°C+ e análise de IA
6. **Destacar**: "Sistema offline-first com busca inteligente e IA preditiva"

---

**Desenvolvido por**: Equipe FieldNode - SENAI-SP 2026
