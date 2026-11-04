# DEPLOY

**Responsável:** A CONFIRMAR  
**Semana:** S10  
**Status:** ESQUELETO  
**Tarefa de preenchimento:** S10-Tx (confirmar identificador exato no roadmap)  
**Última atualização:** 2026-11-04 — criação do esqueleto (S0-T4)

> **Atenção:** o status deste documento só poderá mudar de `ESQUELETO` para outro quando:
> - as seções obrigatórias estiverem preenchidas com dados reais de S10;
> - as evidências estiverem anexadas ou referenciadas;
> - os critérios de conclusão forem atendidos;
> - a revisão da semana S10 for realizada.
>
> **Regra:** não declarar ambiente de produção pronto sem validação. Diferenciar sempre:
> `desenvolvimento` / `demonstração` / `produção`.

---

## 1. Objetivo

Documentar o processo completo de instalação, configuração, execução e
atualização do ambiente FieldNode — com diferenciação clara entre
desenvolvimento, demonstração e produção.

TODO(responsável-S10, por quê: um documento de deploy ausente ou impreciso é bloqueante para qualquer avaliação real do sistema, quando: início de S10): definir o objetivo técnico específico, os ambientes alvo e os requisitos de cada um.

---

## 2. Escopo

### Incluído

TODO(responsável-S10, por quê: delimitar o que será documentado aqui, quando: S10): listar os ambientes e os passos que serão cobertos.

### Fora do escopo

TODO(responsável-S10, por quê: evitar que este documento prometa ambientes que ainda não existem, quando: S10): registrar o que não será tratado (ex: Kubernetes, deploy em nuvem pública, CI/CD automatizado).

---

## 3. Contexto atual do FieldNode

**Estado verificado em 2026-11-04 (S0-T3):**

- `docker-compose.yml` — serviços: `web` (Django+Gunicorn), `worker` (mqtt_listen), `mosquitto`, `db` (MySQL 8)
- Stack Docker **não verificada em execução real** nesta auditoria (daemon Docker indisponível)
- Execução local sem Docker: Python 3.10/3.12, SQLite, Django `runserver` — confirmada (298/301 testes passando)
- Frontend: `npm run dev` documentado; build de produção com débito técnico (Issue #2)
- `.env.example` presente com variáveis documentadas
- Healthchecks definidos no Compose mas não verificados

TODO(responsável-S10, por quê: atualizar com o estado real após as semanas anteriores, quando: início de S10): complementar com mudanças ocorridas após S0.

---

## 4. Especificação e conteúdo técnico

### 4.1 Arquitetura de implantação

TODO(responsável-S10, por quê: o diagrama de deploy é a referência para qualquer troubleshooting, quando: S10): documentar com diagrama ou texto: onde cada serviço roda, como se comunicam e quais portas expõem.

**Referência atual:** README.md §"Serviços" (parcial).

### 4.2 Pré-requisitos

TODO(responsável-S10, por quê: pré-requisitos incompletos causam falhas silenciosas, quando: S10): listar versões exatas de cada dependência. Referência atual:
- Docker ≥ 29.x (verificado em auditoria S0)
- Docker Compose v5.x
- Python 3.10 ou 3.12 (ambos testados em S0)
- Node.js ≥ 20 (referência do roadmap; v24 disponível no host)

### 4.3 Variáveis de ambiente

TODO(responsável-S10, por quê: variáveis mal configuradas são a causa mais comum de falhas de deploy, quando: S10): documentar cada variável com: nome, descrição, obrigatória/opcional, valor padrão seguro, onde é usada.

**Referência atual:** README.md §"Variáveis de Ambiente" (parcial, expandir).

### 4.4 Configuração de banco

TODO(responsável-S10, por quê: configuração de banco errada causa perda de dados ou falha silenciosa, quando: S10): documentar configuração do MySQL (charset, collation, permissões), do SQLite (apenas dev) e as diferenças entre os dois.

### 4.5 Docker e Docker Compose

TODO(responsável-S10, por quê: o Compose é o método de execução recomendado mas não foi verificado em S0, quando: S10): documentar os comandos completos, a ordem de inicialização e os healthchecks esperados.

**Aviso:** `docker compose up --build -d` não foi verificado em execução real na auditoria S0 (daemon indisponível). Verificar e documentar resultado real.

### 4.6 Migrações

TODO(responsável-S10, por quê: migrações mal executadas corrompem o banco, quando: S10): documentar o comando de migração, a ordem de execução e o que fazer quando uma migration falha.

**Estado atual:** 26 migrations; `0026_rename_tempumi_ambiente` pendente no SQLite local.

### 4.7 Inicialização dos serviços

TODO(responsável-S10, por quê: a ordem de inicialização afeta se os serviços sobem corretamente, quando: S10): documentar a ordem e os critérios de "serviço pronto" para cada componente.

### 4.8 Healthchecks

TODO(responsável-S10, por quê: healthchecks são a evidência de que o sistema está funcionando, quando: S10): documentar o endpoint, a resposta esperada e o critério de "healthy" para cada serviço.

**Estado atual:** `/api/health/` — `{"status":"ok","database":"ok",...}` verificado em SQLite local.

### 4.9 Atualização

TODO(responsável-S10, por quê: atualização sem procedimento documentado é arriscada, quando: S10): documentar o passo a passo para atualizar o sistema sem perda de dados.

### 4.10 Rollback

TODO(responsável-S10, por quê: sem procedimento de rollback, qualquer deploy é irreversível, quando: S10): documentar como reverter para a versão anterior em caso de falha.

### 4.11 Persistência

TODO(responsável-S10, por quê: volumes Docker mal configurados causam perda de dados, quando: S10): documentar quais dados precisam ser persistidos, em que volume e como.

### 4.12 Backups

TODO(responsável-S10, por quê: sem backup, qualquer falha pode ser catastrófica, quando: S10): documentar como fazer backup do banco, dos modelos de IA e dos arquivos de configuração.

### 4.13 Segurança

TODO(responsável-S10, por quê: configurações de segurança não são opcionais em produção, quando: S10): documentar checklist de segurança antes de qualquer exposição pública. Referência: `docs/SEGURANCA.md` e checklist Django (`manage.py check --deploy`).

**Nunca usar `runserver` em produção.**

### 4.14 Solução de problemas

TODO(responsável-S10, por quê: problemas documentados são resolvidos mais rápido, quando: S10): listar os problemas mais comuns e como diagnosticá-los.

**Problemas conhecidos em S0:**
- Build do frontend falha com `Cannot find module 'typescript'` (Issue #2)
- Docker daemon pode estar parado no Windows (requer elevação administrativa)
- Migration `0026` pendente no SQLite local

---

## 5. Evidências e validação

TODO(responsável-S10, por quê: evidências verificáveis são o que separa afirmação de fato, quando: após execução de S10): adicionar:
- saída de `docker compose ps` com todos os serviços healthy
- saída do healthcheck de cada serviço
- comando exato de execução bem-sucedida

**Evidências atuais (S0):**
- `docs/evidence/s0/compose_up.txt` — tentativa falhou (daemon indisponível)
- `docs/evidence/s0/health.json` — HTTP 200 em SQLite local (não Compose)

---

## 6. Limitações e riscos

TODO(responsável-S10, por quê: registro antecipado evita surpresas, quando: S10): complementar.

**Limitações conhecidas em S0:**
- Stack Docker Compose não verificada em execução real
- Build do frontend com débito técnico (Issue #2)
- Migration `0026` pendente no SQLite local
- MySQL 8 não verificado fora do Compose (daemon indisponível)
- Sem procedimento de backup documentado
- Sem checklist de segurança de produção executado

---

## 7. Critérios de conclusão

TODO(responsável-S10, por quê: critérios claros permitem verificação objetiva, quando: S10): definir critérios verificáveis.

**Critérios propostos (a confirmar em S10):**
- [ ] Stack Docker Compose verificada em execução real (todos os healthchecks passando)
- [ ] Todas as variáveis de ambiente documentadas
- [ ] Procedure de migração documentado e testado
- [ ] Checklist de segurança de produção executado
- [ ] Procedure de backup documentado
- [ ] Revisão por outro membro realizada

---

## 8. Histórico de alterações

| Data | Responsável | Alteração |
|---|---|---|
| 2026-11-04 | S0-T4 (Antigravity) | Criação do esqueleto com estado verificado em S0 |
