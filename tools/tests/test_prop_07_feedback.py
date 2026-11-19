"""Teste de propriedade: estrutura do Feedback (Req. 4.4, 4.5, 4.7, 9.2)."""

import copy

from hypothesis import given, settings, strategies as st

from tools.feedback import (
    AVISO_MAX,
    ELEMENTOS_STAR,
    RUBRICA_PADRAO,
    TEXTO_MAX,
    calcular_nota_final,
    validar_feedback,
)

_palavra = st.text(alphabet="abcdefghijklmnopqrstuvwxyzáéíóãç", min_size=1, max_size=12)


def _frase(draw_words):
    return " ".join(draw_words).capitalize() + "."


_frase_st = st.lists(_palavra, min_size=1, max_size=8).map(_frase)


def _texto(min_frases, max_frases):
    return st.lists(_frase_st, min_size=min_frases, max_size=max_frases).map(" ".join)


_justificativa = _texto(1, 3)
_texto_longo = _texto(1, 5)  # bem abaixo de 1.000 caracteres
_aviso = st.text(
    alphabet=st.characters(blacklist_categories=("Cs", "Cc")), min_size=1, max_size=AVISO_MAX
).filter(lambda s: s.strip() != "")
_itens = st.one_of(_texto_longo, st.lists(_texto_longo, min_size=1, max_size=3))


@st.composite
def _feedbacks(draw):
    comportamental = draw(st.booleans())
    notas = {c: draw(st.integers(0, 10)) for c in RUBRICA_PADRAO}
    fb = {
        "notas_por_criterio": notas,
        "justificativas": {c: draw(_justificativa) for c in RUBRICA_PADRAO},
        "nota_final": calcular_nota_final(RUBRICA_PADRAO, notas),
        "pontos_fortes": draw(_itens),
        "pontos_de_melhoria": draw(_itens),
        "resposta_sugerida": draw(_texto_longo),
        "aviso": draw(_aviso),
    }
    if comportamental or draw(st.booleans()):
        fb["verificacao_star"] = {e: draw(st.booleans()) for e in ELEMENTOS_STAR}
    return fb, comportamental


def _campos(resultado):
    return {c.split(".")[0].split("[")[0] for c in resultado.campos_invalidos}


# Feature: ia-entrevistador, Property 7: Estrutura do Feedback
@settings(max_examples=100, deadline=None)
@given(_feedbacks())
def test_feedback_bem_formado_e_valido(par):
    """**Validates: Requirements 4.4, 4.5, 4.7, 9.2**"""
    fb, comportamental = par
    assert validar_feedback(fb, RUBRICA_PADRAO, comportamental).valido


# Feature: ia-entrevistador, Property 7: Estrutura do Feedback
@settings(max_examples=100, deadline=None)
@given(
    _feedbacks(),
    st.sampled_from(
        [
            "nota_fora_da_faixa",
            "justificativa_sem_frase",
            "justificativa_com_4_frases",
            "sem_pontos_fortes",
            "sem_pontos_de_melhoria",
            "sem_resposta_sugerida",
            "resposta_sugerida_longa",
            "sem_aviso",
            "aviso_longo",
            "sem_star",
        ]
    ),
    st.data(),
)
def test_feedback_malformado_e_rejeitado(par, defeito, data):
    """**Validates: Requirements 4.4, 4.5, 4.7, 9.2**"""
    fb, comportamental = copy.deepcopy(par[0]), par[1]
    criterio = data.draw(st.sampled_from(list(RUBRICA_PADRAO)))
    esperado = None

    if defeito == "nota_fora_da_faixa":
        fb["notas_por_criterio"][criterio] = data.draw(st.sampled_from([-1, 11, 100]))
        esperado = "notas_por_criterio"
    elif defeito == "justificativa_sem_frase":
        fb["justificativas"][criterio] = data.draw(st.sampled_from(["", "   ", "..."]))
        esperado = "justificativas"
    elif defeito == "justificativa_com_4_frases":
        fb["justificativas"][criterio] = data.draw(_texto(4, 6))
        esperado = "justificativas"
    elif defeito == "sem_pontos_fortes":
        fb["pontos_fortes"] = data.draw(st.sampled_from([[], "", None]))
        esperado = "pontos_fortes"
    elif defeito == "sem_pontos_de_melhoria":
        del fb["pontos_de_melhoria"]
        esperado = "pontos_de_melhoria"
    elif defeito == "sem_resposta_sugerida":
        fb["resposta_sugerida"] = data.draw(st.sampled_from(["", "  ", None]))
        esperado = "resposta_sugerida"
    elif defeito == "resposta_sugerida_longa":
        fb["resposta_sugerida"] = ("Palavra " * TEXTO_MAX)[: TEXTO_MAX + 1 + data.draw(st.integers(0, 50))]
        esperado = "resposta_sugerida"
    elif defeito == "sem_aviso":
        fb["aviso"] = data.draw(st.sampled_from(["", "   ", None]))
        esperado = "aviso"
    elif defeito == "aviso_longo":
        fb["aviso"] = "a" * (AVISO_MAX + data.draw(st.integers(1, 100)))
        esperado = "aviso"
    elif defeito == "sem_star":
        comportamental = True
        fb.pop("verificacao_star", None)
        esperado = "verificacao_star"

    resultado = validar_feedback(fb, RUBRICA_PADRAO, comportamental)
    assert not resultado.valido
    assert esperado in _campos(resultado)
