# 🛡️ FAQ - Defesa Técnica (Banca Examinadora)

Este documento contém os principais argumentos técnicos para sustentar as decisões de design do FieldNode.

### 1. Como vocês garantem que um alerta é real e não erro do sensor?
**Resposta:** Utilizamos um pipeline de validação em três camadas:
1.  **Filtro no Edge (ESP32):** Implementamos uma média móvel simples. Picos isolados de vibração são descartados para evitar ruídos de impacto momentâneo.
2.  **Deduplicação por UUID:** Cada leitura possui um ID único gerado no sensor. Isso garante que, em caso de múltiplas tentativas de sincronização offline, o backend não processe o mesmo alerta duas vezes.
3.  **Isolation Forest (Backend):** O alerta só é classificado como "Anomalia" se o modelo de Machine Learning identificar que o comportamento foge estatisticamente do padrão histórico daquela máquina específica.

### 2. Por que usar ESP-NOW em vez de LoRa ou Wi-Fi comum?
**Resposta:**
- **VS Wi-Fi:** O Wi-Fi exige um roteador/ponto de acesso central. No campo, o ESP-NOW permite que as máquinas se comuniquem diretamente com o Gateway (P2P), reduzindo infraestrutura e consumo de energia.
- **VS LoRa:** Embora o LoRa tenha mais alcance, o ESP-NOW oferece uma taxa de dados muito maior (até 1Mbps), o que é essencial para descarregar o "batch" de dados acumulado offline rapidamente quando a máquina se aproxima do Gateway.

### 3. Como evitar o "Excesso de Alertas" (Alert Fatigue) para o operador?
**Resposta:** Implementamos uma lógica de **Histerese e Cooldown**:
- Se uma temperatura atinge 85°C, um alerta é gerado.
- O sistema só permite um novo alerta daquela mesma categoria para aquela máquina após um período de 30 minutos, ou se a temperatura baixar de um "limite de segurança" (ex: 70°C) e subir novamente. Isso evita que o operador receba 100 notificações por um problema que ele já está ciente.

### 4. O sistema é realmente Offline-First? E se o Gateway cair?
**Resposta:** Sim. O dado nasce no ESP32 e é armazenado em uma fila local (Buffer). Se o Gateway estiver offline, o ESP32 retém os dados. Se o Gateway receber mas o Backend (Nuvem) estiver fora, o Gateway armazena no SQLite local. A sincronização é transacional: o dado só é deletado da ponta após o `HTTP 201 Created` do servidor central.

### 5. Qual o diferencial competitivo frente a soluções de mercado (ex: John Deere Operations Center)?
**Resposta:** Custo e Resiliência em "Zonas de Sombra". Soluções de grandes fabricantes são proprietárias (travadas no hardware deles) e dependem de conectividade celular constante ou infraestrutura cara. O FieldNode é agnóstico (instala em qualquer máquina antiga) e focado no protocolo P2P para áreas onde o 4G não chega.

---
*Dica para a equipe: Se a banca perguntar sobre segurança, foquem na X-API-Key e na segregação de rede do Gateway Local.*