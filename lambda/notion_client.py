"""
Notion API client para o Log Lady.
Encapsula todas as operações com a Notion API.
"""

import logging
import time

import requests

from config import NOTION_TOKEN, NOTION_API_URL, NOTION_VERSION, DESTINOS

logger = logging.getLogger(__name__)

MAX_RETRIES = 1
RETRY_DELAY_S = 0.5
REQUEST_TIMEOUT_S = 7


def notion_headers() -> dict:
    """Headers padrão para a Notion API."""
    return {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }


def _request_with_retry(method: str, url: str, **kwargs) -> requests.Response:
    """Executa request HTTP com 1 retry em caso de falha transiente."""
    kwargs.setdefault("timeout", REQUEST_TIMEOUT_S)
    kwargs.setdefault("headers", notion_headers())

    last_error = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = getattr(requests, method)(url, **kwargs)
            response.raise_for_status()
            return response
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            last_error = e
            if attempt < MAX_RETRIES:
                logger.warning(f"Retry {attempt + 1}/{MAX_RETRIES} para {method.upper()} {url}")
                time.sleep(RETRY_DELAY_S)
            continue
        except requests.exceptions.RequestException as e:
            # Erros não-transientes (4xx, etc.) — não faz retry
            raise

    raise last_error


def adicionar_checkbox(page_id: str, texto: str) -> bool:
    """Adiciona um item to-do (checkbox) no final de uma página do Notion."""
    url = f"{NOTION_API_URL}/blocks/{page_id}/children"
    payload = {
        "children": [
            {
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": texto},
                        }
                    ],
                    "checked": False,
                },
            }
        ]
    }

    try:
        _request_with_retry("patch", url, json=payload)
        logger.info(f"Checkbox adicionado em {page_id}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao adicionar checkbox: {e}")
        return False


def ler_checkboxes_pendentes(page_id: str, limite: int = 10) -> list:
    """Lê os blocos to-do não marcados de uma página. Suporta paginação."""
    url = f"{NOTION_API_URL}/blocks/{page_id}/children"
    pendentes = []
    start_cursor = None

    while True:
        params = {"page_size": 100}
        if start_cursor:
            params["start_cursor"] = start_cursor

        try:
            response = _request_with_retry("get", url, params=params)
            data = response.json()

            for block in data.get("results", []):
                if block.get("type") == "to_do":
                    todo = block.get("to_do", {})
                    if not todo.get("checked", True):
                        rich_text = todo.get("rich_text", [])
                        if rich_text:
                            texto = rich_text[0].get("text", {}).get("content", "")
                            if texto:
                                pendentes.append(
                                    {"id": block["id"], "texto": texto}
                                )

                if len(pendentes) >= limite:
                    return pendentes

            # Paginação: continuar se houver mais blocos
            if data.get("has_more") and len(pendentes) < limite:
                start_cursor = data.get("next_cursor")
            else:
                break

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao ler checkboxes: {e}")
            return pendentes

    return pendentes


def marcar_checkbox(block_id: str) -> bool:
    """Marca um bloco to-do como checked."""
    url = f"{NOTION_API_URL}/blocks/{block_id}"
    payload = {"to_do": {"checked": True}}

    try:
        _request_with_retry("patch", url, json=payload)
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao marcar checkbox: {e}")
        return False


def encontrar_e_marcar_tarefa(page_id: str, nome_tarefa: str) -> tuple:
    """Procura uma tarefa pelo nome (parcial) e marca como concluída."""
    pendentes = ler_checkboxes_pendentes(page_id, limite=50)

    nome_lower = nome_tarefa.lower()
    for item in pendentes:
        if nome_lower in item["texto"].lower():
            sucesso = marcar_checkbox(item["id"])
            return sucesso, item["texto"]

    return False, ""


def pesquisar_no_notion(query: str) -> list:
    """Pesquisa por texto no workspace inteiro do Notion."""
    url = f"{NOTION_API_URL}/search"
    payload = {"query": query, "page_size": 5}

    try:
        response = _request_with_retry("post", url, json=payload)
        data = response.json()

        resultados = []
        for item in data.get("results", []):
            titulo = ""
            props = item.get("properties", {})

            # Tentar extrair título
            for prop_name, prop_value in props.items():
                if prop_value.get("type") == "title":
                    title_arr = prop_value.get("title", [])
                    if title_arr:
                        titulo = title_arr[0].get("plain_text", "")
                    break

            if not titulo:
                # Tentar pelo child_page
                if item.get("type") == "child_page":
                    titulo = item.get("child_page", {}).get("title", "")

            if titulo:
                resultados.append(titulo)

        return resultados
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro na pesquisa: {e}")
        return []


def obter_resumo_diario() -> dict:
    """Obtém um resumo do dia: foco da semana + rotina pendente."""
    resumo = {"foco": [], "rotina": []}

    # Ler foco da semana
    foco = ler_checkboxes_pendentes(DESTINOS["foco"]["page_id"], limite=5)
    resumo["foco"] = [item["texto"] for item in foco]

    # Ler rotina pendente
    rotina = ler_checkboxes_pendentes(DESTINOS["rotina"]["page_id"], limite=5)
    resumo["rotina"] = [item["texto"] for item in rotina]

    return resumo
