"""Teste de propriedade: resultado de cenário de teste (Req. 10.4, 10.6)."""

from hypothesis import given, settings, strategies as st

from tools.docs_md import ITEM_COMPORTAMENTO, resultado_cenario

_nome = st.text(alphabet="abcdefghijklmnopqrstuvwxyz ", min_size=1, max_size=12)
_checklist = st.dictionaries(_nome, st.booleans(), max_size=8)
# Verificações com prefixo distinto evitam colisão de nomes com o checklist.
_verificacoes = st.dictionaries(_nome.map(lambda s: "v:" + s), st.booleans(), max_size=8)


# Feature: ia-entrevistador, Property 16: Resultado de cenário de teste
# **Validates: Requirements 10.4, 10.6**
@settings(max_examples=200)
@given(_checklist, _verificacoes, st.booleans())
def test_resultado_cenario(checklist, verificacoes, diverge):
    r = resultado_cenario(checklist, verificacoes, diverge)

    esperados = {n for n, ok in checklist.items() if not ok}
    esperados |= {n for n, ok in verificacoes.items() if not ok}
    if diverge:
        esperados.add(ITEM_COMPORTAMENTO)

    # Reprovado se e somente se há ao menos um item/verificação reprovado ou divergência.
    assert r.reprovado == bool(esperados)
    # Itens reprovados listados, sem repetição e sem aprovados.
    assert set(r.itens_reprovados) == esperados
    assert len(r.itens_reprovados) == len(set(r.itens_reprovados))
    if not r.reprovado:
        assert r.itens_reprovados == ()
