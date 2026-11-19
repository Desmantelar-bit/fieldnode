# Carga S10-T7

Os perfis usam as rotas reais do backend e escrevem resultados brutos em
`artifacts/load/`. A latência medida é o tempo da requisição HTTP até a resposta;
ela não substitui uma medição interna de persistência.

```powershell
$env:FIELDNODE_LOAD_DEVICE_KEY = 'chave-da-credencial-provisionada'
python scripts/load/load_test.py a --duration-seconds 30
python scripts/load/load_test.py b --duration-seconds 30
python scripts/load/load_test.py c --duration-seconds 30
python scripts/load/load_test.py d --count 500
python scripts/load/load_test.py e --duration-seconds 60 --confirm-replay
$env:FIELDNODE_LOAD_TOKEN = 'token-de-usuario-de-teste'
python scripts/load/load_test.py f --dashboard-users 10 --dashboard-requests 100
python scripts/load/explain_queries.py
```

O perfil E representa seis horas no timestamp dos dados, mas sua duração real é
limitada por `--duration-seconds`. Ele nunca roda sem `--confirm-replay`.
Para o aceite S10-T7, execute cada perfil três vezes, preserve cada JSON e
anote ambiente, commit, versão do MySQL e contaminação concorrente em
`docs/RELATORIO_CARGA.md`.
