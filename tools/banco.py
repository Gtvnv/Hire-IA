"""Validação do Banco_de_Perguntas em tabela Markdown (Req. 2.1 a 2.4, 2.6, 2.7).

Funções puras: não alteram a entrada e devolvem todos os erros de uma vez.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Sequence

COLUNAS = ("número", "pergunta", "categoria", "dificuldade", "resposta de referência")
CATEGORIAS = ("Técnica", "Comportamental", "Situacional")
DIFICULDADES = ("Básico", "Intermediário", "Avançado")

TOTAL_INICIAL = 10
TOTAL_EXPANSAO = 5
MIN_POR_CATEGORIA = 2
MIN_DIFICULDADE_PREDOMINANTE = 5
RESPOSTA_MAX = 1000

# Dificuldade predominante por Senioridade (Req. 2.4).
DIFICULDADE_POR_SENIORIDADE = {
    "Estagiário": "Básico",
    "Júnior": "Básico",
    "Pleno": "Intermediário",
    "Sênior": "Avançado",
    "Especialista": "Avançado",
}

_SEPARADOR_CELULA = re.compile(r"^:?-{1,}:?$")
_PIPE_ESCAPADO = "\x00"


@dataclass(frozen=True)
class Pergunta:
    numero: str
    pergunta: str
    categoria: str
    dificuldade: str
    resposta_de_referencia: str

    def como_tupla(self) -> tuple[str, str, str, str, str]:
        return (
            self.numero,
            self.pergunta,
            self.categoria,
            self.dificuldade,
            self.resposta_de_referencia,
        )


@dataclass(frozen=True)
class ResultadoBanco:
    perguntas: tuple[Pergunta, ...] = field(default_factory=tuple)
    erros: tuple[str, ...] = field(default_factory=tuple)

    @property
    def valido(self) -> bool:
        return not self.erros


def _dividir_linha(linha: str) -> list[str]:
    """Divide uma linha de tabela em células, respeitando `\\|` como pipe literal."""
    texto = linha.strip().replace("\\|", _PIPE_ESCAPADO)
    if texto.startswith("|"):
        texto = texto[1:]
    if texto.endswith("|"):
        texto = texto[:-1]
    return [c.replace(_PIPE_ESCAPADO, "|").strip() for c in texto.split("|")]


def _linha_de_tabela(linha: str) -> bool:
    return linha.strip().startswith("|")


def _linha_separadora(celulas: Sequence[str]) -> bool:
    return bool(celulas) and all(_SEPARADOR_CELULA.match(c) for c in celulas)


def _normalizar_cabecalho(celula: str) -> str:
    return " ".join(celula.lower().split())


def interpretar_tabela(texto: str) -> ResultadoBanco:
    """Interpreta a tabela Markdown do banco e valida apenas a estrutura (Req. 2.7).

    Procura o primeiro bloco de linhas iniciadas por `|`. Exige cabeçalho com as
    cinco colunas, nesta ordem, linha separadora e linhas com cinco células.
    """
    linhas = [l for l in texto.splitlines() if _linha_de_tabela(l)]
    if not linhas:
        return ResultadoBanco(erros=("Nenhuma tabela Markdown encontrada.",))

    erros: list[str] = []
    cabecalho = [_normalizar_cabecalho(c) for c in _dividir_linha(linhas[0])]
    if tuple(cabecalho) != COLUNAS:
        erros.append(
            "Colunas inválidas. Esperado: " + ", ".join(COLUNAS) + "; encontrado: " + ", ".join(cabecalho) + "."
        )
        return ResultadoBanco(erros=tuple(erros))

    if len(linhas) < 2 or not _linha_separadora(_dividir_linha(linhas[1])):
        return ResultadoBanco(erros=("Linha separadora do cabeçalho ausente.",))

    perguntas: list[Pergunta] = []
    for indice, linha in enumerate(linhas[2:], start=1):
        celulas = _dividir_linha(linha)
        if len(celulas) != len(COLUNAS):
            erros.append(
                f"Linha {indice} tem {len(celulas)} células; esperado {len(COLUNAS)}."
            )
            continue
        perguntas.append(Pergunta(*celulas))
    return ResultadoBanco(perguntas=tuple(perguntas), erros=tuple(erros))


def validar_banco(
    texto: str,
    senioridade: str,
    total_esperado: int | None = TOTAL_INICIAL,
) -> ResultadoBanco:
    """Valida o Banco_de_Perguntas em Markdown para a Senioridade informada.

    Regras: colunas (2.7), total de linhas (2.1; `None` ignora a contagem, útil
    após expansão), categoria e dificuldade válidas (2.2, 2.3), resposta de
    referência não vazia com até 1.000 caracteres (2.3), numeração sequencial
    a partir de 1, mínimo de 2 por categoria (2.2) e mínimo de 5 na dificuldade
    predominante da Senioridade (2.4).
    """
    leitura = interpretar_tabela(texto)
    erros: list[str] = list(leitura.erros)
    perguntas = leitura.perguntas

    predominante = DIFICULDADE_POR_SENIORIDADE.get(senioridade)
    if predominante is None:
        erros.append(
            "Senioridade inválida. Valores aceitos: " + ", ".join(DIFICULDADE_POR_SENIORIDADE) + "."
        )

    # Sem tabela legível não há o que conferir além dos erros já coletados.
    if not perguntas and erros:
        return ResultadoBanco(perguntas=perguntas, erros=tuple(erros))

    if total_esperado is not None and len(perguntas) != total_esperado:
        erros.append(f"O banco tem {len(perguntas)} perguntas; esperado {total_esperado}.")

    for posicao, p in enumerate(perguntas, start=1):
        if p.numero != str(posicao):
            erros.append(f"Linha {posicao}: número '{p.numero}' fora da sequência (esperado {posicao}).")
        if not p.pergunta:
            erros.append(f"Pergunta {posicao}: texto da pergunta vazio.")
        if p.categoria not in CATEGORIAS:
            erros.append(
                f"Pergunta {posicao}: categoria '{p.categoria}' inválida. Valores aceitos: "
                + ", ".join(CATEGORIAS)
                + "."
            )
        if p.dificuldade not in DIFICULDADES:
            erros.append(
                f"Pergunta {posicao}: dificuldade '{p.dificuldade}' inválida. Valores aceitos: "
                + ", ".join(DIFICULDADES)
                + "."
            )
        if not p.resposta_de_referencia:
            erros.append(f"Pergunta {posicao}: resposta de referência vazia.")
        elif len(p.resposta_de_referencia) > RESPOSTA_MAX:
            erros.append(
                f"Pergunta {posicao}: resposta de referência excede {RESPOSTA_MAX} caracteres "
                f"(informado: {len(p.resposta_de_referencia)})."
            )

    for categoria in CATEGORIAS:
        qtd = sum(1 for p in perguntas if p.categoria == categoria)
        if qtd < MIN_POR_CATEGORIA:
            erros.append(
                f"Categoria {categoria} tem {qtd} perguntas; mínimo de {MIN_POR_CATEGORIA}."
            )

    if predominante is not None:
        qtd = sum(1 for p in perguntas if p.dificuldade == predominante)
        if qtd < MIN_DIFICULDADE_PREDOMINANTE:
            erros.append(
                f"Dificuldade {predominante} tem {qtd} perguntas para {senioridade}; "
                f"mínimo de {MIN_DIFICULDADE_PREDOMINANTE}."
            )

    return ResultadoBanco(perguntas=perguntas, erros=tuple(erros))


def verificar_expansao(
    banco_anterior: str,
    banco_novo: str,
    novas: int = TOTAL_EXPANSAO,
) -> ResultadoBanco:
    """Confere a expansão do banco (Req. 2.6).

    O novo banco deve ter `novas` linhas a mais, e as linhas anteriores devem
    aparecer inalteradas e na mesma ordem, como prefixo do novo banco.
    """
    antes = interpretar_tabela(banco_anterior)
    depois = interpretar_tabela(banco_novo)
    erros: list[str] = [f"Banco anterior: {e}" for e in antes.erros]
    erros += [f"Banco novo: {e}" for e in depois.erros]
    if erros:
        return ResultadoBanco(perguntas=depois.perguntas, erros=tuple(erros))

    if len(depois.perguntas) != len(antes.perguntas) + novas:
        erros.append(
            f"O banco expandido tem {len(depois.perguntas)} perguntas; "
            f"esperado {len(antes.perguntas) + novas} ({novas} a mais)."
        )

    for posicao, original in enumerate(antes.perguntas, start=1):
        if posicao > len(depois.perguntas):
            erros.append(f"Pergunta {posicao} do banco anterior foi removida.")
            continue
        if depois.perguntas[posicao - 1].como_tupla() != original.como_tupla():
            erros.append(f"Pergunta {posicao} do banco anterior foi alterada ou reordenada.")

    return ResultadoBanco(perguntas=depois.perguntas, erros=tuple(erros))
