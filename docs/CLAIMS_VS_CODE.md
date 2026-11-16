# Claims versus codigo

| Afirmacao | Situacao verificavel |
|---|---|
| Existe um detector oficial | `api_tcc/services/anomaly_detection.py` concentra o contrato e a execucao; o modulo legado apenas encaminha compatibilidade. |
| O sistema usa modelo treinado | Somente quando ha artefato compativel e integro; caso contrario, o resultado e `baseline_estatistico` ou indisponivel. |
| O detector preve falhas | Nao sustentado pelo codigo ou pelo benchmark sintetico. |
| O benchmark valida campo | Nao. O relatorio identifica explicitamente metricas sinteticas, nao de campo. |
| Artefato pode ser auditado | Metadados incluem versao, features, amostras, hash do dataset e hash derivado do modelo. |
| Avaliacao publica valida o produto | Nao. CWRU e experimento independente de sinais de rolamento; nao demonstra transferencia para colheitadeiras. |
| O IF fornece probabilidade de quebra ou RUL | Nao. A saida e score de anomalia. |

## Topologia e hardware

| Afirmacao | Situacao verificavel |
| --- | --- |
| O notebook e o gateway da demo | IMPLEMENTADO como hospedeiro do Compose: Mosquitto, Django, worker, banco e frontend. |
| Existe gateway ESP32 funcional | NAO IMPLEMENTADO. O firmware atual cobre apenas o no DS18B20 -> MQTT; nao ha codigo ESP-NOW nem evidencia fisica de gateway. |
| ESP32 #2 retransmite ESP-NOW para MQTT | ROADMAP/PLANEJADO para a bancada; nao confundir com o cliente Python ou com diagramas. |
| O ESP32 #2 hospeda o dashboard principal | NAO IMPLEMENTADO e tecnicamente incorreto para o Next.js completo. Uma pagina estatica embarcada simples seria outra capacidade. |
| Broker MQTT local | IMPLEMENTADO no container `mosquitto` do Compose; isso e broker no notebook, nao broker embarcado. |
| Dashboard local sem internet | IMPLEMENTADO somente enquanto notebook, rede local e servicos locais estiverem ativos; nao ha gateway fisico substituto. |
| Operacao offline em hardware | NAO VERIFICADO. O `edge_client.py` tem outbox SQLite de bancada; o firmware S8-T1 nao tem outbox persistente e o simulador MQTT nao persiste publicacoes falhas. |
| Mini-PC/Raspberry com a pilha local | ROADMAP/PROPOSTO; desempenho, armazenamento, seguranca e manutencao ainda nao foram validados. |
| Firmware PlatformIO possui configuração de build e testes host-side | CONFIGURADO no checkout para `esp32dev` e `native`; testes host-side validados (7 casos de teste aprovados em host); compilação esp32dev/CI no runner permanece sem substituir validação em placa. |
| Cada dispositivo possui credencial individual no backend | IMPLEMENTADO no contrato S2-T8 para ingestao HTTP/MQTT, com hash, rotacao e revogacao; a gravacao segura dessa credencial na flash nao esta comprovada. |
| Credenciais do firmware estao protegidas contra extracao | NAO SUSTENTADO. Flash Encryption e Secure Boot permanecem roadmap; a chave em flash pode ser extraida com acesso fisico adequado. |
| O firmware possui Secure Boot ou Flash Encryption | ROADMAP; nenhuma eFuse foi alterada e nenhum mecanismo foi validado neste checkout. |
| O sistema possui OTA segura | DEFER. Nao ha implementacao validada de assinatura, rollback e recuperacao. |
| Hardware foi validado em campo | NAO VERIFICADO. A evidencia atual e de bancada e host-side. |

As classificacoes acima sao deliberadamente separadas de simulacao e de
validacao fisica. Nenhum teste de software transforma um simulador em hardware.
