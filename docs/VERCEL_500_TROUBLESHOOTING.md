# Correção para erro 500 na Vercel

Se aparecer:

```text
500: ERRO_INTERNO_DO_SERVIDOR
Código: FUNCTION_INVOCATION_FAILED
```

use esta versão corrigida do pacote. Ela deixa a demo mais tolerante ao ambiente serverless da Vercel.

## Causas mais comuns

1. `DATABASE_URL` criada na Vercel, mas deixada vazia.
2. `ENABLE_SCHEDULER` ou `DISABLE_DASHBOARD_AUTH` criadas vazias, o que causava falha de validação booleana.
3. FastAPI em serverless não executando inicialização/lifespan antes da primeira rota.
4. Caminhos relativos para `app/static` ou `app/templates` em runtime serverless.

## Variáveis recomendadas para demo

No painel da Vercel, deixe assim:

```env
APP_NAME=Évora LeadFlow
APP_ENV=demo
TIMEZONE=America/Sao_Paulo
ENABLE_SCHEDULER=false
DATABASE_URL=sqlite:////tmp/leadflow_demo.db
DASHBOARD_USERNAME=evora
DASHBOARD_PASSWORD=uma_senha_forte
DISABLE_DASHBOARD_AUTH=false
```

Variáveis opcionais como `OPENAI_API_KEY`, `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID` e `WHATSAPP_APP_SECRET` podem ficar ausentes. Evite criá-las com valor vazio.

## Depois de alterar variáveis

Faça um redeploy completo:

```text
Vercel → Project → Deployments → Redeploy
```

Use a opção para redeploy sem cache quando disponível.

## Teste

Acesse primeiro:

```text
https://SEU-PROJETO.vercel.app/health
```

Depois:

```text
https://SEU-PROJETO.vercel.app/
```
