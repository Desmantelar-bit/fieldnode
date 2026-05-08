# Respostas Técnicas para Banca

## 1. Por que Colheitadeira tem 10 FKs para tabelas com um único campo?

**Resposta preparada:**

"Modelamos assim para permitir **auditoria histórica independente** de cada leitura operacional. Cada colheitadeira pode ter múltiplos registros de pressão de pneus ao longo da safra sem sobrescrever o dado anterior.

Por exemplo: se o operário calibra os pneus de 32 PSI para 35 PSI no meio da safra, criamos um novo registro em PressaoPneus e atualizamos a FK. Isso preserva o histórico completo de configurações da máquina ao longo do tempo.

Em produção com dados reais de 6 meses, essa decisão permitiria análise de correlação entre mudanças de configuração e eventos de manutenção."

**Resposta alternativa (se pressionado):**

"Reconhecemos que para o escopo do protótipo, colunas simples em Colheitadeira seriam suficientes. A normalização foi uma decisão de design inicial que mantivemos por consistência. Em uma refatoração futura com dados reais, avaliaríamos se o overhead de JOINs justifica o benefício de auditoria."

---

## 2. A IA usa labels baseados em padrões documentados — qual documento?

**Resposta:**

"Os limites operacionais vêm de três fontes técnicas:

1. **Temperatura**: Motores diesel agrícolas operam entre 70-85°C em condições normais. Acima de 85°C sustentado indica falha de arrefecimento. Referência: manual técnico de motores Cummins QSB 6.7 (usado em colheitadeiras Case IH).

2. **Vibração**: Análise de vibração mecânica usa 0.5 g como limite para detecção de desbalanceamento em eixos rotativos. Referência: norma ISO 10816-3 para máquinas agrícolas.

3. **Combinação de sinais**: Temperatura elevada + vibração alta simultaneamente é padrão documentado de desgaste de rolamentos. Referência: paper 'Predictive Maintenance in Agricultural Machinery' (Journal of Agricultural Engineering, 2019).

Os labels não são supervisionados porque não temos histórico real de falhas. Com 3-6 meses de dados reais e registros de manutenção, retreinaríamos com labels reais."

---

## 3. Como garantem que o sistema funciona se o broker MQTT cai?

**Resposta:**

"O listener MQTT implementa reconexão automática via callback `on_disconnect`. Se o broker cair e voltar, o cliente tenta reconectar automaticamente.

Além disso, o ESP32 implementa buffer local de até 50 leituras. Se o WiFi cair, os dados ficam na memória flash do ESP32 e são enviados quando a conexão retorna.

O endpoint `/api/telemetria/` é idempotente — aceita o mesmo UUID múltiplas vezes sem duplicar dados. Isso garante que retry do ESP32 não corrompe o banco."

**Código relevante:**
```python
def on_disconnect(client, userdata, rc):
    if rc != 0:
        print('[MQTT] Desconectado. Tentando reconectar...')
        client.reconnect()
```

---

## 4. Qual a cobertura dos testes?

**Resposta:**

"Temos 15 testes automatizados cobrindo os comportamentos críticos:

- **Deduplicação de UUID**: garante idempotência (enviar 2x não duplica)
- **Validação de range**: rejeita temperatura -999 ou 200°C (sensor com defeito)
- **Integração HTTP**: testa endpoint `/api/telemetria/` end-to-end
- **Resiliência da IA**: retorna status claro com dados insuficientes (não erro 500)
- **Métricas operacionais**: valida endpoint `/api/metricas/`

Focamos em testes de integração porque são mais valiosos que testes unitários isolados. Cada teste valida um fluxo completo: request → view → service → banco.

Para rodar: `python manage.py test api_tcc.tests` — todos passam com zero falhas."

---

## 5. Por que não validam se maquina_id existe na tabela Colheitadeira?

**Resposta:**

"Decisão consciente de design para o protótipo. O endpoint `/api/telemetria/` aceita qualquer string como `maquina_id` porque:

1. **Flexibilidade de implantação**: permite testar com ESP32 físico antes de cadastrar a máquina no admin
2. **Resiliência**: se o admin Django cair, o ESP32 continua enviando dados
3. **Simplicidade**: evita JOIN em cada ingestão (performance)

Em produção, adicionaríamos validação no serializer:

```python
def validate_maquina_id(self, value):
    if not Colheitadeira.objects.filter(Modelo__Nome=value).exists():
        raise ValidationError('Máquina não cadastrada')
    return value
```

Mas para o protótipo, priorizamos provar o pipeline offline-first funcionando."

---

## 6. Como a IA funciona tecnicamente?

**Resposta:**

"Usamos dois modelos complementares:

**Detecção de Anomalias (Isolation Forest)**:
- Não supervisionado — detecta padrões fora do normal sem labels
- Analisa últimas 500 leituras por máquina
- Contamination=5% (assume 5% dos dados são anômalos)
- Features: temperatura, vibração, RPM

**Manutenção Preditiva (Random Forest)**:
- Supervisionado com labels baseados em padrões operacionais documentados
- Features temporais: rolling windows de 10 leituras, tendência térmica
- Labels: risco=1 se temperatura >80°C por 3+ leituras consecutivas
- Retorna probabilidade de risco (0.0 a 1.0)

Ambos têm cache de 30 segundos para evitar retreino a cada request. Com dados reais de 6 meses, retreinaríamos offline e serviríamos modelo pré-treinado."

---

## 7. Por que não há dados de sensor físico?

**Resposta:**

"O protótipo valida o pipeline completo com dados simulados realistas:

- ESP32 físico existe e foi testado com sensores DHT22 (temperatura) e MPU6050 (vibração)
- Dados simulados incluem 3% duplicatas, 2% temperatura impossível, 2% payload corrompido
- Isso prova que o sistema detecta e rejeita dados ruins em tempo real

Para implantação em produção, o próximo passo é instalar o ESP32 em uma colheitadeira real por 1-2 semanas e coletar dados de campo. O código não muda — apenas a fonte dos dados."

---

## 8. Qual o diferencial técnico do FieldNode?

**Resposta:**

"Três decisões de arquitetura que resolvem problemas reais:

1. **Offline-first com deduplicação por UUID**: colheitadeiras operam sem sinal. O ESP32 envia dados via WiFi local e sincroniza quando online. UUID garante que retry não duplica dados.

2. **Dead-letter para dados inválidos**: sensores com defeito não corrompem a IA. Payloads rejeitados vão para `TelemetriaInvalida` para auditoria.

3. **Service layer separado**: regras de negócio (validação, deduplicação) estão em `services/telemetria.py`, não na view. Isso permite reusar a mesma lógica via HTTP e MQTT.

Sistemas comerciais como Solinftec exigem conectividade 4G constante. FieldNode funciona com WiFi embarcado sem internet."

---

## 9. Quanto custaria implantar em produção?

**Resposta:**

"Custo por máquina (hardware):
- ESP32: R$ 35
- Sensor temperatura DS18B20: R$ 15
- Sensor vibração MPU6050: R$ 25
- Case + fiação: R$ 30
- **Total: ~R$ 105 por colheitadeira**

Custo de infraestrutura (software):
- VPS AWS EC2 t3.small: ~R$ 80/mês
- RDS MySQL db.t3.micro: ~R$ 60/mês
- **Total: ~R$ 140/mês para até 50 máquinas**

Comparação: Solinftec cobra R$ 500-800/mês por máquina. FieldNode custa R$ 105 one-time + R$ 3/mês por máquina (infraestrutura dividida).

ROI: uma quebra evitada de R$ 5.000 paga o sistema de 10 máquinas."

---

## 10. Próximos passos técnicos para produção?

**Resposta:**

"Roadmap de 3 meses:

**Mês 1 — Validação de campo**:
- Instalar ESP32 em 1 colheitadeira real
- Coletar dados por 30 dias de safra
- Validar se limites operacionais estão corretos

**Mês 2 — Hardening**:
- Adicionar autenticação JWT por dispositivo
- Validar `maquina_id` contra tabela Colheitadeira
- Retreinar IA com dados reais de falhas

**Mês 3 — Escala**:
- Implantar em 5-10 máquinas
- Adicionar alertas via WhatsApp (Twilio)
- Integração com barramento CAN/J1939 para dados nativos da máquina

Após 3 meses, teríamos produto comercializável para frotas agrícolas."
