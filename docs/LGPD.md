# LGPD — Cuidados mínimos do Évora LeadFlow

## Dados tratados

- Nome do lead.
- Telefone.
- Origem.
- Interesse imobiliário.
- Faixa aproximada de entrada/parcela.
- Histórico comercial.
- Status do atendimento.
- Objeções e motivo de perda.

## Regras práticas para o MVP

1. Coletar apenas dados necessários para atendimento comercial.
2. Registrar origem do lead.
3. Restringir acesso: corretor vê sua carteira; gestão vê equipe.
4. Guardar logs de interação.
5. Não expor dados de uma carteira para outra.
6. Definir prazo de retenção para leads perdidos/inativos.
7. Permitir exclusão ou anonimização quando aplicável.
8. Evitar automação direta com cliente final no MVP.
9. Usar senha forte e HTTPS em produção.
10. Configurar segredo do app Meta para validar assinatura do webhook.

## Produção

Antes de usar com clientes reais, revisar:

- Política de privacidade.
- Base legal do tratamento.
- Contratos com operadores.
- Controle de acesso.
- Backup e retenção.
- Processo de atendimento a pedidos de titulares.
