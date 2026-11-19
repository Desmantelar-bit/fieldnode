# Backup e restore

## Estado

Os scripts oficiais existem, mas RPO/RTO só são considerados medidos depois de uma execução registrada em `docs/evidence/s10/S10-T5_REPORT.md`. Um hash prova integridade do arquivo; não prova que o banco restaura.

## Estratégia

`backup.sh` executa `mysqldump --single-transaction` dentro do serviço `db`, limitado ao banco configurado em `MYSQL_DATABASE`, preserva rotinas, triggers e eventos, compacta e cifra com OpenSSL AES-256-CBC + PBKDF2. A passphrase é lida de `FIELDNODE_BACKUP_PASSPHRASE_FILE`; ela não pode estar no repositório, no manifesto ou ao lado do backup.

```bash
mkdir -p backups
printf '%s' 'segredo-fora-do-repo' > /caminho/protegido/fieldnode.backup-key
FIELDNODE_BACKUP_PASSPHRASE_FILE=/caminho/protegido/fieldnode.backup-key ./scripts/backup.sh
```

O manifesto registra identificador, horários e hashes. A retenção inicial é provisória e por quantidade (`FIELDNODE_BACKUP_KEEP`, padrão 7). A remoção nunca deve ser usada antes de haver outro artefato válido. O último backup deve ser preservado operacionalmente.

## Restore de teste

O script exige banco de destino explícito, manifesto, hash, passphrase e confirmação nominal:

```bash
FIELDNODE_BACKUP_PASSPHRASE_FILE=/caminho/protegido/fieldnode.backup-key \
FIELDNODE_RESTORE_DATABASE=fieldnode_restore_test \
FIELDNODE_RESTORE_CONFIRM=RESTORE_TEST_fieldnode_restore_test \
./scripts/restore.sh backups/fieldnode_YYYYMMDDTHHMMSSZ.sql.gz.enc
```

O banco de teste deve ser isolado, criado no Compose e validado com contagens por tabela, hashes de amostras e `manage.py check`. Não executar sobre produção. O dump não contém arquivos persistidos, modelos ML, segredos, configuração externa ou estado do broker; esses itens precisam de procedimento próprio.

Para fixtures descartáveis, `scripts/test_backup_restore.sh` cria dois bancos isolados, insere três linhas, executa os scripts oficiais, restaura e compara a contagem. Ele exige a mesma passphrase externa e deixa os bancos de fixture para limpeza automática.

## RPO e RTO

RPO observado é o intervalo entre o horário de referência do incidente e o último backup válido. RTO observado inclui preparação, verificação, descriptografia, importação e readiness da aplicação. Nenhuma meta é afirmada antes de execução real e repetível.
