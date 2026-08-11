# Alexa + Notion Integration — Guia de Setup

## Visão Geral

```
Tu falas → Alexa → AWS Lambda → Notion API → Página certa no teu Notion
```

**Tempo estimado:** 1h30  
**Custo:** 0€ (tudo no free tier)

---

## Como funciona o roteamento

A skill analisa o que dizes e coloca no lugar certo automaticamente:

| O que dizes | Para onde vai |
|---|---|
| "anota qualquer coisa" | 📥 Inbox |
| "compra leite" | 🛒 Lista de Compras |
| "ideia fazer um app" | 💡 Ideias |
| "leitura artigo sobre X" | 📚 Leituras |
| "foco terminar relatório" | 🏠 Foco da Semana |
| "rotina limpar cozinha" | 🧹 Rotina Diária |

Também podes forçar o destino: "anota X **no foco**" ou "adiciona Y **nas compras**"

---

## Pré-requisitos

- Conta Amazon Developer (mesma conta da tua Alexa)
- Conta AWS (free tier)
- Workspace do Notion "The Good Place"

---

## PARTE 1: Preparar o Notion (10 min)

### 1.1 Criar uma Integration no Notion

1. Vai a: https://www.notion.so/my-integrations
2. Clica **"New integration"**
3. Preenche:
   - **Name:** `Alexa Skill`
   - **Associated workspace:** The Good Place
   - **Capabilities:** marca Read content, Update content, Insert content
4. Clica **Submit**
5. **Copia o "Internal Integration Secret"** (começa com `ntn_`)
   - ⚠️ Guarda isto! Vais precisar mais tarde.

### 1.2 Dar acesso às páginas

A Integration precisa de acesso a cada página que vamos usar. Para cada uma:

1. Abre a página no Notion
2. Clica nos **`•••`** (menu, canto superior direito)
3. Vai a **Connections** → **Connect to** → procura "Alexa Skill"
4. Confirma

**Páginas que precisam de acesso:**
- 📥 Inbox
- 🛒 Lista de Compras (dentro de Operação Casa Limpa)
- 💡 Ideias
- 📚 Leituras
- 🏠 Homepage
- 🧹 Rotina Diária + Gatos

💡 **Dica:** Se dás acesso à Homepage, as sub-páginas diretas podem herdar o acesso.
Mas para garantir, conecta cada uma individualmente.

---

## PARTE 2: Criar a Lambda na AWS (20 min)

### 2.1 Fazer login na AWS

1. Vai a: https://console.aws.amazon.com
2. Se não lembrares a conta, tenta "Forgot password" com os teus emails
3. Se precisares criar uma nova: https://aws.amazon.com/free/

### 2.2 Preparar o pacote ZIP

Abre o PowerShell na pasta do projeto:

```powershell
cd lambda

# Instalar dependências numa pasta local
pip install -r requirements.txt -t ./package

# Copiar o código para a pasta
Copy-Item lambda_function.py -Destination ./package/

# Criar o ZIP
Compress-Archive -Path ./package/* -DestinationPath ../lambda-deployment.zip -Force
```

### 2.3 Criar a Lambda Function

1. Na AWS Console, pesquisa por **Lambda**
2. Clica **"Create function"**
3. Preenche:
   - **Function name:** `alexa-notion-skill`
   - **Runtime:** Python 3.11
   - **Architecture:** x86_64
4. Clica **Create function**

### 2.4 Upload do código

1. Em **Code source**, clica **"Upload from"** → **".zip file"**
2. Seleciona `lambda-deployment.zip`
3. Clica **Save**

### 2.5 Configurar o handler

1. Em **Runtime settings** → **Edit**
2. **Handler:** `lambda_function.lambda_handler`
3. **Save**

### 2.6 Variáveis de ambiente

1. **Configuration** → **Environment variables** → **Edit**
2. Adiciona:
   - `NOTION_TOKEN` = o token `ntn_...` do passo 1.1
3. **Save**

(Não precisa de DATABASE_ID — os page IDs já estão hardcoded no código)

### 2.7 Timeout

1. **Configuration** → **General configuration** → **Edit**
2. **Timeout:** 10 segundos
3. **Save**

### 2.8 Trigger da Alexa

1. **Configuration** → **Triggers** → **Add trigger**
2. Seleciona **Alexa Skills Kit**
3. **⚠️ IMPORTANTE:** Marca "Skill ID verification" e cola o Skill ID (ver passo 3.5)
   - Isto impede que outras skills invoquem a tua Lambda
4. **Add**

### 2.9 Copiar o ARN

1. No topo da Lambda, copia o **Function ARN**
   - Ex: `arn:aws:lambda:eu-west-1:123456789:function:alexa-notion-skill`

---

## PARTE 3: Criar a Alexa Skill (25 min)

### 3.1 Developer Console

1. Vai a: https://developer.amazon.com/alexa/console/ask
2. Login com a mesma conta da tua Alexa

### 3.2 Criar a Skill

1. **Create Skill**
2. Preenche:
   - **Skill name:** `Meu Caderno`
   - **Primary locale:** Portuguese (BR)
   - **Model:** Custom
   - **Backend:** Provision your own
3. Template: **Start from Scratch**

### 3.3 Interaction Model

1. Menu lateral → **Interaction Model** → **JSON Editor**
2. Apaga tudo
3. Cola o conteúdo de `interaction-model.json`
4. **Save Model** → **Build Model** (espera 1-2 min)

### 3.4 Endpoint

1. Menu lateral → **Endpoint**
2. **AWS Lambda ARN**
3. **Default Region:** cola o ARN do passo 2.9
4. **Save Endpoints**

### 3.5 Skill ID → Lambda

1. Copia o **Skill ID** (tipo `amzn1.ask.skill.xxx...`)
2. Na AWS Lambda → **Triggers** → edita e adiciona o Skill ID

---

## PARTE 4: Testar (10 min)

### No Simulator

1. Separador **Test** → muda para **Development**
2. Testa:
   - "abre meu caderno"
   - "anota ligar para o dentista"
   - "compra papel higiénico"
   - "ideia automatizar a rega"
   - "lê as minhas tarefas"
   - "o que tenho nas compras"
   - "marca leite como feita"

### No teu Echo/Alexa

- "Alexa, abre meu caderno"
- "Compra pão"
- "Lê as compras"

---

## Troubleshooting

| Problema | Solução |
|---|---|
| "Não consegui anotar" | Verifica se a Integration tem acesso à página (passo 1.2) |
| "Não encontrei tarefa X" | A busca é parcial — tenta palavras-chave da tarefa |
| Timeout | Verifica se timeout ≥ 10s |
| Skill não aparece na Alexa | Confirma que é a mesma conta Amazon + teste em "Development" |
| Erro nos logs | AWS Lambda → Monitor → CloudWatch Logs |

---

## Exemplos de uso no dia-a-dia

```
"Alexa, abre meu caderno"
  → "Olá! Sou o teu caderno..."

"Compra leite e pão"
  → "Pronto! Anotei 'leite e pão' no 🛒 Lista de Compras."

"Anota ligar para a mãe"
  → "Pronto! Anotei 'ligar para a mãe' no 📥 Inbox."

"Ideia criar um podcast sobre produtividade"
  → "Pronto! Anotei 'criar um podcast sobre produtividade' no 💡 Ideias."

"O que tenho no foco?"
  → "Tens 3 itens no Foco da Semana: limpar a casa, campanha, e procurar itens perdidos."

"Marca campanha como feita"
  → "Feito! Marquei 'Campanha' como concluída."

"Anota ver filme X nas leituras"
  → "Feito! Coloquei 'ver filme X' no 📚 Leituras."
```

---

## Próximos Passos (Fase 2+)

- [ ] Resumo diário por voz ("o que tenho para hoje?")
- [ ] Pesquisa por voz no workspace inteiro
- [ ] Adicionar conteúdo a páginas específicas de projetos
- [ ] Notificações proativas (Notion → Alexa)
- [ ] Editar/mover itens entre destinos
- [ ] Integração com agenda (criar eventos)
