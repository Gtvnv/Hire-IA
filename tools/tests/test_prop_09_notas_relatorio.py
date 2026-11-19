"""Teste de propriedade: notas do Relatório_Final (Req. 5.1)."""

import math
from decimal import Decimal
from fractions import Fraction

from hypothesis import given, settings, strategies as st

from tools.relatorio import (
    RespostaAvaliada,
    calcular_nota_geral,
    calcular_notas_por_categoria,
)

_CATEGORIAS = ["Python", "SQL", "Arquitetura", "Comportamental", "Redes"]

# Nota final de 0 a 10 com uma casa decimal (décimos inteiros de 0 a 100).
_notas = st.integers(0, 100).map(lambda d: Decimal(d) / 10)

_respostas = st.lists(
    st.builds(RespostaAvaliada, categoria=st.sampled_from(_CATEGORIAS), nota=_notas),
    min_size=0,
    max_size=30,
)


def _media_oraculo(notas) -> Decimal:
    """Média exata (Fraction) com round-half-up a uma casa, sem Decimal quantize."""
    exata = sum((Fraction(n) for n in notas), Fraction(0)) / len(notas)
    decimos = math.floor(exata * 10 + Fraction(1, 2))
    return Decimal(decimos) / 10


# Feature: ia-entrevistador, Property 9: Notas do Relatório_Final
# **Validates: Requirements 5.1**
@settings(max_examples=200, deadline=None)
@given(respostas=_respostas)
def test_notas_do_relatorio_final(respostas):
    geral = calcular_nota_geral(respostas)
    por_categoria = calcular_notas_por_categoria(respostas)

    if not respostas:
        assert geral is None
        assert por_categoria == {}
        return

    # Nota geral: média aritmética de todas as notas, uma casa decimal.
    assert geral == _media_oraculo([r.nota for r in respostas])
    assert geral.as_tuple().exponent == -1
    assert Decimal(0) <= geral <= Decimal(10)

    # Notas por categoria: somente categorias com ao menos uma resposta.
    esperado = {}
    for r in respostas:
        esperado.setdefault(r.categoria, []).append(r.nota)
    assert set(por_categoria) == set(esperado)
    for cat, notas in esperado.items():
        assert por_categoria[cat] == _media_oraculo(notas)
        assert por_categoria[cat].as_tuple().exponent == -1
