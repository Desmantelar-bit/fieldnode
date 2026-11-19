# S12-T10 · checklist final de banca

Status atual: **LIBERADO COM RESSALVAS somente para preparação local; não
liberado como release final de banca.** Os campos sem evidência permanecem
pendentes. Preencher datas, responsáveis e hashes reais no dia do ensaio.

## Freeze de 72 horas

- [ ] Data da banca confirmada: **NÃO REGISTRADA neste checkout**.
- [ ] Freeze iniciado pelo menos 72 h antes.
- [ ] Branch, commit e working tree registrados.
- [ ] Testes e `git diff --check` executados.
- [ ] Sem funcionalidades, refatorações ou dependências novas após o freeze.
- [ ] Exceção pós-freeze tem prefixo `fix:`, evidência reproduzível, revisão,
  teste, risco, reversão e decisão registrada.

## Gates de liberação

| Gate | Condição | Estado |
|---|---|---|
| A · Código | freeze, testes, CI e referência | **PENDENTE** |
| B · Infraestrutura | Compose, backup, imagens, migrations e preflight | **PARCIAL**: Compose local ativo; pacote não fechado |
| C · Demonstração | roteiro, reset, fluxo, vídeo e fallback | **PARCIAL**: roteiro existe; vídeo não registrado |
| D · Contingência | notebook reserva, backup e ensaio cronometrado | **PENDENTE** |
| E · Material físico | cabos, fontes, extensão, hotspot, adaptadores e projetor | **PENDENTE** |
| F · Decisão | LIBERADO / LIBERADO COM RESSALVAS / NÃO LIBERADO | **NÃO LIBERADO** até A–E serem revisados |

## Preparação executável

```bash
# ambiente local, sem expor .env
docker compose config
docker compose ps
make demo-reset
make preflight

# backup: exige passphrase em arquivo protegido
FIELDNODE_BACKUP_PASSPHRASE_FILE=/caminho/passphrase ./scripts/backup.sh

# exportação seletiva das imagens em execução
./scripts/save_demo_images.sh
```

O backup deve ser restaurado em banco descartável com `scripts/restore.sh`.
Não executar reset ou restore sobre dados reais. `make demo-reset` exige
`DEMO_MODE=True` e `DEMO_USERNAME` e é idempotente, usando os dados sintéticos
do comando de demonstração; ele não deve ser usado como limpeza de produção.

## Checklist físico

- [ ] Notebook principal e carregador.
- [ ] Notebook reserva preparado e reproduzido, ou limitação registrada.
- [ ] Fontes, cabos USB/dados, extensão e hub.
- [ ] HDMI e adaptadores sobressalentes.
- [ ] Hotspot e celular carregado.
- [ ] Projetor testado com a resolução prevista.
- [ ] ESP32, sensores, protoboard e fixações somente se fizerem parte do setup real.
- [ ] Backup, imagens e vídeo em armazenamento local.

## Plano de contingência

| Componente | Detecção | Recuperação segura | Fallback | Meta |
|---|---|---|---|---:|
| Hardware/sensor | sem leitura ou log | parar a etapa física, conferir fonte/conector e registrar | simulador identificado | < 2 min no ensaio |
| Rede/hotspot | celular não abre rota local | manter notebook/Compose, trocar para hotspot reserva | apresentação no notebook | < 2 min |
| Docker | container parado/healthcheck falha | `docker compose ps`, logs, reinício controlado | vídeo local | < 2 min |
| Banco | health/migrations/dados ausentes | restaurar backup de demo em ambiente isolado | vídeo local | < 2 min |
| Frontend | rota não abre ou erro de API | validar backend/URL e recarregar | notebook ou vídeo | < 2 min |
| Projetor | HDMI/resolução falha | trocar cabo/adaptador e usar tela do notebook | vídeo no notebook | < 2 min |
| Notebook | falha de boot/bateria | migrar para reserva preparada | vídeo local | < 2 min |
| Fluxo demo | alerta/decisão não aparece | interromper narrativa, não fabricar dado, usar gravação | vídeo local | < 2 min |

Durante a recuperação: não apagar volumes indiscriminadamente, não rodar
migration destrutiva, não alterar firmware e não criar resultado sintético
apresentado como ao vivo.

## Ensaio de falhas e decisão

Para cada componente, registrar início, detecção, diagnóstico, recuperação,
tempo total, intervenção e resultado. A meta de 2 minutos é critério de
avaliação, não resultado presumido.

| Ensaio | Data | Falha | Tempo total | Meta atingida | Evidência |
|---|---|---|---:|---|---|
| E1 | NÃO EXECUTADO | NÃO SELECIONADA | NÃO MEDIDO | NÃO VERIFICADO | AUSENTE |

Só marcar **LIBERADO** após os gates críticos, backup/restauração, fallback,
preflight e ensaio estarem evidenciados. Preparar não é validar; validar não é
liberar; liberar não é prometer que nada falhará.
