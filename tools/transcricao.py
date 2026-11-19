"""Validação das mensagens do Entrevistador_Simulado (Req. 3.2, 3.3, 3.4).

Funções puras: não alteram a entrada e devolvem todas as violações de uma vez.

Modelo da transcrição: sequência de ``Mensagem`` em ordem cronológica. Cada
mensagem do entrevistador é uma pergunta ``NOVA`` ou de ``APROFUNDAMENTO``
(sobre a resposta anterior do candidato). Mensagens do candidato não reiniciam
a contagem de aprofundamentos; apenas uma pergunta nova a reinicia.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable

PAPEL_ENTREVISTADOR = "entrevistador"
PAPEL_CANDIDATO = "candidato"

TIPO_NOVA = "nova"
TIPO_APROFUNDAMENTO = "aprofundamento"

MAX_PERGUNTAS_POR_MENSAGEM = 1
MAX_APROFUNDAMENTOS_CONSECUTIVOS = 1

# Faixas Unicode usadas por emojis, pictogramas, símbolos e seletores.
_EMOJI_RE = re.compile(
    "["
    "\U0001F000-\U0001FAFF"  # pictogramas, emoticons, transporte, suplementares
    "\U0001F1E6-\U0001F1FF"  # bandeiras (indicadores regionais)
    "\u2600-\u27BF"  # símbolos diversos e dingbats
    "\u2300-\u23FF"  # símbolos técnicos diversos (relógios, etc.)
    "\u2B00-\u2BFF"  # setas e símbolos diversos (estrelas)
    "\u2190-\u21FF"  # setas (↩ ↪ etc.)
    "\u2900-\u297F"  # setas suplementares
    "\u3030\u303D\u3297\u3299"
    "\u00A9\u00AE\u203C\u2049\u2122\u2139\u24C2\u25AA-\u25FE"
    "\u200D\u20E3\uFE0F"  # ZWJ, keycap, seletor de variação
    "]"
)

_PERGUNTA_RE = re.compile(r"[?\uFF1F\u061F\u2753\u2754]")


@dataclass(frozen=True)
class Mensagem:
    papel: str
    texto: str
    tipo: str | None = None  # TIPO_NOVA ou TIPO_APROFUNDAMENTO (só entrevistador)


@dataclass(frozen=True)
class ViolacaoTranscricao:
    indice: int
    regra: str  # "perguntas", "emoji" ou "aprofundamento"
    mensagem: str


@dataclass(frozen=True)
class ResultadoTranscricao:
    violacoes: tuple[ViolacaoTranscricao, ...] = field(default_factory=tuple)

    @property
    def valido(self) -> bool:
        return not self.violacoes


def contar_perguntas(texto: str) -> int:
    """Conta as perguntas da mensagem (cada ponto de interrogação, em qualquer
    variante, encerra uma pergunta)."""
    return len(_PERGUNTA_RE.findall(texto))


def contem_emoji(texto: str) -> bool:
    return _EMOJI_RE.search(texto) is not None


def validar_mensagem(texto: str, indice: int = 0) -> tuple[ViolacaoTranscricao, ...]:
    """Valida uma mensagem isolada: no máximo uma pergunta e nenhum emoji."""
    violacoes: list[ViolacaoTranscricao] = []
    n = contar_perguntas(texto)
    if n > MAX_PERGUNTAS_POR_MENSAGEM:
        violacoes.append(
            ViolacaoTranscricao(
                indice,
                "perguntas",
                f"A mensagem contém {n} perguntas; o máximo é {MAX_PERGUNTAS_POR_MENSAGEM}.",
            )
        )
    if contem_emoji(texto):
        violacoes.append(
            ViolacaoTranscricao(indice, "emoji", "A mensagem contém emoji.")
        )
    return tuple(violacoes)


def validar_transcricao(mensagens: Iterable[Mensagem]) -> ResultadoTranscricao:
    """Valida toda a transcrição.

    Regras sobre as mensagens do entrevistador: no máximo uma pergunta, nenhum
    emoji e no máximo uma pergunta de aprofundamento consecutiva.
    """
    violacoes: list[ViolacaoTranscricao] = []
    aprofundamentos = 0
    for i, msg in enumerate(mensagens):
        if msg.papel != PAPEL_ENTREVISTADOR:
            continue
        violacoes.extend(validar_mensagem(msg.texto, i))
        if msg.tipo == TIPO_APROFUNDAMENTO:
            aprofundamentos += 1
            if aprofundamentos > MAX_APROFUNDAMENTOS_CONSECUTIVOS:
                violacoes.append(
                    ViolacaoTranscricao(
                        i,
                        "aprofundamento",
                        "Mais de uma pergunta de aprofundamento consecutiva "
                        "sobre a mesma resposta.",
                    )
                )
        else:
            aprofundamentos = 0
    return ResultadoTranscricao(tuple(violacoes))
