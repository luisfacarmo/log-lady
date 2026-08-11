"""
Testes de integração para os handlers da Alexa com mock do Notion.
Valida que os handlers respondem corretamente sem chamar a API real.
"""

import pytest
from unittest.mock import patch, MagicMock
from notion_client import (
    adicionar_checkbox,
    ler_checkboxes_pendentes,
    marcar_checkbox,
    encontrar_e_marcar_tarefa,
    pesquisar_no_notion,
    obter_resumo_diario,
)


# =============================================================================
# NOTION HELPERS — Sucesso
# =============================================================================


class TestAdicionarCheckbox:
    """Testes para adicionar_checkbox()."""

    def test_sucesso(self, mock_notion_success):
        result = adicionar_checkbox("page-id-fake", "Comprar leite")
        assert result is True
        mock_notion_success.assert_called_once()

    def test_falha_timeout(self, mock_notion_failure):
        result = adicionar_checkbox("page-id-fake", "Algo")
        assert result is False


class TestLerCheckboxesPendentes:
    """Testes para ler_checkboxes_pendentes()."""

    def test_retorna_lista_vazia(self, mock_notion_get_empty):
        result = ler_checkboxes_pendentes("page-id-fake")
        assert result == []

    def test_retorna_apenas_pendentes(self, mock_notion_get_with_todos):
        result = ler_checkboxes_pendentes("page-id-fake")
        # Deve retornar 2 itens (os não-checked)
        assert len(result) == 2
        assert result[0]["texto"] == "Comprar leite"
        assert result[1]["texto"] == "Limpar cozinha"

    def test_respeita_limite(self, mock_notion_get_with_todos):
        result = ler_checkboxes_pendentes("page-id-fake", limite=1)
        assert len(result) == 1


class TestMarcarCheckbox:
    """Testes para marcar_checkbox()."""

    def test_sucesso(self, mock_notion_success):
        result = marcar_checkbox("block-id-fake")
        assert result is True

    def test_falha(self, mock_notion_failure):
        result = marcar_checkbox("block-id-fake")
        assert result is False


class TestEncontrarEMarcarTarefa:
    """Testes para encontrar_e_marcar_tarefa()."""

    def test_encontra_e_marca(self, mock_notion_get_with_todos, mock_notion_success):
        sucesso, nome = encontrar_e_marcar_tarefa("page-id-fake", "leite")
        assert sucesso is True
        assert nome == "Comprar leite"

    def test_nao_encontra(self, mock_notion_get_with_todos):
        # mock_notion_success não está ativo, mas não deve chegar a chamar patch
        sucesso, nome = encontrar_e_marcar_tarefa("page-id-fake", "inexistente xyz")
        assert sucesso is False
        assert nome == ""

    def test_busca_parcial_case_insensitive(self, mock_notion_get_with_todos, mock_notion_success):
        sucesso, nome = encontrar_e_marcar_tarefa("page-id-fake", "COZINHA")
        assert sucesso is True
        assert nome == "Limpar cozinha"


class TestPesquisarNoNotion:
    """Testes para pesquisar_no_notion()."""

    def test_sucesso_com_resultados(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {
                    "properties": {
                        "title": {
                            "type": "title",
                            "title": [{"plain_text": "Mabel"}],
                        }
                    }
                },
                {
                    "type": "child_page",
                    "child_page": {"title": "Página sobre gatos"},
                    "properties": {},
                },
            ]
        }

        with patch("notion_client.requests.post", return_value=mock_response):
            result = pesquisar_no_notion("mabel")
            assert len(result) == 2
            assert "Mabel" in result
            assert "Página sobre gatos" in result

    def test_sem_resultados(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"results": []}

        with patch("notion_client.requests.post", return_value=mock_response):
            result = pesquisar_no_notion("algo inexistente")
            assert result == []

    def test_timeout(self):
        import requests as req

        with patch(
            "notion_client.requests.post",
            side_effect=req.exceptions.Timeout("timeout"),
        ):
            result = pesquisar_no_notion("qualquer")
            assert result == []


class TestObterResumoDiario:
    """Testes para obter_resumo_diario()."""

    def test_retorna_estrutura_correta(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {
                    "id": "b1",
                    "type": "to_do",
                    "to_do": {
                        "checked": False,
                        "rich_text": [{"text": {"content": "Tarefa foco"}}],
                    },
                }
            ]
        }

        with patch("notion_client.requests.get", return_value=mock_response):
            resumo = obter_resumo_diario()
            assert "foco" in resumo
            assert "rotina" in resumo
            assert isinstance(resumo["foco"], list)
            assert isinstance(resumo["rotina"], list)
