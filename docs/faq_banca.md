# FAQ Técnico — Banca FieldNode

Respostas ancoradas no código real do projeto. Cada resposta cita o arquivo e a lógica exata que sustenta o argumento.

---

## 1. Qual o diferencial do FieldNode frente à Solinftec, John Deere Operations Center e similares?

Três diferenças estruturais, não de marketing:

**Offline-first real, não "tolerante a falhas".**
Soluções como Solinftec e JD Operations Center dependem de conectividade celular contínua ou Wi-Fi na sede. O FieldNode foi projetado para o cenário inverso: a rede é a exceção, não a regra. O Service Worker (`frontend-next/public/sw.js`) intercepta chamadas de telemetria quando o browser perde conexão e enfileira via `QUEUE_TELEMETRY`. Quando a rede volta, a fila drena automaticamente para `/api/telemetria/`. No lado do simulador de campo, `scripts/simular_mqtt.py` detecta `Connection refused` no broker MQTT e entra em modo fallback HTTP sem intervenção humana — demonstrado com `MQTT_PORT=1884 DEMO_CYCLES=1`.

**Hardware agnóstico e sem lock-in.**
Soluções de grandes fabricantes são proprietárias: o sensor só funciona com o software deles, o software só funciona com o hardware deles. O FieldNode usa ESP32 (~R$ 50 por nó) e protocolo MQTT padrão. Qualquer máquina com porta serial ou CAN-bus pode ser instrumentada. O backend aceita qualquer `maquina_id` — a validação em `api_tcc/services/telemetria.py` não exige que a máquina esteja pré-cadastrada no banco para aceitar telemetria.

**Custo de implantação.**
Um nó ESP32 com sensor de temperatura, vibração e GPS custa menos de R$ 150. Módulos telemétricos proprietários de fabricantes como John Deere custam entre R$ 2.000 e R$ 8.000 por máquina, com contrato de assinatura anual. Para frotas de pequenos e médios produtores, isso é a diferença entre implantar ou não implantar.

---

## 2. O que acontece quando a IA falha ou não tem dados suficientes?

O pipeline foi projetado para degradar sem quebrar. Há dois cenários distintos:

**Dados insuficientes (caso mais comum no início da implantação).**
A função `carregar_dados()` em `api_tcc/ia/pipeline.py` exige mínimo de 10 leituras antes de alimentar qualquer modelo:

```python
if len(registros) < minimo:
    return {
        "status": "dados_insuficientes",
        "minimo": minimo,
        "atual": len(registros),
    }
```

Quando isso ocorre, `gerar_prescricao()` em `api_tcc/ia/prescricoes.py` retorna `{"status": "dados_insuficientes", "detalhe": "Requer mínimo de 10 leituras, atual: N"}` — sem exceção, sem HTTP 500, sem prescrição inventada. O frontend trata esse estado com `ErrorState` de variante `insufficient`.

**Falha de modelo (exceção inesperada).**
O worker de IA roda em thread daemon separada (`_ia_worker` em `pipeline.py`). Se um modelo lançar exceção, o `try/except` do worker captura, loga via `logger.exception()` e continua processando a fila. A ingestão de telemetria não é afetada — o ESP32 já recebeu `201` antes do worker sequer começar a processar.

```python
try:
    rodar_modelos(maquina_id, modelos=modelos)
except Exception:
    logger.exception("Falha no processamento de IA agendado para %s", maquina_id)
finally:
    _ia_work_queue.task_done()
```

O dado entra no banco independentemente do resultado da IA. A prescrição simplesmente não é gerada naquele ciclo — na próxima leitura, o worker tenta novamente.

---

## 3. O sistema realmente funciona sem internet? Como garante que dados não se perdem?

Sim. A resiliência offline tem três camadas independentes:

**Camada 1 — Service Worker no browser.**
`frontend-next/public/sw.js` intercepta requisições para `/api/telemetria/` quando o dispositivo está offline e enfileira via mensagem `QUEUE_TELEMETRY`. Quando a conexão é restaurada, o worker drena a fila automaticamente. O operador no campo não precisa fazer nada.

**Camada 2 — Fallback HTTP no simulador de campo.**
`scripts/simular_mqtt.py` tenta conectar ao broker MQTT. Se receber `Connection refused`, entra em `loop_fallback_api()` e envia diretamente para `/api/telemetria/` via HTTP com coordenadas GPS reais. O sistema não para — degrada para o protocolo mais simples disponível.

**Camada 3 — Deduplicação UUID no backend.**
O UUID é gerado no dispositivo antes do envio (`str(uuid.uuid4())` no simulador, equivalente no firmware ESP32). Se a rede cair após o servidor receber mas antes de confirmar, o dispositivo reenvia o mesmo pacote. O backend detecta a duplicata em `registrar_leitura()` de `api_tcc/services/telemetria.py`:

```python
if uuid_recebido and LeituraTelemetria.objects.filter(id=uuid_recebido).exists():
    return "duplicata", str(uuid_recebido)
```

Retorna `200` sem gravar novamente. O banco nunca tem duplicatas, independente de quantas vezes o pacote foi reenviado. Isso foi validado nos testes em `api_tcc/tests/test_telemetria.py` — `test_ingestao_duplicada_retorna_200_sem_duplicar`.

---

## 4. Como o GPS é validado? O que acontece quando a máquina não tem GPS?

**Validação do dado GPS.**
`latitude` e `longitude` são campos opcionais no modelo `LeituraTelemetria`. A função `validar_payload()` em `api_tcc/services/telemetria.py` só valida GPS se o campo estiver presente no payload:

```python
if "latitude" in dados and dados["latitude"] is not None:
    lat = float(dados["latitude"])
    if not (-90 <= lat <= 90):
        return False, f"latitude={lat} fora do range [-90, 90]"

if "longitude" in dados and dados["longitude"] is not None:
    lng = float(dados["longitude"])
    if not (-180 <= lng <= 180):
        return False, f"longitude={lng} fora do range [-180, 180]"
```

Um payload sem GPS é aceito normalmente. Um payload com GPS inválido (ex: `latitude: 999`) é rejeitado com `400` e arquivado em `TelemetriaInvalida` para auditoria.

**Comportamento do mapa sem GPS.**
`frontend-next/src/components/MapClient.tsx` tenta buscar posições reais em `/api/maquinas/posicao/`. Se a API falhar ou retornar vazio, o componente entra automaticamente em modo demo:

```typescript
} catch {
    const fallback = buildDemoPositions(new Date().toISOString());
    setPositions(fallback);
    setDemo(true);
}
```

O mapa exibe um banner "Modo Demo - Rota Simulada" com rota pré-definida sobre coordenadas reais do Cerrado brasileiro. O operador sabe que está vendo dados simulados — não há ilusão de precisão.

---

## 5. Por que UUID no sensor e não ID sequencial gerado pelo banco?

O `seq_id` existe e é visível na API — mas é gerado pelo banco após a gravação, não pelo sensor.

O problema com ID sequencial para deduplicação: se o ESP32 envia o pacote, a rede cai antes da confirmação chegar, e o firmware reenvia — o banco não tem como saber que é o mesmo pacote. Geraria dois registros com IDs diferentes para a mesma leitura física.

O UUID é gerado no dispositivo antes do envio. O banco usa o UUID como chave primária (`UUIDField(primary_key=True)`). Reenvios do mesmo pacote são detectados por `filter(id=uuid_recebido).exists()` antes de qualquer `INSERT`. O `seq_id` é gerado sequencialmente no `save()` do modelo e serve para consultas ordenadas por humanos e para o frontend exibir histórico em ordem.

---

## 6. Como a segurança foi tratada?

Três decisões conscientes, proporcionais ao contexto de protótipo acadêmico:

**API Key no header.** Todo `POST /api/telemetria/` exige `X-API-Key` validado em `views_ingestao.py`. O ESP32 não suporta JWT nativamente sem biblioteca que consome ~30% da memória flash disponível. API key simples é o equilíbrio correto entre segurança e limitação de hardware.

**Segredos fora do repositório.** `.env` está no `.gitignore`. O repositório contém apenas `.env.example` com placeholders. `SECRET_KEY` e `FIELDNODE_API_KEY` nunca foram commitados.

**CORS configurado.** `CORS_ALLOWED_ORIGINS` em `.env` restringe quais origens podem chamar a API. Em produção, apenas o domínio do frontend é permitido.

---

## 7. Por que Django e não FastAPI, Node.js ou outra stack mais "moderna"?

Quatro razões técnicas, não de preferência:

- **ORM + migrations prontos.** O modelo de dados do FieldNode tem 12 tabelas relacionadas. Django ORM e `makemigrations` eliminam SQL manual e versionam o schema junto com o código.
- **Admin gratuito.** O Django Admin gerou a interface de cadastro de colheitadeiras, operários e modelos sem uma linha de frontend extra — útil para demo e para o orientador explorar o banco.
- **Ecossistema Python para IA.** scikit-learn, pandas e numpy rodam no mesmo processo que o Django. Com FastAPI seria o mesmo, mas com Node seria necessário um microserviço Python separado — complexidade desnecessária para o escopo do projeto.
- **TestCase integrado.** `python manage.py test` roda os testes com banco em memória SQLite sem configuração adicional. Os 3 casos de `api_tcc/tests/test_telemetria.py` rodam em 0.111s.
