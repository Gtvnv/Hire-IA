"""Teste de propriedade: formato das mensagens do entrevistador (Req. 3.2, 3.3, 3.4)."""

from hypothesis import given, settings, strategies as st

from tools.transcricao import (
    PAPEL_CANDIDATO,
    PAPEL_ENTREVISTADOR,
    TIPO_APROFUNDAMENTO,
    TIPO_NOVA,
    Mensagem,
    validar_transcricao,
)

_EMOJIS = ["😀", "🚀", "👍", "🎉", "✅", "❤️", "⭐", "🇧🇷", "👨‍💻", "1️⃣", "⏰", "➡️"]

_palavra = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyzáéíóúãõç", min_size=1, max_size=8
)
_trecho = st.lists(_palavra, min_size=1, max_size=6).map(" ".join)


@st.composite
def _texto_entrevistador(draw):
    """Texto com 0..3 perguntas e 0..2 emojis em posições arbitrárias."""
    n_perg = draw(st.integers(0, 3))
    emojis = draw(st.lists(st.sampled_from(_EMOJIS), max_size=2))
    partes = [draw(_trecho) + "?" for _ in range(n_perg)]
    if not partes:
        partes = [draw(_trecho) + "."]
    for e in emojis:
        partes.insert(draw(st.integers(0, len(partes))), e)
    return " ".join(partes), n_perg, len(emojis) > 0


@st.composite
def _mensagem(draw):
    if draw(st.booleans()):
        texto, n_perg, tem_emoji = draw(_texto_entrevistador())
        tipo = draw(st.sampled_from([TIPO_NOVA, TIPO_APROFUNDAMENTO]))
        return Mensagem(PAPEL_ENTREVISTADOR, texto, tipo), n_perg, tem_emoji
    texto = draw(_trecho) + draw(st.sampled_from(["?", "??", "", " 😀"]))
    return Mensagem(PAPEL_CANDIDATO, texto), 0, False


_transcricao = st.lists(_mensagem(), min_size=0, max_size=12)


def _esperado(itens):
    """Violações esperadas, calculadas independentemente do módulo."""
    esperado = set()
    seguidos = 0
    for i, (msg, n_perg, tem_emoji) in enumerate(itens):
        if msg.papel != PAPEL_ENTREVISTADOR:
            continue
        if n_perg > 1:
            esperado.add((i, "perguntas"))
        if tem_emoji:
            esperado.add((i, "emoji"))
        if msg.tipo == TIPO_APROFUNDAMENTO:
            seguidos += 1
            if seguidos > 1:
                esperado.add((i, "aprofundamento"))
        else:
            seguidos = 0
    return esperado


# Feature: ia-entrevistador, Property 12: Regras de formato das mensagens do entrevistador
# **Validates: Requirements 3.2, 3.3, 3.4**
@settings(max_examples=200)
@given(itens=_transcricao)
def test_formato_das_mensagens_do_entrevistador(itens):
    mensagens = [m for m, _, _ in itens]
    resultado = validar_transcricao(mensagens)

    obtido = {(v.indice, v.regra) for v in resultado.violacoes}
    esperado = _esperado(itens)

    assert obtido == esperado
    assert resultado.valido == (not esperado)
    # Mensagens do candidato nunca geram violações.
    for v in resultado.violacoes:
        assert mensagens[v.indice].papel == PAPEL_ENTREVISTADOR


# Feature: ia-entrevistador, Property 12: Regras de formato das mensagens do entrevistador
# **Validates: Requirements 3.2, 3.3, 3.4**
@settings(max_examples=100)
@given(
    textos=st.lists(_texto_entrevistador(), min_size=1, max_size=6),
    candidato=_trecho,
)
def test_transcricao_conforme_e_valida(textos, candidato):
    """Transcrição conforme (1 pergunta, sem emoji, aprofundamento isolado) é válida."""
    mensagens = []
    for k, (texto, _, _) in enumerate(textos):
        limpo = "".join(c for c in texto if c not in "".join(_EMOJIS))
        limpo = limpo.replace("?", ".") + "?"
        tipo = TIPO_APROFUNDAMENTO if k % 2 else TIPO_NOVA
        mensagens.append(Mensagem(PAPEL_ENTREVISTADOR, limpo, tipo))
        mensagens.append(Mensagem(PAPEL_CANDIDATO, candidato))
    assert validar_transcricao(mensagens).valido
