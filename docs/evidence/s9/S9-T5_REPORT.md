# S9-T5 - Incident Engine v0.1

Foi criado o modelo persistente `Incident` com `IncidentEvent`, preservando os
eventos individuais, contexto organizacional, estado aberto/fechado, rótulo
`Sintomas simultâneos` e hipótese opcional não confirmada. O serviço
`api_tcc/services/incidents.py` usa janela configurável de 10 minutos baseada
no `event_time`, é idempotente e não agrupa eventos sem timestamp factual.

A integração ocorre depois da persistência do evento. Falha no agrupamento é
registrada sem apagar o Event. O cooldown de 15 minutos existente não foi
alterado. A API de leitura está em `GET /api/incidents/` com isolamento pelas
máquinas acessíveis ao usuário.

Evidência automatizada: `python -m pytest api_tcc/tests/test_s9_t4_t5.py api_tcc/tests/test_consequence.py -q` passou com 12 testes, incluindo três eventos em oito minutos em um incidente e outro evento em quarenta minutos em novo incidente.

Limitações: a primeira versão agrupa por máquina; agrupamento entre máquinas
por frente/grafo e interface dedicada de incidentes ainda não foram adicionados.
Os testes são sintéticos e não constituem validação física ou causal em campo.
