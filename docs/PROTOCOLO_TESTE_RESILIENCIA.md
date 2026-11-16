# S6-T5 - Protocolo de teste de resiliência

## Objetivo

Medir a sincronização offline do cliente real (`simulators/edge_client.py`)
quando somente o serviço `web` fica indisponível. O banco, o broker e a
outbox local permanecem ativos.

## Critérios escritos antes da execução

Uma rodada só pode ser marcada como `VALID` se todos os critérios forem
atendidos:

| Critério | Regra de sucesso |
|---|---|
| Perda classe A | 0 leituras perdidas |
| Perda classe B | 0 leituras perdidas |
| Duplicata persistida | 0 linhas duplicadas por `(device_id, message_id)` |
| Recuperação | tempo entre API saudável e último ACK registrado, publicado por rodada |
| Ordem temporal | sequência recebida em ordem crescente de `event_time` |
| Outbox | todas as leituras terminam como `SINCRONIZADA` |

O limite de recuperação deve ser definido pela banca antes da execução. O
script publica o valor observado; ele não transforma um número ruim em
sucesso por decreto.

## Cenários

| Rodada | Indisponibilidade solicitada | Serviço interrompido | Leituras |
|---|---:|---|---:|
| R1 | 30 s | `web` | `--count` |
| R2 | 300 s | `web` | `--count` |
| R3 | 1800 s | `web` | `--count` |

Cada rodada recebe um `device_id` próprio. Isso impede que o cursor ou a
idempotência de uma rodada contaminem a seguinte.

## Execução

```powershell
$env:FIELDNODE_DEVICE_KEY = '<credencial do dispositivo provisionado>'
python simulators/teste_resiliencia.py --count 100 --output-dir docs/evidence/s6
```

O comando derruba e sobe apenas `web`, aguarda `/api/health/`, grava a saída
bruta e os bancos SQLite da outbox em `docs/evidence/s6/`. O JSON principal é
`resultados.json`; a tabela também é impressa no terminal.

Antes da execução oficial, conferir:

```powershell
docker version
docker compose ps
Invoke-RestMethod http://127.0.0.1:8000/api/health/
```

## Resultado publicado

Esta seção só deve ser preenchida depois de três rodadas observadas. Não
copiar números de ensaio curto, teste unitário ou execução de outra tarefa.

| Rodada | Geradas | Recebidas | Perdidas | Dup. persistidas | Ordem `event_time` | Recuperação (s) | Status |
|---|---:|---:|---:|---:|---|---:|---|
| R1 | NÃO EXECUTADO | NÃO EXECUTADO | NÃO EXECUTADO | NÃO EXECUTADO | NÃO EXECUTADO | NÃO EXECUTADO | PENDENTE |
| R2 | NÃO EXECUTADO | NÃO EXECUTADO | NÃO EXECUTADO | NÃO EXECUTADO | NÃO EXECUTADO | NÃO EXECUTADO | PENDENTE |
| R3 | NÃO EXECUTADO | NÃO EXECUTADO | NÃO EXECUTADO | NÃO EXECUTADO | NÃO EXECUTADO | NÃO EXECUTADO | PENDENTE |

## Limite da evidência

> validado em simulador de software; não comprova alcance de rádio nem comportamento em hardware

O resultado sustenta a formulação: **sincronização resiliente com deduplicação
e recuperação de falhas, validada nos cenários documentados**. Ele não sustenta
alcance de rádio, tolerância elétrica, comportamento do ESP32 ou validação de
campo.
