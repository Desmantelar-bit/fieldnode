# Frentes e equipes v0.1

O cadastro operacional está disponível em `/frentes`. A tela permite criar uma
relação simples entre duas `Machine` e importar relações em CSV sem SQL.

O CSV exige o cabeçalho:

```text
origem,destino,tipo,front,de,ate
```

`origem` e `destino` usam `Machine.external_code`; `front` aceita o UUID ou o
código cadastrado da `Front`; datas aceitam ISO-8601. Os tipos permitidos são
`ALIMENTA`, `TRANSPORTA_PARA` e `DEPENDE_DE`.

A API valida todas as linhas antes da gravação e executa a operação em
transação. Se uma linha for rejeitada, nenhuma relação daquela importação é
persistida e o retorno lista a linha e o motivo. O comando equivalente é:

```text
python manage.py importar_links caminho.csv --organization <uuid>
```

Essa primeira versão não faz drag-and-drop. Ela entrega o vínculo operacional
com formulário e relatório de rejeição, que é o caminho curto entre a demo e
um cadastro auditável.
