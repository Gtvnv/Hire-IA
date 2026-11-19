"""Relatório_Final: notas, conteúdo por número de respostas e plano de estudo (Req. 5.1 a 5.5).

Funções puras: não alteram a entrada e devolvem todos os erros de uma vez.
As médias usam Fraction (exato) e arredondamento ROUND_HALF_UP para uma casa
decimal, sem passar por float, de forma consistente com `tools/feedback.py`.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction
from typing import Any, Iterable, Mapping, Sequence

from tools.feedback import ErroFeedback, ResultadoValidacao, _decimal

NOTA_MIN = Decimal(0)
NOTA_MAX = Decimal(10)

MIN_RESPOSTAS_COMPLETO = 3
PONTOS_COMPLETO = 3
PONTOS_PARCIAL_MAX = 2
PONTO_MAX = 200
RESUMO_MAX = 1000
PLANO_MIN = 1
PLANO_MAX = 5

_UMA_CASA = Decimal("0.1")


@dataclass(frozen=True)
class RespostaAvaliada:
    """Pergunta respondida: categoria e nota final (0 a 10)."""

    categoria: str
    nota: Decimal


# ------------------------------------------------------------------------ Médias


def _para_decimal(valor: Any) -> Decimal:
    d = _decimal(valor)
    if d is None or not NOTA_MIN <= d <= NOTA_MAX:
        raise ValueError("A nota deve ser numérica, de 0 a 10.")
    return d


def _media(notas: Sequence[Decimal]) -> Decimal:
    """Média exata arredondada a uma casa decimal, ROUND_HALF_UP."""
    soma = sum((Fraction(n) for n in notas), Fraction(0))
    media = soma / len(notas)
    # ROUND_HALF_UP exato: floor(media * 10 + 1/2) décimos (notas são >= 0).
    dezenas = (media * 10 + Fraction(1, 2)).__floor__()
    return (Decimal(dezenas) * _UMA_CASA).quantize(_UMA_CASA, rounding=ROUND_HALF_UP)


def calcular_nota_geral(respostas: Iterable[RespostaAvaliada]) -> Decimal | None:
    """Média aritmética de todas as notas, uma casa decimal. None se n = 0 (Req. 5.1, 5.5)."""
    notas = [_para_decimal(r.nota) for r in respostas]
    return _media(notas) if notas else None


def calcular_notas_por_categoria(
    respostas: Iterable[RespostaAvaliada],
) -> dict[str, Decimal]:
    """Nota média por categoria, só para categorias com ao menos uma resposta (Req. 5.1)."""
    grupos: dict[str, list[Decimal]] = {}
    for r in respostas:
        grupos.setdefault(r.categoria, []).append(_para_decimal(r.nota))
    return {cat: _media(notas) for cat, notas in grupos.items()}


# ------------------------------------------------------------------ Plano de estudo


def ordenar_plano_de_estudo(
    topicos: Iterable[Mapping[str, Any]],
    notas_por_categoria: Mapping[str, Decimal],
) -> list[Mapping[str, Any]]:
    """Ordena tópicos (com chave 'categoria') por nota da categoria crescente e,
    em empate, por nome da categoria (Req. 5.3). A ordenação é estável."""
    return sorted(
        topicos,
        key=lambda t: (notas_por_categoria[t["categoria"]], t["categoria"]),
    )


# --------------------------------------------------------------------- Relatório


def _validar_pontos(
    campo: str,
    pontos: Any,
    minimo: int,
    maximo: int,
    erros: list[ErroFeedback],
) -> None:
    if not isinstance(pontos, (list, tuple)):
        erros.append(ErroFeedback(campo, f"{campo} deve ser uma lista."))
        return
    if not minimo <= len(pontos) <= maximo:
        esperado = str(minimo) if minimo == maximo else f"de {minimo} a {maximo}"
        erros.append(ErroFeedback(campo, f"{campo} deve ter {esperado} itens (informado: {len(pontos)})."))
    for i, p in enumerate(pontos):
        texto = p.get("texto") if isinstance(p, Mapping) else None
        categoria = p.get("categoria") if isinstance(p, Mapping) else None
        if not isinstance(texto, str) or texto.strip() == "" or len(texto) > PONTO_MAX:
            erros.append(
                ErroFeedback(f"{campo}[{i}]", f"O texto deve ter de 1 a {PONTO_MAX} caracteres.")
            )
        if not isinstance(categoria, str) or categoria.strip() == "":
            erros.append(ErroFeedback(f"{campo}[{i}]", "O item deve estar vinculado a uma categoria."))


def validar_relatorio(
    relatorio: Mapping[str, Any],
    respostas: Sequence[RespostaAvaliada],
) -> ResultadoValidacao:
    """Valida o Relatório_Final conforme o número n de respostas (Req. 5.1 a 5.5).

    Campos: parcial, nota_geral, nota_por_categoria, resumo, pontos_fortes,
    pontos_de_melhoria (itens com 'texto' e 'categoria') e plano_de_estudo
    (itens com 'topico' e 'categoria').
    n >= 3: 3 pontos de cada tipo; 0 < n < 3: parcial, 0 a 2 de cada;
    n = 0: sem nota geral, notas por categoria nem plano de estudo.
    """
    erros: list[ErroFeedback] = []
    n = len(respostas)
    esperadas = calcular_notas_por_categoria(respostas)
    geral = calcular_nota_geral(respostas)

    if n == 0:
        for campo in ("nota_geral", "nota_por_categoria", "plano_de_estudo"):
            if relatorio.get(campo) not in (None, {}, [], ()):
                erros.append(ErroFeedback(campo, f"Sem respostas, {campo} não deve ser gerado."))
        return ResultadoValidacao(tuple(erros))

    parcial = n < MIN_RESPOSTAS_COMPLETO
    if relatorio.get("parcial") is not parcial:
        erros.append(
            ErroFeedback("parcial", "O relatório deve ser marcado como parcial." if parcial
                         else "O relatório completo não deve ser marcado como parcial.")
        )

    informada = _decimal(relatorio.get("nota_geral"))
    if informada is None or informada != geral:
        erros.append(ErroFeedback("nota_geral", f"A nota geral deveria ser {geral}."))

    por_categoria = relatorio.get("nota_por_categoria")
    if not isinstance(por_categoria, Mapping) or set(por_categoria) != set(esperadas):
        erros.append(
            ErroFeedback("nota_por_categoria", "Deve haver nota apenas para categorias com resposta.")
        )
    else:
        for cat, esperada in esperadas.items():
            valor = _decimal(por_categoria[cat])
            if valor is None or valor != esperada:
                erros.append(
                    ErroFeedback(f"nota_por_categoria.{cat}", f"A nota de '{cat}' deveria ser {esperada}.")
                )

    resumo = relatorio.get("resumo")
    if not isinstance(resumo, str) or resumo.strip() == "" or len(resumo) > RESUMO_MAX:
        erros.append(ErroFeedback("resumo", f"O resumo deve ter de 1 a {RESUMO_MAX} caracteres."))

    minimo, maximo = (0, PONTOS_PARCIAL_MAX) if parcial else (PONTOS_COMPLETO, PONTOS_COMPLETO)
    _validar_pontos("pontos_fortes", relatorio.get("pontos_fortes"), minimo, maximo, erros)
    _validar_pontos("pontos_de_melhoria", relatorio.get("pontos_de_melhoria"), minimo, maximo, erros)

    plano = relatorio.get("plano_de_estudo")
    if not isinstance(plano, (list, tuple)) or not PLANO_MIN <= len(plano) <= PLANO_MAX:
        erros.append(
            ErroFeedback("plano_de_estudo", f"O plano deve ter de {PLANO_MIN} a {PLANO_MAX} tópicos.")
        )
    else:
        categorias_ok = all(
            isinstance(t, Mapping) and t.get("categoria") in esperadas for t in plano
        )
        if not categorias_ok:
            erros.append(
                ErroFeedback("plano_de_estudo", "Cada tópico deve ter uma categoria com resposta.")
            )
        elif list(plano) != ordenar_plano_de_estudo(plano, esperadas):
            erros.append(
                ErroFeedback(
                    "plano_de_estudo",
                    "O plano deve seguir a nota média da categoria crescente e, em empate, o nome da categoria.",
                )
            )

    return ResultadoValidacao(tuple(erros))
