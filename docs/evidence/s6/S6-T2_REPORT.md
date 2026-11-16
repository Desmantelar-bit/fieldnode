# S6-T2 · Relatório de evidências

## Implementação

- `scripts/capacity_calc.py`: cálculo por taxa, tamanho, duração, fração C,
  compressão, overhead e margem.
- `scripts/measure_storage.py`: crescimento físico SQLite e estatísticas por
  classe.
- `simulators/storage_policy.py`: limiares, reserva, admissão e falha
  explícita de persistência.
- `simulators/edge_client.py`: compressão C, agregação, descarte registrado,
  leitura do armazenamento real e decodificação antes do envio.
- `contracts/sync.v1.json` e `api_tcc/sync_contract.py`: contrato e runtime.

## Comandos de evidência

```powershell
python -m pytest simulators/test_edge_client.py simulators/test_storage_policy.py scripts/test_capacity_calc.py -q
python -m pytest api_tcc/tests/test_sync_contract.py -q
python scripts/measure_storage.py --count 90
python scripts/capacity_calc.py --rate 0.5 --bytes 220 --days 14
```

Os números publicados devem ser copiados da saída executada no ambiente alvo.
Este relatório não inventa capacidade física do ESP32.

## Resultado MEDIDO nesta execução

`python scripts/measure_storage.py --count 90` produziu 57.344 B antes,
139.264 B depois, crescimento de 81.920 B e 910,22 B físicos por mensagem.
Foram observadas 9 mensagens A, 27 B e 54 C. O payload persistido mediano foi
508 B em A e 507 B em B/C. A diferença entre payload e crescimento físico é
overhead SQLite e deve ser considerada no dimensionamento.

Com 0,5 msg/s, 60% de overhead e sem compressão presumida, a projeção de 14
dias foi 604.800 mensagens, 550,50 MB brutos e 880,80 MB estimados. A mesma
projeção para 7 dias foi 302.400 mensagens, 275,25 MB brutos e 440,40 MB.

## Integridade

Os testes verificam preservação de A/B, registro de perdas C, falha explícita
quando não há espaço, reversão da codificação comprimida antes do POST e
remoção somente após ACK validado. A suíte completa e a validação física em S8
são etapas separadas e precisam de seus próprios resultados.
