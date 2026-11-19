"""Teste de propriedade: ordenação do plano de estudo (Req. 5.3)."""

from decimal import Decimal

from hypothesis import given, settings, strategies as st

from tools.relatorio import (
    PLANO_MAX,
    PLANO_MIN,
    RespostaAvaliada,
    calcular_nota_geral,
    calcular_notas_por_categoria,
    ordenar_plano_de_estudo,
    validar_relatorio,
)

# Poucas categorias e notas inteiras (0 a 10) para produzir empates com frequência.
_categorias = st.sampled_from(["Python", "Banco de Dados", "Arquitetura", "Comportamental", "API", "Testes"])
_notas = st.integers(min_value=0, max_value=10).map(Decimal)
_respostas = st.lists(
    st.builds(RespostaAvaliada, categoria=_categorias, nota=_notas), min_size=3, max_size=12
)


@st.composite
def _cenarios(draw):
    respostas = draw(_respostas)
    notas = calcular_notas_por_categoria(respostas)
    categorias = sorted(notas)
    topicos = draw(
        st.lists(
            st.sampled_from(categorias), min_size=PLANO_MIN, max_size=PLANO_MAX
        ).map(lambda cats: [{"topico": f"Estudar {c} #{i}", "categoria": c} for i, c in enumerate(cats)])
    )
    # Ordem de entrada arbitrária.
    embaralhado = draw(st.permutations(topicos))
    return respostas, notas, list(embaralhado)


def _relatorio(respostas, notas, plano):
    ponto = {"texto": "Ponto.", "categoria": next(iter(notas))}
    return {
        "parcial": False,
        "nota_geral": calcular_nota_geral(respostas),
        "nota_por_categoria": dict(notas),
        "resumo": "Resumo.",
        "pontos_fortes": [ponto] * 3,
        "pontos_de_melhoria": [ponto] * 3,
        "plano_de_estudo": plano,
    }


# Feature: ia-entrevistador, Property 11: Ordenação do plano de estudo
# Validates: Requirements 5.3
@settings(max_examples=200, deadline=None)
@given(_cenarios())
def test_plano_ordenado_por_nota_e_nome(cenario):
    respostas, notas, topicos = cenario
    plano = ordenar_plano_de_estudo(topicos, notas)

    assert PLANO_MIN <= len(plano) <= PLANO_MAX
    assert sorted(t["topico"] for t in plano) == sorted(t["topico"] for t in topicos)

    chaves = [(notas[t["categoria"]], t["categoria"]) for t in plano]
    assert chaves == sorted(chaves)

    # O relatório com o plano ordenado é válido quanto ao plano.
    resultado = validar_relatorio(_relatorio(respostas, notas, plano), respostas)
    assert not [e for e in resultado.erros if e.campo == "plano_de_estudo"]


# Feature: ia-entrevistador, Property 11: Ordenação do plano de estudo
# Validates: Requirements 5.3
@settings(max_examples=200, deadline=None)
@given(_cenarios())
def test_plano_fora_de_ordem_e_rejeitado(cenario):
    respostas, notas, topicos = cenario
    ordenado = ordenar_plano_de_estudo(topicos, notas)
    invertido = list(reversed(ordenado))
    chave = lambda p: [(notas[t["categoria"]], t["categoria"]) for t in p]
    if chave(invertido) == chave(ordenado):
        return  # todos os tópicos com a mesma chave: ordem indistinguível

    resultado = validar_relatorio(_relatorio(respostas, notas, invertido), respostas)
    assert any(e.campo == "plano_de_estudo" for e in resultado.erros)


def test_empate_de_nota_desempata_por_nome_da_categoria():
    notas = {"Zeta": Decimal("5.0"), "Alfa": Decimal("5.0"), "Beta": Decimal("2.0")}
    topicos = [
        {"topico": "z", "categoria": "Zeta"},
        {"topico": "a", "categoria": "Alfa"},
        {"topico": "b", "categoria": "Beta"},
    ]
    plano = ordenar_plano_de_estudo(topicos, notas)
    assert [t["categoria"] for t in plano] == ["Beta", "Alfa", "Zeta"]


def _relatorio_parcial(respostas, plano):
    notas = calcular_notas_por_categoria(respostas)
    return {
        "parcial": True,
        "nota_geral": calcular_nota_geral(respostas),
        "nota_por_categoria": dict(notas),
        "resumo": "Resumo.",
        "pontos_fortes": [],
        "pontos_de_melhoria": [],
        "plano_de_estudo": plano,
    }


# Feature: ia-entrevistador, Property 11: Ordenação do plano de estudo
# Validates: Requirements 5.3
@settings(max_examples=100, deadline=None)
@given(st.lists(st.builds(RespostaAvaliada, categoria=_categorias, nota=_notas), min_size=1, max_size=2))
def test_relatorio_parcial_plano_ordenado_e_valido(respostas):
    notas = calcular_notas_por_categoria(respostas)
    topicos = [{"topico": f"Estudar {c}", "categoria": c} for c in sorted(notas, reverse=True)]
    plano = ordenar_plano_de_estudo(topicos, notas)

    chaves = [(notas[t["categoria"]], t["categoria"]) for t in plano]
    assert chaves == sorted(chaves)

    resultado = validar_relatorio(_relatorio_parcial(respostas, plano), respostas)
    assert resultado.erros == ()


def test_parcial_com_duas_categorias_fora_de_ordem_e_rejeitado():
    respostas = [RespostaAvaliada("Python", Decimal(9)), RespostaAvaliada("API", Decimal(2))]
    notas = calcular_notas_por_categoria(respostas)
    topicos = [{"topico": "p", "categoria": "Python"}, {"topico": "a", "categoria": "API"}]
    # Ordem correta: API (2) antes de Python (9).
    ok = validar_relatorio(_relatorio_parcial(respostas, ordenar_plano_de_estudo(topicos, notas)), respostas)
    assert ok.erros == ()
    ruim = validar_relatorio(_relatorio_parcial(respostas, topicos), respostas)
    assert any(e.campo == "plano_de_estudo" for e in ruim.erros)


def test_parcial_com_uma_resposta_aceita_plano_de_um_topico():
    respostas = [RespostaAvaliada("API", Decimal(4))]
    plano = [{"topico": "Estudar API", "categoria": "API"}]
    assert validar_relatorio(_relatorio_parcial(respostas, plano), respostas).erros == ()
    vazio = validar_relatorio(_relatorio_parcial(respostas, []), respostas)
    assert any(e.campo == "plano_de_estudo" for e in vazio.erros)
