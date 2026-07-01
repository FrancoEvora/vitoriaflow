# Évora LeadFlow — Arquitetura v0.1

## Objetivo

O Évora LeadFlow é um CRM ativo via WhatsApp, operado pela Vitória, uma agente comercial para corretores de loteamentos.

O MVP resolve quatro problemas:

1. Cadastro de lead sem fricção.
2. Qualificação comercial orientada.
3. Próxima melhor ação e script de abordagem.
4. Follow-up ativo e visibilidade para gestão.

## Componentes

```text
WhatsApp do corretor
        ↓
Webhook WhatsApp / FastAPI
        ↓
VitoriaAgent
        ↓
PostgreSQL
        ↓
Dashboard interno + rotinas de follow-up
```

## Serviços

| Serviço | Função |
|---|---|
| FastAPI | API, webhook e dashboard |
| PostgreSQL | Banco transacional |
| Redis | Preparado para filas e automações futuras |
| APScheduler | Lembrete diário para corretores |
| OpenAI opcional | Recomendações comerciais com linguagem natural |
| WhatsApp Cloud API | Envio e recebimento de mensagens |

## Decisão de MVP

A primeira versão evita conversar diretamente com o cliente final. A Vitória conversa com os corretores, o que reduz risco operacional e facilita a adoção.

## Principais tabelas

| Tabela | Uso |
|---|---|
| users | Corretores, gestores e administradores |
| developments | Empreendimentos/loteamentos |
| leads | Oportunidades comerciais |
| interactions | Histórico de mensagens e eventos |
| tasks | Follow-ups e pendências |
| materials | Biblioteca comercial |
| lead_recommendations | Diagnósticos, estratégias e scripts |
| conversation_sessions | Estado da conversa com cada corretor |

## Estados comerciais iniciais

- novo
- qualificado
- visita agendada
- visita realizada
- proposta
- reservado
- ganho
- perdido

## Escalabilidade futura

Para virar SaaS, criar:

- organizations
- organization_users
- billing_plans
- audit_logs avançados
- permissões por empreendimento
- multi-tenant database strategy
- isolamento de dados por empresa
