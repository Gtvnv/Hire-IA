"""Teste de propriedade: nota final ponderada (Req. 4.3)."""

import math
from decimal import Decimal
from fractions import Fraction

from hypothesis import given, settings, strategies as st

from tools.feedback import calcular_nota_final, conferir_nota_final

_NOMES = ["C1", "C2", "C3", "C4", "C5"]


@st.composite
def _rubricas(draw):
    """Rubrica válida: cinco pesos inteiros > 0 somando 100."""
    cortes = sorted(draw(st.sets(st.integers(1, 99), min_size=4, max_size=4)))
    limites = [0, *cortes, 100]
    pesos = [limites[i + 1] - limites[i] for i in range(5)]
    return dict(zip(_NOMES, pesos))


_notas = st.fixed_dictionaries({n: st.integers(0, 10) for n in _NOMES})


def _oraculo(rubrica, notas) -> Fraction:
    """Nota esperada, calculada com Fraction: round-half-up de soma/100 a 1 casa."""
    exata = sum(Fraction(rubrica[n]) * notas[n] for n in rubrica) / 100
    return Fraction(math.floor(exata * 10 + Fraction(1, 2)), 10)


# Feature: ia-entrevistador, Property 6: Nota final ponderada
# **Validates: Requirements 4.3**
@settings(max_examples=200, deadline=None)
@given(rubrica=_rubricas(), notas=_notas)
def test_nota_final_ponderada(rubrica, notas):
    esperada = _oraculo(rubrica, notas)
    nota = calcular_nota_final(rubrica, notas)

    assert Fraction(nota) == esperada
    assert Decimal(0) <= nota <= Decimal(10)
    assert nota.as_tuple().exponent == -1  # uma casa decimal

    # A nota informada igual à calculada é aceita, em várias representações.
    assert conferir_nota_final(rubrica, notas, nota)
    assert conferir_nota_final(rubrica, notas, str(nota))
    assert conferir_nota_final(rubrica, notas, float(esperada))

    # Uma nota diferente (±0,1) é rejeitada.
    for delta in (Fraction(1, 10), Fraction(-1, 10)):
        outra = esperada + delta
        if 0 <= outra <= 10:
            assert not conferir_nota_final(rubrica, notas, str(Decimal(outra.numerator) / Decimal(outra.denominator)))
