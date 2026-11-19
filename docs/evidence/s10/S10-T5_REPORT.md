# S10-T5 - evidência

Status inicial: **PENDENTE DE EXECUÇÃO REAL**.

Implementado: `scripts/backup.sh`, `scripts/restore.sh`, manifesto/hash, cifra com passphrase externa, retenção provisória e padrões no `.gitignore`.

Também foi criado `scripts/test_backup_restore.sh`, que monta dois bancos descartáveis no MySQL do Compose, executa o fluxo oficial e compara contagens. A sintaxe dos três scripts foi validada em container Linux.

Ainda não declarado: restore em Compose limpo, contagens por tabela, hashes de amostras, integridade relacional, log real e RPO/RTO. Esses campos só podem ser preenchidos após executar o procedimento com banco isolado e fixtures sintéticas.
