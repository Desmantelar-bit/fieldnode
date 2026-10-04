# Status S6-T3

**Decisão:** obsoleto / superado arquiteturalmente. Não implementar o cartão como escrito.

O cartão pressupõe um `frontend/dashboard.html` monolítico para modularizar. Esse arquivo não faz parte da arquitetura atual: o frontend ativo é `frontend-next`, baseado em Next.js, React e TypeScript. A modularidade pretendida já foi absorvida pela migração.

| Requisito original | Situação atual |
| --- | --- |
| Modularizar `dashboard.html` | Não aplicável: o arquivo legado não existe na arquitetura atual. |
| Extrair `charts.js`, `prescricao.js` e `popup.js` | Não aplicável: não recriar módulos vanilla; a separação pertence à arquitetura React existente. |
| Manter HTML como orquestrador fino | Superado pelo dashboard React e seus componentes. |
| Evitar introduzir React/TypeScript | Premissa desatualizada: essa já é a stack do frontend ativo. |
| Dependência S6-T1 | Considerada atendida na auditoria fornecida. |

**Registro:** “S6-T3 obsoleto — objetivo já coberto pelo frontend-next”. Os critérios literais do cartão (extração dos três arquivos, contagem antes/depois e regressão visual) não foram executados, pois seu objeto não existe na arquitetura atual. Nenhum código foi alterado; não recriar `dashboard.html` nem introduzir JavaScript vanilla para satisfazer o cartão.