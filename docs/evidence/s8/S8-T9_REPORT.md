# S8-T9 - CI do firmware

## Implementação

- Workflow criado: `.github/workflows/firmware.yml`.
- Job removido de `contracts.yml` para não manter dois pipelines de firmware
  redundantes.
- Eventos: pull request para `main`, push em `main` e `workflow_dispatch`.
- Permissão: `contents: read`.
- PlatformIO Core fixado em `6.1.16`.
- Plataforma `espressif32` fixada em `6.6.0`; dependências do firmware foram
  fixadas no `firmware/platformio.ini`.
- Cache do PlatformIO usa a chave derivada de `firmware/platformio.ini`.
- `include/secrets.example.h` é copiado apenas durante o job para
  `include/secrets.h` e não é publicado.
- O artefato contém o `.bin`, `SHA256SUMS` e metadados do build de CI.
- O README recebeu badge e instruções para exigir o check na proteção da branch.

## Estados de verificação

| Categoria | Estado | Evidência |
|---|---|---|
| BUILD LOCAL | PENDENTE | `pio run -d firmware` chegou à instalação de `espressif32@6.6.0` e terminou com `HTTPClientError` no ambiente atual |
| CI EXECUTADO | PENDENTE | O workflow ainda não foi executado no GitHub Actions |
| TESTES HOST | VERIFICADO | `pio test -d firmware -e native` executou com sucesso (7 casos de teste aprovados em host) |
| ARTEFATO PUBLICADO | PENDENTE | Depende de execução real do Actions |
| PROTEÇÃO DE BRANCH CONFIGURADA | PENDENTE | Requer configuração administrativa no GitHub; não foi alterada |

## Comandos locais executados

```text
python -m pip install platformio==6.1.16                 OK
python -m platformio --version                           PlatformIO Core 6.1.16
python -m platformio run -d firmware                     HTTPClientError ao instalar espressif32@6.6.0
python -m platformio test -d firmware -e native          OK (7 test cases succeeded)
```

O arquivo temporário `firmware/include/secrets.h` foi criado a partir do
exemplo somente para a tentativa local e removido depois. Não há credencial
real no exemplo nem no artefato local.

## Segurança e limitações

O workflow não concede permissão de escrita, não faz deploy e não acessa placa
física. O binário publicado deve ser tratado como build de CI, não como
firmware certificado, assinado ou validado em campo. Pull requests de forks
usam apenas o exemplo público de configuração.

O badge aponta para o workflow real. Ele só refletirá estado verde depois que o
GitHub Actions executar o job com sucesso; badge no README não é evidência de
execução passada.
