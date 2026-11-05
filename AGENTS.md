# AGENTS.md — Contrato Operacional FieldNode

> Estado das tarefas: `FIELDNODE_LEVIATA_ROADMAP_V5.md` não está presente neste checkout. Não infira status sem roadmap disponível e evidências verificáveis.
>
> Regra: nada é marcado pronto sem a evidência da tarefa.
>
> Nunca afirmar em README/UI algo ausente de `docs/CLAIMS_VS_CODE.md`.

---

## 1. Objetivo

Este arquivo estabelece as regras operacionais gerais e de entrada para agentes de inteligência artificial e desenvolvedores que atuam no repositório **FieldNode**. O objetivo é garantir rigor metodológico, segurança, rastreabilidade e integridade arquitetural em todas as alterações.

---

## 2. Fontes de Referência e Hierarquia

Consulte os documentos oficiais conforme o tipo de informação necessária:

- **Sequência e estado das tarefas:** o roadmap `FIELDNODE_LEVIATA_ROADMAP_V5.md` não está presente neste checkout; solicite a fonte atual antes de atribuir status às tarefas.
- **Auditoria técnica e baseline reprodutível:** [`docs/BASELINE.md`](docs/BASELINE.md).
- **Matriz de afirmações e limites metodológicos:** [`docs/CLAIMS_VS_CODE.md`](docs/CLAIMS_VS_CODE.md).
- **Contrato operacional detalhado:** [`docs/agents/CONTRATO.md`](docs/agents/CONTRATO.md).

---

## 3. Regras Operacionais Essenciais

Todo agente deve cumprir impreterivelmente as seguintes diretrizes:

1. **Evidência antes de alteração:** Inspecione o repositório antes de editar. Nunca presuma que um arquivo, função, dependência ou comportamento existe ou não existe sem verificar no filesystem.
2. **Respeito estrito ao escopo:** Mantenha as alterações estritamente limitadas à tarefa designada. Não faça refatorações amplas, renomeações globais ou reorganizações estruturais sem solicitação explícita.
3. **Preservação de alterações preexistentes:** Não sobrescreva ou reverta trabalho de outros membros ou etapas anteriores. Identifique dependências antes de alterar.
4. **Proibição de invenção:** Não invente arquivos, dados, testes, resultados de benchmark, métricas de precisão ou funcionalidades inexistentes.
5. **Verificação real obrigatória:** Nunca declare sucesso sem executar os testes ou comandos correspondentes. Não declare "testes passaram" ou "build ok" sem evidência verificada.
6. **Proteção de segredos:** Nunca introduza senhas, chaves de API, credenciais ou tokens no código, logs ou bundles do frontend.
7. **Revisão de diff:** Inspecione integralmente o `git diff` antes de submeter alterações para assegurar ausência de efeitos colaterais e código morto.
8. **Segurança do Git e histórico:** Não reescreva histórico (`rebase`, `reset --hard`), não utilize `push --force` e não execute comandos destrutivos sem autorização explícita.
9. **Critério de conclusão:** Uma tarefa só pode ser dada como concluída quando todos os seus critérios de aceite forem validados com evidências documentadas.

---

## 4. Contrato Operacional Detalhado

As diretrizes técnicas aprofundadas para **Backend (Django)**, **Frontend (Next.js)**, **Banco de Dados & Migrações**, **Telemetria & Offline-First**, **Segurança (OWASP)**, **Testes** e **Definition of Done** estão detalhadas em:

👉 [`docs/agents/CONTRATO.md`](docs/agents/CONTRATO.md)

Consulte o contrato detalhado antes de iniciar qualquer implementação técnica ou arquitetural no repositório.
