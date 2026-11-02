# Store address (policy)

- Scenario: `policy-store-address`
- Model: `qwen3:4b`
- Talking as: Visitor
- Result: **PASS**

## Visitor

Qual é o endereço da loja?

> Tool call: `search_policies`

```json
{
  "query": "endereço da loja"
}
```

Result:

```json
[
  {
    "section": "1.2",
    "title": "1.2 Dados da Empresa",
    "parent_title": "Sobre a Empório da Música",
    "text": "Campo | Informação\nRazão Social | Empório da Música Instrumentos Musicais Ltda.\nNome Fantasia | Empório da Música\nCNPJ | 12.345.678/0001-90\nEndereço | Rua 14 de Maio, 3200 — Centro, Campo Grande - MS, 79202-333\nTelefone / WhatsApp | (67) 3341-4444\nE-mail | contato@empóriodamusica.com.br\nFundação | 2008"
  },
  {
    "section": "2",
    "title": "2 Horário de Funcionamento",
    "parent_title": null,
    "text": "O atendimento presencial na loja segue os horários abaixo. O atendimento via WhatsApp segue o\nmesmo horário, com respostas automáticas fora do expediente.\nDia | Horário\nSegunda a Sexta-feira | 09:00 às 18:00\nSábado | 09:00 às 13:00\nDomingo e Feriados | Fechado\nEm datas especiais (Black Friday, Aniversário da Loja, Natal), o horário pode ser estendido.\nAlterações serão comunicadas com antecedência nas redes sociais e no atendimento via WhatsApp."
  },
  {
    "section": "7",
    "title": "7 Atendimento via WhatsApp",
    "parent_title": null,
    "text": "O canal de WhatsApp (67) 3321-4500 é o principal meio de atendimento remoto da Empório da\nMúsica. O atendimento pode ser realizado por atendentes humanos ou pelo assistente virtual."
  },
  {
    "section": "9",
    "title": "9 Privacidade e Proteção de Dados",
    "parent_title": null,
    "text": "A Empório da Música está em conformidade com a Lei Geral de Proteção de Dados (LGPD — Lei nº\n13.709/2018). Os dados pessoais coletados durante o atendimento (nome, telefone, e-mail,\nendereço) são utilizados exclusivamente para:\n• | Processamento e entrega de pedidos.\n• | Comunicação sobre status de pedidos e rastreamento.\n• | Envio de promoções e novidades (mediante consentimento explícito do cliente).\n• | Cumprimento de obrigações legais e fiscais.\nDados de clientes não são compartilhados com terceiros para fins de marketing. O cliente pode\nsolicitar a exclusão de seus dados a qualquer momento entrando em contato pelo WhatsApp ou\ne-mail."
  }
]
```

## Assistant

O endereço da loja é **Rua 14 de Maio, 3200 — Centro, Campo Grande - MS, 79202-333**. 😊
