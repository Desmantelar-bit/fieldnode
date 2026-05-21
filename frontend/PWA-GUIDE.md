# 📱 FieldNode PWA - Guia de Instalação

## Como Instalar o FieldNode como App no Celular

### Android (Chrome)

1. **Abra o Chrome** no seu celular Android
2. **Navegue para** `http://127.0.0.1:8000/frontend/dashboard.html`
3. **Aguarde** o banner "Adicionar à tela inicial" aparecer
4. **Toque em "Adicionar"** quando solicitado
5. **Confirme** tocando em "Instalar"

**Alternativa manual:**
- Toque no **menu (⋮)** do Chrome
- Selecione **"Adicionar à tela inicial"**
- Confirme a instalação

### iOS (Safari)

1. **Abra o Safari** no seu iPhone/iPad
2. **Navegue para** `http://127.0.0.1:8000/frontend/dashboard.html`
3. **Toque no ícone de compartilhar** (□↑)
4. **Role para baixo** e toque em **"Adicionar à Tela de Início"**
5. **Confirme** tocando em "Adicionar"

### Desktop (Chrome/Edge)

1. **Abra o navegador** (Chrome ou Edge)
2. **Navegue para** `http://127.0.0.1:8000/frontend/dashboard.html`
3. **Clique no ícone de instalação** (⊕) na barra de endereços
4. **Confirme** clicando em "Instalar"

## Funcionalidades PWA

✅ **Funciona offline** - Dashboard continua funcionando sem internet
✅ **Ícone na tela inicial** - Acesso rápido como app nativo
✅ **Tela cheia** - Interface sem barras do navegador
✅ **Cache inteligente** - Assets carregam instantaneamente
✅ **Atualizações automáticas** - Notificação quando nova versão disponível

## Recursos Offline

- **Dashboard completo** funciona sem conexão
- **Dados em cache** das últimas sessões
- **Interface responsiva** otimizada para mobile
- **Sincronização automática** quando conexão retorna

## Troubleshooting

### "Não aparece opção de instalar"
- Certifique-se que está usando HTTPS ou localhost
- Verifique se o manifest.json está carregando corretamente
- Tente recarregar a página

### "App não funciona offline"
- Aguarde o service worker ser instalado completamente
- Recarregue a página uma vez após a primeira visita
- Verifique o console do navegador para erros

### "Ícones não aparecem"
- Os ícones são gerados automaticamente
- Para produção, substitua por ícones personalizados do FieldNode

## Para Desenvolvedores

### Testando PWA

```bash
# 1. Inicie o servidor Django
python manage.py runserver

# 2. Acesse via localhost (necessário para PWA)
http://127.0.0.1:8000/frontend/dashboard.html

# 3. Abra DevTools > Application > Service Workers
# Verifique se o SW está registrado e ativo
```

### Atualizando PWA

1. **Modifique** o `CACHE_NAME` em `sw.js`
2. **Recarregue** a página
3. **Notificação** de atualização aparecerá automaticamente

### Customização

- **Ícones**: Substitua arquivos em `/frontend/icons/`
- **Manifest**: Edite `/frontend/manifest.json`
- **Service Worker**: Modifique `/frontend/sw.js`

## Demonstração na Banca

### Pontos de Destaque

1. **Mostre a instalação** em tempo real no celular
2. **Demonstre funcionamento offline** desconectando Wi-Fi
3. **Exiba sincronização** ao reconectar
4. **Compare com apps nativos** - mesma experiência UX

### Script Sugerido

> "Agora vou demonstrar como o FieldNode funciona como Progressive Web App. 
> Vou instalar diretamente no celular... [instala]... 
> Agora vou desconectar a internet... [desconecta]... 
> Como podem ver, o dashboard continua funcionando normalmente. 
> Isso é crucial no campo, onde a conectividade é intermitente."

---

**Nota**: Este PWA foi otimizado para demonstração. Em produção, 
adicione ícones personalizados e configure domínio HTTPS adequado.