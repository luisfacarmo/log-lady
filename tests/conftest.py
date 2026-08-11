"""
Configuração compartilhada para pytest.
Garante que os módulos lambda estão no path e configura mocks padrão.
"""

import sys
import os
from unittest.mock import patch

import pytest

# Adicionar o diretório lambda ao path para importar os módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lambda"))

# Garantir que NOTION_TOKEN existe (evitar erros de import)
os.environ.setdefault("NOTION_TOKEN", "ntn_test_fake_token_for_testing")


@pytest.fixture
def mock_notion_success():
    """Mock que simula uma resposta de sucesso do Notion (patch requests.patch)."""
    with patch("notion_client.requests.patch") as mock_patch:
        mock_patch.return_value.status_code = 200
        mock_patch.return_value.raise_for_status = lambda: None
        mock_patch.return_value.json.return_value = {"results": []}
        yield mock_patch


@pytest.fixture
def mock_notion_failure():
    """Mock que simula falha do Notion."""
    import requests as req

    with patch("notion_client.requests.patch") as mock_patch:
        mock_patch.side_effect = req.exceptions.Timeout("Connection timed out")
        yield mock_patch


@pytest.fixture
def mock_notion_get_empty():
    """Mock para GET que retorna lista vazia de blocos."""
    with patch("notion_client.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = {"results": []}
        yield mock_get


@pytest.fixture
def mock_notion_get_with_todos():
    """Mock para GET que retorna blocos to-do."""
    with patch("notion_client.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = {
            "results": [
                {
                    "id": "block-id-1",
                    "type": "to_do",
                    "to_do": {
                        "checked": False,
                        "rich_text": [{"text": {"content": "Comprar leite"}}],
                    },
                },
                {
                    "id": "block-id-2",
                    "type": "to_do",
                    "to_do": {
                        "checked": False,
                        "rich_text": [{"text": {"content": "Limpar cozinha"}}],
                    },
                },
                {
                    "id": "block-id-3",
                    "type": "to_do",
                    "to_do": {
                        "checked": True,
                        "rich_text": [{"text": {"content": "Tarefa já feita"}}],
                    },
                },
            ]
        }
        yield mock_get
