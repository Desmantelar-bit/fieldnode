# FieldNode — Roteiro Oficial da Demonstração (Banca)

> **Regra de Ouro:** Não improvise. Siga o roteiro passo a passo para garantir que todas as camadas do sistema (Ingestão, IA, Frontend e Resiliência) sejam apresentadas perfeitamente.

## Pré-requisitos (Antes de projetar a tela)

1. Certifique-se de que o backend está rodando: `python manage.py runserver`
2. Certifique-se de que o frontend está rodando: `npm run dev`
3. Deixe um terminal extra aberto na pasta `scripts/` para rodar os simuladores.

---

## Passo 1: O Cenário Ideal (Status Normal)

* **Ação Terminal:** Execute `python scripts/simular_cenarios.py` e acione a função `cenario_normal`.
* **Ação UI:** Abra o Dashboard do FieldNode.
* **Discurso/Demonstração:** Mostre as leituras de temperatura e vibração fluindo sem alarmes. Destaque que o status global da frota e da máquina está **Verde (NORMAL)**.

## Passo 2: A Injeção de Anomalia

* **Ação Terminal:** Interrompa o script anterior e acione `cenario_temperatura_crescente`.
* **Ação UI:** Volte ao Dashboard e aguarde alguns segundos.
* **Discurso/Demonstração:** Mostre a linha do gráfico subindo progressivamente. Aponte para a mudança de cor do card (para **ATENÇÃO** ou **CRÍTICO**) no exato momento em que o limite estatístico é cruzado pelas leituras.

## Passo 3: O Motor de Prescrição

* **Ação UI:** Clique no botão/ícone para abrir os detalhes ou a tela de "Prescrição" da máquina alarmada.
* **Discurso/Demonstração:** Leia o motivo específico diagnosticado pelo sistema ("temperatura acima de 85°C"). Destaque a recomendação técnica operacional ("Inspeção imediata recomendada...").

## Passo 4: Navegação Segura (Bug Fix)

* **Ação UI:** Clique no botão "Voltar" ou na "Sidebar" para retornar ao mapa ou dashboard.
* **Discurso/Demonstração:** Faça essa transição de forma natural para provar a fluidez do frontend (SPA), mostrando que não há *crashes* de estado ao desmontar componentes pesados.

## Passo 5: Geração de Relatório Executivo

* **Ação UI:** Navegue até a tela de Relatórios e clique em "Exportar XLSX".
* **Ação Externa:** Abra o arquivo baixado no Microsoft Excel ou Google Sheets.
* **Discurso/Demonstração:** Mostre o nível de maturidade do software exibindo as 3 abas separadas (Resumo, Telemetria, Eventos), ressaltando a formatação condicional das células calculada direto no backend.

## Passo 6: O Teste de Resiliência (Fogo Cruzado)

* **Ação Terminal:** Dê um `CTRL+C` abrupto no terminal que está rodando o `runserver` do Django (derrube a API).
* **Ação UI:** Continue na tela do frontend.
* **Discurso/Demonstração:** "Em campo, a internet falha o tempo todo." Mostre o indicador "API online" da Sidebar mudando graciosamente para vermelho/offline em até 15 segundos, **sem que a tela inteira exploda ou dê erro 500**.

## Passo 7: Recuperação Automática

* **Ação Terminal:** Suba o `runserver` novamente.
* **Ação UI:** Observe o indicador na Sidebar voltar a ficar verde.
* **Discurso/Demonstração:** "Assim que o Gateway retoma conexão, o sistema volta a operar e ingerir o buffer de telemetria sem intervenção humana." Fim da demonstração.
