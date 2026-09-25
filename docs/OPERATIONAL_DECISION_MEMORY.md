# Memória de Decisão Operacional (Operational Decision Memory)

Este documento descreve o ciclo de vida e a máquina de estados das decisões operacionais (`Decision`) no FieldNode, registrando como recomendações geradas pelo sistema evoluem mediante ação humana.

## 1. O que é uma Decision?

Uma `Decision` representa uma recomendação operacional gerada pelo sistema de inteligência ou por regras determinísticas, aguardando validação ou execução por um operador. É a ponte entre a inferência automatizada e a responsabilidade humana.

Diferente de telemetria pura ou alertas transitórios, a `Decision` é auditável: armazena quem tomou a decisão, quando e o motivo (se fornecido).

## 2. Máquina de Estados e Transições

O ciclo de vida de uma Decision segue uma máquina de estados rígida, protegida no backend (Django) e refletida na UI (Next.js).

### Status Disponíveis

* **PENDENTE**: Estado inicial. A recomendação foi gerada mas ainda não sofreu intervenção humana.
* **APROVADA**: Um usuário autenticado concordou com a recomendação (mas ela ainda não foi necessariamente executada fisicamente).
* **REJEITADA**: Um usuário autenticado discordou da recomendação ou decidiu ignorá-la de forma consciente (estado terminal).
* **EXECUTADA**: A ação física correspondente à recomendação foi realizada e registrada no sistema (estado terminal).
* **EXPIRADA**: A decisão ficou pendente por tempo superior à janela de validade e o sistema a invalidou, possivelmente substituindo por uma recomendação mais nova (estado terminal).

### Transições Permitidas (Frontend / Ações Humanas)

As ações humanas ocorrem através do modal de prescrição (`PrescricaoModal`), onde o usuário interage com o registro correspondente.

| Estado Atual | Ação na Interface       | Próximo Estado | Comportamento UI / Condição |
| :--- | :--- | :--- | :--- |
| **PENDENTE** | Clicar em "Aprovar ação" | **APROVADA**   | Requer usuário autenticado. Exibe input opcional de "Resultado observado". |
| **PENDENTE** | Clicar em "Rejeitar"    | **REJEITADA**  | Requer usuário autenticado. Exibe confirmação de segurança nativa (prompt). Campo opcional de "Motivo da rejeição". |
| **APROVADA** | Clicar "Marcar executada" | **EXECUTADA**  | Requer usuário autenticado. Exibe confirmação de segurança nativa. |
| *Qualquer terminal* | N/A | N/A | (REJEITADA, EXECUTADA, EXPIRADA) A UI não exibe mais botões de ação, tratando a decisão como finalizada (histórico). |

*Nota: Transições inválidas (ex: PENDENTE → EXECUTADA diretamente) são bloqueadas pelo backend (HTTP 400), independentemente da interface.*

## 3. Atores e Permissões

* **Sistema (Pipeline ML / Event Engine)**: Único responsável por criar decisões no estado `PENDENTE`.
* **Operador/Admin Autenticado**: Usuários logados, pertencentes à mesma organização da máquina (com papéis adequados), têm permissão para disparar ações (`PATCH /api/decisions/<id>/`) que transitam a Decision para `APROVADA`, `REJEITADA` ou `EXECUTADA`.
* **Usuário Anônimo (Modo Demo Público)**: Consegue ver a prescrição, mas ao tentar aprovar/rejeitar, é interceptado no frontend e redirecionado para a página de Login, preservando a rota de retorno (parâmetro `?next=`). O backend também retornará 401/403 (Unauthorized/Forbidden) caso o endpoint receba chamadas sem token.

## 4. Integração Frontend (UI)

O `PrescricaoModal` no Next.js atua como o ponto de controle.
- Não há interface otimista (Optimistic UI). A UI aguarda o JSON de resposta (HTTP 200) do `PATCH` para atualizar a visualização (fonte da verdade do backend).
- O modal exibe de forma clara quem tomou a decisão (`decidido_por_username`) e a observação (`outcome_texto`) assim que a transição de estado ocorre com sucesso.
