"""Teste de propriedade: expansão do banco preserva as perguntas (Req. 2.6)."""

from hypothesis import given, settings, strategies as st

from tools.banco import (
    CATEGORIAS,
    COLUNAS,
    DIFICULDADES,
    TOTAL_EXPANSAO,
    verificar_expansao,
)

_celula = st.text(
    alphabet=st.characters(
        whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters=" ,.?"
    ),
    min_size=1,
    max_size=40,
).map(str.strip).filter(bool)

_linha = st.tuples(_celula, st.sampled_from(CATEGORIAS), st.sampled_from(DIFICULDADES), _celula)


def _tabela(linhas) -> str:
    """Renderiza linhas (pergunta, categoria, dificuldade, resposta) com numeração sequencial."""
    saida = [
        "| " + " | ".join(c.capitalize() for c in COLUNAS) + " |",
        "|" + "---|" * len(COLUNAS),
    ]
    for numero, (pergunta, categoria, dificuldade, resposta) in enumerate(linhas, start=1):
        saida.append(f"| {numero} | {pergunta} | {categoria} | {dificuldade} | {resposta} |")
    return "\n".join(saida)


_anteriores = st.lists(_linha, min_size=1, max_size=15)
_novas = st.lists(_linha, min_size=TOTAL_EXPANSAO, max_size=TOTAL_EXPANSAO)


# Feature: ia-entrevistador, Property 4: Expansão do banco preserva as perguntas
# **Validates: Requirements 2.6**
@settings(max_examples=100)
@given(_anteriores, _novas)
def test_expansao_valida_e_aceita(anteriores, novas):
    antes = _tabela(anteriores)
    depois = _tabela(anteriores + novas)

    resultado = verificar_expansao(antes, depois)

    assert resultado.valido, resultado.erros
    assert len(resultado.perguntas) == len(anteriores) + TOTAL_EXPANSAO
    for original, atual in zip(_tabela_para_tuplas(anteriores), resultado.perguntas):
        assert atual.como_tupla() == original


def _tabela_para_tuplas(linhas):
    return [
        (str(n), p, c, d, r) for n, (p, c, d, r) in enumerate(linhas, start=1)
    ]


# Feature: ia-entrevistador, Property 4: Expansão do banco preserva as perguntas
# **Validates: Requirements 2.6**
@settings(max_examples=100)
@given(_anteriores, _novas, st.data())
def test_expansao_violada_e_rejeitada(anteriores, novas, data):
    antes = _tabela(anteriores)
    violacao = data.draw(
        st.sampled_from(["menos_linhas", "mais_linhas", "alterada", "removida"])
    )

    if violacao == "menos_linhas":
        depois = _tabela(anteriores + novas[:-1])
    elif violacao == "mais_linhas":
        extra = data.draw(_linha)
        depois = _tabela(anteriores + novas + [extra])
    elif violacao == "alterada":
        indice = data.draw(st.integers(0, len(anteriores) - 1))
        p, c, d, r = anteriores[indice]
        alteradas = list(anteriores)
        alteradas[indice] = (p + " X", c, d, r)
        depois = _tabela(alteradas + novas)
    else:  # removida: mantém o total, mas descarta uma anterior
        indice = data.draw(st.integers(0, len(anteriores) - 1))
        sem = anteriores[:indice] + anteriores[indice + 1 :]
        extra = data.draw(_linha)
        depois = _tabela(sem + novas + [extra])

    resultado = verificar_expansao(antes, depois)

    if violacao == "removida" and all(
        a == b for a, b in zip(anteriores, sem + novas + [extra])
    ):
        return  # a remoção coincidiu com um prefixo idêntico; nada a detectar
    assert not resultado.valido
