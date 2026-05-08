# Guia Rápido — Dia da Apresentação

**⏱️ Tempo total de setup: 5 minutos**

---

## 🚀 Setup Rápido (15 minutos antes)

### 1. Abrir 3 terminais

**Terminal 1 — Django API**:
```bash
cd C:\Users\AlunoDev25\Documents\Dev\TCC\Api-TCC
.venv\Scripts\activate
python manage.py runserver
```

**Terminal 2 — Simulador de Dados**:
```bash
cd C:\Users\AlunoDev25\Documents\Dev\TCC\Api-TCC
.venv\Scripts\activate
python esp_simulator_multi.py
```

**Terminal 3 — Validação (opcional)**:
```bash
cd C:\Users\AlunoDev25\Documents\Dev\TCC\Api-TCC
.venv\Scripts\activate
python validar_sistema.py
```

### 2. Abrir navegador com 4 abas

1. **Dashboard**: http://127.0.0.1:8000/
2. **Admin Django**: http://127.0.0.1:8000/admin/
3. **Swagger**: http://127.0.0.1:8000/swagger/
4. **Cola técnica**: Abrir `docs/DEFESA-BANCA.md` no VSCode

---

## 🎤 Roteiro de Demo (5 minutos)

### Slide 1: O Problema (30s)
**Fala**: "Colheitadeiras operam em áreas sem sinal. Dados de temperatura, vibração e RPM ficam presos no campo. Quebras inesperadas custam R$ 5.000 ou mais."

**Ação**: Nenhuma (apenas falar).

---

### Slide 2: A Solução (1min)
**Fala**: "FieldNode resolve isso com telemetria local via WiFi embarcado e sincronização automática quando a conectividade retorna."

**Ação**: 
1. Mostrar dashboard atualizando em tempo real
2. Apontar para as 4 máquinas com status colorido
3. Clicar em uma máquina CRÍTICA (vermelha)
4. Mostrar popup com análise de IA e histórico

---

### Slide 3: Arquitetura (1min)
**Fala**: "O ESP32 envia dados via WiFi local. O gateway recebe e envia para a API Django quando há conectividade. O sistema garante deduplicação por UUID e rejeita dados inválidos."

**Ação**:
1. Abrir aba do Swagger
2. Mostrar endpoint `/api/telemetria/`
3. Explicar: "Este é o endpoint que o ESP32 usa"
4. Abrir aba do Admin Django
5. Mostrar tabela `TelemetriaInvalida`
6. Explicar: "Dados rejeitados vão para auditoria, não corrompem a IA"

---

### Slide 4: Qualidade Técnica (1min)
**Fala**: "O sistema tem 19 testes automatizados cobrindo deduplicação, validação de range e resiliência da IA."

**Ação**:
1. Voltar para Terminal 3
2. Rodar: `python manage.py test api_tcc.tests`
3. Mostrar: "19 tests... OK"
4. Abrir VSCode em `api_tcc/services/telemetria.py`
5. Mostrar service layer com comentários
6. Explicar: "Regras de negócio separadas da view — arquitetura limpa"

---

### Slide 5: Viabilidade (1min)
**Fala**: "O custo é R$ 105 por máquina (hardware) mais R$ 3/mês de infraestrutura. Comparado com R$ 500-800/mês da Solinftec, o ROI é imediato."

**Ação**:
1. Mostrar slide com tabela de custos (se tiver)
2. Explicar próximos passos:
   - "Instalar ESP32 em 1 colheitadeira real por 30 dias"
   - "Coletar dados de campo"
   - "Retreinar IA com histórico real de falhas"

---

### Slide 6: Perguntas
**Fala**: "Estamos prontos para perguntas."

**Ação**: Ter `docs/DEFESA-BANCA.md` aberto para consulta rápida.

---

## 🚨 Plano B (Se Algo Quebrar)

### Dashboard não carrega
**Ação**:
1. Verificar se Django está rodando (Terminal 1)
2. Se não estiver, rodar: `python manage.py runserver`
3. Se ainda não funcionar, mostrar Swagger e fazer request manual

**Fala**: "O dashboard depende do servidor Django. Vou mostrar a API funcionando diretamente."

---

### IA dá timeout
**Ação**:
1. Abrir VSCode em `api_tcc/ia/manutencao.py`
2. Mostrar código de cache (linha ~8)
3. Explicar: "Com dados reais, o modelo seria pré-treinado offline"

**Fala**: "O cache de 30 segundos evita retreino a cada request. Em produção, serviríamos modelo pré-treinado."

---

### Simulador crasha
**Ação**:
1. Mostrar logs de execução anterior (se tiver)
2. Abrir VSCode em `esp_simulator_multi.py`
3. Mostrar código que gera caos (duplicatas, temperatura impossível)

**Fala**: "O simulador gera 3% duplicatas e 2% dados corrompidos para testar resiliência. O sistema detecta e rejeita em tempo real."

---

### Perguntam sobre os FKs
**Ação**:
1. Abrir `docs/DEFESA-BANCA.md` pergunta #1
2. Ler resposta preparada

**Fala**: "Modelamos assim para permitir auditoria histórica independente. Cada colheitadeira pode ter múltiplos registros de pressão ao longo da safra sem sobrescrever o dado anterior."

---

## 📋 Checklist 5 Minutos Antes

- [ ] Terminal 1: Django rodando (`Starting development server...`)
- [ ] Terminal 2: Simulador rodando (`Enviando leitura...`)
- [ ] Navegador: Dashboard mostrando 4 máquinas atualizando
- [ ] Navegador: Admin Django aberto e logado
- [ ] Navegador: Swagger aberto
- [ ] VSCode: `docs/DEFESA-BANCA.md` aberto
- [ ] Projetor: Testado e funcionando
- [ ] Áudio: Testado (se for usar)

---

## 🎯 Comandos Úteis Durante Demo

### Mostrar testes passando:
```bash
python manage.py test api_tcc.tests
```

### Validar sistema completo:
```bash
python validar_sistema.py
```

### Limpar banco e popular do zero:
```bash
python manage.py flush --no-input
python simular_dados.py
```

### Ver logs de erro:
```bash
type logs\fieldnode_errors.log
```

### Fazer request manual para API:
```bash
curl -X GET http://127.0.0.1:8000/api/metricas/
```

---

## 💡 Dicas de Apresentação

### O que fazer:
- ✅ Falar com confiança (você conhece o código)
- ✅ Mostrar código real (não apenas slides)
- ✅ Explicar decisões de design (não apenas o que faz)
- ✅ Admitir limitações (falta de dados reais)
- ✅ Focar no valor (offline-first resolve problema real)

### O que NÃO fazer:
- ❌ Pedir desculpas por limitações
- ❌ Dizer "não sei" sem tentar responder
- ❌ Ficar muito tempo em um slide
- ❌ Ler slides (falar naturalmente)
- ❌ Ignorar perguntas da banca

---

## 🎤 Frases-Chave para Usar

**Sobre arquitetura**:
"Separamos regras de negócio da view usando service layer — isso permite reusar a mesma lógica via HTTP e MQTT."

**Sobre qualidade**:
"Temos 19 testes automatizados cobrindo os comportamentos críticos: deduplicação, validação de range e resiliência da IA."

**Sobre IA**:
"Usamos Isolation Forest para detecção de anomalias e Random Forest para manutenção preditiva, com features temporais como rolling windows e tendência térmica."

**Sobre viabilidade**:
"O custo é R$ 105 por máquina contra R$ 500-800/mês da Solinftec. Uma quebra evitada paga o sistema de 10 máquinas."

**Sobre próximos passos**:
"O próximo passo é instalar em 1 colheitadeira real por 30 dias e coletar dados de campo. Com histórico real de falhas, retreinaríamos a IA com labels supervisionados."

---

## 📞 Contatos de Emergência

**Se algo der muito errado**:
1. Respirar fundo
2. Voltar para o Plano B
3. Focar no que funciona (testes, Swagger, código)
4. Lembrar: a banca quer que você passe

**Lembrete final**: Você conhece o código melhor que qualquer um na sala. Confiança é metade da nota.

---

**Boa sorte! 🚀**
