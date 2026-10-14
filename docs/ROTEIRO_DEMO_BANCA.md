# Roteiro de demonstração da banca - S10

**Objetivo.** Demonstrar o closed loop de software do FieldNode: leitura de telemetria, cálculo do Trust Score, criação de Event, persistência de Decision, aprovação humana autenticada e registro de outcome.

O roteiro não prova leitura de um sensor físico, redução de custo, prevenção de falha em campo ou execução mecânica numa máquina. A temperatura crítica é uma entrada determinística de simulador. O sistema registra a recomendação; a execução física continua fora do escopo.

## Pré-requisitos

- Docker Desktop com o engine `dockerDesktopLinuxEngine` em execução.
- Arquivo `.env` preenchido localmente, sem colocar chaves neste documento.
- `FIELDNODE_API_KEY` disponível apenas no shell que executa o simulador.
- `FIELDNODE_AUTH_TOKEN` disponível apenas no shell do executor para consultar a prescrição canônica; obtenha-o pelo login autorizado, sem registrá-lo no roteiro ou no vídeo.
- Python do ambiente virtual para o executor local, ou `docker compose exec web` para comandos dentro do Compose.
- Conta autorizada para o dashboard. A senha deve ser obtida por canal seguro.

## Preparação

```powershell
docker compose config --quiet
docker compose up --build -d
docker compose ps
docker compose exec web python manage.py migrate
docker compose exec web python manage.py popular_tudo
Invoke-RestMethod http://127.0.0.1:8000/api/health/
```

O `popular_tudo` reaproveita entidades existentes e marca máquinas criadas por ele como `Machine.is_demo=True`, mas a execução local encontrou colisão de chave composta em dados residuais. Trate falha do seed como falha de preparação e corrija o estado pelo procedimento oficial do ambiente, sem apagar volumes por reflexo. Não use `docker compose down -v` como preparação normal, porque isso apaga o banco inteiro.

## Ensaio cronometrado de 5-7 minutos

| Tempo | Ação | Evidência | Narração |
|---|---|---|---|
| 0:00-0:40 | Mostrar `docker compose ps` e `/api/health/`. | `web`, `db`, `mosquitto` saudáveis e JSON com `status: ok`. | “O ambiente está de pé antes de qualquer dado ser enviado.” |
| 0:40-1:40 | Executar `python scripts/s10_closed_loop_demo.py --device-id COLH-01 --machine-id COLH-01`. | ACK com `message_id`, `payload_hash`, cursor e `reading_id`; temperatura 115 °C. | “A leitura vem pelo cliente de borda real, que grava na outbox antes do envio.” |
| 1:40-2:30 | Abrir a leitura no Admin ou consultar `/api/telemetria/?maquina_id=COLH-01` autenticado. | `trust_score` entre 0 e 1 e associação à `Machine` correta. | “Trust Score é um escore heurístico dos critérios implementados, não uma verdade física do sensor.” |
| 2:30-3:30 | Abrir `/maquinas/COLH-01/prescricao` no dashboard, que consulta `/api/prescricoes/COLH-01/`. | `decision_id` pendente; no Admin, Event `TEMP_ALTA` com `severidade=CRITICO`. O status agregado da análise pode permanecer `ATENCAO` quando o histórico da máquina dilui um sinal isolado. | “A regra crítica de temperatura gerou um Event persistido; a decisão exibida aponta para esse Event, sem confundir score agregado com severidade factual.” |
| 3:30-4:40 | Fazer login, revisar a recomendação e clicar **Aprovar ação**. | Resposta 200; Decision passa a `APROVADA`; usuário e horário persistidos. | “A recomendação não se autoautoriza: existe revisão humana.” |
| 4:40-5:40 | Registrar uma observação factual, por exemplo: “Aprovação realizada durante a demonstração; execução física não realizada.” | `outcome_texto` persistido no retorno e no Admin. | “Outcome documental não é prova de intervenção mecânica.” |
| 5:40-6:40 | Mostrar Admin: `LeituraTelemetria`, `Event`, `Decision` e `MachineDataHealth`. | IDs e relações batem com a saída do executor. | “A história é rastreável no banco, não só desenhada na tela.” |

Para demonstrar também a transição de execução, só clique **Marcar como executada** se uma execução correspondente realmente tiver ocorrido. Para a banca técnica padrão, termine em `APROVADA` com outcome documental honesto.

## Procedimento de repetição

Cada ensaio usa uma nova `message_id` e um novo `reading_id`, preservando a outbox e o cursor do EdgeClient. Registre o JSON impresso em `artifacts/s10/ensaio-XX.json`. A execução só conta como qualificação quando Compose, persistência, Trust Score, Event, Decision, aprovação no dashboard e outcome forem confirmados.

Não misture uma execução local SQLite com uma execução Compose na mesma contagem. O critério S10 exige três execuções Compose consecutivas. Se o segundo ensaio falhar, reinicie a sequência depois da correção.

## Troubleshooting

- **Docker indisponível:** confirme `docker version` e inicie Docker Desktop. Não marque o ensaio como executado.
- **`web` não fica saudável:** veja `docker compose logs web db --tail=100`; confirme `.env`, migrações e conectividade com `db`.
- **401 na ingestão:** confira apenas se o shell usa a mesma `FIELDNODE_API_KEY` do `.env`; não imprima a chave.
- **Leitura rejeitada:** confira ranges e campos do payload. Não desative validação.
- **Decision não aparece:** confira a resposta do executor, `decision_status` e a prescrição da mesma máquina; aguarde somente o tempo necessário para a leitura ficar disponível.
- **Cooldown:** use uma nova execução identificável e respeite o cooldown. Não altere o banco diretamente para forçar Event.
- **Aprovação rejeitada:** confirme login, token e permissão da organização; o backend exige `IsAuthenticated` e autorização para a Machine.
- **Dashboard stale:** recarregue a rota e confirme o retorno do endpoint, distinguindo dado antigo de erro.

## Evidência e contingência

O vídeo de fallback deve ser gravado durante a terceira execução qualificada e precisa mostrar ambiente, leitura, score, Event, Decision, aprovação e outcome sem expor credenciais. Um vídeo prova uma execução anterior; não substitui a verificação do estado atual.

Se a captura não estiver disponível, guarde os JSONs, logs e capturas de tela legíveis e registre o vídeo como **NÃO PRODUZIDO**. Não converter intenção em evidência, porque a banca costuma perceber esse truque antes do segundo slide.
