# Correção do erro 500 na Vercel

Se a Vercel mostrar `500: ERRO_INTERNO_DO_SERVIDOR` com código `FUNCTION_INVOCATION_FAILED`, o runtime Python iniciou a função mas a aplicação quebrou durante a invocação.

Esta versão foi ajustada para a demo premium:

- usa SQLite em memória por padrão (`DATABASE_URL=sqlite://`);
- inicializa e popula o banco de forma preguiçosa também dentro da dependência `get_db`, não apenas no lifespan;
- usa caminhos absolutos para `app/static` e `app/templates`;
- inclui `/api/debug/startup` para verificar ambiente, diretórios e esquema do banco.

## Variáveis recomendadas na Vercel para a demo

```env
APP_NAME=Évora LeadFlow
APP_ENV=demo
TIMEZONE=America/Sao_Paulo
ENABLE_SCHEDULER=false
DATABASE_URL=sqlite://
DASHBOARD_USERNAME=evora
DASHBOARD_PASSWORD=troque_por_uma_senha_forte
DISABLE_DASHBOARD_AUTH=false
```

Depois de alterar variáveis, faça **Redeploy**.

## Testes após deploy

```text
https://SEU-PROJETO.vercel.app/health
https://SEU-PROJETO.vercel.app/api/health
https://SEU-PROJETO.vercel.app/api/debug/startup
https://SEU-PROJETO.vercel.app/
```

`/api/health`, `/api/debug/startup` e `/` pedem Basic Auth.
