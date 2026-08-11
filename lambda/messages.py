"""
Mensagens de resposta da Alexa para o Log Lady.
Centralizadas para fácil manutenção e consistência de tom.
"""

# --- LaunchRequest ---
LAUNCH_SPEECH = (
    "E aí! Sou o seu caderno. "
    "Pode dizer coisas como: anota algo, compra leite, "
    "nova ideia, minhas tarefas, resumo do dia, "
    "ou busca alguma coisa. O que vai ser?"
)
LAUNCH_REPROMPT = "O que você quer fazer?"

# --- Anotar ---
ANOTAR_SUCESSO = "Beleza! Anotei '{texto}' no {emoji} {nome}. Mais alguma coisa?"
ANOTAR_ERRO = "Puts, deu ruim tentando anotar. Tenta de novo?"
ANOTAR_VAZIO = "Não entendi. O que você quer anotar?"

# --- Listar ---
LISTAR_VAZIO = "Tá limpo! Nada pendente no {nome}. Mais alguma coisa?"
LISTAR_UM = "Você tem um item no {nome}: {item}. Mais alguma coisa?"
LISTAR_VARIOS = "Você tem {count} itens no {nome}: {lista}. Mais alguma coisa?"

# --- Marcar Concluída ---
MARCAR_SUCESSO = "Feito! Risquei '{nome_tarefa}' do {emoji} {nome}. Mais alguma coisa?"
MARCAR_NAO_ENCONTRADA = "Não achei '{tarefa}' em lugar nenhum. Tenta com outro nome."
MARCAR_VAZIO = "Qual tarefa você quer marcar como feita?"

# --- Resumo ---
RESUMO_INTRO = "Bom dia! Aqui vai seu resumo. "
RESUMO_FOCO = (
    "No foco da semana você tem {count} "
    "{item_word}: {lista}"
)
RESUMO_FOCO_LIMPO = "Seu foco da semana tá limpo"
RESUMO_ROTINA = (
    "Na rotina tem {count} "
    "{item_word} pendente: {lista}"
)
RESUMO_TUDO_LIMPO = "Tá tudo em dia! Nada pendente no foco nem na rotina. Mais alguma coisa?"

# --- Pesquisa ---
PESQUISA_VAZIO_SLOT = "O que você quer buscar?"
PESQUISA_SEM_RESULTADO = "Não achei nada sobre '{termo}' no seu Notion. Quer buscar outra coisa?"
PESQUISA_UM = "Achei uma página: {resultado}. Mais alguma coisa?"
PESQUISA_VARIOS = "Achei {count} resultados pra '{termo}': {lista}. Mais alguma coisa?"

# --- Help ---
HELP_SPEECH = (
    "Você pode usar o caderno assim: "
    "Fala 'anota' seguido do que quer guardar e eu coloco no lugar certo. "
    "Fala 'compra leite' e vai pra lista de compras. "
    "Fala 'ideia' seguido de algo e vai pras ideias. "
    "Fala 'minhas tarefas' pra ouvir o que tá pendente. "
    "Fala 'resumo do dia' pro resumo geral. "
    "Fala 'busca' seguido de algo pra procurar no Notion. "
    "Ou fala 'marca' seguido do nome pra riscar uma tarefa."
)

# --- Cancel/Stop ---
CANCEL_SPEECH = "Falou! Seu caderno tá sempre aqui."

# --- Fallback ---
FALLBACK_SPEECH = (
    "Não entendi. Tenta falar: "
    "anota algo, compra algo, minhas tarefas, "
    "resumo do dia, busca alguma coisa, "
    "ou marca algo como feito."
)

# --- Erro genérico ---
ERRO_GENERICO = "Eita, deu algum erro. Tenta de novo?"

# --- Reprompts ---
REPROMPT_GENERICO = "O que mais?"
REPROMPT_TENTA = "Tenta de novo?"
