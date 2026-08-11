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
| Roteamento inteligente (~75 regex) | ✅ Working | 70 testes, follow-up context |
| Anotar com classificação automática | ✅ Working | 6 destinos + session follow-ups |
| Listar tarefas pendentes | ✅ Working | Paginação completa |
| Marcar tarefa como concluída | ✅ Working | Busca otimizada (last_destino first) |
| Resumo diário (foco + rotina) | ✅ Working | Limitado a 3+3 items |
| Pesquisa por voz no workspace | ✅ Working | Top 5 resultados |
| Session continuity + follow-ups | ✅ Working | "compra leite" → "pão" → "café" |
| Retry + error handling | ✅ Working | 1 retry em falhas transientes |
| Structured logging | ✅ Working | intent, session, duration, destino |
| Testes automatizados | ✅ Working | 84 testes, pytest |
| Deploy automatizado | ✅ Working | deploy.ps1 + versioning |
| Input validation | ✅ Working | Max 200 chars |

## Features

- [x] Roteamento automático por contexto (compras, rotina, ideias, leituras, foco, inbox)
- [x] Override explícito de destino ("coloca no foco X")
- [x] Follow-ups contextuais ("compra leite" → "pão" → "café")
- [x] Listar tarefas pendentes de qualquer página (com paginação)
- [x] Marcar tarefas como concluídas (busca parcial, case-insensitive, otimizada)
- [x] Resumo diário: foco da semana + rotina pendente (limitado a 3+3)
- [x] Pesquisa por voz no workspace inteiro
- [x] Linguagem natural pt-BR
- [x] Sessão persistente com context follow-ups
- [x] Retry automático em falhas transientes (1x)
- [x] Input validation (200 chars max)
- [x] Structured logging (intent, session, duration, destino)
- [x] Deploy automatizado com versioning (deploy.ps1)
- [ ] One-shot commands (sem abrir skill)
- [ ] Confirmação para ações destrutivas
- [ ] Leitura completa de páginas específicas

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
│   ├── lambda_function.py  # Alexa handlers + wiring (entry point)
│   ├── config.py           # DESTINOS, API constants
│   ├── routing.py          # ~75 regex rules + determinar_destino()
│   ├── notion_client.py    # Notion API ops (retry, pagination)
│   ├── messages.py         # Centralized response strings
│   ├── requirements.txt    # ask-sdk-core, requests
│   └── package/            # Deployment dependencies
├── tests/
│   ├── conftest.py         # Fixtures e mocks
│   ├── test_routing.py     # 70 testes de roteamento
│   └── test_handlers.py    # 14 testes de Notion helpers
├── deploy.ps1              # Automated deploy (test → package → upload → version)
├── rollback.ps1            # List versions / rollback guide
├── interaction-model.json  # Alexa interaction model (5 custom intents)
├── pytest.ini              # pytest config
├── SETUP.md                # Installation guide
└── AUDITORIA.md            # Technical audit + roadmap
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

# Deploy to Lambda (runs tests first)
./deploy.ps1

# Deploy skipping tests
./deploy.ps1 -SkipTests

# List Lambda versions
./rollback.ps1 -Version list
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
