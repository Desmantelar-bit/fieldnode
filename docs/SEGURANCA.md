# Segurança

Este documento registra o modelo de segurança atual do FieldNode. Ele descreve o estado do MVP, não uma promessa de segurança de produção.

## Autenticação

- A autenticação administrativa atual usa DRF `TokenAuthentication`.
- `POST`, `PUT`, `PATCH` e `DELETE` nos cadastros administrativos exigem usuário autenticado.
- `POST /api/telemetria/` e `POST /api/telemetria/lote/` continuam sendo endpoints máquina-a-máquina protegidos por `X-API-Key`, validada no backend.
- GETs públicos existem para demonstração, dashboard e consultas operacionais do MVP.
- O frontend usa `Authorization: Token <token>` para operações autenticadas e não deve receber `FIELDNODE_API_KEY`.
- O BFF Next.js já mantém o token DRF em cookie `HttpOnly` (`fieldnode_session`); o browser recebe apenas dados de perfil. `localStorage` armazena somente o perfil visual, nunca o token.

## MQTT por dispositivo (S2-T1)

Cada dispositivo autentica com username igual ao `device_id`. `DeviceCredential` guarda o hash Django da credencial, estado de provisionamento, estado ativo/revogado e datas de ciclo de vida; o Mosquitto mantém o hash no password file no formato produzido por `mosquitto_passwd`. A senha em claro é gerada pelo provisionador e exibida uma única vez. Ela não é persistida no banco ou repositório.

`mosquitto/acl.conf` aplica estas permissões:

- `fieldnode-worker`: lê `fieldnode/+/telemetria` e `fieldnode/+/status`, escreve somente em `fieldnode/_ack/#`.
- usuário de dispositivo `%u`: escreve somente em `fieldnode/%u/telemetria` e `fieldnode/%u/status`, lê somente `fieldnode/_ack/%u`.

O worker exige `MQTT_WORKER_USERNAME=fieldnode-worker` e um arquivo secreto em `MQTT_WORKER_PASSWORD_FILE`; segredo ausente resulta em erro de inicialização sem tentativa anônima. O callback também valida forma do tópico, JSON, existência de credencial ativa e igualdade exata entre `device_id` do payload e do tópico. Divergências são persistidas em `DeadLetterEntry` com `contexto=MQTT_SPOOF`, sem processar leitura ou estado de máquina. `maquina_id` não prova identidade.

Provisionamento local: execute primeiro `python scripts/provision_mqtt_worker.py`; o segredo do worker fica em `mosquitto/worker-secrets/worker_password`, diretório ignorado pelo Git, e o hash entra em `mosquitto/broker-secrets/passwordfile`. Então execute `python scripts/provision_device.py <device_id>`. Ambos exigem `mosquitto_passwd` no PATH, não passam senha em argumentos de processo, e recusam sobrescrever credencial existente sem `--rotate`. Revogue com `python scripts/provision_device.py --revoke <device_id>`; reprovisione uma identidade revogada com `--rotate`. O Compose monta o diretório de hashes somente no broker; no boot, o entrypoint copia o password file para o volume privado `/mosquitto/data` e o entrega ao UID/GID 1883 usado pelo broker. O broker é reiniciado automaticamente se estiver ativo, encerrando sessões MQTT existentes para que credencial revogada/substituída não continue válida numa conexão aberta; reinicie o worker após rotação do segredo dele. Se o banco ou arquivo falhar, a operação restaura o arquivo anterior.

Para reconstruir uma demo, use um dispositivo por credencial, por exemplo `python scripts/provision_device.py demo-tractor-01`; grave a senha exibida uma vez no firmware de bancada e descarte a cópia temporária. Não há senha universal nem fallback anônimo. `DeviceCredential.device_id` é a identidade de transporte e deve coincidir com o `device_id` do contrato de telemetria. A autenticação HTTP individual existente também compara a identidade da chave com cada payload; a chave global legada não representa uma identidade individual e precisa ser removida antes de operação compartilhada.

Autenticação MQTT e ACL não criptografam o transporte. O listener atual usa MQTT sem TLS na rede local, portanto não protege credenciais e payloads contra interceptação no segmento. HTTPS local e TLS do broker não são implementados aqui; HTTPS local segue a decisão D-35/S13-T12. A prova local/demo não equivale a piloto compartilhado seguro.

## Proteção de autenticação (S2-T2)

`AnonRateThrottle` limita requisições anônimas a 60/min e `UserRateThrottle` usuários autenticados a 300/min. Login aplica limite atômico adicional de 5/min por IP e por identidade normalizada; os IPs vêm de `REMOTE_ADDR` (cabeçalho `X-Forwarded-For` não é confiado). Após cinco falhas por identidade em janela de 15 minutos, novas tentativas recebem 429 genérico. O estado do lockout e dos limites críticos está em `SecurityCounter`, no banco compartilhado, com operações transacionais; indisponibilidade do banco falha fechada. Em desenvolvimento e produção, `DatabaseCache` usa a tabela `fieldnode_throttle_cache`, criada por migration. Os limites globais do DRF também usam esse cache compartilhado.

Registro inicia desabilitado (`REGISTRATION_ENABLED=False`) e é sempre bloqueado em `DEMO_MODE=True`. Quando habilitado fora da demo, permite no máximo 3 tentativas/hora por IP. Com registro desabilitado a resposta é sempre 403, sem criar usuário. Respostas de falha de login são genéricas e não revelam existência da conta.

Swagger/ReDoc só são roteados quando `SWAGGER_ENABLED=True` (default acompanha `DEBUG`, portanto é desabilitado fora de desenvolvimento). As duas chamadas Gemini enviam `GEMINI_API_KEY` em `x-goog-api-key`, não na URL.

## Modelo de ameaça e isolamento

| Ativo / fronteira | Ameaça | Controle atual | Evidência/limite |
|---|---|---|---|
| Telemetria MQTT | dispositivo publica em identidade alheia | ACL `%u` e comparação de identidade do payload/tópico | integração broker ainda precisa ser executada no Compose |
| Login | brute force distribuído ou por IP | contadores compartilhados por IP, usuário e lockout | validação de carga entre 2 workers pendente |
| Cadastro | spam/criação em demo | flags do servidor e throttle condicionado a cadastro habilitado | teste local cobre flags; 50 chamadas pendentes |
| Gemini | chave exposta em logs/proxy URL | header `x-goog-api-key` | chamadas mockadas pendentes |
| Browser | roubo de token via JS | cookie `HttpOnly` via BFF Next.js | cookie não significa proteção CSRF para outros deployments; origem é validada no BFF |
| Dados multi-organização | leitura ou escrita cruzada | Membership e filtros por organização já existentes | suíte de isolamento deve ser executada para provar toda matriz |

Limitações: `DatabaseCache` em SQLite é compartilhado apenas entre processos que usam o mesmo arquivo e não é adequado a escrita concorrente elevada; produção multi-worker deve usar MySQL. `SecurityCounter` usa transação/row lock no banco e precisa ser validado em MySQL com duas instâncias Gunicorn. Agende `python manage.py cleanup_security_counters` em execução periódica (por exemplo, a cada 15 minutos); a tabela verifica expiração em cada consulta, mas este repositório ainda não instala um scheduler.

## Demo Mode

`DEMO_MODE=True` significa que leituras públicas anônimas de demonstração, quando existentes, são limitadas a máquinas marcadas explicitamente com `Machine.is_demo=True`.

`DEMO_MODE` não é autorização, não é autenticação e não é bypass de permissões.

`Machine.is_demo=True` significa apenas que a máquina foi criada para demonstração controlada. Não significa que dado real foi autorizado para publicação.

Com `DEMO_MODE=False`, o backend segue o contrato normal de segurança do MVP. A flag desativada não transforma `is_demo=True` em substituto de autenticação e não cria uma regra nova de exposição.

## Leituras Públicas

Quando o request é anônimo e `DEMO_MODE=True`, as leituras públicas ligadas a telemetria consultam somente registros associados a `Machine.is_demo=True`.

O caso mínimo validado é:

```text
GET /api/leituras/ultimas/
DEMO_MODE=True
Machine demo: is_demo=True -> aparece
Machine real: is_demo=False -> não aparece
```

O filtro é aplicado no backend antes da resposta ser serializada.

## CORS

A configuração atual usa `CORS_ALLOWED_ORIGINS` por variável de ambiente. O projeto não usa `CORS_ALLOW_ALL_ORIGINS=True` como regra permanente.

CORS restringe consumo pelo navegador, mas não substitui autenticação. Requests diretos fora do navegador ainda precisam ser protegidos por permissões, token ou API key conforme o endpoint.

## DÍVIDA / LIMITAÇÃO CONHECIDA

- Não há MFA.
- O token DRF padrão não possui expiração adequada para um piloto real.
- O isolamento multi-tenant ainda não deve ser tratado como completo para produção.
- Endpoints GET públicos existem no contrato atual do MVP e precisam ser revisados antes de piloto com dados reais.


## Dívidas Técnicas Reveladas pela Validação Comercial (John Deere, Solinftec, Case IH)

As conversas de validação comercial de 2026-09-19 tornaram concretas as seguintes lacunas de segurança e integração para um piloto real:

**Upload pós-offline (Case IH):** a preocupação explícita foi com a segurança e confiabilidade do upload de dados acumulados após horas offline. O mecanismo atual de deduplicação UUID cobre a idempotência, mas não há autenticação mútua no canal de sincronização nem verificação de integridade do payload acumulado (hash end-to-end). Antes de piloto real, o canal de ressincronização precisa de autenticação e verificação de integridade.

**Integração com sistemas de BI proprietários (Case IH / Clealco):** usinas que consomem dados brutos via exportação CSV/XLSX para sistemas proprietários precisam de um canal autenticado de exportação. O endpoint atual de exportação é público (sem token). Para piloto real, exportação de dados operacionais deve exigir autenticação.

**Sensores externos sem CAN (John Deere e Case IH):** máquinas antigas sem barramento J1939 acessível dependem de sensores externos. O FieldNode atual não tem modelo de autenticação ou validação de origem para sensores externos além da `X-API-Key` global. Para frotas mistas em piloto real, cada dispositivo de borda deveria ter identidade própria.

**Dashboard local offline-first na cabine:** o Service Worker atual cobre fila de telemetria offline, mas não um dashboard operacional acessível sem internet. Isso não é uma vulnerabilidade de segurança, mas é uma lacuna funcional citada pelos três especialistas como requisito de piloto.

## Decisão Atual Sobre Token

Nesta fase, o FieldNode usa DRF `TokenAuthentication`. JWT, OAuth, SSO, refresh token e access token customizado ficam fora do escopo deste bloco.

A decisão é coerente com o estágio atual: equipe de TCC, protótipo controlado e eventual piloto pequeno. Para piloto real, essa decisão precisa ser reavaliada.


## Estado de autenticacao e segredos

- O navegador recebe a sessao em cookie HttpOnly, SameSite=Strict e, em producao, Secure. O proxy Next encaminha o token DRF ao Django sem expor o token ao JavaScript.
- A sessao e conferida na entrada e periodicamente enquanto o app esta aberto; uma resposta de expiracao retorna ao login.
- A permissao global da API exige autenticacao. Acesso anonimo de demonstracao depende de permissao explicita e do filtro de dados demo.
- Mosquitto exige usuario e senha. O Compose publica a porta MQTT somente em 127.0.0.1.
- .env e ignorado pelo Git; .env.example contem valores de exemplo. Se credenciais reais foram publicadas em outro clone, fork ou remoto, revogue-as no servico de origem e atualize dispositivos e ambientes consumidores. Apagar um arquivo local nao invalida copias ja expostas.
- A chave de ingestao ainda e compartilhada entre dispositivos; identidade individual por dispositivo permanece como limitacao conhecida.
