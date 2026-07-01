# Deploy do Évora LeadFlow no GitHub e Vercel

Este guia publica o MVP do **Évora LeadFlow** em um repositório GitHub e faz o deploy no **Vercel** como aplicação FastAPI.

> Estado atual do projeto: FastAPI + dashboard HTML/Jinja + PostgreSQL externo. Não há frontend Next.js separado nesta versão do pacote.

## 1. Pré-requisitos

Instale no seu computador:

```bash
git --version
python --version
node --version
```

Opcional, mas recomendado:

```bash
npm install --global vercel@latest
```

Também é útil instalar o GitHub CLI:

```bash
# macOS
brew install gh

# depois autentique
gh auth login
```

## 2. Criar o repositório no GitHub

Entre na pasta do projeto:

```bash
cd evora-leadflow
```

Inicialize o Git:

```bash
git init
git add .
git commit -m "MVP do Évora LeadFlow"
git branch -M main
```

Crie um repositório privado e envie o código:

```bash
gh repo create evora-leadflow --private --source=. --remote=origin --push
```

Alternativa manual:

1. Crie um repositório privado chamado `evora-leadflow` no GitHub.
2. Copie a URL do repositório.
3. Rode:

```bash
git remote add origin https://github.com/SEU_USUARIO/evora-leadflow.git
git push -u origin main
```

## 3. Criar o banco PostgreSQL externo

O Vercel não deve usar o PostgreSQL do `docker-compose.yml`. Esse banco é apenas local.

Use um banco PostgreSQL gerenciado, por exemplo:

- Neon via Vercel Marketplace
- Supabase
- Railway
- Render PostgreSQL

Copie a URL de conexão. Ela deve ficar parecida com:

```env
DATABASE_URL=postgresql+psycopg2://usuario:senha@host:5432/database?sslmode=require
```

Alguns provedores entregam `postgresql://...`. Isso normalmente também funciona com SQLAlchemy/psycopg2. Se houver erro de SSL, adicione `?sslmode=require`.

## 4. Importar o projeto no Vercel

No painel do Vercel:

1. Clique em **Add New Project**.
2. Importe o repositório `evora-leadflow` do GitHub.
3. Use a pasta raiz do projeto.
4. O Vercel deve detectar Python/FastAPI automaticamente.
5. Mantenha o deploy conectado à branch `main`.

A versão atual já inclui:

- `vercel.json`
- `.python-version`
- `pyproject.toml`
- endpoint FastAPI em `app/main.py`

## 5. Variáveis de ambiente no Vercel

Configure no Vercel, em **Project Settings > Environment Variables**:

```env
APP_NAME=Évora LeadFlow
APP_ENV=vercel
TIMEZONE=America/Sao_Paulo
ENABLE_SCHEDULER=false
DAILY_REMINDER_HOUR=8
DATABASE_URL=postgresql+psycopg2://usuario:senha@host:5432/database?sslmode=require
DASHBOARD_USERNAME=evora
DASHBOARD_PASSWORD=troque_por_uma_senha_forte
WHATSAPP_VERIFY_TOKEN=crie_um_token_longo
WHATSAPP_ACCESS_TOKEN=
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_APP_SECRET=
WHATSAPP_GRAPH_VERSION=v23.0
DEFAULT_MANAGER_PHONE=
CRON_SECRET=crie_um_secret_longo
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5.5
```

Observações:

- `ENABLE_SCHEDULER=false` é importante no Vercel, porque o ambiente é serverless.
- A rotina diária deve ser feita pelo Vercel Cron, já configurado em `vercel.json`.
- O cron `0 11 * * *` roda às 11:00 UTC, equivalente a 08:00 em São Paulo.
- Não suba `.env` para o GitHub. Use apenas `.env.example` como referência.

## 6. Fazer o deploy

Observação sobre o cron: o `vercel.json` inclui um Cron Job diário em `/api/cron/daily-reminders`. O endpoint aceita chamadas do Vercel Cron pelos cabeçalhos padrão e usa `CRON_SECRET` para proteger chamadas manuais ou integrações externas com `Authorization: Bearer <CRON_SECRET>`.


Pelo painel do Vercel, clique em **Deploy**.

Ou pela CLI:

```bash
vercel login
vercel link
vercel deploy --prod
```

## 7. Testar produção

Após o deploy, teste:

```text
https://SEU-PROJETO.vercel.app/health
https://SEU-PROJETO.vercel.app/
https://SEU-PROJETO.vercel.app/api/health
```

O painel `/` e as rotas `/api/*` usam autenticação Basic Auth com:

```env
DASHBOARD_USERNAME
DASHBOARD_PASSWORD
```

## 8. Conectar o WhatsApp depois do deploy

No Meta for Developers, configure o webhook com:

```text
Callback URL: https://SEU-PROJETO.vercel.app/webhooks/whatsapp
Verify token: o mesmo valor de WHATSAPP_VERIFY_TOKEN
```

Depois preencha no Vercel:

```env
WHATSAPP_ACCESS_TOKEN=token_da_meta
WHATSAPP_PHONE_NUMBER_ID=id_do_numero
WHATSAPP_APP_SECRET=secret_do_app
```

## 9. Atenção para mensagens proativas

A rotina diária da Vitória chama corretores ativamente. Em produção, para WhatsApp real, mensagens iniciadas fora da janela de atendimento precisam ser feitas com templates aprovados na Meta.

Neste MVP, o envio usa mensagem de texto simples para facilitar teste. Antes de operar com equipe real, ajuste `app/services/whatsapp.py` para enviar templates aprovados nos lembretes proativos.

## 10. Fluxo de atualização depois que estiver no GitHub

Sempre que fizer alterações:

```bash
git add .
git commit -m "descreva a alteração"
git push
```

O Vercel fará novo deploy automaticamente quando a branch `main` for atualizada.
