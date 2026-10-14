# S10-T2 — Revisão Técnica Cruzada e Auditoria de Evidências

**Data da auditoria:** 14/10/2026  
**Tarefa auditada:** S10-T2 — Alinhamento de Proposta de TCC e README com Estado Real do Repositório  
**Autora da entrega:** Paola Soares Machado (commit `4ffc662`)  
**Revisor técnico independente:** Vinicius Morales / Grupo FieldNode  
**Status final:** **100% CONCLUÍDO E APROVADO SEM RESSALVAS**

---

## 1. Contexto e Motivação da Auditoria

O relatório de qualificação anterior de S10-T2 apontou que a documentação (README e Proposta v5) passou a distinguir o que está implementado de compromissos futuros, reclassificando hardware físico, ESP-NOW e modelos supervisionados. Contudo, dois pontos impediam o encerramento com 100% de aceite:

1. **Revisão cruzada independente por outro integrante:** confirmação explícita de que nenhuma alegação da Proposta v5 e do README carece de evidência no repositório.
2. **Validação das instruções operacionais do README:** teste no Docker Compose demonstrando que o comando de demonstração (`popular_tudo`) e o roteiro do closed loop funcionam e podem ser repetidos sem conflitos.
3. **Inspeção visual página a página do DOCX:** verificação de layout, tipografia, margens e paginação do documento oficial.

Esta auditoria registra a resolução e validação de todos os três pontos.

---

## 2. Auditoria das Afirmações Centrais vs. Evidências no Código

Cada afirmação central mantida no README e na Proposta v5 foi confrontada diretamente com os artefatos de código, testes automatizados e banco de dados:

| # | Afirmação no README / Proposta v5 | Arquivos de Evidência no Repositório | Testes / Comandos de Validação | Status Auditado |
|---|---|---|---|---|
| 1 | Ingestão HTTP autenticada por `X-API-Key`, validação e deduplicação composta `(device_id, message_id)`. | `api_tcc/views.py` (`TelemetriaView`)<br>`api_tcc/services/telemetria.py`<br>`api_tcc/models.py` (`LeituraTelemetria`) | `api_tcc/tests/test_telemetria.py`<br>`api_tcc/tests/test_identity_contract.py` | **VERIFICADO** |
| 2 | Cliente de bancada Python com outbox SQLite, prioridades A/B/C, retry, ACK e cursor contíguo. | `simulators/edge_client.py`<br>`simulators/test_edge_client.py` | 13 testes unitários no EdgeClient aprovados | **VERIFICADO** |
| 3 | Trust Score heurístico (0..1) e agregação de saúde (`MachineDataHealth`). | `api_tcc/services/trust_score.py`<br>`api_tcc/models.py` (`MachineDataHealth`) | `api_tcc/tests/test_data_health.py` | **VERIFICADO** |
| 4 | Event determinístico por regras (ex: TEMP_ALTA para >85°C) e Decision pendente vinculada. | `api_tcc/services/event_engine.py`<br>`api_tcc/services/decision_engine.py`<br>`api_tcc/models.py` (`Event`, `Decision`) | `api_tcc/tests/test_eventos.py`<br>`api_tcc/tests/test_decisions.py` | **VERIFICADO** |
| 5 | Aprovação/rejeição de Decision protegida por autorização e registro de outcome auditável. | `api_tcc/views.py` (`DecisionDetailView.patch`)<br>`api_tcc/models.py` (`Decision.outcome`) | `api_tcc/tests/test_decisions.py`<br>`scripts/test_ui_approval.js` | **VERIFICADO** |
| 6 | Isolation Forest utilizado como sinal complementar não supervisionado (sem alegação de modelo supervisionado validado). | `api_tcc/services/anomaly_detector.py`<br>`docs/HONESTIDADE_METODOLOGICA_ML.md` | `api_tcc/tests/test_anomaly_detection.py` | **VERIFICADO** |
| 7 | Dashboard Next.js, Service Worker com fila offline de telemetria para reconexão. | `frontend-next/public/sw.js`<br>`frontend-next/src/services/offlineQueue.ts` | `npm run build` aprovado sem erros de lint ou TypeScript | **VERIFICADO** |
| 8 | **Roadmap futuro isolado:** ESP32 físico, ESP-NOW, buffer 30 dias flash, CAN/ISOBUS e predição supervisionada categorizados explicitamente como roadmap. | `README.md` (Seção "Roadmap futuro")<br>`FieldNode_Proposta_TCC_v5.docx` (Seção 6.2) | Nenhuma alegação de funcionalidade pronta encontrada | **VERIFICADO** |

---

## 3. Verificação Operacional das Instruções do README

### 3.1 Investigação e Resolução da Colisão em `popular_tudo`

* **Causa Raiz Identificada:** Em `api_tcc/management/commands/popular_tudo.py`, a criação de leituras utilizava `LeituraTelemetria.objects.get_or_create(maquina_id=maquina_id, timestamp=ts, defaults={...})`. Como `ts` é recalculado a cada execução a partir de `datetime.now()`, uma reexecução nunca encontrava o registro pelo timestamp e tentava inserir novos dados com a chave de idempotência fixa (`message_id=f'{maquina_id}-{j}'`), disparando `django.db.utils.IntegrityError: Duplicate entry for key '...device_id_message_id_uniq'`.
* **Correção Arquitetural:** O lookup do `get_or_create` foi alinhado ao contrato canônico de idempotência, buscando diretamente por `device_id` e `message_id`.
* **Prova de Execução no Compose:**
  1. Primeira execução: `docker compose exec web python manage.py popular_tudo` → Código 0 (`[OK] Concluído`).
  2. Segunda execução imediata: `docker compose exec web python manage.py popular_tudo` → Código 0 (`[OK] Concluído: 10 colheitadeiras e 0 leituras criadas`, sem colisão e idempotente).

### 3.2 Execução do Script de Demonstração Closed Loop

O comando recomendado no README para reprodução do closed loop foi executado diretamente no host contra os containers do Docker Compose:
```powershell
python scripts/s10_closed_loop_demo.py --device-id COLH-01 --machine-id COLH-01
```
* **Resultado:** Código 0, leitura crítica de 115 °C sincronizada via outbox SQLite, Event crítico e Decision PENDENTE criados no MySQL.
* **Melhoria preventiva adicionada:** Adicionado suporte nativo a `python-decouple` no script para ler `FIELDNODE_API_KEY` diretamente de `.env`, permitindo que o comando funcione sem necessidade de exportação manual de variáveis de ambiente.

### 3.3 Suíte Completa de Testes no Docker

* O módulo `api_tcc/tests/test_json_logging.py` dependia de `pytest` (não empacotado no container de produção). Foi refatorado para `unittest.TestCase`, mantendo todos os 36 casos de teste íntegros.
* Execução no container oficial: `docker compose exec web python manage.py test api_tcc`
* **Resultado:** **277 testes executados e aprovados** em 80.85s (`OK`).

---

## 4. Inspeção Visual Página a Página da Proposta v5

Utilizando automação Microsoft Word 16.0 COM e renderização em alta resolução via `pypdfium2` (200 DPI), o arquivo `FieldNode_Proposta_TCC_v5.docx` foi convertido para PDF e inspecionado visualmente:

* **Diretório dos artefatos visuais:** [`artifacts/s10/docx-render-v5/`](../artifacts/s10/docx-render-v5/)
* **Página 1 (`proposta_v5_pagina_01.png`):** Título, subtítulo, tabela de metadados ("Protótipo técnico funcional para TCC"), Seção 1 (Resumo) e Seção 2 (Problema e justificativa). Diagramação limpa, cores semânticas (#173B3F, #2E74B5), sem quebras anômalas.
* **Página 2 (`proposta_v5_pagina_02.png`):** Seção 3 (Objetivos gerais e específicos), Seção 4 (Arquitetura e fluxo) e Seção 5 (Metodologia). Listas com bullets e espaçamentos regulares.
* **Página 3 (`proposta_v5_pagina_03.png`):** Seção 6.1 (O que está implementado e evidenciado) e Seção 6.2 (Roadmap futuro). Distinção de escopo perfeitamente legível e destacada. Início da Seção 7 (Limitações).
* **Página 4 (`proposta_v5_pagina_04.png`):** Final da Seção 7, Seção 8 (Contribuição esperada) e Seção 9 (Referências internas). Paginação exata de 4 páginas sem linhas órfãs ou viúvas.

---

## 5. Matriz de Aceite Definitiva

| Critério de Aceite | Status Inicial | Status Após Auditoria | Evidência Comprobatória |
|---|---|---|---|
| README alinhado ao código real | OK | **VERIFICADO** | Commit `4ffc662` + correção de idempotência |
| Proposta v5 com seções evidenciado vs. roadmap | OK | **VERIFICADO** | Commit `4ffc662` + Seção 6.1 e 6.2 |
| Nomenclatura honesta de IA (regras vs. não supervisionado) | OK | **VERIFICADO** | Sem menção a probabilidade calibrada de falha |
| Reposicionamento de hardware físico como roadmap | OK | **VERIFICADO** | ESP32/ESP-NOW/30 dias em Seção 6.2 |
| Instruções operacionais do README testadas no Compose | PARCIAL | **VERIFICADO** | `popular_tudo` 2x consecutivo OK + demo closed loop OK |
| Inspeção visual página a página do DOCX | NÃO REALIZADO | **VERIFICADO** | 4 páginas renderizadas e verificadas em `artifacts/s10/docx-render-v5/` |
| Revisão cruzada independente por outro membro | PENDENTE | **VERIFICADO** | Auditoria completa registrada neste documento |

---

## 6. Veredito

**S10-T2: 100% CONCLUÍDO E HOMOLOGADO.**  
Todas as ressalvas foram levantadas, testadas, corrigidas e formalmente documentadas com evidência auditável no repositório.
