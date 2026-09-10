# Scripts Auxiliares do FieldNode

Esta pasta contém scripts utilitários para preparação, validação e testes da
API. **Nenhum destes arquivos é executado em produção pelo Django.** Execute-os
a partir da raiz do repositório, por exemplo: `python scripts/<arquivo>.py`.

## Dados e demonstração

- `seed_data.py`: ponto de entrada único para população de dados. Aceita
  `--scenario {simples,completo,stress}`:
  - `simples` — 8 colheitadeiras, dados fixos, 96 leituras. Limpa o banco.
    Bom para demo e smoke test.
  - `completo` — 10 colheitadeiras `COLH-01..10`, 500 leituras com GPS real
    (Goiás/DF). Idempotente (`get_or_create`).
  - `stress` — 20 colheitadeiras `STRESS-01..20`, 4 000 leituras via
    `bulk_create`. Para validar performance de escrita em massa.
- `limpar_banco.py`: remove os dados do banco respeitando a ordem das relações.
- `adicionar_telemetrias.py`: adiciona leituras de telemetria para testes locais.
- `criar_prescricoes_teste.py`: cria prescrições de exemplo.
- `demo_pane.py`: prepara dados usados na demonstração.
- `simular_cenarios.py`: envia cenários determinísticos, como Normal e
  Temperatura Crescente.
- `simular_mqtt.py`: simula um gateway MQTT com fallback HTTP.

## Validação e testes

- `teste_carga.py` e `stress_test.py`: exercitam concorrência, latência e rate
  limit da ingestão.
- `teste_deduplicacao.py`: envia o mesmo UUID em paralelo e valida a proteção
  contra duplicação.
- `teste_fluxo_completo.py`: valida o fluxo de ingestão e consultas da API.
- `testar_django_client.py`, `testar_http.py`, `teste_busca.py`,
  `testar_operarios.py` e `testar_prescricoes.py`: verificações manuais de
  endpoints e contratos específicos.
- `teste_health_checklist.py` e `testar_semana5_ui_decisao.py`: checklists de
  saúde da API e do fluxo de interface.
- `validar_sistema.py`: verifica arquivos e contratos esperados pelo projeto.

## Execução comum

```bash
python scripts/seed_data.py --scenario simples
python scripts/simular_cenarios.py
python scripts/teste_deduplicacao.py
```
