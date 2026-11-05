# Contrato de telemetria v1

Este documento acompanha `contracts/severity.v1.json`, fonte de verdade para
unidades e limiares. O hardware real permanece no contrato v0 até migração
explícita por versão.

## Vibração

- `vibracao`: índice adimensional `indice_0_10`, faixa 0–10.
- `vibracao_unit`: unidade declarada; default de compatibilidade `indice_0_10`.
- `vibracao_rms_g` e `vibracao_pico_g`: grandezas futuras e opcionais.
- `vibracao_curtose`: definição futura e campo opcional.

Payload sem `vibracao_unit` recebe `indice_0_10` por compatibilidade. Isso não
reclassifica dados históricos ambíguos. Unidade desconhecida ou `g` é rejeitada;
não existe conversão implícita entre índice e aceleração.

Valores nulos, não numéricos, não finitos ou fora de 0–10 são rejeitados antes
da persistência. A unidade é guardada em `LeituraTelemetria.vibracao_unit`.

## Proveniência temporal

Cada leitura pode declarar `time_source` como `rtc`, `gateway`, `ntp` ou
`unsynced`. O padrão para clientes legados é `unsynced`; timestamp recebido sem
proveniência não é tratado como relógio confiável.

`boot_id` e `uptime_ms` devem ser enviados juntos. Para uma leitura sem relógio,
é permitido omitir `timestamp` quando esses campos existem. Ela recebe um horário
provisório de ingestão e `event_time_confidence=low`; o Trust Score sofre
penalidade explícita por hora do dispositivo não confiável.

Uma leitura `gateway`, `rtc` ou `ntp` com boot e uptime registra a primeira âncora
confiável daquele par `device_id + boot_id`. Para o mesmo boot, leituras
`unsynced` são reconstruídas por:

```text
event_time = anchor_timestamp + (uptime_ms - anchor_uptime_ms)
```

Uma âncora de outro `boot_id` nunca é reutilizada. A leitura mantém
`time_source=unsynced` e confiança baixa após reconstrução, pois a hora foi
inferida. Sem boot/uptime ou âncora confiável, não há reconstrução.

O hash ACK é calculado sobre o payload ordenado, excluindo o campo `id`, que é
somente o UUID interno da linha. `device_id + message_id` seguem como identidade;
replays legados com hash anterior são aceitos quando o hash original coincide.

`time_source=gateway` usa a recepção do servidor como event time. `clock_skew_ms`
fica nulo se não houver medição explícita de gateway confiável. O servidor não
infere skew por `received_em - timestamp`: esse delta mistura atraso de transporte
e erro do relógio. O hardware real permanece no contrato v0 até migração explícita.

## Exibição e evolução

Gráficos, tabelas, cards, tooltips e eixos devem mostrar `indice_0_10` para
`vibracao`. RMS, pico e curtose são grandezas distintas. Uma futura adoção de
acelerômetro acrescentará campos e versão de schema, sem reinterpretar leituras.
