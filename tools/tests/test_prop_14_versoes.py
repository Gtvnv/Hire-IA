"""Teste de propriedade: histórico de versões do prompt (Req. 7.1, 7.2)."""

from hypothesis import given, settings, strategies as st

from tools.prompts_md import validar_historico_versoes, verificar_imutabilidade

_palavra = st.text(alphabet="abcdefghijklmnopqrstuvwxyzáéíóúãõç", min_size=1, max_size=10)
_texto = st.lists(_palavra, min_size=1, max_size=8).map(" ".join)
_campo = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz áéíóúç", min_size=1, max_size=500
).filter(lambda s: s.strip() == s and s != "")
_data = st.dates().map(lambda d: d.strftime("%Y-%m-%d"))
_versao = st.fixed_dictionaries(
    {"texto": _texto, "data": _data, "motivo": _campo, "resultado": _campo}
)
_versoes = st.lists(_versao, min_size=1, max_size=6)


def _prompt(n: int, texto: str) -> str:
    return f"## Prompt v{n}\n\n{texto}\n"


def _hist(n: int, v: dict) -> str:
    return (
        f"### v{n}\n"
        f"- **Data:** {v['data']}\n"
        f"- **Motivo:** {v['motivo']}\n"
        f"- **Resultado:** {v['resultado']}\n"
    )


def _md(versoes: list[dict], numeros: list[int] | None = None) -> str:
    numeros = numeros or list(range(1, len(versoes) + 1))
    prompts = "\n".join(_prompt(n, v["texto"]) for n, v in zip(numeros, versoes))
    hist = "\n".join(_hist(n, v) for n, v in zip(numeros, versoes))
    return f"# Prompt\n\n{prompts}\n## Histórico de versões\n\n{hist}"


# Feature: ia-entrevistador, Property 14: Histórico de versões
# **Validates: Requirements 7.1, 7.2**
@settings(max_examples=100, deadline=None)
@given(_versoes)
def test_historico_sem_lacunas_e_completo_e_valido(versoes):
    assert validar_historico_versoes(_md(versoes)).valido


# Feature: ia-entrevistador, Property 14: Histórico de versões
# **Validates: Requirements 7.1**
@settings(max_examples=100, deadline=None)
@given(_versoes.filter(lambda v: len(v) >= 2), st.data())
def test_historico_com_lacuna_e_invalido(versoes, data):
    k = len(versoes)
    # remove um identificador de v1..v(k+1), deixando uma lacuna
    ausente = data.draw(st.integers(1, k), label="ausente")
    numeros = [n for n in range(1, k + 2) if n != ausente]
    assert not validar_historico_versoes(_md(versoes, numeros)).valido


# Feature: ia-entrevistador, Property 14: Histórico de versões
# **Validates: Requirements 7.1**
@settings(max_examples=100, deadline=None)
@given(_versoes, st.sampled_from(["data", "motivo", "resultado"]), st.data())
def test_campo_invalido_e_rejeitado(versoes, campo, data):
    i = data.draw(st.integers(0, len(versoes) - 1), label="indice")
    ruim = {
        "data": data.draw(st.sampled_from(["2024-13-40", "01/02/2024", "x"])),
        "motivo": "a" * 501,
        "resultado": "a" * 501,
    }[campo]
    versoes[i] = {**versoes[i], campo: ruim}
    res = validar_historico_versoes(_md(versoes))
    assert not res.valido
    assert f"v{i + 1}.{campo}" in res.campos_invalidos


# Feature: ia-entrevistador, Property 14: Histórico de versões
# **Validates: Requirements 7.2**
@settings(max_examples=100, deadline=None)
@given(_versoes, _versao)
def test_nova_versao_preserva_anteriores(versoes, nova):
    anterior = _md(versoes)
    novo = _md(versoes + [nova])
    assert verificar_imutabilidade(anterior, novo).valido
    assert validar_historico_versoes(novo).valido


# Feature: ia-entrevistador, Property 14: Histórico de versões
# **Validates: Requirements 7.2**
@settings(max_examples=100, deadline=None)
@given(_versoes, _texto, st.data())
def test_alterar_versao_anterior_e_detectado(versoes, extra, data):
    i = data.draw(st.integers(0, len(versoes) - 1), label="indice")
    alterado = [dict(v) for v in versoes]
    alterado[i]["texto"] = versoes[i]["texto"] + " " + extra
    res = verificar_imutabilidade(_md(versoes), _md(alterado))
    assert not res.valido
    assert res.campos_invalidos == (f"v{i + 1}",)


# Feature: ia-entrevistador, Property 14: Histórico de versões
# **Validates: Requirements 7.2**
@settings(max_examples=100, deadline=None)
@given(_versoes.filter(lambda v: len(v) >= 2), st.data())
def test_remover_versao_anterior_e_detectado(versoes, data):
    i = data.draw(st.integers(0, len(versoes) - 1), label="indice")
    restantes = versoes[:i] + versoes[i + 1 :]
    res = verificar_imutabilidade(_md(versoes), _md(restantes))
    assert not res.valido
