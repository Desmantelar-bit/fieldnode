# S2-T4 · Chave do Gemini em header, sem vazar em log

## Arquivos alterados

- `api_tcc/services/agentic.py`
- `api_tcc/ia/explicacao_llm.py`
- `api_tcc/api/views_prescricao.py`
- `api_tcc/middleware.py`
- `setup/settings.py`
- `api_tcc/tests/test_agentic.py`
- `api_tcc/tests/test_resiliencia_llm.py`

## Chamadas e segredo

As duas chamadas HTTP encontradas, em `services/agentic.py` e `ia/explicacao_llm.py`, enviam a chave apenas no header `x-goog-api-key`, com `Content-Type: application/json`; nenhuma coloca a chave na URL ou no corpo. Ambas usam timeout de 2 segundos. A chamada agentiva suprime o encadeamento da exceção HTTP ao convertê-la para erro de domínio, sem incluir URL ou segredo na mensagem.

`RedactSecretsFilter`, em `api_tcc.middleware`, mascara `key=...` e `x-goog-api-key` em mensagens formatadas, argumentos e texto de exceção. Está associado aos handlers `file` e `console` da configuração `LOGGING`. A filtragem preserva o restante da mensagem e tipos de exceção úteis.

## Resiliência e cache

O circuito da explicação tem três falhas consecutivas para abrir por 120 segundos, usa lock de thread para controlar a tentativa `HALF_OPEN` única e fecha após sucesso. Timeout, falha de conexão, HTTP inválido, JSON/estrutura inesperada e chave ausente resultam em fallback baseado na recomendação determinística já calculada.

Limitação: o estado do circuit breaker é mantido em memória por processo, preservando o mecanismo existente; workers distintos do Gunicorn têm contadores independentes. A tentativa de recuperação é única dentro de cada processo.

Para decisões persistidas, a explicação é cacheada pela chave `decision_id` no backend Django configurado (DatabaseCache compartilhado). Sucesso dura 3600 segundos; fallback dura 120 segundos, permitindo nova tentativa após essa janela. Um lock de cache por decisão reduz chamadas concorrentes duplicadas; chamadas que encontram lock em andamento retornam fallback. Falha do cache não interrompe a resposta operacional. Pré-visualizações sem decisão persistida não têm `decision_id` e, por isso, não recebem esse cache.

O prompt continua sendo montado pelo backend a partir dos campos da análise existente. Não há acesso do Gemini ao banco. A consolidação de autorização e seleção definitiva de evidências permanece pendente de S5-T7.

## Evidência

- Teste focado (Swagger + resiliência LLM + agentic): **15 passed**, com `USE_SQLITE=True`, incluindo recuperação `HALF_OPEN`.
- `python manage.py check`: sem problemas.
- Busca `rg -n -i 'key=' api_tcc -g '*.py'`: nenhuma chamada de produção monta query string com chave Gemini. As ocorrências relevantes remanescentes são regex de redação, testes negativos/assertions e nomes `key` de modelos/autenticação/throttling que não representam envio ao Gemini.
- A primeira execução de testes usando o MySQL do `.env` não iniciou os testes porque a conta `fieldnode_user` recebeu `Access denied`; a repetição explícita com SQLite completou com sucesso.

