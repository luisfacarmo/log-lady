"""
Sistema de roteamento inteligente do Log Lady.
Classifica texto livre em destinos Notion baseado em padrões regex.
"""

import re


# --- Regras de roteamento (padrões -> destino) ---
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
            r"\bfarm\u00e1cia\b",
            r"\bpreciso comprar\b",
            # Alimentos comuns
            r"\bleite\b",
            r"\bp\u00e3o\b",
            r"\bfeij\u00e3o\b",
            r"\barroz\b",
            r"\bcaf\u00e9\b",
            r"\ba\u00e7\u00facar\b",
            r"\b\u00f3leo\b",
            r"\bazeite\b",
            r"\bmanteiga\b",
            r"\bqueijo\b",
            r"\bovo(s)?\b",
            r"\bfrango\b",
            r"\bcarne\b",
            r"\bpeixe\b",
            r"\bfruta(s)?\b",
            r"\bbanana(s)?\b",
            r"\bma\u00e7\u00e3(s)?\b",
            r"\btomate(s)?\b",
            r"\bcebola(s)?\b",
            r"\balho\b",
            r"\bbatata(s)?\b",
            r"\bmacarr\u00e3o\b",
            r"\bmolho\b",
            r"\bsal\b",
            r"\bvinagre\b",
            r"\bcerveja(s)?\b",
            r"\bvinho\b",
            r"\brefrigerante\b",
            r"\b\u00e1gua\b",
            r"\bsuco\b",
            r"\biogurte\b",
            r"\bcereal\b",
            r"\bbolacha(s)?\b",
            r"\bbiscoito(s)?\b",
            r"\bchocolate\b",
            r"\bsorvete\b",
            r"\bpresunto\b",
            r"\bsalsicha(s)?\b",
            r"\blingui(\u00e7|c)a(s)?\b",
            r"\bfarinha\b",
            r"\bfermento\b",
            r"\bleite condensado\b",
            r"\bcreme de leite\b",
            r"\bdetergente\b",
            r"\bsab\u00e3o\b",
            r"\bsab(\u00e3|a)o em p\u00f3\b",
            r"\bamaciante\b",
            r"\bdesinfetante\b",
            r"\b\u00e1lcool\b",
            r"\bpapel (higi\u00eanico|higi\u00e9nico|toalha)\b",
            r"\bguardanapo(s)?\b",
            r"\bsaco(s)? de lixo\b",
            r"\besponja(s)?\b",
            r"\bshampoo\b",
            r"\bcondicionador\b",
            r"\bsabonete\b",
            r"\bpasta de dente\b",
            r"\bdesodorante\b",
            r"\bfralda(s)?\b",
            r"\bra\u00e7\u00e3o\b",
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
            r"\bv\u00eddeo\b",
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
            r"\blou\u00e7a\b",
            r"\broupa(s)? (pra|para) lavar\b",
            r"\bestender roupa\b",
            r"\brecolher roupa\b",
            r"\bdobrar roupa\b",
            r"\bcama\b.*\b(arrumar|fazer|esticar)\b",
            r"\b(arrumar|fazer|esticar)\b.*\bcama\b",
        ],
    },
]


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
        r"^p\u00f5e\s+(no|na|nas)\s+(inbox|compras|ideias|leituras|foco|rotina)\s+",
        r"^guarda\s+(no|na|nas)\s+(inbox|compras|ideias|leituras|foco|rotina)\s+",
    ]

    texto_limpo = texto
    for prefixo in override_prefixos:
        texto_limpo = re.sub(prefixo, "", texto_limpo, flags=re.IGNORECASE)

    prefixos_para_remover = {
        "compras": [
            r"^comprar?\s+",
            r"^lista de compras\s+",
            r"^adiciona(r)?\s+(\u00e0|na|a)\s+lista\s+",
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
