# J1939 - bancada

Este módulo decodifica quadros CAN estendidos de 29 bits sem depender do driver
CAN. Ele é deliberadamente puro para permitir teste host-side e não afirma que o
FieldNode foi conectado a uma máquina agrícola.

| PGN | Nome | SPN | Parâmetro | Regra |
|---:|---|---:|---|---|
| 61444 | EEC1 | 190 | `engine.rpm` | bytes 4-5 LE, `raw * 0.125 rpm` |
| 65262 | ET1 | 110 | `engine.coolant_temp` | byte 1, `raw - 40 C` |
| 65263 | EFL/P1 | 100 | `engine.oil_pressure` | byte 4, `raw * 4 kPa` |
| 65226 | DM1 | - | `dtc.active` | DTC de 4 bytes após os 2 bytes de lâmpadas |

Para os campos implementados, `0xFF` e `0xFFFF` são tratados como ausentes;
valores reservados ou payloads incompatíveis não viram zero nem medição.

Fontes públicas consultadas:

- https://www.diva-portal.org/smash/get/diva2%3A1622990/FULLTEXT01.pdf
- https://auroragenerators.com/wp-content/uploads/dynagen-tough-series-J1939-reference-manual-en.pdf
- https://support.enovationcontrols.com/hc/article_attachments/115005111993/J1939.pdf
- https://pyramidsolutions.com/wp-content/uploads/2018/07/J1939-Data-Mapping-Explained_Final.pdf

As fontes públicas não substituem a SAE J1939-71/-73. Compatibilidade com ECU,
fabricante ou máquina real permanece `VALIDATE_NOW`.
