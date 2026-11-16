# S6-T5 - Estado da execução

## Estado

**PENDENTE - sem números publicados.**

O protocolo foi atualizado e a bancada Compose foi verificada em 15/11/2026:

- `docker version`: VERIFICADO;
- `docker compose ps`: `db`, `frontend`, `mosquitto` e `web` ativos; `web` saudável;
- `/api/health/`: `status=ok`, banco `ok`;
- migration `0049_leituratelemetria_priority_class`: aplicada no container;
- credencial HTTP: não disponível no processo host que executa
  `simulators/teste_resiliencia.py`.

As três rodadas oficiais R1/R2/R3 não foram executadas. Portanto, não há
`resultados.json` nem tabela real a publicar neste arquivo. O limite de
evidência permanece:

> validado em simulador de software; não comprova alcance de rádio nem comportamento em hardware

## Próximo comando autorizado

Depois de disponibilizar a chave individual do dispositivo no processo host:

```powershell
$env:FIELDNODE_DEVICE_KEY = '<chave individual provisionada>'
python simulators/teste_resiliencia.py --count 100 --output-dir docs/evidence/s6
```

O `resultados.json` produzido pelo script é a fonte dos números. Nenhum número
de ensaio curto ou de outra rodada deve ser copiado para o relatório oficial.
