# Log Lady

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg)](https://www.python.org/)
[![Alexa](https://img.shields.io/badge/Alexa-Custom_Skill-00CAFF.svg)](https://developer.amazon.com/alexa)
[![Notion](https://img.shields.io/badge/Notion-API-000000.svg)](https://developers.notion.com/)

> Controla o teu Notion por voz. Alexa Custom Skill em pt-BR para o workspace "The Good Place".
>
> *"My log has something to tell you."*

> [!WARNING]
> Projeto pessoal em desenvolvimento ativo. A skill funciona em development mode mas não está publicada na Alexa Skills Store. Alexa+ pode interferir na invocação — ver secção Troubleshooting.

## What is this?

Log Lady é uma Alexa Skill que permite controlar um workspace Notion inteiramente por voz. Diz "Alexa, abre meu caderno" e podes anotar, listar tarefas, marcar como feitas, pedir um resumo do dia ou pesquisar no workspace — tudo em português brasileiro natural.

O roteamento é inteligente: diz "compra leite" e vai para a Lista de Compras; diz "ideia para um app" e vai para Ideias; diz "limpar cozinha" e vai para Rotina.

## Current Status

| Component | Status | Notes |
|-----------|--------|-------|
| Roteamento inteligente (~75 regex) | ✅ Working | 70 testes passando |
| Anotar com classificação automática | ✅ Working | 6 destinos |
| Listar tarefas pendentes | ✅ Working | Por página |
| Marcar tarefa como concluída | ✅ Working | Busca parcial |
| Resumo diário (foco + rotina) | ✅ Working | Validado |
| Pesquisa por voz no workspace | ✅ Working | Top 5 resultados |
| Session continuity | ✅ Working | shouldEndSession=false |
| Testes automatizados | ✅ Working | 84 testes, pytest |
| Follow-ups ("e também...") | 🔧 Planned | Fase 5 |
| Deploy automatizado | 🔧 Planned | Fase 7 |

## Features

- [x] Roteamento automático por contexto (compras, rotina, ideias, leituras, foco, inbox)
- [x] Override explícito de destino ("coloca no foco X")
- [x] Listar tarefas pendentes de qualquer página
- [x] Marcar tarefas como concluídas (busca parcial, case-insensitive)
- [x] Resumo diário: foco da semana + rotina pendente
- [x] Pesquisa por voz no workspace inteiro
- [x] Linguagem natural pt-BR
- [x] Sessão persistente ("Mais alguma coisa?")
- [ ] Follow-ups contextuais ("e também...")
- [ ] Confirmação para ações destrutivas
- [ ] One-shot commands (sem abrir skill)
- [ ] Deploy automatizado com rollback

## Destinos

| Comando de exemplo | Destino | Emoji |
|---|---|---|
| "compra leite" | Lista de Compras | 🛒 |
| "limpar banheiro" | Rotina Diária | 🧹 |
| "ideia para o projeto" | Ideias | 💡 |
| "ver depois esse vídeo" | Leituras | 📚 |
| "foco terminar relatório" | Foco da Semana | 🏠 |
| "anota ligar pro dentista" | Inbox (fallback) | 📥 |

## Architecture

```
alexa-notion-skill/
├── lambda/
│   ├── lambda_function.py  # Handlers + routing + Notion client (monolito)
│   ├── requirements.txt    # ask-sdk-core, requests
│   └── package/            # Deployment dependencies
├── tests/
│   ├── conftest.py         # Fixtures e mocks
│   ├── test_routing.py     # 70 testes de roteamento
│   └── test_handlers.py    # 14 testes de Notion helpers
├── interaction-model.json  # Alexa interaction model (5 custom intents)
├── pytest.ini              # Configuração pytest
├── SETUP.md                # Guia de instalação completo
└── AUDITORIA.md            # Auditoria técnica e roadmap
```

## Tech Stack

- **Runtime:** Python 3.11 (AWS Lambda)
- **Voice:** Alexa Skills Kit (ASK SDK Core 1.19.0)
- **API:** Notion API v2022-06-28
- **HTTP:** Requests 2.31.0
- **Tests:** pytest 8.3 + mocks
- **Cloud:** AWS Lambda + CloudWatch
- **Interaction:** Custom model, pt-BR, 5 intents, AMAZON.SearchQuery slots

## Building

### Prerequisites

- [Python 3.11+](https://www.python.org/)
- [AWS CLI](https://aws.amazon.com/cli/) configured
- [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask) account
- Notion Integration token (see SETUP.md)

### Development

```powershell
# Install test dependencies
pip install -r tests/requirements-test.txt
pip install ask-sdk-core requests

# Run tests
python -m pytest

# Package for deploy
cd lambda
pip install -r requirements.txt -t ./package
Copy-Item lambda_function.py -Destination ./package/
Compress-Archive -Path ./package/* -DestinationPath ../lambda-deployment.zip -Force
```

### Testing

```powershell
# All tests
python -m pytest

# Only routing
python -m pytest tests/test_routing.py

# Verbose with coverage
python -m pytest -v --cov=lambda
```

## Contributing

This is a personal project, but ideas are welcome:

1. Open an issue describing the use case or voice command
2. For routing improvements: add test cases to `tests/test_routing.py` first
3. PRs should pass all 84 existing tests before merge

## License

MIT
