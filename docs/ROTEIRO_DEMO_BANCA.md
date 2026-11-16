# Roteiro de demonstração de bancada - S8-T6

Este roteiro é para uma demonstração física de operação offline. Ele não publica
`0% de perda`, `alerta em menos de 3 s` ou qualquer outro número antes de medir.
Os números do slide devem sair de `simulators/teste_resiliencia.py` e dos três
ensaios físicos registrados no relatório S8-T6.

## Pré-requisitos

- S8-T1 a S8-T5 e S6-T5 revisados.
- Notebook, gateway, sensor, alimentação e hotspot identificados.
- Dashboard local e logs seriais abertos antes da banca.
- `FIELDNODE_DEVICE_KEY` disponível somente no processo autorizado do ensaio.
- Cronômetro ou gravação contínua com relógio visível.
- Fallback: vídeo real da terceira execução, com localização registrada no relatório.

## Execução cronometrada

1. **Online, 0:00:** mostrar a leitura fluindo; registrar `device_id`, `boot_id` e sequência.
2. **Corte, T0:** interromper apenas o uplink do notebook. Não alterar código, configuração ou alimentação.
3. **Offline:** confirmar o último dado conhecido no dashboard local e registrar o estado stale.
4. **Estímulo seguro:** aquecer o sensor pelo método aprovado e iniciar o cronômetro.
5. **Alerta:** registrar o instante no gateway, buzzer, LED ou dashboard. Calcular `t_alerta`; não presumir 3 s.
6. **Reconexão:** religar o uplink e aguardar o painel de sincronização mostrar o backlog reduzindo.
7. **Integridade:** conferir geradas, persistidas, sincronizadas, duplicatas e identificadores.
8. **Decisão:** mostrar a decisão pendente pelo fluxo real e aprová-la com ação humana registrada.

## Checklist de segurança

- [ ] cabos e alimentação inspecionados;
- [ ] dispositivos estáveis e protegidos;
- [ ] estímulo térmico aprovado e interrompível;
- [ ] sem chama, curto ou conexão elétrica improvisada;
- [ ] corte e recuperação de rede identificados;
- [ ] responsável pela execução definido;
- [ ] qualquer participante pode interromper a demonstração.

## Três ensaios obrigatórios

| Ensaio | Início | Corte | Alerta | Reconexão | Backlog final | Intervenções | Estado |
|---|---|---|---:|---|---:|---|---|
| R1 | NÃO EXECUTADO | NÃO EXECUTADO | NÃO MEDIDO | NÃO EXECUTADO | NÃO MEDIDO | - | PENDENTE |
| R2 | NÃO EXECUTADO | NÃO EXECUTADO | NÃO MEDIDO | NÃO EXECUTADO | NÃO MEDIDO | - | PENDENTE |
| R3 | NÃO EXECUTADO | NÃO EXECUTADO | NÃO MEDIDO | NÃO EXECUTADO | NÃO MEDIDO | - | PENDENTE |

O vídeo da terceira execução só deve ser referenciado depois de existir em caminho real.
Se uma execução falhar, preservar logs e usar o vídeo validado, sem editar a continuidade.

## Fallback e limites

Se sensor, rádio, dashboard, alerta ou sincronização falhar, apresentar o vídeo identificado.
Não acionar alerta manualmente nem declarar operação local contínua sem evidência. A demonstração
física e os resultados automatizados de `teste_resiliencia` são evidências distintas.
