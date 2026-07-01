# Évora LeadFlow — Demo Premium com Vitória simulada

Esta versão é uma demo funcional e visualmente inspirada nos mockups premium do Évora LeadFlow.

## O que funciona agora

- Dashboard executivo inspirado nas telas conceituais.
- Página de Leads com funil, filtros, tabela e detalhe lateral.
- Página da Vitória com conversa simulada no estilo WhatsApp.
- Página de Materiais e Playbooks.
- Página de Relatórios de gestão comercial.
- Corretores, empreendimentos e configurações.
- API `/api/simulate-message` para simular mensagens recebidas pela Vitória.
- Banco SQLite efêmero por padrão, ideal para demo na Vercel sem PostgreSQL.
- Seeds automáticos com dados de loteadora, corretores, leads, materiais, interações e tarefas.

## O que ainda não está conectado

- Meta WhatsApp Cloud API real.
- Templates aprovados na Meta.
- Número oficial da Vitória.
- PostgreSQL permanente.
- Envio real de mensagens para corretores/clientes.

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

Usuário e senha padrão:

```text
evora
leadflow-demo
```

## Testar a Vitória simulada

Abra:

```text
http://localhost:8000/vitoria
```

Use exemplos:

```text
Vitória, tenho um lead
Meus leads
Leads parados
Script para objeção de preço
```

Ou via API:

```bash
curl -X POST http://localhost:8000/api/simulate-message \
  -u evora:leadflow-demo \
  -H "Content-Type: application/json" \
  -d '{"from_phone":"5516999999999","text":"tenho um lead","profile_name":"Lucas Andrade"}'
```

## Deploy na Vercel

1. Suba o projeto para um repositório privado no GitHub.
2. Importe o repositório na Vercel.
3. Configure as variáveis de ambiente usando `.env.example` como base.
4. Para demo rápida, mantenha:

```env
DATABASE_URL=sqlite:////tmp/leadflow_demo.db
ENABLE_SCHEDULER=false
APP_ENV=demo
```

5. Faça deploy.
6. Acesse a URL da Vercel com Basic Auth.

## Transformar demo em produção depois

Quando formos conectar a operação real:

1. Trocar `DATABASE_URL` para PostgreSQL gerenciado.
2. Configurar `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID` e `WHATSAPP_APP_SECRET`.
3. Configurar webhook real da Meta em `/webhooks/whatsapp`.
4. Criar templates da Vitória na Meta.
5. Alterar rotinas proativas para `send_template`.
6. Definir permissões por corretor, gestor e administrador.
