# Incident Engine v0.1

O Incident Engine agrupa `Event` existentes em um `Incident` persistente. Ele
reduz repetição visual sem apagar alertas, alterar severidade ou substituir o
cooldown/deduplicação do Event Engine.

## Regra de agrupamento

A janela inicial é `INCIDENT_WINDOW_MINUTES = 10`. A referência é sempre o
`event_time` de `LeituraTelemetria.timestamp`; sem esse horário factual o evento
fica sem agrupamento. Eventos da mesma máquina e organização podem compartilhar
um incidente aberto dentro da janela. O incidente é encerrado somente por fluxo
explícito.

O rótulo padrão é **Sintomas simultâneos**. Proximidade temporal é correlação
operacional, não causa confirmada. `hipotese_causa` permanece nulo até existir
uma hipótese fornecida por fonte autorizada e deve ser exibida como não
confirmada.

`IncidentEvent` preserva cada evento original e possui unicidade por incidente
e evento, tornando a associação idempotente. A organização vem da máquina do
evento; não há fallback para outra organização.

O custo de parada é uma premissa opcional em `OrganizationPolicy` e não possui
valor padrão. Quando existe custo BRL válido e horizonte calculado pelo
Consequence Engine, a fórmula é `custo_hora_parada * horizonte_minutos / 60`.
O resultado é uma estimativa matemática com premissa do cliente, nunca prejuízo
confirmado. A funcionalidade não pertence ao pitch.
