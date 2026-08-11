"""
Alexa + Notion Integration - Lambda Function (Fase 2)
=====================================================
Skill: "Meu Caderno"

Adaptado para pt-BR e workspace "The Good Place".
Usa páginas + checklists com roteamento inteligente.

Funcionalidades:
  - Anotar (com roteamento automático por contexto)
  - Listar tarefas pendentes de qualquer página
  - Marcar tarefa como concluída
  - Resumo diário (foco da semana + rotina)
  - Pesquisa por voz no workspace

Invocation: "Alexa, abre meu caderno"
"""

import os
import re
import json
import logging
import requests
from datetime import datetime

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler,
    AbstractExceptionHandler,
)
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

# --- Configuração ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
NOTION_API_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

# --- Mapa de destinos (Page IDs do workspace "The Good Place") ---
DESTINOS = {
    "inbox": {
        "page_id": "3b893dba-e012-8150-b6a4-ca51020b7aa3",
        "nome": "Inbox",
        "emoji": "📥",
    },
    "compras": {
        "page_id": "3b593dba-e012-8107-bddc-c152bc341e47",
        "nome": "Lista de Compras",
        "emoji": "🛒",
    },
    "ideias": {
        "page_id": "3b893dba-e012-811c-9fb8-d0d16a6c5506",
        "nome": "Ideias",
        "emoji": "💡",
    },
    "leituras": {
        "page_id": "3b893dba-e012-81ec-9d98-c6b6c7f853d7",
        "nome": "Leituras",
        "emoji": "📚",
    },
    "foco": {
        "page_id": "c4e6c45c-cf08-4b09-9c95-ac271d5c051a",
        "nome": "Foco da Semana",
        "emoji": "🏠",
    },
    "rotina": {
        "page_id": "3b593dba-e012-81f6-9640-efee30a62efc",
        "nome": "Rotina Diária",
        "emoji": "🧹",
    },
}

# --- Regras de roteamento (padrões → destino) ---
REGRAS_ROTEAMENTO = [
    # Override explícito ("coloca no/nas X")
    {
        "destino": "inbox",
        "padroes": [
            r"\bno inbox\b",
            r"\bna caixa\b",
            r"\bna entrada\b",
        ],
    },
    {
        "destino": "compras",
        "padroes": [
            r"\bnas compras\b",
            r"\bna lista de compras\b",
            r"\bno mercado\b",
            r"\bno supermercado\b",
            r"\bcompr(ar|a|as|ei)\b",
            r"\blista de compras\b",
            r"\bsupermercado\b",
            r"\bmercado\b",
            r"\bfarmácia\b",
            r"\bpreciso comprar\b",
            # Alimentos comuns
            r"\bleite\b",
            r"\bpão\b",
            r"\bfeijão\b",
            r"\barroz\b",
            r"\bcafé\b",
            r"\baçúcar\b",
            r"\bóleo\b",
            r"\bazeite\b",
            r"\bmanteiga\b",
            r"\bqueijo\b",
            r"\bovo(s)?\b",
            r"\bfrango\b",
            r"\bcarne\b",
            r"\bpeixe\b",
            r"\bfruta(s)?\b",
            r"\bbanana(s)?\b",
            r"\bmaçã(s)?\b",
            r"\btomate(s)?\b",
            r"\bcebola(s)?\b",
            r"\balho\b",
            r"\bbatata(s)?\b",
            r"\bmacarrão\b",
            r"\bmolho\b",
            r"\bsal\b",
            r"\bvinagre\b",
            r"\bcerveja(s)?\b",
            r"\bvinho\b",
            r"\brefrigerante\b",
            r"\bágua\b",
            r"\bsuco\b",
            r"\biogurte\b",
            r"\bcereal\b",
            r"\bbolacha(s)?\b",
            r"\bbiscoito(s)?\b",
            r"\bchocolate\b",
            r"\bsorvete\b",
            r"\bpresunto\b",
            r"\bsalsicha(s)?\b",
            r"\blingui(ç|c)a(s)?\b",
            r"\bfarinha\b",
            r"\bfermento\b",
            r"\bleite condensado\b",
            r"\bcreme de leite\b",
            r"\bdetergente\b",
            r"\bsabão\b",
            r"\bsab(ã|a)o em pó\b",
            r"\bamaciante\b",
            r"\bdesinfetante\b",
            r"\bálcool\b",
            r"\bpapel (higiênico|higiénico|toalha)\b",
            r"\bguardanapo(s)?\b",
            r"\bsaco(s)? de lixo\b",
            r"\besponja(s)?\b",
            r"\bshampoo\b",
            r"\bcondicionador\b",
            r"\bsabonete\b",
            r"\bpasta de dente\b",
            r"\bdesodorante\b",
            r"\bfralda(s)?\b",
            r"\bração\b",
            r"\bareia (de|dos) gato(s)?\b",
            r"\bcatnip\b",
            r"\bpetisco(s)?\b",
        ],
    },
    # Ideias
    {
        "destino": "ideias",
        "padroes": [
            r"\bnas ideias\b",
            r"\bna ideia\b",
            r"\bideia\b",
            r"\be se\b",
            r"\bprojeto\b",
            r"\bexperiment(ar|o)\b",
            r"\bpodia\b",
            r"\btalvez\b.*\bfazer\b",
        ],
    },
    # Leituras
    {
        "destino": "leituras",
        "padroes": [
            r"\bnas leituras\b",
            r"\bna leitura\b",
            r"\bleitura\b",
            r"\blink\b",
            r"\bartigo\b",
            r"\bvídeo\b",
            r"\bver depois\b",
            r"\bpodcast\b",
            r"\blivro\b",
            r"\bthread\b",
            r"https?://",
        ],
    },
    # Foco / Tarefas prioritárias
    {
        "destino": "foco",
        "padroes": [
            r"\bno foco\b",
            r"\bfoco\b",
            r"\bprioridade\b",
            r"\bhoje\b.*\b(fazer|preciso)\b",
            r"\burgente\b",
            r"\bimportante\b",
        ],
    },
    # Rotina
    {
        "destino": "rotina",
        "padroes": [
            r"\bna rotina\b",
            r"\brotina\b",
            r"\bgatos?\b",
            r"\blimpar\b",
            r"\blimpeza\b",
            r"\bvarrer\b",
            r"\blavar\b",
            r"\bfaxina\b",
            r"\besfregar\b",
            r"\borganizar\b",
            r"\barrumar\b",
            r"\bpassar pano\b",
            r"\baspir(ar|ador)\b",
            r"\bcaixa(s)? de areia\b",
            r"\blixo\b",
            r"\blixeira\b",
            r"\blouça\b",
            r"\broupa(s)? (pra|para) lavar\b",
            r"\bestender roupa\b",
            r"\brecolher roupa\b",
            r"\bdobrar roupa\b",
            r"\bcama\b.*\b(arrumar|fazer|esticar)\b",
            r"\b(arrumar|fazer|esticar)\b.*\bcama\b",
        ],
    },
]


def notion_headers():
    """Headers padrão para a Notion API."""
    return {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }


# =============================================================================
# ROTEAMENTO INTELIGENTE
# =============================================================================


def determinar_destino(texto: str) -> str:
    """Analisa o texto e determina o destino baseado em padrões."""
    texto_lower = texto.lower()

    for regra in REGRAS_ROTEAMENTO:
        for padrao in regra["padroes"]:
            if re.search(padrao, texto_lower):
                return regra["destino"]

    return "inbox"


def limpar_texto(texto: str, destino: str) -> str:
    """Remove prefixos de comando do texto para guardar apenas o conteúdo útil."""
    # Remover overrides explícitos de destino
    override_prefixos = [
        r"^coloca\s+(no|na|nas)\s+(inbox|compras|ideias|leituras|foco|rotina)\s+",
        r"^adiciona\s+(no|na|nas)\s+(inbox|compras|ideias|leituras|foco|rotina)\s+",
        r"^mete\s+(no|na|nas)\s+(inbox|compras|ideias|leituras|foco|rotina)\s+",
        r"^põe\s+(no|na|nas)\s+(inbox|compras|ideias|leituras|foco|rotina)\s+",
        r"^guarda\s+(no|na|nas)\s+(inbox|compras|ideias|leituras|foco|rotina)\s+",
    ]

    texto_limpo = texto
    for prefixo in override_prefixos:
        texto_limpo = re.sub(prefixo, "", texto_limpo, flags=re.IGNORECASE)

    prefixos_para_remover = {
        "compras": [
            r"^comprar?\s+",
            r"^lista de compras\s+",
            r"^adiciona(r)?\s+(à|na|a)\s+lista\s+",
            r"^preciso comprar\s+",
        ],
        "ideias": [
            r"^ideia\s+",
            r"^e se\s+",
            r"^nova ideia\s+",
        ],
        "leituras": [
            r"^leitura\s+",
            r"^salva(r)?\s+(o\s+)?link\s+",
            r"^ver depois\s+",
        ],
        "foco": [
            r"^foco\s+",
            r"^prioridade\s+",
        ],
        "rotina": [
            r"^rotina\s+",
        ],
    }

    prefixos = prefixos_para_remover.get(destino, [])
    for prefixo in prefixos:
        texto_limpo = re.sub(prefixo, "", texto_limpo, flags=re.IGNORECASE)

    return texto_limpo.strip() or texto


# =============================================================================
# NOTION API HELPERS
# =============================================================================


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
        response = requests.patch(url, headers=notion_headers(), json=payload, timeout=7)
        response.raise_for_status()
        logger.info(f"Checkbox adicionado em {page_id}: {texto}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao adicionar checkbox: {e}")
        if hasattr(e, "response") and e.response is not None:
            logger.error(f"Response body: {e.response.text}")
        return False


def ler_checkboxes_pendentes(page_id: str, limite: int = 10) -> list:
    """Lê os blocos to-do não marcados de uma página."""
    url = f"{NOTION_API_URL}/blocks/{page_id}/children"
    params = {"page_size": 100}

    try:
        response = requests.get(
            url, headers=notion_headers(), params=params, timeout=7
        )
        response.raise_for_status()
        data = response.json()

        pendentes = []
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
                break

        return pendentes
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao ler checkboxes: {e}")
        return []


def marcar_checkbox(block_id: str) -> bool:
    """Marca um bloco to-do como checked."""
    url = f"{NOTION_API_URL}/blocks/{block_id}"
    payload = {
        "to_do": {
            "checked": True,
        }
    }

    try:
        response = requests.patch(url, headers=notion_headers(), json=payload, timeout=7)
        response.raise_for_status()
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
    payload = {
        "query": query,
        "page_size": 5,
    }

    try:
        response = requests.post(url, headers=notion_headers(), json=payload, timeout=7)
        response.raise_for_status()
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


# =============================================================================
# ALEXA HANDLERS
# =============================================================================


class LaunchRequestHandler(AbstractRequestHandler):
    """Quando o usuário abre a skill."""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        speech = (
            "E aí! Sou o seu caderno. "
            "Pode dizer coisas como: anota algo, compra leite, "
            "nova ideia, minhas tarefas, resumo do dia, "
            "ou busca alguma coisa. O que vai ser?"
        )
        return (
            handler_input.response_builder.speak(speech)
            .ask("O que você quer fazer?")
            .response
        )


class AnotarIntentHandler(AbstractRequestHandler):
    """Anotar/criar item — roteia automaticamente para o destino certo."""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("AnotarIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        slots = handler_input.request_envelope.request.intent.slots
        texto = slots.get("texto", None)

        if not texto or not texto.value:
            speech = "Não entendi. O que você quer anotar?"
            return (
                handler_input.response_builder.speak(speech)
                .ask(speech)
                .response
            )

        texto_original = texto.value
        destino_key = determinar_destino(texto_original)
        destino = DESTINOS[destino_key]

        texto_limpo = limpar_texto(texto_original, destino_key)

        if adicionar_checkbox(destino["page_id"], texto_limpo):
            speech = (
                f"Beleza! Anotei '{texto_limpo}' "
                f"no {destino['emoji']} {destino['nome']}. "
                f"Mais alguma coisa?"
            )
        else:
            speech = "Puts, deu ruim tentando anotar. Tenta de novo?"

        return (
            handler_input.response_builder.speak(speech)
            .ask("O que mais?")
            .response
        )


class ListarTarefasIntentHandler(AbstractRequestHandler):
    """Listar tarefas pendentes."""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("ListarTarefasIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        slots = handler_input.request_envelope.request.intent.slots
        local = slots.get("local", None)

        # Determinar de onde ler
        destino_key = "inbox"
        if local and local.value:
            local_lower = local.value.lower()
            mapa_local = {
                "inbox": "inbox",
                "caixa de entrada": "inbox",
                "compras": "compras",
                "lista de compras": "compras",
                "ideias": "ideias",
                "leituras": "leituras",
                "foco": "foco",
                "foco da semana": "foco",
                "rotina": "rotina",
            }
            destino_key = mapa_local.get(local_lower, "inbox")

        destino = DESTINOS[destino_key]
        pendentes = ler_checkboxes_pendentes(destino["page_id"])

        if not pendentes:
            speech = f"Tá limpo! Nada pendente no {destino['nome']}. Mais alguma coisa?"
        elif len(pendentes) == 1:
            speech = (
                f"Você tem um item no {destino['nome']}: "
                f"{pendentes[0]['texto']}. Mais alguma coisa?"
            )
        else:
            nomes = [p["texto"] for p in pendentes]
            lista = ", ".join(nomes[:-1]) + f" e {nomes[-1]}"
            speech = (
                f"Você tem {len(pendentes)} itens no {destino['nome']}: {lista}. "
                f"Mais alguma coisa?"
            )

        return (
            handler_input.response_builder.speak(speech)
            .ask("O que mais?")
            .response
        )


class MarcarConcluidaIntentHandler(AbstractRequestHandler):
    """Marcar tarefa como concluída."""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("MarcarConcluidaIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        slots = handler_input.request_envelope.request.intent.slots
        tarefa = slots.get("tarefa", None)

        if not tarefa or not tarefa.value:
            speech = "Qual tarefa você quer marcar como feita?"
            return (
                handler_input.response_builder.speak(speech)
                .ask(speech)
                .response
            )

        tarefa_value = tarefa.value

        # Procurar em todos os destinos
        for key, dest in DESTINOS.items():
            sucesso, nome_completo = encontrar_e_marcar_tarefa(
                dest["page_id"], tarefa_value
            )
            if sucesso:
                speech = (
                    f"Feito! Risquei '{nome_completo}' "
                    f"do {dest['emoji']} {dest['nome']}. Mais alguma coisa?"
                )
                return (
                    handler_input.response_builder.speak(speech)
                    .ask("O que mais?")
                    .response
                )

        speech = (
            f"Não achei '{tarefa_value}' em lugar nenhum. "
            f"Tenta com outro nome."
        )

        return (
            handler_input.response_builder.speak(speech)
            .ask("Tenta de novo?")
            .response
        )


class ResumoIntentHandler(AbstractRequestHandler):
    """Resumo diário: foco + rotina pendente."""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("ResumoIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        resumo = obter_resumo_diario()

        partes = []

        if resumo["foco"]:
            foco_lista = ", ".join(resumo["foco"])
            partes.append(
                f"No foco da semana você tem {len(resumo['foco'])} "
                f"{'item' if len(resumo['foco']) == 1 else 'itens'}: {foco_lista}"
            )
        else:
            partes.append("Seu foco da semana tá limpo")

        if resumo["rotina"]:
            rotina_lista = ", ".join(resumo["rotina"])
            partes.append(
                f"Na rotina tem {len(resumo['rotina'])} "
                f"{'coisa' if len(resumo['rotina']) == 1 else 'coisas'} pendente: {rotina_lista}"
            )

        if not partes:
            speech = "Tá tudo em dia! Nada pendente no foco nem na rotina. Mais alguma coisa?"
        else:
            speech = "Bom dia! Aqui vai seu resumo. " + ". ".join(partes) + ". Mais alguma coisa?"

        return (
            handler_input.response_builder.speak(speech)
            .ask("O que mais?")
            .response
        )


class PesquisarIntentHandler(AbstractRequestHandler):
    """Pesquisar por voz no workspace do Notion."""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("PesquisarIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        slots = handler_input.request_envelope.request.intent.slots
        termo = slots.get("termo", None)

        if not termo or not termo.value:
            speech = "O que você quer buscar?"
            return (
                handler_input.response_builder.speak(speech)
                .ask(speech)
                .response
            )

        termo_value = termo.value
        resultados = pesquisar_no_notion(termo_value)

        if not resultados:
            speech = f"Não achei nada sobre '{termo_value}' no seu Notion. Quer buscar outra coisa?"
        elif len(resultados) == 1:
            speech = f"Achei uma página: {resultados[0]}. Mais alguma coisa?"
        else:
            lista = ", ".join(resultados[:-1]) + f" e {resultados[-1]}"
            speech = (
                f"Achei {len(resultados)} resultados pra '{termo_value}': {lista}. "
                f"Mais alguma coisa?"
            )

        return (
            handler_input.response_builder.speak(speech)
            .ask("O que mais?")
            .response
        )


# --- Handlers padrão (obrigatórios) ---


class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        speech = (
            "Você pode usar o caderno assim: "
            "Fala 'anota' seguido do que quer guardar e eu coloco no lugar certo. "
            "Fala 'compra leite' e vai pra lista de compras. "
            "Fala 'ideia' seguido de algo e vai pras ideias. "
            "Fala 'minhas tarefas' pra ouvir o que tá pendente. "
            "Fala 'resumo do dia' pro resumo geral. "
            "Fala 'busca' seguido de algo pra procurar no Notion. "
            "Ou fala 'marca' seguido do nome pra riscar uma tarefa."
        )
        return (
            handler_input.response_builder.speak(speech)
            .ask("O que vai ser?")
            .response
        )


class CancelStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("AMAZON.CancelIntent")(
            handler_input
        ) or is_intent_name("AMAZON.StopIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        speech = "Falou! Seu caderno tá sempre aqui."
        return handler_input.response_builder.speak(speech).response


class FallbackIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        speech = (
            "Não entendi. Tenta falar: "
            "anota algo, compra algo, minhas tarefas, "
            "resumo do dia, busca alguma coisa, "
            "ou marca algo como feito."
        )
        return (
            handler_input.response_builder.speak(speech)
            .ask("O que você quer fazer?")
            .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        return handler_input.response_builder.response


class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input: HandlerInput, exception: Exception) -> bool:
        return True

    def handle(self, handler_input: HandlerInput, exception: Exception) -> Response:
        logger.error(f"Erro inesperado: {exception}", exc_info=True)
        speech = "Eita, deu algum erro. Tenta de novo?"
        return (
            handler_input.response_builder.speak(speech)
            .ask("Quer tentar de novo?")
            .response
        )


# =============================================================================
# SKILL BUILDER
# =============================================================================

sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(AnotarIntentHandler())
sb.add_request_handler(ListarTarefasIntentHandler())
sb.add_request_handler(MarcarConcluidaIntentHandler())
sb.add_request_handler(ResumoIntentHandler())
sb.add_request_handler(PesquisarIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

# Entry point para AWS Lambda
lambda_handler = sb.lambda_handler()
