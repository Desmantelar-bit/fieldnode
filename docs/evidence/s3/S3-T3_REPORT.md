# S3-T3 · Faixa Atenção agora e fila P1/P2/P3

**Status: parcial.** A faixa e o resumo agregado foram implementados, com classificação heurística compartilhada. O teste com participante externo, a gravação/capturas e a tela própria da fila ainda não foram realizados.

## Diagnóstico

- A dashboard já mostrava `PriorityEvents`, mas consumia somente eventos e atualizava a cada 30 s.
- A listagem de eventos e decisões é paginada. Somar resultados no navegador não daria contagens globais confiáveis.
- A API filtra máquinas pelo usuário/organização via `get_machines_for_request`.
- A fórmula de `priority_score` permanece no backend e não usa Trust Score como multiplicador, conforme S1-T3.
- `docs/CLAIMS_VS_CODE.md` e uma rota `/decisoes` não existem neste checkout.

## Implementação

- Criado `contracts/attention.v1.json`, com P1 ≥ 0,60, P2 ≥ 0,30 e P3 abaixo de 0,30; crítico sempre P1. O contrato registra bandas como heurística não calibrada.
- Criado `GET /api/attention/summary/`, que conta decisões pendentes, decisões pendentes críticas (riscos críticos), eventos abertos críticos e máquinas cujo Trust agregado é inferior ao limite `LOW_TRUST_SCORE_THRESHOLD` existente (0,75). Retorna também os dez eventos abertos de maior prioridade, ordenados no banco.
- A consulta usa um endpoint e restringe as entidades às máquinas autorizadas. A contagem de dados instáveis reutiliza o critério de Trust baixo já existente; não foi criado threshold paralelo.
- `AttentionStrip` substitui `PriorityEvents` no topo do dashboard e atualiza por `usePolling` a cada 5 s. Evento com `needs_verification` mostra “Verificar sensor” sem alterar sua banda.
- Como ainda não existe fila de decisões, “Resolver agora” leva à listagem existente `/maquinas`. A fila dedicada é pendência da S3-T5.

## Origem das contagens

| Rótulo | Consulta |
| --- | --- |
| Decisões pendentes | `Decision.status=PENDENTE` |
| Riscos críticos | decisões pendentes com `severidade=CRITICO` |
| Eventos críticos | eventos abertos com `severidade=CRITICO` |
| Máquinas com confiança baixa | `MachineDataHealth.trust_score_medio < 0,75` |

## Validação e evidência

- Testes TypeScript dos limites 0.2999, 0.30, 0.5999, 0.60, score alto, crítico com score baixo e scores inválidos: **VERIFICADO** (execução descrita no relatório final da sessão).
- Testes da API para contagens, evento crítico, `needs_verification` e isolamento de organização: **VERIFICADO**, 2 testes aprovados.
- Inspeção de rede: o componente faz uma chamada a `/api/attention/summary/` por ciclo; não foi gravada uma sessão de navegador para medir tráfego real.
- Teste dos cinco segundos com pessoa externa: **NÃO VERIFICADO**. Nenhum participante foi testado e não há gravação/captura.
- E2E Playwright com evento criado durante polling: **NÃO VERIFICADO**.
- `npm run type-check`: **VERIFICADO**.
- `npm run lint`: **VERIFICADO**.
- `npm run test:contracts`: **VERIFICADO**, 3 testes aprovados (inclui limites P1/P2/P3 e override crítico).
- `python manage.py check` e `git diff --check`: **VERIFICADO**.
- `npm run build`: **VERIFICADO**, build de produção concluído.
- A execução ampla de eventos/decisões/saúde teve 1 falha: teste preexistente `test_leitura_com_temperatura_critica_gera_event_temp_alta` esperava evidência `boa`, recebeu `insuficiente`. A execução focada da faixa e de saúde passou: 22 testes.

## Arquivos e limites

Contrato, endpoint agregado, schema/serviço tipado, classificador, faixa, integração no dashboard e testes foram adicionados/alterados. Os cortes são heurísticas não calibradas. A UI chama “riscos críticos” as decisões pendentes críticas; eventos críticos são contados separadamente. Não há fila dedicada, gravação, teste humano nem E2E comprovando latência real.
