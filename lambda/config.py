"""
Configuração central do Log Lady.
Destinos do workspace Notion e constantes.
"""

import os

# --- Notion API ---
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
NOTION_API_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

# --- Mapa de destinos (Page IDs do workspace "The Good Place") ---
DESTINOS = {
    "inbox": {
        "page_id": "3b893dba-e012-8150-b6a4-ca51020b7aa3",
        "nome": "Inbox",
        "emoji": "\U0001f4e5",
    },
    "compras": {
        "page_id": "3b593dba-e012-8107-bddc-c152bc341e47",
        "nome": "Lista de Compras",
        "emoji": "\U0001f6d2",
    },
    "ideias": {
        "page_id": "3b893dba-e012-811c-9fb8-d0d16a6c5506",
        "nome": "Ideias",
        "emoji": "\U0001f4a1",
    },
    "leituras": {
        "page_id": "3b893dba-e012-81ec-9d98-c6b6c7f853d7",
        "nome": "Leituras",
        "emoji": "\U0001f4da",
    },
    "foco": {
        "page_id": "c4e6c45c-cf08-4b09-9c95-ac271d5c051a",
        "nome": "Foco da Semana",
        "emoji": "\U0001f3e0",
    },
    "rotina": {
        "page_id": "3b593dba-e012-81f6-9640-efee30a62efc",
        "nome": "Rotina Di\u00e1ria",
        "emoji": "\U0001f9f9",
    },
}
