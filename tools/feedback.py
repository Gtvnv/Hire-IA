"""Rubrica, nota final ponderada e estrutura do Feedback (Req. 4.2 a 4.7, 9.2).

Funções puras: não alteram a entrada e devolvem todos os erros de uma vez.
O cálculo da nota usa aritmética inteira/Decimal com arredondamento
ROUND_HALF_UP, sem passar por float.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping

NUM_CRITERIOS = 5
PESO_TOTAL = 100
NOTA_MIN = 0
NOTA_MAX = 10

TEXTO_MAX = 1000
AVISO_MAX = 200
JUSTIFICATIVA_MIN_FRASES = 1
JUSTIFICATIVA_MAX_FRASES = 3

ELEMENTOS_STAR = ("Situação", "Tarefa", "Ação", "Resultado")

RUBRICA_PADRAO: Mapping[str, int] = {
    "Correção técnica": 30,
    "Clareza": 20,
    "Profundidade": 20,
    "Estrutura da resposta": 15,
    "Exemplos práticos": 15,
}

MOTIVO_RESPOSTA_EM_BRANCO = (
    "A resposta está vazia ou em branco. Envie novamente a resposta para a mesma pergunta."
)


@dataclass(frozen=True)
class ErroFeedback:
    campo: str
    mensagem: str


@dataclass(frozen=True)
class ResultadoValidacao:
    erros: tuple[ErroFeedback, ...] = field(default_factory=tuple)

    @property
    def valido(self) -> bool:
        return not self.erros

    @property
    def campos_invalidos(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(e.campo for e in self.erros))


@dataclass(frozen=True)
class RespostaEmBranco:
    """Resultado da regra de resposta em branco (Req. 4.6)."""

    nota_final: Decimal
    motivo: str
    reenviar: bool
    avanca: bool


def _inteiro(valor: Any) -> bool:
    return isinstance(valor, int) and not isinstance(valor, bool)


def _decimal(valor: Any) -> Decimal | None:
    if isinstance(valor, bool) or valor is None:
        return None
    try:
        d = Decimal(valor) if isinstance(valor, (int, Decimal)) else Decimal(str(valor))
    except (InvalidOperation, ValueError):
        return None
    return d if d.is_finite() else None


# --------------------------------------------------------------------------- Rubrica


def validar_rubrica(rubrica: Mapping[str, Any]) -> ResultadoValidacao:
    """Cinco critérios nomeados, pesos inteiros > 0 que somam 100 (Req. 4.2)."""
    erros: list[ErroFeedback] = []
    if len(rubrica) != NUM_CRITERIOS:
        erros.append(
            ErroFeedback(
                "rubrica",
                f"A Rubrica deve ter {NUM_CRITERIOS} critérios (informado: {len(rubrica)}).",
            )
        )
    pesos_ok = True
    for nome, peso in rubrica.items():
        if not isinstance(nome, str) or nome.strip() == "":
            erros.append(ErroFeedback("rubrica", "Todo critério deve ter um nome não vazio."))
        if not _inteiro(peso) or peso <= 0:
            pesos_ok = False
            erros.append(
                ErroFeedback(f"rubrica.{nome}", f"O peso de '{nome}' deve ser inteiro e maior que 0.")
            )
    if pesos_ok and sum(rubrica.values()) != PESO_TOTAL:
        erros.append(
            ErroFeedback(
                "rubrica",
                f"Os pesos devem somar {PESO_TOTAL} (soma atual: {sum(rubrica.values())}).",
            )
        )
    return ResultadoValidacao(tuple(erros))


# ----------------------------------------------------------------------- Nota final


def calcular_nota_final(rubrica: Mapping[str, int], notas: Mapping[str, int]) -> Decimal:
    """round1(soma(peso × nota) / 100) com ROUND_HALF_UP, de forma exata.

    Levanta ValueError se a Rubrica for inválida ou se as notas não forem
    inteiros de 0 a 10, um por critério da Rubrica.
    """
    if not validar_rubrica(rubrica).valido:
        raise ValueError("Rubrica inválida.")
    if set(notas) != set(rubrica):
        raise ValueError("As notas devem cobrir exatamente os critérios da Rubrica.")
    for nome, nota in notas.items():
        if not _inteiro(nota) or not NOTA_MIN <= nota <= NOTA_MAX:
            raise ValueError(f"A nota de '{nome}' deve ser inteira de {NOTA_MIN} a {NOTA_MAX}.")
    soma = sum(rubrica[c] * notas[c] for c in rubrica)  # inteiro; valor real = soma / 100
    # soma/100 arredondado a 1 casa, meio para cima: floor((soma + 5) / 10) / 10
    return Decimal((soma + 5) // 10).scaleb(-1)


def conferir_nota_final(
    rubrica: Mapping[str, int], notas: Mapping[str, int], nota_informada: Any
) -> bool:
    """Verdadeiro se a nota informada é igual à nota final calculada."""
    informada = _decimal(nota_informada)
    if informada is None:
        return False
    try:
        return informada == calcular_nota_final(rubrica, notas)
    except ValueError:
        return False


# ---------------------------------------------------------------------- Frases/texto

_FIM_DE_FRASE = re.compile(r"[.!?…]+(?=\s|$)")


def contar_frases(texto: str) -> int:
    """Conta frases: trechos não vazios separados por . ! ? … seguidos de espaço ou fim."""
    partes = _FIM_DE_FRASE.split(texto)
    return sum(1 for p in partes if re.search(r"\w", p))


def _validar_texto(campo: str, valor: Any, erros: list[ErroFeedback]) -> None:
    if not isinstance(valor, str) or contar_frases(valor) < 1:
        erros.append(ErroFeedback(campo, f"{campo} deve ter ao menos 1 frase."))
    elif len(valor) > TEXTO_MAX:
        erros.append(ErroFeedback(campo, f"{campo} excede {TEXTO_MAX} caracteres."))


def _validar_itens(campo: str, valor: Any, erros: list[ErroFeedback]) -> None:
    """Aceita um texto ou uma lista não vazia de textos."""
    if isinstance(valor, str):
        _validar_texto(campo, valor, erros)
    elif isinstance(valor, (list, tuple)) and len(valor) > 0:
        for i, item in enumerate(valor):
            _validar_texto(f"{campo}[{i}]", item, erros)
    else:
        erros.append(ErroFeedback(campo, f"{campo} deve ter ao menos um item."))


# ------------------------------------------------------------------------- Feedback


def validar_feedback(
    feedback: Mapping[str, Any],
    rubrica: Mapping[str, int] = RUBRICA_PADRAO,
    comportamental: bool = False,
) -> ResultadoValidacao:
    """Valida a estrutura do Feedback (Req. 4.4, 4.5, 4.7, 9.2).

    Campos: notas_por_criterio, justificativas, nota_final, pontos_fortes,
    pontos_de_melhoria, resposta_sugerida, verificacao_star (obrigatória só se
    `comportamental`) e aviso (até 200 caracteres).
    """
    erros: list[ErroFeedback] = []
    erros.extend(validar_rubrica(rubrica).erros)
    criterios = set(rubrica)

    notas = feedback.get("notas_por_criterio")
    notas_validas = False
    if not isinstance(notas, Mapping) or set(notas) != criterios:
        erros.append(
            ErroFeedback("notas_por_criterio", "Deve haver uma nota por critério da Rubrica.")
        )
    else:
        notas_validas = True
        for nome, nota in notas.items():
            if not _inteiro(nota) or not NOTA_MIN <= nota <= NOTA_MAX:
                notas_validas = False
                erros.append(
                    ErroFeedback(
                        f"notas_por_criterio.{nome}",
                        f"A nota de '{nome}' deve ser inteira de {NOTA_MIN} a {NOTA_MAX}.",
                    )
                )

    justificativas = feedback.get("justificativas")
    if not isinstance(justificativas, Mapping) or set(justificativas) != criterios:
        erros.append(ErroFeedback("justificativas", "Deve haver uma justificativa por critério."))
    else:
        for nome, texto in justificativas.items():
            n = contar_frases(texto) if isinstance(texto, str) else 0
            if not JUSTIFICATIVA_MIN_FRASES <= n <= JUSTIFICATIVA_MAX_FRASES:
                erros.append(
                    ErroFeedback(
                        f"justificativas.{nome}",
                        f"A justificativa de '{nome}' deve ter de {JUSTIFICATIVA_MIN_FRASES} "
                        f"a {JUSTIFICATIVA_MAX_FRASES} frases.",
                    )
                )

    nota_final = feedback.get("nota_final")
    if _decimal(nota_final) is None:
        erros.append(ErroFeedback("nota_final", "A nota final é obrigatória e deve ser numérica."))
    elif notas_validas and validar_rubrica(rubrica).valido:
        if not conferir_nota_final(rubrica, notas, nota_final):  # type: ignore[arg-type]
            esperada = calcular_nota_final(rubrica, notas)  # type: ignore[arg-type]
            erros.append(
                ErroFeedback("nota_final", f"A nota final deveria ser {esperada} (nota informada: {nota_final}).")
            )

    _validar_itens("pontos_fortes", feedback.get("pontos_fortes"), erros)
    _validar_itens("pontos_de_melhoria", feedback.get("pontos_de_melhoria"), erros)
    _validar_texto("resposta_sugerida", feedback.get("resposta_sugerida"), erros)

    star = feedback.get("verificacao_star")
    if comportamental:
        if (
            not isinstance(star, Mapping)
            or set(star) != set(ELEMENTOS_STAR)
            or not all(isinstance(v, bool) for v in star.values())
        ):
            erros.append(
                ErroFeedback(
                    "verificacao_star",
                    "Pergunta comportamental exige o estado (presente/ausente) de "
                    + ", ".join(ELEMENTOS_STAR)
                    + ".",
                )
            )

    aviso = feedback.get("aviso")
    if not isinstance(aviso, str) or aviso.strip() == "":
        erros.append(ErroFeedback("aviso", "O aviso de estimativa é obrigatório."))
    elif len(aviso) > AVISO_MAX:
        erros.append(ErroFeedback("aviso", f"O aviso excede {AVISO_MAX} caracteres."))

    return ResultadoValidacao(tuple(erros))


# ---------------------------------------------------------------- Resposta em branco


def resposta_em_branco(resposta: Any) -> bool:
    """Verdadeiro para None, vazio ou só com espaços, tabs e quebras de linha."""
    return resposta is None or (isinstance(resposta, str) and resposta.strip() == "")


def avaliar_resposta_em_branco(resposta: Any) -> RespostaEmBranco | None:
    """Regra do Req. 4.6: em branco gera nota 0, motivo e reenvio, sem avançar.

    Devolve None se a resposta não estiver em branco (avaliação normal).
    """
    if not resposta_em_branco(resposta):
        return None
    return RespostaEmBranco(
        nota_final=Decimal("0.0"),
        motivo=MOTIVO_RESPOSTA_EM_BRANCO,
        reenviar=True,
        avanca=False,
    )
