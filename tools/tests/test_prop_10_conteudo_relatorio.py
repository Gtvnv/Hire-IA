"""Teste de propriedade: conteúdo do relatório conforme o número de respostas (Req. 5.2, 5.4, 5.5)."""

from decimal import Decimal

from hypothesis import given, settings, strategies as st

from tools.relatorio import (
    RespostaAvaliada,
    calcular_nota_geral,
    calcular_notas_por_categoria,
    ordenar_plano_de_estudo,
    validar_relatorio,
)

_CATEGORIAS = ["tecnica", "comportamental", "lideranca", "arquitetura"]
_texto = st.text(alphabet="abcdefghijklmnopqrstuvwxyz ", min_size=1, max_size=40).filter(
    lambda s: s.strip() != ""
)
_nota = st.integers(0, 100).map(lambda i: Decimal(i) / 10)
_resposta = st.builds(RespostaAvaliada, st.sampled_from(_CATEGORIAS), _nota)
_categoria = st.sampled_from(_CATEGORIAS)
_ponto = st.fixed_dictionaries({"texto": _texto, "categoria": _categoria})

# n = 0, 1, 2 e 3 ou mais.
_respostas = st.one_of(
    st.just([]),
    st.lists(_resposta, min_size=1, max_size=1),
    st.lists(_resposta, min_size=2, max_size=2),
    st.lists(_resposta, min_size=3, max_size=10),
)


@st.composite
def _cenarios(draw):
    """Respostas e um relatório válido para o número n de respostas."""
    respostas = draw(_respostas)
    n = len(respostas)
    if n == 0:
        return respostas, {
            "parcial": True,
            "resumo": draw(_texto),
            "pontos_fortes": [],
            "pontos_de_melhoria": [],
        }
    notas = calcular_notas_por_categoria(respostas)
    parcial = n < 3
    qtd = draw(st.integers(0, 2)) if parcial else 3
    qtd_melhoria = draw(st.integers(0, 2)) if parcial else 3
    topicos = draw(
        st.lists(
            st.fixed_dictionaries({"topico": _texto, "categoria": st.sampled_from(sorted(notas))}),
            min_size=1,
            max_size=5,
        )
    )
    return respostas, {
        "parcial": parcial,
        "nota_geral": calcular_nota_geral(respostas),
        "nota_por_categoria": notas,
        "resumo": draw(_texto),
        "pontos_fortes": draw(st.lists(_ponto, min_size=qtd, max_size=qtd)),
        "pontos_de_melhoria": draw(st.lists(_ponto, min_size=qtd_melhoria, max_size=qtd_melhoria)),
        "plano_de_estudo": ordenar_plano_de_estudo(topicos, notas),
    }


# Feature: ia-entrevistador, Property 10: Conteúdo do relatório conforme o número de respostas
# **Validates: Requirements 5.2, 5.4, 5.5**
@settings(max_examples=200, deadline=None)
@given(_cenarios())
def test_relatorio_valido_conforme_numero_de_respostas(cenario):
    respostas, relatorio = cenario
    assert validar_relatorio(relatorio, respostas).valido
    if len(respostas) == 0:
        assert "nota_geral" not in relatorio
        assert "nota_por_categoria" not in relatorio
        assert "plano_de_estudo" not in relatorio


# Feature: ia-entrevistador, Property 10: Conteúdo do relatório conforme o número de respostas
# **Validates: Requirements 5.2, 5.4, 5.5**
@settings(max_examples=200, deadline=None)
@given(_cenarios(), st.data())
def test_relatorio_com_contagem_errada_e_rejeitado(cenario, data):
    respostas, relatorio = cenario
    n = len(respostas)
    if n == 0:
        invalido = {**relatorio, "nota_geral": Decimal("5.0")}
        campos = {e.campo for e in validar_relatorio(invalido, respostas).erros}
        assert "nota_geral" in campos
        return
    campo = data.draw(st.sampled_from(["pontos_fortes", "pontos_de_melhoria"]))
    if n >= 3:
        # completo: remover um ponto viola o exigido (exatamente 3)
        invalido = {**relatorio, campo: relatorio[campo][:2]}
    else:
        # parcial: mais de 2 pontos viola o máximo
        invalido = {**relatorio, campo: [{"texto": "x", "categoria": "tecnica"}] * 3}
    campos = {e.campo for e in validar_relatorio(invalido, respostas).erros}
    assert campo in campos
    # parcial ausente/incorreto é rejeitado
    errado = {**relatorio, "parcial": not relatorio["parcial"]}
    assert "parcial" in {e.campo for e in validar_relatorio(errado, respostas).erros}
