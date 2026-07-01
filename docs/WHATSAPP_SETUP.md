# Configuração WhatsApp Cloud API

## Objetivo

Conectar o WhatsApp do corretor à Vitória por meio da Meta WhatsApp Business Platform / Cloud API.

## 1. Criar app na Meta

1. Acesse o Meta for Developers.
2. Crie um app.
3. Adicione o produto WhatsApp.
4. Configure uma WhatsApp Business Account.
5. Obtenha:
   - `WHATSAPP_ACCESS_TOKEN`
   - `WHATSAPP_PHONE_NUMBER_ID`
   - número de teste ou número oficial

## 2. Configurar variáveis

No `.env`:

```env
WHATSAPP_VERIFY_TOKEN=evora-leadflow-verify-token
WHATSAPP_ACCESS_TOKEN=cole-o-token-da-meta
WHATSAPP_PHONE_NUMBER_ID=cole-o-phone-number-id
WHATSAPP_GRAPH_VERSION=v23.0
```

O `WHATSAPP_VERIFY_TOKEN` é uma senha criada por você. Ele precisa ser igual no `.env` e no painel da Meta.

## 3. Expor backend em HTTPS

Em produção, use seu domínio:

```text
https://leadflow.seudominio.com
```

Para teste local, use ngrok ou Cloudflare Tunnel:

```bash
ngrok http 8000
```

O callback ficará assim:

```text
https://seu-endereco-ngrok.ngrok-free.app/webhooks/whatsapp
```

## 4. Configurar webhook na Meta

No painel do app:

- Callback URL: `https://seu-dominio.com/webhooks/whatsapp`
- Verify token: mesmo valor de `WHATSAPP_VERIFY_TOKEN`
- Webhook field: assine pelo menos `messages`

Quando a Meta fizer o GET de verificação, o backend compara o token e devolve o `hub.challenge`.

## 5. Testar mensagem recebida

Depois de configurado, envie uma mensagem do WhatsApp autorizado para o número conectado:

```text
Vitória
```

Resposta esperada:

```text
Olá, Carlos. Aqui é a Vitória, agente comercial do Évora LeadFlow...
```

Se o telefone ainda não existir na tabela de corretores, o MVP cria automaticamente um usuário com nome `Corretor XXXX`.

## 6. Mensagens proativas e templates

Para mensagens iniciadas pela Vitória, especialmente fora da janela de atendimento, crie templates aprovados na Meta.

Sugestões de templates:

### leadflow_rotina_diaria

```text
Bom dia, {{1}}. Aqui é a Vitória. Você tem {{2}} leads ativos no Évora LeadFlow. Quer atualizar seus atendimentos de hoje?
```

### leadflow_lead_parado

```text
{{1}}, o lead {{2}} está sem atualização há {{3}} dias. Deseja registrar avanço ou gerar uma mensagem de retomada?
```

### leadflow_visita

```text
{{1}}, o lead {{2}} tinha visita prevista. Ela aconteceu? Responda: visitou, remarcou ou não compareceu.
```

O código atual envia texto simples. Para produção com templates, crie um método adicional em `app/services/whatsapp.py` usando `type: template`.

## 7. Cuidados operacionais

- Use HTTPS.
- Nunca coloque tokens no repositório GitHub nem em código do lado do cliente.
- Faça rotação de tokens.
- Use logs para auditar mensagens enviadas.
- Primeiro conecte a Vitória aos corretores; só depois avalie automação para clientes finais.
