# Configuração passo a passo — Évora LeadFlow

## 1. Pré-requisitos

Instale:

- Docker Desktop ou Docker Engine.
- Docker Compose.
- Git, se for versionar o projeto.
- Python 3.12+, apenas para rodar scripts locais fora do Docker.

## 2. Copiar variáveis de ambiente

Na raiz do projeto:

```bash
cp .env.example .env
```

Edite `.env` e troque pelo menos:

```env
DASHBOARD_USERNAME=evora
DASHBOARD_PASSWORD=troque_esta_senha
WHATSAPP_VERIFY_TOKEN=crie_um_token_forte
```

## 3. Subir a plataforma local

```bash
docker compose up --build
```

Serviços iniciados:

- `postgres`: PostgreSQL local.
- `redis`: Redis local reservado para evolução do produto.
- `app`: FastAPI + dashboard em `http://localhost:8000`.

## 4. Verificar saúde da aplicação

```bash
curl http://localhost:8000/health
```

Resposta esperada:

```json
{"ok":true,"service":"Évora LeadFlow","env":"local"}
```

## 5. Acessar dashboard

Abra:

```text
http://localhost:8000
```

Use a autenticação básica configurada no `.env`:

```env
DASHBOARD_USERNAME
DASHBOARD_PASSWORD
```

O seed inicial cria:

- Corretor: Carlos Corretor — telefone `5516999990001`.
- Gestora: Mariana Gestora — telefone `5516999990002`.
- Empreendimento: Reserva Évora.
- Materiais comerciais simulados.

## 6. Testar a Vitória sem WhatsApp

Execute:

```bash
python scripts/simulate_message.py
```

Ou teste manualmente:

```bash
curl -X POST http://localhost:8000/api/simulate-message \
  -u evora:troque_esta_senha \
  -H "Content-Type: application/json" \
  -d '{"from_phone":"5516999990001","text":"tenho um lead","profile_name":"Carlos"}'
```

Continue mandando as respostas para o mesmo telefone:

```bash
curl -X POST http://localhost:8000/api/simulate-message \
  -u evora:troque_esta_senha \
  -H "Content-Type: application/json" \
  -d '{"from_phone":"5516999990001","text":"Bruno","profile_name":"Carlos"}'
```

## 7. Acessar Swagger

```text
http://localhost:8000/docs
```

As rotas `/api/*` usam Basic Auth.

## 8. Parar a plataforma

```bash
docker compose down
```

Para apagar o banco local também:

```bash
docker compose down -v
```

## 9. Deploy GitHub + Vercel

Leia:

```text
docs/GITHUB_VERCEL_DEPLOY.md
```

Resumo do ambiente de produção:

- App FastAPI na Vercel.
- Banco PostgreSQL externo/gerenciado.
- `ENABLE_SCHEDULER=false` na Vercel.
- Vercel Cron chamando `/api/cron/daily-reminders`.
- Webhook Meta em `/webhooks/whatsapp`.

## 10. Segurança mínima antes de piloto real

- Repositório GitHub privado.
- Senha forte no dashboard.
- `WHATSAPP_APP_SECRET` preenchido para validar assinatura da Meta.
- Banco com SSL.
- Dados reais apenas depois de revisar LGPD, consentimento e retenção.
- Templates aprovados para mensagens proativas no WhatsApp.
