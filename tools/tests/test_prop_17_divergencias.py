"""Teste de propriedade: divergências entre assistentes (Req. 10.2, 10.7, 10.8)."""

from hypothesis import given, settings, strategies as st

from tools.docs_md import (
    Cenario,
    Execucao,
    calcular_divergencias,
    tem_multiplos_assistentes,
    validar_execucoes,
)

_CRITERIOS = ["clareza", "aderencia", "tom", "formato", "cobertura"]

# Nomes variados, incluindo vazio e só espaços.
_nome = st.one_of(
    st.just(""),
    st.just("   "),
    st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789 .-", min_size=1, max_size=10),
    st.sampled_from(["Kiro", "Claude", "gpt-4", "Gemini 2.5"]),
)


@st.composite
def _execucoes(draw, coincidem=None):
    """2..5 execuções com o mesmo conjunto de critérios."""
    criterios = draw(
        st.lists(st.sampled_from(_CRITERIOS), min_size=1, max_size=5, unique=True)
    )
    n = draw(st.integers(2, 5))
    if coincidem is None:
        coincidem = draw(st.booleans())
    base = {c: draw(st.booleans()) for c in criterios}
    execs = []
    for _ in range(n):
        if coincidem:
            verif = dict(base)
        else:
            verif = {c: draw(st.booleans()) for c in criterios}
        execs.append(
            Execucao(
                assistente=draw(_nome),
                modelo=draw(_nome),
                entrada="mesma entrada",
                verificacoes=verif,
            )
        )
    return execs


def _esperado(execs):
    esperado = {}
    for c in execs[0].verificacoes:
        resultados = {bool(e.verificacoes[c]) for e in execs}
        if len(resultados) > 1:
            pares = [(e.assistente, e.modelo) for e in execs if not e.verificacoes[c]]
            esperado[c] = tuple(dict.fromkeys(pares))
    return esperado


# Feature: ia-entrevistador, Property 17: Divergências entre assistentes são registradas com assistente e modelo
# **Validates: Requirements 10.2, 10.7, 10.8**
@settings(max_examples=200, deadline=None)
@given(execs=_execucoes())
def test_divergencias_listam_criterios_diferentes_com_assistente_e_modelo(execs):
    divergencias = calcular_divergencias(execs)
    assert divergencias == _esperado(execs)
    for criterio, pares in divergencias.items():
        # Cada critério divergente tem ao menos uma execução reprovada indicada.
        assert pares
        reprovados = {(e.assistente, e.modelo) for e in execs if not e.verificacoes[criterio]}
        assert set(pares) == reprovados


# Feature: ia-entrevistador, Property 17: Divergências entre assistentes são registradas com assistente e modelo
# **Validates: Requirements 10.8**
@settings(max_examples=100, deadline=None)
@given(execs=_execucoes(coincidem=True))
def test_resultados_coincidentes_nao_geram_divergencias(execs):
    assert calcular_divergencias(execs) == {}


# Feature: ia-entrevistador, Property 17: Divergências entre assistentes são registradas com assistente e modelo
# **Validates: Requirements 10.2, 10.7**
@settings(max_examples=100, deadline=None)
@given(execs=_execucoes())
def test_validar_execucoes_exige_assistente_e_modelo_nao_vazios(execs):
    resultado = validar_execucoes(execs)
    esperado_ok = all(e.assistente.strip() and e.modelo.strip() for e in execs)
    assert resultado.valido == esperado_ok
    campos_vazios = sum(
        (not e.assistente.strip()) + (not e.modelo.strip()) for e in execs
    )
    assert len(resultado.erros) == campos_vazios


# Feature: ia-entrevistador, Property 17: Divergências entre assistentes são registradas com assistente e modelo
# **Validates: Requirements 10.7**
@settings(max_examples=100, deadline=None)
@given(execs=_execucoes())
def test_multiplos_assistentes_exige_dois_distintos_nao_vazios(execs):
    cenario = Cenario(id="c1", execucoes=tuple(execs))
    distintos = {e.assistente.strip().lower() for e in execs if e.assistente.strip()}
    assert tem_multiplos_assistentes(cenario) == (len(distintos) >= 2)
