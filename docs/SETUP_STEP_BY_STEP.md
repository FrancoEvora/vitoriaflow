# Configuração passo a passo — Évora LeadFlow

## Parte A — Rodar sem WhatsApp

### 1. Entrar na pasta

```bash
cd evora-leadflow
```

### 2. Criar `.env`

```bash
cp .env.example .env
```

### 3. Editar senha do painel

Abra `.env` e configure:

```env
DASHBOARD_USERNAME=evora
DASHBOARD_PASSWORD=uma_senha_forte
```

### 4. Subir a plataforma

```bash
docker compose up --build
```

### 5. Acessar painel

```text
http://localhost:8000
```

Use o usuário e senha do `.env`.

### 6. Testar a Vitória

```bash
curl -X POST http://localhost:8000/api/simulate-message \
  -u evora:uma_senha_forte \
  -H "Content-Type: application/json" \
  -d '{"from_phone":"5516999999999","profile_name":"Carlos","text":"Tenho um lead"}'
```

Continue a conversa repetindo o mesmo comando e trocando o campo `text`.

Sugestão de sequência:

```text
Tenho um lead
Mariana
não tenho
Instagram
Reserva Évora
construir no futuro
entrada de 20 mil e parcela 1500
90 dias
não
entrada
```

No final, a Vitória cria o lead, classifica, gera próxima ação e script.

---

## Parte B — Ativar OpenAI

### 1. Inserir chave

No `.env`:

```env
OPENAI_API_KEY=sua_chave
OPENAI_MODEL=gpt-5.4
```

Se esse modelo não estiver disponível na sua conta, use outro modelo habilitado.

### 2. Reiniciar app

```bash
docker compose restart app
```

Sem `OPENAI_API_KEY`, o MVP continua funcionando com regras comerciais locais.

---

## Parte C — Conectar WhatsApp Cloud API

### 1. Criar app na Meta

No Meta for Developers:

1. Criar app.
2. Adicionar produto WhatsApp.
3. Copiar `Phone Number ID`.
4. Gerar/copiar `Access Token`.
5. Copiar `App Secret`.

### 2. Configurar `.env`

```env
WHATSAPP_VERIFY_TOKEN=um_token_forte_qualquer
WHATSAPP_ACCESS_TOKEN=token_meta
WHATSAPP_PHONE_NUMBER_ID=phone_number_id_meta
WHATSAPP_APP_SECRET=app_secret_meta
WHATSAPP_GRAPH_VERSION=v23.0
```

### 3. Expor localhost com HTTPS

```bash
ngrok http 8000
```

### 4. Configurar webhook na Meta

Callback URL:

```text
https://SEU-NGROK/webhooks/whatsapp
```

Verify token:

```text
mesmo valor de WHATSAPP_VERIFY_TOKEN
```

Evento a assinar:

```text
messages
```

### 5. Testar no WhatsApp

Envie ao número configurado:

```text
Tenho um lead
```

A Vitória deve responder pelo WhatsApp.

---

## Parte D — Operação diária

### Rodar lembretes manualmente

```bash
docker compose exec app python scripts/send_daily_reminders.py
```

### Ver logs

```bash
docker compose logs -f app
```

### Rodar testes

```bash
docker compose exec app pytest -q
```

### Parar tudo

```bash
docker compose down
```

---

## Problemas comuns

### Painel pede senha repetidamente

Confira se o usuário/senha usados no navegador são iguais ao `.env`.

### Webhook não verifica na Meta

Confira:

- URL HTTPS pública;
- caminho `/webhooks/whatsapp`;
- token igual ao `WHATSAPP_VERIFY_TOKEN`;
- app rodando em `docker compose up`.

### WhatsApp recebe, mas não responde

Confira:

- `WHATSAPP_ACCESS_TOKEN`;
- `WHATSAPP_PHONE_NUMBER_ID`;
- permissões do token;
- logs do app.

### Vitória não usa IA generativa

Confira se `OPENAI_API_KEY` está preenchida e se o modelo de `OPENAI_MODEL` está habilitado. Sem chave, ela usa fallback local.
