"""Teste de propriedade da validação do Perfil_da_Vaga.

Feature: ia-entrevistador, Property 1: Validação do Perfil_da_Vaga

**Validates: Requirements 1.1, 1.2, 1.6**
"""

from __future__ import annotations

from hypothesis import given, settings, strategies as st

from tools.perfil import SENIORIDADES, validar_perfil

# Palavra-chave que a mensagem deve citar para cada campo inválido (sem diferenciar caixa).
PALAVRA_CHAVE = {
    "cargo": "cargo",
    "senioridade": "senioridade",
    "tecnologias": "tecnologias",
    "descricao_da_vaga": "descrição da vaga",
}

_ALFABETO = st.characters(whitelist_categories=("Ll", "Lu", "Nd"))


def _texto(tamanhos: list[int]) -> st.SearchStrategy[str]:
    """Texto sem espaços com tamanho nos limites (ou aleatório próximo deles)."""
    return st.one_of(
        st.sampled_from(tamanhos).map(lambda n: "a" * n),
        st.text(_ALFABETO, min_size=0, max_size=tamanhos[-1] + 3),
    )


cargos = _texto([0, 1, 100, 101])
senioridades = st.one_of(
    st.sampled_from(SENIORIDADES),
    st.sampled_from(["", "pleno", "Trainee", "Senior", "Júnior "]),
)
itens_tecnologia = _texto([0, 1, 50, 51])
tecnologias = st.one_of(
    st.none(),
    st.sampled_from([0, 1, 19, 20, 21]).flatmap(
        lambda n: st.lists(itens_tecnologia, min_size=n, max_size=n)
    ),
    st.lists(itens_tecnologia, min_size=0, max_size=21),
)
descricoes = st.one_of(
    st.none(),
    _texto([0, 1, 5000, 5001]),
)


@st.composite
def perfis(draw):
    perfil = {
        "cargo": draw(cargos),
        "senioridade": draw(senioridades),
    }
    tec = draw(tecnologias)
    if tec is not None:
        perfil["tecnologias"] = tec
    desc = draw(descricoes)
    if desc is not None:
        perfil["descricao_da_vaga"] = desc
    return perfil


def _campos_invalidos_esperados(perfil: dict) -> set[str]:
    """Oráculo independente da implementação, direto da propriedade do design."""
    esperados: set[str] = set()
    if not 1 <= len(perfil["cargo"]) <= 100:
        esperados.add("cargo")
    if perfil["senioridade"] not in SENIORIDADES:
        esperados.add("senioridade")
    tec = perfil.get("tecnologias")
    if tec is not None:
        if len(tec) > 20:
            esperados.add("tecnologias")
        for i, item in enumerate(tec):
            if not 1 <= len(item) <= 50:
                esperados.add(f"tecnologias[{i}]")
    desc = perfil.get("descricao_da_vaga")
    if desc is not None and not 1 <= len(desc) <= 5000:
        esperados.add("descricao_da_vaga")
    return esperados


@settings(max_examples=200, deadline=None)
@given(perfis())
def test_perfil_aceito_se_e_somente_se_dentro_dos_limites(perfil):
    resultado = validar_perfil(perfil)
    esperados = _campos_invalidos_esperados(perfil)

    # aceita se e somente se não há campo inválido
    assert resultado.valido == (not esperados)

    # todos os campos inválidos são reportados de uma vez, e nenhum a mais
    assert set(resultado.campos_invalidos) == esperados

    # a mensagem cita todos os campos inválidos
    mensagem = resultado.mensagem.lower()
    for campo in esperados:
        base = campo.split("[")[0]
        assert PALAVRA_CHAVE[base] in mensagem, (campo, resultado.mensagem)
    if not esperados:
        assert resultado.mensagem == ""


@settings(max_examples=100, deadline=None)
@given(
    st.sampled_from([0, 1, 100, 101]),
    st.sampled_from(SENIORIDADES),
    st.sampled_from([0, 1, 20, 21]),
    st.sampled_from([None, 0, 1, 5000, 5001]),
)
def test_limites_exatos(n_cargo, senioridade, n_tec, n_desc):
    perfil = {
        "cargo": "a" * n_cargo,
        "senioridade": senioridade,
        "tecnologias": ["t"] * n_tec,
    }
    if n_desc is not None:
        perfil["descricao_da_vaga"] = "d" * n_desc
    resultado = validar_perfil(perfil)
    esperado_valido = (
        1 <= n_cargo <= 100 and n_tec <= 20 and (n_desc is None or 1 <= n_desc <= 5000)
    )
    assert resultado.valido == esperado_valido
