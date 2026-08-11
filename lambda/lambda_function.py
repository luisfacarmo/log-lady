"""
Log Lady — Alexa + Notion Integration
======================================
Skill: "Meu Caderno"
Invocation: "Alexa, abre meu caderno"

Entry point para AWS Lambda.
Handlers da Alexa que orquestram routing e operações Notion.
"""

import logging

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler,
    AbstractExceptionHandler,
)
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

from config import DESTINOS
from routing import determinar_destino, limpar_texto
from notion_client import (
    adicionar_checkbox,
    ler_checkboxes_pendentes,
    encontrar_e_marcar_tarefa,
    pesquisar_no_notion,
    obter_resumo_diario,
)
import messages as msg

# --- Logging ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# =============================================================================
# ALEXA HANDLERS
# =============================================================================


class LaunchRequestHandler(AbstractRequestHandler):
    """Quando o usuário abre a skill."""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        return (
            handler_input.response_builder.speak(msg.LAUNCH_SPEECH)
            .ask(msg.LAUNCH_REPROMPT)
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
            return (
                handler_input.response_builder.speak(msg.ANOTAR_VAZIO)
                .ask(msg.ANOTAR_VAZIO)
                .response
            )

        texto_original = texto.value
        destino_key = determinar_destino(texto_original)
        destino = DESTINOS[destino_key]

        texto_limpo = limpar_texto(texto_original, destino_key)

        if adicionar_checkbox(destino["page_id"], texto_limpo):
            speech = msg.ANOTAR_SUCESSO.format(
                texto=texto_limpo, emoji=destino["emoji"], nome=destino["nome"]
            )
        else:
            speech = msg.ANOTAR_ERRO

        return (
            handler_input.response_builder.speak(speech)
            .ask(msg.REPROMPT_GENERICO)
            .response
        )


class ListarTarefasIntentHandler(AbstractRequestHandler):
    """Listar tarefas pendentes."""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("ListarTarefasIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        slots = handler_input.request_envelope.request.intent.slots
        local = slots.get("local", None)

        # Determinar de onde ler — derivado de DESTINOS
        destino_key = "inbox"
        if local and local.value:
            local_lower = local.value.lower()
            # Mapa derivado: nome + variações comuns
            mapa_local = {key: key for key in DESTINOS}
            mapa_local.update({
                "caixa de entrada": "inbox",
                "lista de compras": "compras",
                "foco da semana": "foco",
            })
            destino_key = mapa_local.get(local_lower, "inbox")

        destino = DESTINOS[destino_key]
        pendentes = ler_checkboxes_pendentes(destino["page_id"])

        if not pendentes:
            speech = msg.LISTAR_VAZIO.format(nome=destino["nome"])
        elif len(pendentes) == 1:
            speech = msg.LISTAR_UM.format(
                nome=destino["nome"], item=pendentes[0]["texto"]
            )
        else:
            nomes = [p["texto"] for p in pendentes]
            lista = ", ".join(nomes[:-1]) + f" e {nomes[-1]}"
            speech = msg.LISTAR_VARIOS.format(
                count=len(pendentes), nome=destino["nome"], lista=lista
            )

        return (
            handler_input.response_builder.speak(speech)
            .ask(msg.REPROMPT_GENERICO)
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
            return (
                handler_input.response_builder.speak(msg.MARCAR_VAZIO)
                .ask(msg.MARCAR_VAZIO)
                .response
            )

        tarefa_value = tarefa.value

        # Procurar em todos os destinos
        for key, dest in DESTINOS.items():
            sucesso, nome_completo = encontrar_e_marcar_tarefa(
                dest["page_id"], tarefa_value
            )
            if sucesso:
                speech = msg.MARCAR_SUCESSO.format(
                    nome_tarefa=nome_completo,
                    emoji=dest["emoji"],
                    nome=dest["nome"],
                )
                return (
                    handler_input.response_builder.speak(speech)
                    .ask(msg.REPROMPT_GENERICO)
                    .response
                )

        speech = msg.MARCAR_NAO_ENCONTRADA.format(tarefa=tarefa_value)
        return (
            handler_input.response_builder.speak(speech)
            .ask(msg.REPROMPT_TENTA)
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
                msg.RESUMO_FOCO.format(
                    count=len(resumo["foco"]),
                    item_word="item" if len(resumo["foco"]) == 1 else "itens",
                    lista=foco_lista,
                )
            )
        else:
            partes.append(msg.RESUMO_FOCO_LIMPO)

        if resumo["rotina"]:
            rotina_lista = ", ".join(resumo["rotina"])
            partes.append(
                msg.RESUMO_ROTINA.format(
                    count=len(resumo["rotina"]),
                    item_word="coisa" if len(resumo["rotina"]) == 1 else "coisas",
                    lista=rotina_lista,
                )
            )

        if not partes:
            speech = msg.RESUMO_TUDO_LIMPO
        else:
            speech = msg.RESUMO_INTRO + ". ".join(partes) + ". Mais alguma coisa?"

        return (
            handler_input.response_builder.speak(speech)
            .ask(msg.REPROMPT_GENERICO)
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
            return (
                handler_input.response_builder.speak(msg.PESQUISA_VAZIO_SLOT)
                .ask(msg.PESQUISA_VAZIO_SLOT)
                .response
            )

        termo_value = termo.value
        resultados = pesquisar_no_notion(termo_value)

        if not resultados:
            speech = msg.PESQUISA_SEM_RESULTADO.format(termo=termo_value)
        elif len(resultados) == 1:
            speech = msg.PESQUISA_UM.format(resultado=resultados[0])
        else:
            lista = ", ".join(resultados[:-1]) + f" e {resultados[-1]}"
            speech = msg.PESQUISA_VARIOS.format(
                count=len(resultados), termo=termo_value, lista=lista
            )

        return (
            handler_input.response_builder.speak(speech)
            .ask(msg.REPROMPT_GENERICO)
            .response
        )


# --- Handlers padrão (obrigatórios) ---


class HelpIntentHandler(AbstractRequestHandler):
    """Handler para AMAZON.HelpIntent."""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        return (
            handler_input.response_builder.speak(msg.HELP_SPEECH)
            .ask(msg.LAUNCH_REPROMPT)
            .response
        )


class CancelStopIntentHandler(AbstractRequestHandler):
    """Handler para AMAZON.CancelIntent e AMAZON.StopIntent."""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("AMAZON.CancelIntent")(
            handler_input
        ) or is_intent_name("AMAZON.StopIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        return handler_input.response_builder.speak(msg.CANCEL_SPEECH).response


class FallbackIntentHandler(AbstractRequestHandler):
    """Handler para AMAZON.FallbackIntent."""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        return (
            handler_input.response_builder.speak(msg.FALLBACK_SPEECH)
            .ask(msg.LAUNCH_REPROMPT)
            .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler para SessionEndedRequest."""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        return handler_input.response_builder.response


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Handler global de exceções."""

    def can_handle(self, handler_input: HandlerInput, exception: Exception) -> bool:
        return True

    def handle(self, handler_input: HandlerInput, exception: Exception) -> Response:
        logger.error(f"Erro inesperado: {exception}", exc_info=True)
        return (
            handler_input.response_builder.speak(msg.ERRO_GENERICO)
            .ask(msg.REPROMPT_TENTA)
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
