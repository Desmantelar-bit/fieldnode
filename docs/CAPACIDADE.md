# Capacidade e política de armazenamento

## Metodologia

O tamanho é medido no SQLite real, incluindo o arquivo principal e os arquivos
`-wal` e `-shm` quando existentes. A amostra é gerada pelo contrato atual do
edge, com as classes A, B e C:

```powershell
python scripts/measure_storage.py --count 90
```

O tamanho do JSON é apenas uma referência. O número usado para dimensionar é o
crescimento físico observado, que inclui páginas, índices, metadados e WAL.

Execução MEDIDA nesta bancada, com 90 mensagens: banco inicial 57.344 B,
banco final 139.264 B, crescimento 81.920 B e média física de 910,22 B por
mensagem. O tamanho armazenado do payload ficou entre 506 e 508 B por classe;
isso não substitui a média física, que inclui o custo do banco.

## Calculadora

```text
bruto = mensagens_por_segundo × bytes_médios × segundos_offline
estimado = bruto × (frac_C × compressao_C + (1 - frac_C))
            × (1 + overhead) × (1 + margem)
```

Exemplo de execução:

```powershell
python scripts/capacity_calc.py --rate 0.5 --bytes 220 --days 14
```

O padrão não presume compressão. `--compression-c` e `--fraction-c` só devem
ser usados com valores MEDIDOS. Cada valor publicado deve ser marcado como
MEDIDO, ESTIMADO, CONFIGURADO ou DESCONHECIDO.

## Cenários obrigatórios

Devem ser calculados 30 minutos, 5 horas, 6 horas, 24 horas, 72 horas, 7 dias
e 14 dias. Use a medição do ambiente alvo, não os 220 bytes ilustrativos:

```powershell
python scripts/capacity_calc.py --rate <MEDIDO> --bytes <MEDIDO> `
  --hours 0.5 5 6 24 72
python scripts/capacity_calc.py --rate <MEDIDO> --bytes <MEDIDO> `
  --days 7 14
```

Com a medição física de 910,22 B/mensagem, taxa configurada de 0,5 msg/s,
overhead padrão de 60% e sem compressão presumida, o resultado ESTIMADO foi:

| Offline | Mensagens | Bruto | Estimado |
|---:|---:|---:|---:|
| 30 min | 900 | 0,82 MB | 1,31 MB |
| 5 h | 9.000 | 8,19 MB | 13,11 MB |
| 6 h | 10.800 | 9,83 MB | 15,73 MB |
| 24 h | 43.200 | 39,32 MB | 62,91 MB |
| 72 h | 129.600 | 117,96 MB | 188,74 MB |
| 7 dias | 302.400 | 275,25 MB | 440,40 MB |
| 14 dias | 604.800 | 550,50 MB | 880,80 MB |

Essa tabela dimensiona o cenário da bancada. Não é validação da flash do ESP32.

## Política de ocupação

Os limiares são configuráveis e medem o armazenamento persistente real:

| Ocupação | Ação |
|---:|---|
| 90% | comprimir novas mensagens C |
| 95% | agregar C, preservando intervalo, média, mínimo, máximo e contagem |
| 98% | descartar C mais antiga, registrando quantidade e motivo |

A e B não são removidas por essa rotina. A reserva configurada protege espaço
para integridade e admissão das classes críticas. Se não houver espaço físico
ou reserva suficiente, a gravação falha com `StorageFullError`; não há ACK para
uma mensagem não gravada.

Os eventos ficam em `storage_events`; agregados ficam em `c_aggregates` e não
são apresentados como leituras originais.

## Simulador e hardware

O simulador aceita `StoragePolicyConfig(max_bytes=..., reserve_bytes=...)` e
mede o banco local. A capacidade física do ESP32 continua DESCONHECIDA até a
partição, firmware, sistema de arquivos, credenciais, logs, fila e reserva de
desgaste serem medidos em S8. Flash nominal não é espaço de telemetria.

A viabilidade de 14 dias só pode ser concluída depois de combinar a medição do
edge, os cenários calculados e a configuração física real. A meta não é uma
garantia automática do código.
