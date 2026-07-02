# Évora LeadFlow

**Évora LeadFlow** é uma plataforma de CRM ativo para loteadoras, com a agente comercial **Vitória**. Esta versão entrega uma **demo premium funcional** inspirada nos mockups visuais: dashboard, leads, Vitória, materiais e relatórios.

> Status atual: versão demo para GitHub/Vercel, com Vitória e interações de WhatsApp simuladas. A integração real com Meta será feita em etapa posterior.

## Telas principais

- `/` — Dashboard executivo
- `/leads` — CRM e funil de leads
- `/vitoria` — Simulador da Vitória no estilo WhatsApp
- `/materiais` — Biblioteca de materiais e playbooks
- `/relatorios` — Gestão comercial e insights
- `/corretores` — Performance por corretor
- `/empreendimentos` — Produtos/loteamentos
- `/configuracoes` — Status da demo

## Rodar localmente

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Acesse:

```text
http://localhost:8000
```

Credenciais padrão:

```text
Usuário: evora
Senha: leadflow-demo
```

## Simular a Vitória

Pelo navegador:

```text
http://localhost:8000/vitoria
```

Pela API:

```bash
curl -X POST http://localhost:8000/api/simulate-message \
  -u evora:leadflow-demo \
  -H "Content-Type: application/json" \
  -d '{"from_phone":"5516999999999","text":"tenho um lead","profile_name":"Lucas Andrade"}'
```

## Deploy na Vercel

A aplicação é FastAPI e expõe a instância `app` em `app/main.py`. O arquivo `pyproject.toml` aponta o entrypoint para `app.main:app` e `vercel.json` já inclui cron opcional.

Para demo rápida, use SQLite efêmero:

```env
DEMO_FORCE_SQLITE=true
DATABASE_URL=sqlite:////tmp/leadflow_demo.db//tmp/leadflow_demo.db
APP_ENV=demo
ENABLE_SCHEDULER=false
DASHBOARD_USERNAME=evora
DASHBOARD_PASSWORD=troque_por_senha_forte
```

Depois de importar no Vercel, configure as variáveis de ambiente e faça o deploy.

## Estrutura

```text
app/
  main.py
  routers/
  services/
  templates/
  static/
docs/
scripts/
tests/
```

## Documentação

- `docs/DEMO_PREMIUM.md`
- `docs/GITHUB_VERCEL_DEPLOY.md`
- `docs/WHATSAPP_SETUP.md`
- `docs/VITORIA_PLAYBOOK.md`

## Próxima fase

- PostgreSQL permanente.
- Integração real com WhatsApp Cloud API.
- Templates proativos da Vitória na Meta.
- Login por perfil e permissões.
- Versionamento dos playbooks comerciais.

## Hotfix Vercel 500

Se aparecer `500: ERRO_INTERNO_DO_SERVIDOR` / `FUNCTION_INVOCATION_FAILED`, use esta versão ou confira `docs/VERCEL_500_HOTFIX.md`. Para a demo, a variável mais segura é:

```env
DEMO_FORCE_SQLITE=true
DATABASE_URL=sqlite:////tmp/leadflow_demo.db
```

Depois de alterar variáveis na Vercel, faça **Redeploy**.


## Correção rápida para Vercel 500

Se a Vercel exibir `FUNCTION_INVOCATION_FAILED`, confira `docs/VERCEL_500_TROUBLESHOOTING.md`. Esta versão é tolerante a variáveis vazias e inicializa o banco da demo também em runtime serverless.

## Nota de deploy Vercel

Se aparecer `500: FUNCTION_INVOCATION_FAILED`, verifique primeiro os logs do projeto na Vercel. Esta versão já inclui fallback para SQLite em `/tmp` e tolerância a variáveis vazias, então para a demo você pode deixar `DATABASE_URL` vazio e usar:

```env
APP_ENV=vercel
DEMO_FORCE_SQLITE=true
```

Depois de alterar variáveis de ambiente, faça **Redeploy**.
