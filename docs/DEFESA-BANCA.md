# 🛡️ Defesa Técnica - Respostas Padrão para Banca

## 🔐 Segurança e Limitações

### "Por que CORS está aberto?"
**Resposta:** "Em desenvolvimento usamos CORS aberto para facilitar acesso via `file://` durante testes. Em produção, configuramos apenas origens whitelistadas no `CORS_ALLOWED_ORIGINS`. É uma decisão consciente de ambiente."

### "Por que API key simples em vez de JWT?"
**Resposta:** "ESP32 tem limitações de memória. JWT requer bibliotecas adicionais que consomem RAM preciosa. Optamos por API key simples como trade-off documentado entre segurança e viabilidade técnica no hardware embarcado."

### "Por que não há autenticação de usuário?"
**Resposta:** "O sistema é focado em telemetria de máquinas, não usuários finais. A autenticação é por máquina via API key. Para um sistema comercial, adicionaríamos camada de usuários com Django Auth."

## 📊 Dados e Funcionalidades

### "Por que combustível aparece como N/D?"
**Resposta:** "Sensor de combustível requer hardware adicional não implementado nesta versão. Optamos por honestidade técnica em vez de simular dados falsos. É uma limitação conhecida e documentada."

### "Como garantem que os dados não se perdem?"
**Resposta:** "Três camadas: 1) ESP-NOW para comunicação local sem internet, 2) Gateway com armazenamento local, 3) Sincronização com deduplicação por UUID quando há conectividade. O dado existe mesmo offline."

### "E se o Gateway falhar?"
**Resposta:** "Cada ESP32 pode armazenar até 100 leituras na EEPROM. Se o Gateway falha, os nós continuam coletando. Quando o Gateway volta, sincroniza automaticamente via ESP-NOW."

## 🏗️ Arquitetura e Escolhas Técnicas

### "Por que Django e não FastAPI?"
**Resposta:** "Django oferece ORM robusto, admin interface, e ecossistema maduro. Para telemetria agrícola que precisa de confiabilidade, preferimos estabilidade sobre performance pura."

### "Por que MySQL em vez de PostgreSQL?"
**Resposta:** "MySQL é mais comum em infraestrutura agrícola brasileira. Facilita deploy e manutenção em fazendas com equipes técnicas menores."

### "Como escala para milhares de máquinas?"
**Resposta:** "Arquitetura permite sharding por região/fazenda. Cada Gateway serve 10-50 máquinas. Backend Django pode usar load balancer + múltiplas instâncias. É escalável horizontalmente."

## 🧪 Testes e Qualidade

### "Vocês têm testes?"
**Resposta:** "Sim, 19 testes automatizados cobrindo ingestão, validação, deduplicação e APIs. Executamos `python manage.py test` - todos passam. Focamos em testes de integração por serem mais valiosos que unitários isolados."

### "Como garantem qualidade dos dados?"
**Resposta:** "Validação em múltiplas camadas: 1) Range checking (temp 0-150°C), 2) Deduplicação por UUID, 3) Isolation Forest para detecção de anomalias, 4) Logs estruturados para auditoria."

## 🚀 Demonstração e Funcionalidades

### "Mostrem o sistema funcionando"
**Resposta:** "Temos 3 demos: 1) Dashboard em tempo real com MQTT, 2) Simulador de 3 máquinas via `demo_pane.py`, 3) API completa documentada no Swagger. Posso mostrar qualquer uma."

### "Como sabemos que detecta problemas reais?"
**Resposta:** "Isolation Forest identifica padrões anômalos. Exemplo: vibração >0.5 + temperatura >85°C = alerta vermelho. Baseado em thresholds reais de manutenção agrícola."

## 💡 Diferencial e Inovação

### "O que isso tem de novo?"
**Resposta:** "Offline-first para agronegócio. Sistemas comerciais falham sem internet. O FieldNode funciona 100% offline e sincroniza quando possível. É resiliência, não apenas telemetria."

### "Por que não usar solução pronta?"
**Resposta:** "Soluções comerciais custam R$ 50-200k/fazenda e dependem de conectividade constante. Nossa solução é open-source, offline-first e custa <R$ 5k para implementar."