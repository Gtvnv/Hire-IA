"""CLI que valida os artefatos reais do repositório (Req. 6.1, 7.6, 8.1, 8.5, 9.1).

Uso::

    python tools/validar_artefatos.py [--raiz CAMINHO]
    python -m tools.validar_artefatos [--raiz CAMINHO]

Confere os prompts em ``prompts/`` (conformidade e histórico de versões), o
README, o Registro_de_Prompts e o arquivo ``LICENSE``. Cada verificação é
listada como aprovada ou reprovada e, em reprovação, com o campo ausente.
Código de saída 0 se tudo passar, 1 se houver reprovação.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

if __package__ in (None, ""):  # execução direta: python tools/validar_artefatos.py
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools import docs_md, prompts_md  # noqa: E402

RAIZ_PADRAO = Path(__file__).resolve().parent.parent

# Agrupa os erros do Registro por prefixo do campo (antes de '[', '.' ou ':').
_GRUPOS_REGISTRO = (
    ("secoes", "Seções obrigatórias"),
    ("indice", "Índice de prompts"),
    ("fichas", "Fichas dos prompts"),
    ("comparacao", "Comparação de versões do Avaliador"),
    ("licoes", "Lições aprendidas"),
    ("cenarios", "Cenários de teste"),
    ("checklist", "Checklist de qualidade"),
    ("portabilidade", "Portabilidade entre assistentes"),
)
_ALIAS_PREFIXO = {"secao": "secoes", "ficha": "fichas", "cenario": "cenarios", "execucoes": "cenarios"}


@dataclass
class Verificacao:
    nome: str
    campos: list[str] = field(default_factory=list)
    mensagens: list[str] = field(default_factory=list)

    @property
    def aprovada(self) -> bool:
        return not self.mensagens


def _prefixo(campo: str) -> str:
    base = re.split(r"[\[.:]", campo, maxsplit=1)[0]
    return _ALIAS_PREFIXO.get(base, base)


def _verificacao(nome: str, erros) -> Verificacao:
    return Verificacao(
        nome,
        [e.campo for e in erros],
        [e.mensagem for e in erros],
    )


def _ler(caminho: Path) -> str | None:
    try:
        return caminho.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def _verificar_prompts(raiz: Path) -> list[Verificacao]:
    arquivos = docs_md.listar_prompts(raiz)
    if not arquivos:
        return [
            Verificacao(
                "prompts/: arquivos de prompt",
                ["prompts"],
                ["Nenhum arquivo .md encontrado em prompts/."],
            )
        ]
    saida: list[Verificacao] = []
    for arq in arquivos:
        texto = _ler(arq)
        rel = arq.relative_to(raiz).as_posix()
        if texto is None:
            saida.append(Verificacao(f"{rel}: leitura", [rel], ["Arquivo ilegível (UTF-8)."]))
            continue
        conf = prompts_md.validar_arquivo_prompt(texto)
        saida.append(_verificacao(f"{rel}: conformidade (Req. 6.x)", conf.erros))
        hist = prompts_md.validar_historico_versoes(texto)
        saida.append(_verificacao(f"{rel}: histórico de versões (Req. 7.1, 7.2)", hist.erros))
    return saida


def _verificar_readme(raiz: Path) -> list[Verificacao]:
    texto = _ler(raiz / docs_md.CAMINHO_README)
    if texto is None:
        return [
            Verificacao(
                "README.md: existência",
                ["readme"],
                ["O arquivo README.md não existe ou está ilegível."],
            )
        ]
    return [
        _verificacao("README.md: seções na ordem (Req. 8.1)", docs_md.verificar_secoes_readme(texto).erros),
        _verificacao("README.md: tags (Req. 8.5)", docs_md.verificar_tags_readme(texto).erros),
        _verificacao("README.md: links (Req. 8.4, 8.8)", docs_md.verificar_links_readme(texto, raiz).erros),
        _verificacao("README.md: licença (Req. 8.9)", docs_md.verificar_licenca_readme(texto).erros),
    ]


def _verificar_registro(raiz: Path) -> list[Verificacao]:
    caminho = docs_md.CAMINHO_REGISTRO
    texto = _ler(raiz / caminho)
    if texto is None:
        return [
            Verificacao(
                f"{caminho}: existência",
                ["registro"],
                [f"O arquivo {caminho} não existe ou está ilegível."],
            )
        ]
    por_grupo: dict[str, list] = {chave: [] for chave, _ in _GRUPOS_REGISTRO}
    for erro in docs_md.verificar_registro(texto, raiz).erros:
        por_grupo.setdefault(_prefixo(erro.campo), []).append(erro)
    nomes = dict(_GRUPOS_REGISTRO)
    return [
        _verificacao(f"{caminho}: {nomes.get(chave, chave)}", erros)
        for chave, erros in por_grupo.items()
    ]


def _verificar_license(raiz: Path) -> list[Verificacao]:
    arquivo = raiz / docs_md.CAMINHO_LICENSE
    texto = _ler(arquivo)
    erros: list[docs_md.ErroDocs] = []
    if texto is None:
        erros.append(docs_md.ErroDocs("LICENSE", "O arquivo LICENSE não existe."))
    elif not texto.strip():
        erros.append(docs_md.ErroDocs("LICENSE", "O arquivo LICENSE está vazio."))
    return [_verificacao("LICENSE: presença (Req. 8.9)", erros)]


def validar(raiz: Path) -> list[Verificacao]:
    raiz = Path(raiz)
    return [
        *_verificar_prompts(raiz),
        *_verificar_readme(raiz),
        *_verificar_registro(raiz),
        *_verificar_license(raiz),
    ]


def formatar(verificacoes: list[Verificacao]) -> str:
    linhas: list[str] = []
    for v in verificacoes:
        if v.aprovada:
            linhas.append(f"[aprovada]  {v.nome}")
            continue
        linhas.append(f"[reprovada] {v.nome}")
        for campo, msg in zip(v.campos, v.mensagens):
            linhas.append(f"    campo ausente/inválido: {campo} - {msg}")
    reprovadas = sum(not v.aprovada for v in verificacoes)
    linhas.append("")
    linhas.append(
        f"Total: {len(verificacoes)} verificações, "
        f"{len(verificacoes) - reprovadas} aprovadas, {reprovadas} reprovadas."
    )
    return "\n".join(linhas)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Valida os artefatos do repositório.")
    parser.add_argument("--raiz", type=Path, default=RAIZ_PADRAO, help="raiz do repositório")
    args = parser.parse_args(argv)
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8")
    verificacoes = validar(args.raiz)
    print(formatar(verificacoes))
    return 1 if any(not v.aprovada for v in verificacoes) else 0


if __name__ == "__main__":
    sys.exit(main())
