# S12-T11 - acesso a máquina real e piloto observacional

Status: **MATERIAL DE ABORDAGEM PRONTO; CONTATOS, AUTORIZAÇÃO E PILOTO PENDENTES.**

Este documento organiza a busca por acesso institucional a uma máquina agrícola real. Ele não afirma que exista parceiro, carta assinada ou validação de campo. A política atual confirma que o FieldNode ainda não foi validado em máquina real (`docs/VALIDACAO_DE_CAMPO.md`).

## 1. Resumo de uma página

### Problema a investigar

Em operações agrícolas, informações de máquina podem chegar atrasadas, incompletas ou por canais diferentes. O FieldNode quer investigar, com profissionais, se uma coleta observacional e uma visão de contexto ajudam a reconhecer ocorrências e encaminhá-las para revisão humana. Isso é uma hipótese de pesquisa, não uma afirmação universal nem promessa de redução de falhas.

### O que é o FieldNode

O FieldNode combina uma fonte de telemetria, um gateway e uma API para registrar leituras, qualidade, origem e tempo. O software local valida e deduplica dados, aplica regras de triagem e pode apresentar eventos para revisão humana. Hoje há código, simuladores e testes locais; a operação em máquina agrícola, o conjunto físico de sensores e a utilidade dos alertas ainda precisam de avaliação real.

### O que queremos avaliar

- qualidade, origem e continuidade dos dados autorizados;
- comportamento do enlace no ambiente escolhido;
- contexto operacional dos sinais observados;
- utilidade percebida dos alertas, sem automatizar decisões;
- tempo até reconhecer um alerta, conforme definição conjunta;
- limitações, falsos alarmes e situações em que o dado não basta.

### O que não será feito

- nenhuma escrita no barramento CAN;
- nenhuma alteração de ECU ou de configuração crítica;
- nenhum acionamento remoto ou controle da máquina;
- nenhuma interferência na operação;
- nenhuma instalação sem aprovação e supervisão de pessoa autorizada;
- nenhuma coleta sem consentimento e autorização;
- nenhuma promessa de diagnóstico, previsão de falha ou resultado financeiro.

Se a instalação exigir algo além de observação autorizada e leitura, a atividade deve parar para reavaliação técnica e de segurança.

## 2. Pedido formal e curto

O primeiro contato pede uma conversa, não acesso imediato ao equipamento. Adaptar o texto ao canal e ao perfil; não enviar para pessoas sem vínculo legítimo conhecido.

### Professor ou mentor técnico

> Olá, [nome]. Somos a equipe do FieldNode, um projeto acadêmico que investiga telemetria e apoio à observação operacional de máquinas agrícolas. Estamos revisando os riscos e limites antes de qualquer avaliação em ambiente real. Pela sua experiência com [tema], gostaríamos de pedir uma conversa de 20 minutos para entender requisitos e cuidados. Não estamos pedindo acesso a máquina nem prometendo resultado. Posso enviar um resumo de uma página?

### Profissional de manutenção

> Olá, [nome]. Estamos estudando como equipes de manutenção recebem, verificam e registram sinais de máquinas agrícolas. O FieldNode é um protótipo de observação; não altera a máquina, não escreve no barramento e não substitui o profissional. Você teria 20 minutos para contar como esse processo funciona na prática? A conversa é voluntária e podemos anonimizar o registro.

### Usina ou responsável pela frota

> Olá, [nome]. Somos a equipe do FieldNode e estamos investigando um possível teste observacional de telemetria em operação agrícola. O software atual é de bancada e ainda não foi validado em máquina real. Gostaríamos primeiro de entender requisitos, segurança e critérios de uma eventual avaliação de duas semanas, sem compromisso de instalação ou contratação. Há alguém responsável por manutenção, frota ou tecnologia com quem possamos conversar?

### Oficina ou concessionária

> Olá, [nome]. Estamos desenvolvendo o FieldNode, um protótipo para registrar sinais autorizados e apoiar a revisão humana de ocorrências em máquinas agrícolas. Procuramos uma conversa técnica com uma oficina ou concessionária, sem pedir credenciais, dados confidenciais ou intervenção em equipamento. Você teria disponibilidade para comentar quais cuidados e informações seriam necessários antes de qualquer avaliação?

## 3. Registro de contatos

Preencher somente com contatos reais, obtidos por referência legítima ou canal institucional. Usar identificador e anonimização quando necessário. A ausência de resposta não é rejeição.

| ID | Organização ou contato autorizado | Perfil | Origem do contato | Canal | Data de abordagem | Status | Próxima ação | Observações |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| - | Nenhum contato registrado no checkout | - | - | - | - | PENDENTE | Identificar 5 a 10 contatos reais | Não inventar nomes, telefones, e-mails ou vínculos |

Status permitidos: `IDENTIFICADO`, `A ABORDAR`, `ABORDAGEM ENVIADA`, `RESPONDEU`, `CONVERSA AGENDADA`, `INTERESSE EM AVALIAÇÃO`, `INTERESSE EM PILOTO`, `CARTA EM DISCUSSÃO`, `CARTA ASSINADA`, `RECUSOU`, `SEM RESPOSTA`, `ENCERRADO`.

Meta operacional: enviar pelo menos cinco pedidos entre as semanas 1 e 2 e registrar cada resposta, inclusive ausência de resposta.

## 4. Plano preliminar de duas semanas

### Escopo

- ambiente e máquina: definir com o parceiro; não presumir colheitadeira, marca ou local;
- duração: 14 dias corridos, ou período menor acordado e registrado;
- modo: exclusivamente observacional e supervisionado;
- dados: somente sinais, metadados e eventos previamente autorizados;
- saída: relatório de dados, incidentes, limitações e avaliação conjunta;
- remoção: retirar o dispositivo, revogar credenciais, apagar ou devolver dados conforme o termo e registrar a retirada.

### Aprovações e responsabilidades

Antes de começar, identificar quem aprova a instalação, quem supervisiona a operação, quem pode interromper, quem recebe os dados e quem autoriza a remoção. A equipe do FieldNode não decide sozinha sobre segurança da máquina ou da operação.

### Dados possíveis

Registrar apenas o que for autorizado: identificador da máquina ou pseudônimo, timestamp, origem do dado, sinais observados, qualidade do enlace, estado de sincronização, eventos gerados, confirmação humana e incidentes. Não coletar credenciais, dados pessoais desnecessários, informações proprietárias ou localização precisa sem necessidade e autorização.

### Métricas a acordar antes

As metas numéricas devem ser definidas com o parceiro antes do início. As métricas candidatas são:

| Métrica | Definição preliminar | Fonte | Meta |
| --- | --- | --- | --- |
| Tempo até reconhecer alerta | intervalo entre alerta recebido e reconhecimento humano | logs e registro do operador | A acordar |
| Falso alarme | alerta classificado como não útil pelo responsável, com justificativa | revisão humana | Acordar definição; não presumir diagnóstico |
| % de OS abertas | proporção de alertas que, quando aplicável, geram OS autorizada | sistema de OS do parceiro | Acordar denominador |
| Disponibilidade do enlace | tempo ou leituras recebidas em relação ao período observado | gateway e logs | Acordar janela e tolerância |
| Dados insuficientes | eventos sem contexto para decisão | revisão amostral | Acompanhar, não esconder |

Nenhuma dessas métricas, isoladamente, prova eficácia mecânica ou retorno financeiro.

### Sequência

1. Semana 0: revisão por professor/mentor, autorização, análise de risco e definição das métricas.
2. Dia 1: instalação supervisionada, inventário, teste de leitura e registro do estado inicial.
3. Dias 2 a 6: observação sem intervenção; checagem diária de dados e incidentes.
4. Dia 7: revisão intermediária; continuar, ajustar ou interromper.
5. Dias 8 a 13: observação e entrevistas curtas, se autorizadas.
6. Dia 14: retirada ou encerramento acordado, conferência de dados e avaliação conjunta.

## 5. Interrupção imediata

Interromper a coleta e, se necessário, remover o equipamento quando houver:

- risco à segurança de pessoas, máquina ou operação;
- interferência, instabilidade ou suspeita de interferência na máquina;
- tentativa de escrita no barramento, controle remoto ou alteração não autorizada;
- aquecimento, alimentação, fixação ou dano físico fora do esperado;
- coleta de dados além do escopo autorizado;
- perda de controle sobre credenciais ou dados;
- pedido do responsável autorizado, sem necessidade de justificativa;
- qualquer condição em que a equipe não consiga explicar o comportamento do sistema.

## 6. Evidências e aceite

Para declarar esta tarefa concluída, anexar ou referenciar: cinco ou mais abordagens reais, tabela atualizada, respostas, revisão do material por professor/mentor, autorização formal quando houver, carta assinada quando houver e relatório final. Sem isso, o estado permanece `PENDENTE`, e o resultado deve virar pauta de `PROXIMO_CICLO.md`.

### Limites

Um contato não é parceiro; interesse não é autorização; carta não é piloto; piloto não é prova de eficácia. Esses estágios devem continuar separados no registro.
