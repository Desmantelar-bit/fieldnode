# S12-T10 · relatório de preparação

Status: **IMPLEMENTADO PARCIALMENTE; ensaios e liberação ainda pendentes.**

## Implementado

- `docs/CHECKLIST_FINAL.md` formaliza freeze de 72 horas, gates, checklist
  físico, contingência e registro de ensaio.
- `scripts/preflight.sh` mantém as verificações existentes e acrescenta
  validação do Compose, manifesto de imagens, backup e vídeo de fallback,
  distinguindo `OK`, `WARN` e `FAIL`.
- `scripts/demo_reset.sh` e `make demo-reset` executam migrations, população
  sintética idempotente e `manage.py check`, exigindo `DEMO_MODE=True` e
  `DEMO_USERNAME` antes de tocar o container web. Não removem volumes.
- `scripts/save_demo_images.sh` exporta somente as imagens listadas pelo
  Compose, grava hashes SHA-256 e manifesto, e pode ser chamado por
  `make save-demo-images`.

## Estado verificado nesta tarefa

- **Docker:** servidor `29.4.3`; `docker compose ps` mostrou db, mosquitto,
  web, worker e frontend em execução, com db/web saudáveis na inspeção.
- **Tag:** existe `v0.3.0-baseline`; `v1.0.0-banca` não foi criada. A working
  tree já tinha alterações do usuário, portanto não há base limpa para uma
  tag de release honesta.
- **Backup:** `scripts/backup.sh` e `scripts/restore.sh` existem, mas não foram
  executados nesta tarefa: exigem passphrase externa e restauração em banco
  descartável.
- **Imagens Docker:** `scripts/save_demo_images.sh` executado; cinco imagens
  foram exportadas em `release-artifacts/docker-images/` com hashes no
  manifesto. `docker load` em daemon isolado ainda não foi validado.
- **Reset:** comando implementado; não executado nesta tarefa para evitar tocar
  o banco ativo sem confirmação explícita de que ele é demo descartável.
- **Preflight:** executado. Compose, containers, health, migrations, MQTT e
  espaço passaram; frontend falhou com `curl: (52) Empty reply from server`.
  Hostname HTTPS, uplink, vídeo e backup ficaram como `WARN`. Portanto o gate
  de preflight não está aprovado.
- **Notebook reserva, vídeo local, checklist físico e ensaio de falhas:** sem
  evidência suficiente no checkout; permanecem pendentes.

## Decisão de gate

**NÃO LIBERADO como `v1.0.0-banca`.** O estado local permite continuar a
preparação, mas não comprova backup restaurado, pacote offline, fallback,
notebook reserva ou recuperação abaixo de dois minutos. Dar uma tag agora seria
só colocar crachá de segurança numa hipótese.

## Procedimento para fechar os gates

1. Definir data da banca, responsável e janela de freeze.
2. Executar `make demo-reset` em ambiente explicitamente demo e guardar a saída.
3. Executar `scripts/backup.sh` com passphrase fora do repositório e restaurar
   em banco descartável com hash e contagens registradas.
4. Executar `make save-demo-images`; testar `docker load` em daemon isolado e
   registrar tamanhos, hashes e dependências de bind mount.
5. Gravar e verificar o vídeo de fallback local.
6. Preparar o notebook reserva e executar o roteiro completo.
7. Derrubar cada componente de forma reversível, medir recuperação e anexar a
   ata ou vídeo. A meta de `< 2 min` deve ser medida, nunca presumida.
8. Reexecutar preflight e só então decidir entre `LIBERADO`, `LIBERADO COM
   RESSALVAS` ou `NÃO LIBERADO`.

Nenhum comando desta entrega criou tag, fez push, apagou volume ou publicou
segredo.
