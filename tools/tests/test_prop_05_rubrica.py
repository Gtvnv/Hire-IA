"""Teste de propriedade: pesos da Rubrica (Req. 4.2)."""

from hypothesis import given, settings, strategies as st

from tools.feedback import NUM_CRITERIOS, PESO_TOTAL, validar_rubrica

_nomes = st.text(
    alphabet=st.characters(blacklist_categories=("Cs",)), min_size=1, max_size=20
).filter(lambda s: s.strip() != "")

_peso_qualquer = st.one_of(
    st.integers(min_value=-50, max_value=150),
    st.booleans(),
    st.floats(min_value=-10, max_value=120, allow_nan=False),
    st.none(),
    st.text(max_size=3),
)


@st.composite
def _rubricas_validas(draw):
    cortes = sorted(draw(st.sets(st.integers(1, PESO_TOTAL - 1), min_size=4, max_size=4)))
    limites = [0, *cortes, PESO_TOTAL]
    pesos = [limites[i + 1] - limites[i] for i in range(NUM_CRITERIOS)]
    nomes = draw(st.lists(_nomes, min_size=NUM_CRITERIOS, max_size=NUM_CRITERIOS, unique=True))
    return dict(zip(nomes, pesos))


@st.composite
def _rubricas_arbitrarias(draw):
    n = draw(st.integers(min_value=0, max_value=8))
    nomes = draw(st.lists(_nomes, min_size=n, max_size=n, unique=True))
    pesos = draw(st.lists(_peso_qualquer, min_size=n, max_size=n))
    return dict(zip(nomes, pesos))


@st.composite
def _rubricas_quase_validas(draw):
    """Cinco critérios com pesos inteiros, soma e positividade ajustadas ao acaso."""
    nomes = draw(st.lists(_nomes, min_size=NUM_CRITERIOS, max_size=NUM_CRITERIOS, unique=True))
    pesos = draw(
        st.lists(st.integers(-5, 100), min_size=NUM_CRITERIOS, max_size=NUM_CRITERIOS)
    )
    return dict(zip(nomes, pesos))


def _esperado_valido(rubrica) -> bool:
    """Oráculo independente da implementação."""
    if len(rubrica) != NUM_CRITERIOS:
        return False
    pesos = list(rubrica.values())
    if not all(type(p) is int and p > 0 for p in pesos):
        return False
    return sum(pesos) == PESO_TOTAL


# Feature: ia-entrevistador, Property 5: Pesos da Rubrica
# **Validates: Requirements 4.2**
@settings(max_examples=200)
@given(st.one_of(_rubricas_validas(), _rubricas_arbitrarias(), _rubricas_quase_validas()))
def test_rubrica_valida_sse_cinco_criterios_pesos_inteiros_positivos_somando_100(rubrica):
    assert validar_rubrica(rubrica).valido == _esperado_valido(rubrica)


# Feature: ia-entrevistador, Property 5: Pesos da Rubrica
# **Validates: Requirements 4.2**
@settings(max_examples=100)
@given(_rubricas_validas())
def test_rubrica_gerada_com_pesos_corretos_e_aceita(rubrica):
    assert validar_rubrica(rubrica).valido
