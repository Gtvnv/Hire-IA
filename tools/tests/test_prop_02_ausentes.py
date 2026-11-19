"""Teste de propriedade: campos obrigatórios ausentes (Req. 1.4, 2.8)."""

import copy

from hypothesis import given, settings, strategies as st

from tools.perfil import AUSENTE, CAMPOS_OBRIGATORIOS, SENIORIDADES, validar_perfil

_texto = st.text(
    alphabet=st.characters(blacklist_categories=("Cs",)), min_size=1, max_size=50
).filter(lambda s: s.strip() != "")

_valores_validos = {
    "cargo": _texto,
    "senioridade": st.sampled_from(SENIORIDADES),
}

# Como o campo ausente se manifesta: omitido, None ou só com espaços.
_forma_ausencia = st.sampled_from(["omitido", "none", "espacos"])


@st.composite
def _perfis(draw):
    ausentes = draw(st.sets(st.sampled_from(CAMPOS_OBRIGATORIOS)))
    perfil = {}
    for campo in CAMPOS_OBRIGATORIOS:
        if campo in ausentes:
            forma = draw(_forma_ausencia)
            if forma == "none":
                perfil[campo] = None
            elif forma == "espacos":
                perfil[campo] = draw(st.text(alphabet=" \t\n", max_size=5))
        else:
            perfil[campo] = draw(_valores_validos[campo])
    if draw(st.booleans()):
        perfil["tecnologias"] = draw(
            st.lists(st.text(min_size=1, max_size=50), max_size=20)
        )
    if draw(st.booleans()):
        perfil["descricao_da_vaga"] = draw(st.text(min_size=1, max_size=200))
    return perfil, ausentes


# Feature: ia-entrevistador, Property 2: Campos obrigatórios ausentes são todos listados
# **Validates: Requirements 1.4, 2.8**
@settings(max_examples=100)
@given(_perfis())
def test_campos_obrigatorios_ausentes_sao_todos_listados(dados):
    perfil, ausentes = dados
    original = copy.deepcopy(perfil)

    resultado = validar_perfil(perfil)

    # Lista exatamente os campos ausentes.
    assert set(resultado.campos_ausentes) == ausentes
    assert len(resultado.campos_ausentes) == len(ausentes)
    for campo in ausentes:
        assert campo in resultado.mensagem
    for campo in set(CAMPOS_OBRIGATORIOS) - ausentes:
        assert campo not in resultado.campos_invalidos
    assert all(e.tipo == AUSENTE for e in resultado.erros)
    assert resultado.valido == (not ausentes)

    # Campos informados permanecem inalterados.
    assert perfil == original
