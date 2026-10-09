# FAQ - Defesa Técnica (Banca Examinadora)

> **Nota de escopo (S8-T3):** Este documento foi revisado para distinguir o que
> está implementado e testado em software neste checkout do que depende de
> hardware físico futuro. Alegações sem evidência no repositório foram
> reescritas como proposta/roadmap.

Este documento contém os principais argumentos técnicos para sustentar as decisões de design do FieldNode.

### 1. Como vocês garantem que um alerta é real e não erro do sensor?
**Resposta:** Utilizamos um pipeline de validação em três camadas:
1. **Validação de range no backend:** `validar_payload()` em `api_tcc/services/telemetria.py` rejeita leituras fora dos limites físicos (temperatura 0–150 °C, vibração 0–10, RPM 0–5000). Payloads inválidos são arquivados em `TelemetriaInvalida` para auditoria. Um filtro de média móvel no edge (ESP32 ou similar) é a direção planejada para descartar picos isolados antes do envio; não está implementado em firmware neste checkout.
2. **Deduplicação por UUID:** Cada leitura possui um UUID gerado antes do envio (`str(uuid.uuid4())` no simulador Python; o equivalente em firmware ESP32 é etapa futura). O backend detecta reenvios em `registrar_leitura()` e retorna `200` sem duplicar o banco.
3. **Isolation Forest (Backend):** O alerta só é classificado como "Anomalia" se o modelo identificar que o comportamento foge estatisticamente do padrão histórico daquela máquina. Implementado em `api_tcc/ia/pipeline.py`.

### 2. Por que ESP-NOW e não LoRa ou Wi-Fi comum? (Proposta de arquitetura futura)
**Resposta:** ESP-NOW é a direção planejada para comunicação P2P entre dispositivos de borda, mas não foi implementada nem testada neste checkout. O contrato de telemetria documenta os transportes `http`, `mqtt` e `ble`; ESP-NOW não consta entre os transportes atualmente suportados.

A justificativa de design para essa escolha futura permanece válida como proposta:
- **VS Wi-Fi:** ESP-NOW dispensa roteador central, permitindo comunicação direta entre nós (P2P) com menor consumo de energia.
- **VS LoRa:** ESP-NOW oferece maior taxa de dados para descarregar lotes acumulados offline quando o dispositivo se aproxima do gateway.

Essas características precisam ser medidas em bancada antes de serem apresentadas como capacidade entregue.

### 3. Como evitar o "Excesso de Alertas" (Alert Fatigue) para o operador?
**Resposta:** O pipeline atual usa thresholds determinísticos centralizados em `api_tcc/ia/pipeline.py` e documentados em `docs/limiares.md` (temperatura > 85 °C, vibração > 0.8, RPM < 1300). Uma lógica de histerese e cooldown — que só permite novo alerta da mesma categoria após período de resfriamento ou retorno ao limite seguro — é a evolução planejada; não está implementada neste checkout.

### 4. O sistema é realmente Offline-First? E se o gateway cair?
**Resposta:** Sim, com a arquitetura de software demonstrada neste checkout. O cliente Python (`simulators/edge_client.py`) grava leituras em outbox SQLite antes de sincronizar, usa `message_id` para idempotência e só avança o cursor local após ACK do servidor. Os resultados de S8-T1 e S8-T2 documentam 100/100 leituras recuperadas após interrupções de 35 s, 305 s e 1808 s, com zero perdas e zero duplicatas.

O que não está comprovado neste checkout: buffer em hardware ESP32 físico, retenção após perda de energia no dispositivo, gateway com SQLite local em hardware dedicado. Essas são etapas de validação física futura.

### 5. Qual o diferencial competitivo frente a soluções de mercado (ex: John Deere Operations Center)?
**Resposta:** Custo de implantação e resiliência em zonas sem conectividade. Soluções de grandes fabricantes são proprietárias e dependem de conectividade celular constante. O FieldNode foi projetado para aceitar telemetria de qualquer fonte que respeite o contrato de dados — o backend não exige que a máquina esteja pré-cadastrada. A integração com máquinas antigas via porta serial ou barramento CAN/J1939 é a direção planejada; não foi demonstrada com hardware físico neste checkout.

---
*Se a banca perguntar sobre segurança: o modelo atual usa `X-API-Key` na ingestão e `TokenAuthentication` DRF nas operações administrativas. As limitações conhecidas estão documentadas em `docs/SEGURANCA.md`.*