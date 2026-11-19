"""Validação do Perfil_da_Vaga (Req. 1.1, 1.2, 1.4, 1.6, 2.8).

Função pura: não altera a entrada e devolve todos os erros de uma vez.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

SENIORIDADES = ("Estagiário", "Júnior", "Pleno", "Sênior", "Especialista")
CAMPOS_OBRIGATORIOS = ("cargo", "senioridade")

CARGO_MAX = 100
TECNOLOGIAS_MAX_ITENS = 20
TECNOLOGIA_MAX = 50
DESCRICAO_MAX = 5000

IDIOMA_PADRAO = "português do Brasil"

AUSENTE = "ausente"
EXCEDE_LIMITE = "excede_limite"
VALOR_INVALIDO = "valor_invalido"


@dataclass(frozen=True)
class ErroCampo:
    """Erro de um campo. `campo` usa o nome do campo (item de lista: `tecnologias[i]`)."""

    campo: str
    tipo: str
    mensagem: str
    limite: int | None = None
    valores_aceitos: tuple[str, ...] = ()


@dataclass(frozen=True)
class ResultadoPerfil:
    erros: tuple[ErroCampo, ...] = field(default_factory=tuple)

    @property
    def valido(self) -> bool:
        return not self.erros

    @property
    def campos_invalidos(self) -> tuple[str, ...]:
        """Nomes dos campos com erro, sem repetição, na ordem de ocorrência."""
        return tuple(dict.fromkeys(e.campo for e in self.erros))

    @property
    def campos_ausentes(self) -> tuple[str, ...]:
        return tuple(e.campo for e in self.erros if e.tipo == AUSENTE)

    @property
    def mensagem(self) -> str:
        """Mensagem única que lista todos os campos com erro (vazia se válido)."""
        return " ".join(e.mensagem for e in self.erros)


def _em_branco(valor: Any) -> bool:
    return valor is None or (isinstance(valor, str) and valor.strip() == "")


def _erro_tamanho(campo: str, rotulo: str, tamanho: int, maximo: int) -> ErroCampo:
    return ErroCampo(
        campo=campo,
        tipo=EXCEDE_LIMITE,
        limite=maximo,
        mensagem=f"{rotulo} excede o limite de {maximo} caracteres (informado: {tamanho}).",
    )


def validar_perfil(perfil: Mapping[str, Any]) -> ResultadoPerfil:
    """Valida o Perfil_da_Vaga e devolve todos os campos inválidos ou ausentes.

    Campos: cargo (obrigatório, 1 a 100), senioridade (obrigatório, enum),
    tecnologias (0 a 20 itens, 1 a 50 caracteres cada), descricao_da_vaga
    (opcional, 1 a 5.000; `None` equivale a omitida) e idioma (opcional).
    Valor ausente, `None` ou só com espaços em cargo/senioridade conta como ausente.
    """
    erros: list[ErroCampo] = []

    # cargo
    cargo = perfil.get("cargo")
    if _em_branco(cargo):
        erros.append(ErroCampo("cargo", AUSENTE, "Campo obrigatório ausente: cargo."))
    elif not isinstance(cargo, str):
        erros.append(ErroCampo("cargo", VALOR_INVALIDO, "O cargo deve ser um texto."))
    elif len(cargo) > CARGO_MAX:
        erros.append(_erro_tamanho("cargo", "O cargo", len(cargo), CARGO_MAX))

    # senioridade
    senioridade = perfil.get("senioridade")
    if _em_branco(senioridade):
        erros.append(
            ErroCampo(
                "senioridade",
                AUSENTE,
                "Campo obrigatório ausente: senioridade. Valores aceitos: "
                + ", ".join(SENIORIDADES)
                + ".",
                valores_aceitos=SENIORIDADES,
            )
        )
    elif senioridade not in SENIORIDADES:
        erros.append(
            ErroCampo(
                "senioridade",
                VALOR_INVALIDO,
                "Senioridade inválida. Valores aceitos: " + ", ".join(SENIORIDADES) + ".",
                valores_aceitos=SENIORIDADES,
            )
        )

    # tecnologias (opcional)
    tecnologias = perfil.get("tecnologias")
    if tecnologias is not None:
        if isinstance(tecnologias, str) or not isinstance(tecnologias, (list, tuple)):
            erros.append(
                ErroCampo("tecnologias", VALOR_INVALIDO, "As tecnologias devem ser uma lista de textos.")
            )
        else:
            if len(tecnologias) > TECNOLOGIAS_MAX_ITENS:
                erros.append(
                    ErroCampo(
                        "tecnologias",
                        EXCEDE_LIMITE,
                        f"A lista de tecnologias excede o limite de {TECNOLOGIAS_MAX_ITENS} itens "
                        f"(informado: {len(tecnologias)}).",
                        limite=TECNOLOGIAS_MAX_ITENS,
                    )
                )
            for i, item in enumerate(tecnologias):
                nome = f"tecnologias[{i}]"
                if not isinstance(item, str) or item == "":
                    erros.append(
                        ErroCampo(
                            nome,
                            VALOR_INVALIDO,
                            f"O item {i + 1} de tecnologias deve ter de 1 a {TECNOLOGIA_MAX} caracteres.",
                            limite=TECNOLOGIA_MAX,
                        )
                    )
                elif len(item) > TECNOLOGIA_MAX:
                    erros.append(
                        _erro_tamanho(nome, f"O item {i + 1} de tecnologias", len(item), TECNOLOGIA_MAX)
                    )

    # descricao_da_vaga (opcional)
    descricao = perfil.get("descricao_da_vaga")
    if descricao is not None:
        if not isinstance(descricao, str):
            erros.append(
                ErroCampo("descricao_da_vaga", VALOR_INVALIDO, "A descrição da vaga deve ser um texto.")
            )
        elif descricao == "":
            erros.append(
                ErroCampo(
                    "descricao_da_vaga",
                    VALOR_INVALIDO,
                    f"A descrição da vaga, quando informada, deve ter de 1 a {DESCRICAO_MAX} caracteres.",
                    limite=DESCRICAO_MAX,
                )
            )
        elif len(descricao) > DESCRICAO_MAX:
            erros.append(
                _erro_tamanho("descricao_da_vaga", "A descrição da vaga", len(descricao), DESCRICAO_MAX)
            )

    # idioma (opcional, padrão aplicado pelo chamador)
    idioma = perfil.get("idioma")
    if idioma is not None and not isinstance(idioma, str):
        erros.append(ErroCampo("idioma", VALOR_INVALIDO, "O idioma deve ser um texto."))

    return ResultadoPerfil(erros=tuple(erros))
