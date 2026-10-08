# Limitações e escopo de hardware

O `edge_client.py` é um simulador Python externo ao Django. Ele valida em
bancada a persistência local, retry, replay idempotente e confirmação por hash.

Isso não comprova ainda o comportamento de um ESP32 sob restrição de RAM,
flash, energia, temperatura, reboot inesperado, corrupção de armazenamento ou
perda intermitente de rádio. Também não comprova 30 dias de buffer offline.

Quando houver hardware físico, uma API key global gravada na flash poderá ser
extraída por acesso físico e usada para forjar telemetria. A direção futura é
uma credencial por `device_id`, rotação periódica e, idealmente, assinatura
assimétrica com proteção de chave em hardware/flash encryption. Isso permanece
fora do escopo deste simulador.
