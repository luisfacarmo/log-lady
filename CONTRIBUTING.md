# Contributing

Contributions are welcome! Here's how to get started.

## How to contribute

1. Fork this repository
2. Create a branch for your change (`git checkout -b feat/my-feature`)
3. Make your changes
4. Test locally (see below)
5. Commit with a clear message (`feat: add X` or `fix: resolve Y`)
6. Open a Pull Request

## Local setup

### Requirements
- Python 3.10+
- AWS CLI (configured with Lambda deploy permissions)
- A Notion integration token (for testing)
- pytest

### Install
```bash
cd lambda
pip install -r requirements.txt

# Test dependencies
pip install pytest
```

### Run tests
```bash
pytest -v
```

### Deploy (staging)
```bash
./deploy.ps1
```

## Commit style

We follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` — new feature
- `fix:` — bug fix
- `docs:` — documentation only
- `chore:` — maintenance, deps, CI

## What we accept

- Bug fixes with evidence (logs, test cases)
- New intents/handlers (discuss in an Issue first)
- Improved Notion API integration
- Documentation improvements
- Translations for the interaction model

## What we don't accept

- Breaking changes to the interaction model without discussion
- Credentials, API keys, or secrets in code
- PRs that mix unrelated changes
- Direct commits to `master` — always use a PR

## Architecture notes

- **Runtime**: AWS Lambda (Python)
- **Skill**: Alexa Custom Skill (ASK SDK)
- **Backend**: Notion API via `notion_client` module
- **Language**: pt-BR interaction model
- **Modules**: `config`, `routing`, `notion_client`, `messages`

## Questions?

Open an Issue. We'll respond as soon as possible.
