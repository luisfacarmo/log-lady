"""
Testes unitários para o sistema de roteamento.
Valida determinar_destino() contra a matriz de regressão completa.
"""

import pytest
from routing import determinar_destino, limpar_texto


# =============================================================================
# MATRIZ DE REGRESSÃO — determinar_destino()
# =============================================================================


class TestRoteamentoCompras:
    """Comandos que devem ir para 🛒 compras."""

    @pytest.mark.parametrize(
        "texto",
        [
            "compra feijão",
            "comprar leite",
            "preciso comprar detergente",
            "feijão",
            "arroz",
            "café",
            "pasta de dente",
            "shampoo",
            "ração",
            "papel higiênico",
            "sabão em pó",
            "saco de lixo",
            "cerveja",
            "banana",
            "frango",
            "nas compras açúcar",
            "na lista de compras macarrão",
            "no mercado azeite",
        ],
    )
    def test_compras(self, texto):
        assert determinar_destino(texto) == "compras"


class TestRoteamentoRotina:
    """Comandos que devem ir para 🧹 rotina."""

    @pytest.mark.parametrize(
        "texto",
        [
            "limpar banheiro",
            "lavar a louça",
            "varrer a sala",
            "faxina no quarto",
            "caixas de areia",
            "arrumar a cama",
            "passar pano no chão",
            "aspirar tapete",
            "lixeira cheia",
            "na rotina esfregar o box",
        ],
    )
    def test_rotina(self, texto):
        assert determinar_destino(texto) == "rotina"


class TestRoteamentoIdeias:
    """Comandos que devem ir para 💡 ideias."""

    @pytest.mark.parametrize(
        "texto",
        [
            "ideia para o projeto",
            "nova ideia de app",
            "e se a gente fizesse diferente",
            "projeto de automação",
            "experimentar receita nova",
            "nas ideias criar um bot",
        ],
    )
    def test_ideias(self, texto):
        assert determinar_destino(texto) == "ideias"


class TestRoteamentoLeituras:
    """Comandos que devem ir para 📚 leituras."""

    @pytest.mark.parametrize(
        "texto",
        [
            "ver depois esse vídeo",
            "artigo sobre produtividade",
            "podcast sobre história",
            "livro sapiens",
            "link interessante",
            "thread no twitter",
            "nas leituras salvar artigo",
            "https://example.com/artigo",
        ],
    )
    def test_leituras(self, texto):
        assert determinar_destino(texto) == "leituras"


class TestRoteamentoFoco:
    """Comandos que devem ir para 🏠 foco."""

    @pytest.mark.parametrize(
        "texto",
        [
            "foco terminar relatório",
            "prioridade entregar documento",
            "urgente responder email",
            "importante revisar contrato",
            "no foco estudar para prova",
        ],
    )
    def test_foco(self, texto):
        assert determinar_destino(texto) == "foco"


class TestRoteamentoInbox:
    """Comandos genéricos que devem ir para 📥 inbox (fallback)."""

    @pytest.mark.parametrize(
        "texto",
        [
            "ligar para o dentista",
            "lembrar de pagar conta",
            "testar integração",
            "verificar documento",
            "mandar email",
            "no inbox guardar isso",
        ],
    )
    def test_inbox(self, texto):
        assert determinar_destino(texto) == "inbox"


class TestRoteamentoOverrideExplicito:
    """Override explícito com 'no/na/nas [destino]' deve ter precedência."""

    def test_override_inbox(self):
        assert determinar_destino("no inbox comprar leite") == "inbox"

    def test_override_compras(self):
        assert determinar_destino("nas compras ideia de presente") == "compras"

    def test_override_na_entrada(self):
        assert determinar_destino("na entrada limpar algo") == "inbox"


# =============================================================================
# TESTES DE PRECEDÊNCIA — Casos Ambíguos Documentados
# =============================================================================


class TestPrecedencia:
    """
    Testes que documentam o comportamento ATUAL da precedência.
    Alguns destes são ambíguos — o teste documenta qual destino GANHA.
    Se a precedência mudar, estes testes vão falhar (o que é desejável).
    """

    def test_compras_antes_de_leituras(self):
        """'comprar livro' → compras ganha (comprar tem precedência sobre livro)."""
        assert determinar_destino("comprar livro sobre gatos") == "compras"

    def test_ideias_antes_de_rotina(self):
        """'ideia limpar' → ideias ganha (ideia match antes na lista)."""
        assert determinar_destino("ideia limpar o escritório") == "ideias"

    def test_foco_antes_de_rotina(self):
        """'importante limpar' → foco ganha (importante match antes de limpar)."""
        assert determinar_destino("importante limpar banheiro") == "foco"

    def test_ideias_antes_de_foco(self):
        """'e se fizesse faxina' → ideias ganha (e se match antes)."""
        assert determinar_destino("e se a gente fizesse faxina") == "ideias"

    def test_compras_agua(self):
        """'água' sozinho → compras (item de supermercado)."""
        assert determinar_destino("anota água") == "compras"

    def test_compras_racao(self):
        """'ração' → compras (item de compra, não rotina)."""
        assert determinar_destino("anota comprar ração") == "compras"

    def test_compras_areia_gatos(self):
        """'caixa de areia dos gatos' → compras (areia de gatos match compras antes de caixa de areia match rotina)."""
        # BUG CONHECIDO: semanticamente deveria ser rotina quando contexto é "limpar caixa"
        # mas "areia dos gatos" é item de compra. Conflito aceito por ora.
        assert determinar_destino("caixa de areia dos gatos") == "compras"


# =============================================================================
# TESTES DE limpar_texto()
# =============================================================================


class TestLimparTexto:
    """Testes para remoção de prefixos."""

    def test_remove_prefixo_compra(self):
        assert limpar_texto("comprar leite", "compras") == "leite"

    def test_remove_prefixo_ideia(self):
        assert limpar_texto("ideia fazer um app", "ideias") == "fazer um app"

    def test_remove_prefixo_ver_depois(self):
        assert limpar_texto("ver depois vídeo legal", "leituras") == "vídeo legal"

    def test_remove_prefixo_foco(self):
        assert limpar_texto("foco terminar relatório", "foco") == "terminar relatório"

    def test_nao_remove_se_nao_tem_prefixo(self):
        assert limpar_texto("leite", "compras") == "leite"

    def test_texto_generico_inbox(self):
        assert limpar_texto("ligar para o dentista", "inbox") == "ligar para o dentista"

    def test_retorna_original_se_ficaria_vazio(self):
        # Se o texto inteiro for o prefixo, retorna o original
        result = limpar_texto("compra", "compras")
        assert result  # Não deve retornar string vazia
