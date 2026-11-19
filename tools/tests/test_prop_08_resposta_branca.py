"""Teste de propriedade: resposta em branco recebe nota 0 (Req. 4.6)."""

from decimal import Decimal

from hypothesis import given, settings, strategies as st

from tools.feedback import (
    MOTIVO_RESPOSTA_EM_BRANCO,
    avaliar_resposta_em_branco,
    resposta_em_branco,
)

_BRANCOS = [" ", "\t", "\n", "\r", "\r\n", "\u00a0", "\u2003", "\x0b", "\x0c"]

_em_branco = st.lists(st.sampled_from(_BRANCOS), min_size=0, max_size=30).map("".join)

_com_conteudo = st.builds(
    lambda pre, corpo, pos: pre + corpo + pos,
    st.lists(st.sampled_from(_BRANCOS), max_size=5).map("".join),
    st.text(alphabet="abcdefghijklmnopqrstuvwxyzÁÉ0123456789.,!?", min_size=1, max_size=40),
    st.lists(st.sampled_from(_BRANCOS), max_size=5).map("".join),
)


# Feature: ia-entrevistador, Property 8: Resposta em branco recebe nota 0
# **Validates: Requirements 4.6**
@settings(max_examples=100)
@given(resposta=_em_branco)
def test_resposta_em_branco_recebe_nota_zero(resposta):
    resultado = avaliar_resposta_em_branco(resposta)

    assert resposta_em_branco(resposta)
    assert resultado is not None
    assert resultado.nota_final == Decimal("0.0")
    assert resultado.motivo == MOTIVO_RESPOSTA_EM_BRANCO
    assert resultado.motivo.strip() != ""
    assert resultado.reenviar is True
    assert resultado.avanca is False


# Feature: ia-entrevistador, Property 8: Resposta em branco recebe nota 0
# **Validates: Requirements 4.6**
@settings(max_examples=100)
@given(resposta=_com_conteudo)
def test_resposta_com_conteudo_nao_e_em_branco(resposta):
    assert not resposta_em_branco(resposta)
    assert avaliar_resposta_em_branco(resposta) is None
