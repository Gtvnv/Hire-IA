"""Validação do README e do Registro_de_Prompts (Req. 7.3, 7.4, 7.6, 8.1, 8.4, 8.5, 8.8, 8.9, 10.1 a 10.8).

Funções puras: recebem texto (ou a raiz do repositório, para conferir arquivos),
não alteram a entrada e devolvem todos os erros de uma vez. Nada aqui chama
Assistentes_de_IA: as verificações são regras determinísticas sobre o Markdown.

Convenção de Markdown (contrato com as tarefas 8.x e 9.1)
=========================================================

Regras gerais
-------------
* Linhas dentro de blocos de código cercados (``` ou ~~~) nunca são lidas como
  título, campo ou link. Elas só entram como continuação do campo em que estão.
* Comparações de nomes ignoram maiúsculas, acentos e espaços repetidos.
* "Campo" é uma linha no início da linha (sem recuo) no formato
  ``- **Nome:** valor``. O valor continua nas linhas seguintes (recuadas, em bloco
  de código ou em texto comum) até o próximo campo ou título.
* Itens de lista aninhados (recuados) pertencem ao campo anterior.

README (``README.md``, na raiz)
-------------------------------
1. Título ``# ...`` seguido de texto de descrição antes do primeiro ``##``.
2. Seções ``##``, nesta ordem (Req. 8.1): Objetivo, Tags, Funcionalidades,
   Pré-requisitos, Estrutura do repositório, Como usar, Exemplo de sessão,
   Técnicas de engenharia de prompt, Resultados e aprendizados, Limitações,
   Próximos passos, Licença. O título da seção começa com o nome acima.
   "Privacidade e Segurança" é uma subseção ``###`` de Limitações.
3. Tags: uma lista com um marcador por tag, exatamente IA, Engenharia de Prompt,
   IA Generativa e Assistentes de IA (Req. 8.5).
4. Links relativos no formato ``[texto](caminho)``, a partir da raiz: um para cada
   arquivo ``prompts/*.md`` e um para ``docs/registro-de-prompts.md``. Todo link
   relativo deve apontar para arquivo existente (Req. 8.4, 8.8). Links com
   esquema (``https:``, ``mailto:``) e âncoras (``#x``) são ignorados.
5. Licença: cita "MIT" e "LICENSE" (Req. 8.9). O arquivo ``LICENSE`` existe.

Registro_de_Prompts (``docs/registro-de-prompts.md``)
-----------------------------------------------------
Seções ``##`` (títulos começam com): ``Índice de prompts``, ``Fichas dos prompts``,
``Comparação de versões do Avaliador``, ``Lições aprendidas``, ``Cenários de teste``,
``Checklist de qualidade``, ``Portabilidade entre assistentes``.

* Índice de prompts: um link relativo (a partir de ``docs/``, ex.:
  ``../prompts/avaliador-de-respostas.md``) para cada arquivo de ``prompts/``.
* Fichas dos prompts: uma subseção ``###`` por prompt, com os campos
  ``Objetivo`` (1 a 300 caracteres), ``Técnica`` (um único nome), ``Versão atual``
  (``vN``), ``Texto completo`` (texto ou link para o arquivo), ``Exemplo de entrada``
  e ``Exemplo de saída`` (Req. 7.1, 7.6).
* Comparação de versões do Avaliador: uma subseção ``###`` por versão, com título
  começando por ``vN`` e ao menos 3 campos ``- **Entrada 1:** ...``,
  ``- **Entrada 2:** ...``, ``- **Entrada 3:** ...`` (resultado de cada entrada de teste).
  Ao menos 2 versões. Campos da seção: ``Versão adotada`` (``vN``) e ``Motivo``
  (Req. 7.3).
* Lições aprendidas: ao menos 3 subseções ``###``, cada uma com ``Problema``,
  ``Correção`` e ``Versão`` (``vN``) (Req. 7.4).
* Cenários de teste: de 3 a 20 subseções ``### Cenário <ID>: <título>`` (ID único,
  sem espaços). Campos do cenário: ``Cargo``, ``Senioridade`` (um dos cinco valores),
  ``Tecnologias`` (separadas por vírgula, pode ficar vazio com "-"), ``Tipo``
  (``padrao``, ``fluxo``, ``resposta-vazia`` ou ``fora-de-contexto``) e ``Checklist``
  com os cinco itens como lista de tarefas aninhada::

      - **Checklist:**
        - [x] Relevância das perguntas
        - [x] Aderência à Senioridade
        - [x] Formato de saída
        - [x] Coerência das notas
        - [ ] Clareza do Feedback

  Mais ``Resultado`` (``aprovado`` ou ``reprovado``) e, se reprovado,
  ``Itens reprovados`` (nomes separados por ";"). O resultado registrado precisa
  coincidir com o calculado por :func:`resultado_cenario` (Req. 10.4, 10.6).
  Cada cenário tem uma ou mais execuções, em subseções ``#### Execução <n>``, com os
  campos ``Assistente``, ``Modelo`` (não vazios), ``Data`` (AAAA-MM-DD), ``Entrada``,
  ``Saída`` e ``Verificações``, uma lista aninhada ``- <critério>: aprovado`` ou
  ``- <critério>: reprovado``. Em cenários ``resposta-vazia`` e ``fora-de-contexto``
  a execução também traz ``Comportamento esperado``, ``Comportamento observado`` e
  ``Divergência de comportamento`` (``sim`` ou ``não``) (Req. 10.2, 10.4).
  Cenários com 2 ou mais execuções trazem o campo ``Divergências``: ``nenhuma`` ou
  uma lista com cada critério divergente e o assistente e o modelo em que foi
  reprovado (Req. 10.8). Perfis (cargo, Senioridade, tecnologias) distintos entre
  cenários e ao menos 2 Senioridades (Req. 10.1). Ao menos 1 cenário
  ``resposta-vazia`` e 1 ``fora-de-contexto`` (Req. 10.3).
* Checklist de qualidade: um campo por item, ``- **Relevância das perguntas:**
  <condição objetiva>``, e o mesmo para os outros quatro itens (Req. 10.5).
* Portabilidade entre assistentes: texto que cita o ID de ao menos 1 cenário
  executado com a mesma entrada em 2 ou mais assistentes distintos (Req. 10.7).
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Mapping, Sequence
from urllib.parse import unquote

from tools.perfil import SENIORIDADES

# --------------------------------------------------------------------------- #
# Constantes
# --------------------------------------------------------------------------- #

README_SECOES = (
    "Objetivo",
    "Tags",
    "Funcionalidades",
    "Pré-requisitos",
    "Estrutura do repositório",
    "Como usar",
    "Exemplo de sessão",
    "Técnicas de engenharia de prompt",
    "Resultados e aprendizados",
    "Limitações",
    "Próximos passos",
    "Licença",
)
README_TAGS = ("IA", "Engenharia de Prompt", "IA Generativa", "Assistentes de IA")
CAMINHO_REGISTRO = "docs/registro-de-prompts.md"
CAMINHO_README = "README.md"
CAMINHO_LICENSE = "LICENSE"
PASTA_PROMPTS = "prompts"

REGISTRO_SECOES = (
    "Índice de prompts",
    "Fichas dos prompts",
    "Comparação de versões do Avaliador",
    "Lições aprendidas",
    "Cenários de teste",
    "Checklist de qualidade",
    "Portabilidade entre assistentes",
)

CHECKLIST_ITENS = (
    "Relevância das perguntas",
    "Aderência à Senioridade",
    "Formato de saída",
    "Coerência das notas",
    "Clareza do Feedback",
)

TIPOS_CENARIO = ("padrao", "fluxo", "resposta-vazia", "fora-de-contexto")
TIPOS_RESPOSTA_INVALIDA = ("resposta-vazia", "fora-de-contexto")

OBJETIVO_MAX = 300
MIN_ENTRADAS_POR_VERSAO = 3
MIN_VERSOES_COMPARADAS = 2
MIN_LICOES = 3
MIN_CENARIOS = 3
MAX_CENARIOS = 20
MIN_SENIORIDADES = 2

COMPORTAMENTO_ESPERADO = "comportamento esperado"
COMPORTAMENTO_OBSERVADO = "comportamento observado"
ITEM_COMPORTAMENTO = "comportamento esperado e observado divergem"


# --------------------------------------------------------------------------- #
# Tipos de resultado
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class ErroDocs:
    campo: str
    mensagem: str


@dataclass(frozen=True)
class ResultadoDocs:
    erros: tuple[ErroDocs, ...] = field(default_factory=tuple)

    @property
    def valido(self) -> bool:
        return not self.erros

    @property
    def campos_invalidos(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(e.campo for e in self.erros))

    def somar(self, outro: "ResultadoDocs") -> "ResultadoDocs":
        return ResultadoDocs(self.erros + outro.erros)


@dataclass(frozen=True)
class Execucao:
    """Uma execução de cenário (Req. 10.2). `verificacoes`: critério -> aprovado?"""

    assistente: str = ""
    modelo: str = ""
    data: str = ""
    entrada: str = ""
    saida: str = ""
    verificacoes: Mapping[str, bool] = field(default_factory=dict)
    esperado: str = ""
    observado: str = ""
    divergiu: bool | None = None


@dataclass(frozen=True)
class ResultadoCenario:
    reprovado: bool
    itens_reprovados: tuple[str, ...] = field(default_factory=tuple)

    @property
    def rotulo(self) -> str:
        return "reprovado" if self.reprovado else "aprovado"


@dataclass(frozen=True)
class Cenario:
    id: str
    cargo: str = ""
    senioridade: str = ""
    tecnologias: tuple[str, ...] = ()
    tipo: str = ""
    checklist: Mapping[str, bool] = field(default_factory=dict)
    resultado: str = ""
    itens_reprovados: str = ""
    divergencias: str | None = None
    execucoes: tuple[Execucao, ...] = ()


# --------------------------------------------------------------------------- #
# Utilidades de texto e Markdown
# --------------------------------------------------------------------------- #

_CERCA = re.compile(r"^\s*(```|~~~)")
_TITULO = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_CAMPO = re.compile(r"^[-*]\s+\*\*(.+?):\*\*\s*(.*)$")
_ITEM_TAREFA = re.compile(r"^\s*[-*]\s+\[([ xX])\]\s+(.+?)\s*$")
_ITEM_VERIFICACAO = re.compile(r"^\s*[-*]\s+(.+?)\s*:\s*(aprovado|reprovado)\s*$", re.IGNORECASE)
_ITEM_LISTA = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(.*?)\s*$")
_LINK = re.compile(r"(?<!!)\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
_ESQUEMA = re.compile(r"^[A-Za-z][A-Za-z0-9+.\-]*:")
_VERSAO = re.compile(r"^v([1-9]\d*)$")
_DATA = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _norm(texto: str) -> str:
    sem_acento = "".join(
        c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c)
    )
    return " ".join(sem_acento.casefold().split())


def _vazio(texto: str | None) -> bool:
    return texto is None or texto.strip() == ""


@dataclass(frozen=True)
class _Secao:
    nivel: int
    titulo: str
    linhas: tuple[str, ...]


def _secoes(texto: str) -> list[_Secao]:
    """Divide o texto em seções por título, ignorando títulos dentro de cercas."""
    resultado: list[_Secao] = []
    nivel, titulo, linhas = 0, "", []
    em_cerca = False
    for linha in texto.splitlines():
        if _CERCA.match(linha):
            em_cerca = not em_cerca
            linhas.append(linha)
            continue
        m = None if em_cerca else _TITULO.match(linha)
        if m:
            resultado.append(_Secao(nivel, titulo, tuple(linhas)))
            nivel, titulo, linhas = len(m.group(1)), m.group(2), []
        else:
            linhas.append(linha)
    resultado.append(_Secao(nivel, titulo, tuple(linhas)))
    return resultado


def _descendentes(secoes: Sequence[_Secao], i: int) -> list[_Secao]:
    base = secoes[i].nivel
    itens: list[_Secao] = []
    for s in secoes[i + 1 :]:
        if s.nivel <= base:
            break
        itens.append(s)
    return itens


def _achar(secoes: Sequence[_Secao], nome: str, nivel: int | None = None) -> int | None:
    alvo = _norm(nome)
    for i, s in enumerate(secoes):
        if s.nivel > 0 and (nivel is None or s.nivel == nivel) and _norm(s.titulo).startswith(alvo):
            return i
    return None


def _campos(linhas: Sequence[str]) -> dict[str, str]:
    """Extrai campos `- **Nome:** valor`; a chave é normalizada. Mantém o primeiro."""
    campos: dict[str, list[str]] = {}
    atual: list[str] | None = None
    em_cerca = False
    for linha in linhas:
        if _CERCA.match(linha):
            em_cerca = not em_cerca
            if atual is not None:
                atual.append(linha)
            continue
        m = None if em_cerca else _CAMPO.match(linha)
        if m:
            chave = _norm(m.group(1))
            if chave in campos:
                atual = []  # duplicado: descarta o conteúdo, mantém o primeiro
            else:
                atual = [m.group(2)]
                campos[chave] = atual
        elif atual is not None:
            atual.append(linha)
    return {k: "\n".join(v).strip() for k, v in campos.items()}


def _sem_cercas(texto: str) -> str:
    saida: list[str] = []
    em_cerca = False
    for linha in texto.splitlines():
        if _CERCA.match(linha):
            em_cerca = not em_cerca
            continue
        if not em_cerca:
            saida.append(linha)
    return "\n".join(saida)


def _corpo(secao: _Secao) -> str:
    return "\n".join(secao.linhas)


# --------------------------------------------------------------------------- #
# README
# --------------------------------------------------------------------------- #


def verificar_secoes_readme(texto: str) -> ResultadoDocs:
    """Título com descrição e seções na ordem do Req. 8.1."""
    erros: list[ErroDocs] = []
    secoes = _secoes(texto)

    h1 = next((i for i, s in enumerate(secoes) if s.nivel == 1), None)
    if h1 is None:
        erros.append(ErroDocs("titulo", "O README não tem título (# ...)."))
    else:
        primeiro_h2 = next(
            (i for i in range(h1 + 1, len(secoes)) if secoes[i].nivel <= 2), len(secoes)
        )
        descricao = "".join(_corpo(s) for s in secoes[h1:primeiro_h2]).strip()
        if not descricao:
            erros.append(ErroDocs("descricao", "O título do README não é seguido de descrição."))

    h2 = [(i, s) for i, s in enumerate(secoes) if s.nivel == 2]
    ultima_posicao = -1
    for nome in README_SECOES:
        alvo = _norm(nome)
        posicao = next((k for k, (_, s) in enumerate(h2) if _norm(s.titulo).startswith(alvo)), None)
        if posicao is None:
            erros.append(ErroDocs(f"secao:{nome}", f"Seção ausente no README: {nome}."))
            continue
        if posicao < ultima_posicao:
            erros.append(
                ErroDocs(f"secao:{nome}", f"Seção fora de ordem no README: {nome} (Req. 8.1).")
            )
        ultima_posicao = max(ultima_posicao, posicao)
    return ResultadoDocs(tuple(erros))


def extrair_links_relativos(texto: str) -> tuple[str, ...]:
    """Alvos dos links Markdown relativos (sem âncora ou consulta), em ordem, sem blocos de código."""
    alvos: list[str] = []
    for bruto in _LINK.findall(_sem_cercas(texto)):
        if bruto.startswith(("#", "//")) or _ESQUEMA.match(bruto):
            continue
        alvo = unquote(re.split(r"[#?]", bruto, maxsplit=1)[0])
        if alvo:
            alvos.append(alvo)
    return tuple(alvos)


def listar_prompts(raiz: Path) -> tuple[Path, ...]:
    pasta = Path(raiz) / PASTA_PROMPTS
    if not pasta.is_dir():
        return ()
    return tuple(sorted(p for p in pasta.glob("*.md") if p.is_file()))


def _resolver(base: Path, alvo: str, raiz: Path) -> Path | None:
    """Caminho resolvido do link, ou None se sair da raiz do repositório."""
    caminho = (base / alvo).resolve()
    try:
        caminho.relative_to(Path(raiz).resolve())
    except ValueError:
        return None
    return caminho


def verificar_links(
    texto: str,
    raiz: Path,
    base: Path | None = None,
    obrigatorios: Sequence[Path] = (),
    rotulo: str = "link",
) -> ResultadoDocs:
    """Todo link relativo aponta para arquivo existente e cada obrigatório é linkado."""
    raiz = Path(raiz)
    base = Path(base) if base is not None else raiz
    erros: list[ErroDocs] = []
    linkados: set[Path] = set()
    for alvo in extrair_links_relativos(texto):
        if alvo.startswith("/"):
            erros.append(ErroDocs(rotulo, f"O link '{alvo}' não é relativo."))
            continue
        caminho = _resolver(base, alvo, raiz)
        if caminho is None:
            erros.append(ErroDocs(rotulo, f"O link '{alvo}' aponta para fora do repositório."))
        elif not caminho.is_file():
            erros.append(ErroDocs(rotulo, f"O link '{alvo}' aponta para arquivo inexistente."))
        else:
            linkados.add(caminho)
    for obrigatorio in obrigatorios:
        if Path(obrigatorio).resolve() not in linkados:
            nome = Path(obrigatorio).resolve().relative_to(raiz.resolve()).as_posix()
            erros.append(ErroDocs(f"{rotulo}:{nome}", f"Falta link relativo para {nome}."))
    return ResultadoDocs(tuple(erros))


def verificar_links_readme(texto: str, raiz: Path) -> ResultadoDocs:
    """Req. 8.4 e 8.8: links existentes e link para cada prompt e para o Registro."""
    raiz = Path(raiz)
    obrigatorios = [*listar_prompts(raiz), raiz / CAMINHO_REGISTRO]
    return verificar_links(texto, raiz, raiz, obrigatorios, rotulo="link")


def _itens_secao(secao: _Secao) -> list[str]:
    linhas = [ln for ln in _sem_cercas(_corpo(secao)).splitlines() if ln.strip()]
    marcadores = [m.group(1) for ln in linhas if (m := _ITEM_LISTA.match(ln))]
    if marcadores:
        return marcadores
    return [p.strip() for ln in linhas for p in ln.split(",") if p.strip()]


def verificar_tags_readme(texto: str) -> ResultadoDocs:
    """Req. 8.5: exatamente as quatro tags."""
    secoes = _secoes(texto)
    i = _achar(secoes, "Tags", 2)
    if i is None:
        return ResultadoDocs((ErroDocs("tags", "Seção Tags ausente no README."),))
    tags = [t.replace("`", "").strip() for t in _itens_secao(secoes[i])]
    erros: list[ErroDocs] = []
    for t in README_TAGS:
        if t not in tags:
            erros.append(ErroDocs("tags", f"Tag ausente: {t}."))
    for t in tags:
        if t not in README_TAGS:
            erros.append(ErroDocs("tags", f"Tag não permitida: {t}."))
    if len(tags) != len(set(tags)):
        erros.append(ErroDocs("tags", "Há tags repetidas."))
    return ResultadoDocs(tuple(erros))


def verificar_licenca_readme(texto: str, raiz: Path | None = None) -> ResultadoDocs:
    """Req. 8.9: a seção de licença nomeia a MIT e referencia LICENSE; o arquivo existe."""
    erros: list[ErroDocs] = []
    secoes = _secoes(texto)
    i = _achar(secoes, "Licença", 2)
    if i is None:
        erros.append(ErroDocs("licenca", "Seção Licença ausente no README."))
    else:
        corpo = _corpo(secoes[i])
        if "MIT" not in corpo:
            erros.append(ErroDocs("licenca", "A seção Licença não nomeia a licença MIT."))
        if CAMINHO_LICENSE not in corpo:
            erros.append(ErroDocs("licenca", "A seção Licença não referencia o arquivo LICENSE."))
    if raiz is not None:
        arquivo = Path(raiz) / CAMINHO_LICENSE
        if not arquivo.is_file() or not arquivo.read_text(encoding="utf-8").strip():
            erros.append(ErroDocs("licenca:arquivo", "O arquivo LICENSE não existe ou está vazio."))
    return ResultadoDocs(tuple(erros))


def verificar_readme(texto: str, raiz: Path) -> ResultadoDocs:
    return (
        verificar_secoes_readme(texto)
        .somar(verificar_tags_readme(texto))
        .somar(verificar_links_readme(texto, raiz))
        .somar(verificar_licenca_readme(texto, raiz))
    )


# --------------------------------------------------------------------------- #
# Resultado de cenário e divergências (Property 16 e 17)
# --------------------------------------------------------------------------- #


def consolidar_verificacoes(execucoes: Sequence[Execucao]) -> dict[str, bool]:
    """Critério -> aprovado em todas as execuções que o registram."""
    consolidado: dict[str, bool] = {}
    for e in execucoes:
        for criterio, aprovado in e.verificacoes.items():
            consolidado[criterio] = consolidado.get(criterio, True) and bool(aprovado)
    return consolidado


def resultado_cenario(
    checklist: Mapping[str, bool],
    verificacoes: Mapping[str, bool] | None = None,
    divergencia_comportamento: bool = False,
) -> ResultadoCenario:
    """Reprovado se algum item do checklist ou verificação reprovar (Req. 10.4, 10.6).

    `divergencia_comportamento` marca cenário de resposta vazia/fora de contexto cujo
    comportamento observado diverge do esperado. Lista os itens reprovados sem repetição.
    """
    reprovados = [nome for nome, ok in checklist.items() if not ok]
    reprovados += [nome for nome, ok in (verificacoes or {}).items() if not ok]
    if divergencia_comportamento:
        reprovados.append(ITEM_COMPORTAMENTO)
    unicos = tuple(dict.fromkeys(reprovados))
    return ResultadoCenario(reprovado=bool(unicos), itens_reprovados=unicos)


def calcular_divergencias(
    execucoes: Sequence[Execucao],
) -> dict[str, tuple[tuple[str, str], ...]]:
    """Critérios cujo resultado difere entre execuções (Req. 10.8).

    Devolve critério -> pares (assistente, modelo) das execuções em que foi reprovado.
    Vazio quando todos os resultados coincidem.
    """
    por_criterio: dict[str, list[Execucao]] = {}
    for e in execucoes:
        for criterio in e.verificacoes:
            por_criterio.setdefault(criterio, []).append(e)
    divergencias: dict[str, tuple[tuple[str, str], ...]] = {}
    for criterio, lista in por_criterio.items():
        if len({bool(e.verificacoes[criterio]) for e in lista}) > 1:
            pares = [(e.assistente, e.modelo) for e in lista if not e.verificacoes[criterio]]
            divergencias[criterio] = tuple(dict.fromkeys(pares))
    return divergencias


def validar_execucoes(execucoes: Sequence[Execucao]) -> ResultadoDocs:
    """Toda execução tem assistente e modelo não vazios (Req. 10.2, 10.7)."""
    erros: list[ErroDocs] = []
    for n, e in enumerate(execucoes, start=1):
        if _vazio(e.assistente):
            erros.append(ErroDocs(f"execucoes[{n}].assistente", "Assistente vazio."))
        if _vazio(e.modelo):
            erros.append(ErroDocs(f"execucoes[{n}].modelo", "Modelo vazio."))
    return ResultadoDocs(tuple(erros))


def tem_multiplos_assistentes(cenario: Cenario) -> bool:
    """Mesma entrada executada em 2 ou mais assistentes distintos (Req. 10.7)."""
    execs = cenario.execucoes
    assistentes = {_norm(e.assistente) for e in execs if not _vazio(e.assistente)}
    entradas = {_norm(e.entrada) for e in execs}
    return len(assistentes) >= 2 and len(entradas) == 1


# --------------------------------------------------------------------------- #
# Registro_de_Prompts: leitura
# --------------------------------------------------------------------------- #


def _booleano(valor: str) -> bool | None:
    v = _norm(valor)
    if v in ("sim", "s", "true", "verdadeiro"):
        return True
    if v in ("nao", "n", "false", "falso"):
        return False
    return None


def _ler_execucao(secao: _Secao) -> Execucao:
    c = _campos(secao.linhas)
    verificacoes: dict[str, bool] = {}
    for linha in c.get("verificacoes", "").splitlines():
        m = _ITEM_VERIFICACAO.match(linha)
        if m:
            verificacoes[m.group(1).strip()] = m.group(2).casefold() == "aprovado"
    return Execucao(
        assistente=c.get("assistente", ""),
        modelo=c.get("modelo", ""),
        data=c.get("data", ""),
        entrada=c.get("entrada", ""),
        saida=c.get("saida", ""),
        verificacoes=verificacoes,
        esperado=c.get(COMPORTAMENTO_ESPERADO, ""),
        observado=c.get(COMPORTAMENTO_OBSERVADO, ""),
        divergiu=_booleano(c.get("divergencia de comportamento", "")),
    )


def _ler_cenario(secoes: Sequence[_Secao], i: int) -> Cenario:
    secao = secoes[i]
    m = re.match(r"^cenario\s+([^\s:]+)", _norm(secao.titulo))
    ident = re.match(r"^\S+\s+([^\s:]+)", secao.titulo.strip())
    c = _campos(secao.linhas)
    checklist: dict[str, bool] = {}
    for linha in c.get("checklist", "").splitlines():
        t = _ITEM_TAREFA.match(linha)
        if t:
            checklist[t.group(2).strip()] = t.group(1).lower() == "x"
    tecnologias = tuple(
        t.strip() for t in c.get("tecnologias", "").split(",") if t.strip() and t.strip() != "-"
    )
    execucoes = tuple(
        _ler_execucao(s)
        for s in _descendentes(secoes, i)
        if s.nivel == secao.nivel + 1 and _norm(s.titulo).startswith("execucao")
    )
    return Cenario(
        id=ident.group(1) if m and ident else "",
        cargo=c.get("cargo", ""),
        senioridade=c.get("senioridade", ""),
        tecnologias=tecnologias,
        tipo=_norm(c.get("tipo", "")),
        checklist=checklist,
        resultado=_norm(c.get("resultado", "")),
        itens_reprovados=c.get("itens reprovados", ""),
        divergencias=c.get("divergencias"),
        execucoes=execucoes,
    )


def ler_cenarios(texto: str) -> tuple[Cenario, ...]:
    """Cenários de teste do Registro, na ordem do arquivo."""
    secoes = _secoes(texto)
    pai = _achar(secoes, "Cenários de teste", 2)
    if pai is None:
        return ()
    filhos = {id(s) for s in _descendentes(secoes, pai)}
    return tuple(
        _ler_cenario(secoes, i)
        for i, s in enumerate(secoes)
        if id(s) in filhos and s.nivel == 3 and _norm(s.titulo).startswith("cenario")
    )


# --------------------------------------------------------------------------- #
# Registro_de_Prompts: verificação
# --------------------------------------------------------------------------- #


def _verificar_indice_e_fichas(
    secoes: Sequence[_Secao], raiz: Path | None, erros: list[ErroDocs]
) -> None:
    prompts = listar_prompts(raiz) if raiz is not None else ()

    i = _achar(secoes, REGISTRO_SECOES[0], 2)
    if i is not None and raiz is not None:
        texto = "\n".join(_corpo(s) for s in [secoes[i], *_descendentes(secoes, i)])
        resultado = verificar_links(
            texto, Path(raiz), Path(raiz) / "docs", prompts, rotulo="indice"
        )
        erros.extend(resultado.erros)

    i = _achar(secoes, REGISTRO_SECOES[1], 2)
    if i is None:
        return
    fichas = [s for s in _descendentes(secoes, i) if s.nivel == 3]
    minimo = max(len(prompts), 1)
    if len(fichas) < minimo:
        erros.append(
            ErroDocs("fichas", f"Há {len(fichas)} fichas de prompt; o esperado é {minimo} (Req. 7.1).")
        )
    for ficha in fichas:
        c = _campos(ficha.linhas)
        nome = ficha.titulo.strip() or "?"
        for chave, rotulo in (
            ("objetivo", "Objetivo"),
            ("tecnica", "Técnica"),
            ("versao atual", "Versão atual"),
            ("texto completo", "Texto completo"),
            ("exemplo de entrada", "Exemplo de entrada"),
            ("exemplo de saida", "Exemplo de saída"),
        ):
            if _vazio(c.get(chave)):
                erros.append(ErroDocs(f"ficha[{nome}].{chave}", f"Campo ausente na ficha: {rotulo}."))
        objetivo = c.get("objetivo", "")
        if objetivo and not 1 <= len(objetivo) <= OBJETIVO_MAX:
            erros.append(
                ErroDocs(f"ficha[{nome}].objetivo", f"Objetivo deve ter de 1 a {OBJETIVO_MAX} caracteres.")
            )
        tecnica = c.get("tecnica", "")
        if tecnica and (re.search(r"[,;/+\n]", tecnica) or re.search(r"\s(e|ou)\s", tecnica)):
            erros.append(
                ErroDocs(f"ficha[{nome}].tecnica", "A ficha deve ter exatamente uma técnica.")
            )
        versao = c.get("versao atual", "")
        if versao and not _VERSAO.match(versao.strip("` ")):
            erros.append(ErroDocs(f"ficha[{nome}].versao", "Versão atual deve ter o formato vN."))


def _verificar_comparacao(secoes: Sequence[_Secao], erros: list[ErroDocs]) -> None:
    i = _achar(secoes, REGISTRO_SECOES[2], 2)
    if i is None:
        return
    versoes = [
        s for s in _descendentes(secoes, i) if s.nivel == 3 and re.match(r"^v\d+", _norm(s.titulo))
    ]
    if len(versoes) < MIN_VERSOES_COMPARADAS:
        erros.append(
            ErroDocs(
                "comparacao.versoes",
                f"Há {len(versoes)} versões comparadas; o mínimo é {MIN_VERSOES_COMPARADAS} (Req. 7.3).",
            )
        )
    for v in versoes:
        entradas = [k for k in _campos(v.linhas) if re.fullmatch(r"entrada \d+", k)]
        if len(entradas) < MIN_ENTRADAS_POR_VERSAO:
            erros.append(
                ErroDocs(
                    f"comparacao[{v.titulo.strip()}].entradas",
                    f"A versão tem {len(entradas)} entradas de teste; o mínimo é {MIN_ENTRADAS_POR_VERSAO}.",
                )
            )
    c = _campos(secoes[i].linhas)
    adotada = c.get("versao adotada", "").strip("` ")
    if not _VERSAO.match(adotada):
        erros.append(ErroDocs("comparacao.versao_adotada", "Versão adotada ausente ou fora do formato vN."))
    if _vazio(c.get("motivo")):
        erros.append(ErroDocs("comparacao.motivo", "Motivo da versão adotada ausente."))


def _verificar_licoes(secoes: Sequence[_Secao], erros: list[ErroDocs]) -> None:
    i = _achar(secoes, REGISTRO_SECOES[3], 2)
    if i is None:
        return
    licoes = [s for s in _descendentes(secoes, i) if s.nivel == 3]
    if len(licoes) < MIN_LICOES:
        erros.append(
            ErroDocs("licoes", f"Há {len(licoes)} lições aprendidas; o mínimo é {MIN_LICOES} (Req. 7.4).")
        )
    for n, licao in enumerate(licoes, start=1):
        c = _campos(licao.linhas)
        for chave, rotulo in (("problema", "Problema"), ("correcao", "Correção")):
            if _vazio(c.get(chave)):
                erros.append(ErroDocs(f"licoes[{n}].{chave}", f"Lição {n}: campo ausente: {rotulo}."))
        if not _VERSAO.match(c.get("versao", "").strip("` ")):
            erros.append(ErroDocs(f"licoes[{n}].versao", f"Lição {n}: versão ausente ou fora do formato vN."))


def _verificar_execucao(cid: str, n: int, e: Execucao, tipo: str, erros: list[ErroDocs]) -> None:
    pre = f"cenario[{cid}].execucao[{n}]"
    for rotulo, valor in (("assistente", e.assistente), ("modelo", e.modelo)):
        if _vazio(valor):
            erros.append(ErroDocs(f"{pre}.{rotulo}", f"Cenário {cid}, execução {n}: {rotulo} vazio."))
    for rotulo, valor in (("entrada", e.entrada), ("saida", e.saida)):
        if _vazio(valor):
            erros.append(ErroDocs(f"{pre}.{rotulo}", f"Cenário {cid}, execução {n}: {rotulo} ausente."))
    if not _DATA.match(e.data) or not _data_valida(e.data):
        erros.append(ErroDocs(f"{pre}.data", f"Cenário {cid}, execução {n}: data ausente ou fora de AAAA-MM-DD."))
    if not e.verificacoes:
        erros.append(
            ErroDocs(f"{pre}.verificacoes", f"Cenário {cid}, execução {n}: nenhuma verificação aprovado/reprovado.")
        )
    if tipo in TIPOS_RESPOSTA_INVALIDA:
        if _vazio(e.esperado):
            erros.append(ErroDocs(f"{pre}.esperado", f"Cenário {cid}, execução {n}: comportamento esperado ausente."))
        if _vazio(e.observado):
            erros.append(ErroDocs(f"{pre}.observado", f"Cenário {cid}, execução {n}: comportamento observado ausente."))
        if e.divergiu is None:
            erros.append(
                ErroDocs(f"{pre}.divergencia", f"Cenário {cid}, execução {n}: informe 'Divergência de comportamento' (sim/não).")
            )


def _data_valida(data: str) -> bool:
    try:
        datetime.strptime(data, "%Y-%m-%d")
    except ValueError:
        return False
    return True


def _verificar_cenario(c: Cenario, erros: list[ErroDocs]) -> None:
    pre = f"cenario[{c.id}]"
    for rotulo, valor in (("cargo", c.cargo),):
        if _vazio(valor):
            erros.append(ErroDocs(f"{pre}.{rotulo}", f"Cenário {c.id}: campo ausente: {rotulo}."))
    if c.senioridade not in SENIORIDADES:
        erros.append(
            ErroDocs(f"{pre}.senioridade", f"Cenário {c.id}: Senioridade deve ser uma de {', '.join(SENIORIDADES)}.")
        )
    if c.tipo not in TIPOS_CENARIO:
        erros.append(
            ErroDocs(f"{pre}.tipo", f"Cenário {c.id}: Tipo deve ser um de {', '.join(TIPOS_CENARIO)}.")
        )
    if not c.execucoes:
        erros.append(ErroDocs(f"{pre}.execucoes", f"Cenário {c.id}: nenhuma execução registrada."))

    # Checklist de 5 itens (Req. 10.5).
    chaves = {_norm(nome): ok for nome, ok in c.checklist.items()}
    checklist: dict[str, bool] = {}
    for item in CHECKLIST_ITENS:
        valor = next((ok for nome, ok in chaves.items() if nome.startswith(_norm(item))), None)
        if valor is None:
            erros.append(ErroDocs(f"{pre}.checklist", f"Cenário {c.id}: item do checklist ausente: {item}."))
        else:
            checklist[item] = valor

    for n, e in enumerate(c.execucoes, start=1):
        _verificar_execucao(c.id, n, e, c.tipo, erros)

    # Resultado registrado x calculado (Req. 10.4, 10.6).
    diverge = c.tipo in TIPOS_RESPOSTA_INVALIDA and any(e.divergiu for e in c.execucoes)
    esperado = resultado_cenario(checklist, consolidar_verificacoes(c.execucoes), diverge)
    if c.resultado not in ("aprovado", "reprovado"):
        erros.append(ErroDocs(f"{pre}.resultado", f"Cenário {c.id}: Resultado deve ser aprovado ou reprovado."))
    elif c.resultado != esperado.rotulo:
        erros.append(
            ErroDocs(f"{pre}.resultado", f"Cenário {c.id}: Resultado registrado é {c.resultado}, mas o calculado é {esperado.rotulo}.")
        )
    elif esperado.reprovado:
        registrado = _norm(c.itens_reprovados)
        for item in esperado.itens_reprovados:
            if _norm(item) not in registrado:
                erros.append(
                    ErroDocs(f"{pre}.itens_reprovados", f"Cenário {c.id}: item reprovado não listado: {item}.")
                )

    # Divergências entre execuções (Req. 10.8).
    if len(c.execucoes) >= 2:
        divergencias = calcular_divergencias(c.execucoes)
        registro = c.divergencias
        if registro is None or _vazio(registro):
            erros.append(
                ErroDocs(f"{pre}.divergencias", f"Cenário {c.id}: campo Divergências ausente (use 'nenhuma' se não houver).")
            )
        elif not divergencias:
            if _norm(registro) not in ("nenhuma", "nenhum", "nao ha"):
                erros.append(
                    ErroDocs(f"{pre}.divergencias", f"Cenário {c.id}: não há divergências; registre 'nenhuma'.")
                )
        else:
            texto = _norm(registro)
            for criterio, pares in divergencias.items():
                if _norm(criterio) not in texto:
                    erros.append(
                        ErroDocs(f"{pre}.divergencias", f"Cenário {c.id}: divergência não registrada: {criterio}.")
                    )
                    continue
                for assistente, modelo in pares:
                    if _norm(assistente) not in texto or _norm(modelo) not in texto:
                        erros.append(
                            ErroDocs(
                                f"{pre}.divergencias",
                                f"Cenário {c.id}: '{criterio}' deve indicar assistente '{assistente}' e modelo '{modelo}'.",
                            )
                        )


def _chave_perfil(c: Cenario) -> tuple[str, str, tuple[str, ...]]:
    return (_norm(c.cargo), _norm(c.senioridade), tuple(sorted(_norm(t) for t in c.tecnologias)))


def _verificar_cenarios(secoes: Sequence[_Secao], texto: str, erros: list[ErroDocs]) -> tuple[Cenario, ...]:
    cenarios = ler_cenarios(texto)
    if not MIN_CENARIOS <= len(cenarios) <= MAX_CENARIOS:
        erros.append(
            ErroDocs(
                "cenarios",
                f"Há {len(cenarios)} cenários; o esperado é de {MIN_CENARIOS} a {MAX_CENARIOS} (Req. 10.1).",
            )
        )
    ids = [c.id for c in cenarios]
    for ident in dict.fromkeys(i for i in ids if ids.count(i) > 1):
        erros.append(ErroDocs("cenarios.id", f"Identificador de cenário repetido: {ident}."))
    for c in cenarios:
        if not c.id:
            erros.append(ErroDocs("cenarios.id", "Cenário sem identificador."))
        _verificar_cenario(c, erros)
    perfis = [_chave_perfil(c) for c in cenarios]
    if len(set(perfis)) != len(perfis):
        erros.append(ErroDocs("cenarios.perfil", "Há cenários com Perfil_da_Vaga repetido (Req. 10.1)."))
    if len({c.senioridade for c in cenarios if c.senioridade in SENIORIDADES}) < MIN_SENIORIDADES:
        erros.append(
            ErroDocs("cenarios.senioridades", f"Os cenários cobrem menos de {MIN_SENIORIDADES} Senioridades (Req. 10.1).")
        )
    for tipo, rotulo in (("resposta-vazia", "resposta vazia"), ("fora-de-contexto", "resposta fora de contexto")):
        if not any(c.tipo == tipo for c in cenarios):
            erros.append(ErroDocs(f"cenarios.{tipo}", f"Falta cenário de {rotulo} (Req. 10.3)."))
    return cenarios


def _verificar_checklist_qualidade(secoes: Sequence[_Secao], erros: list[ErroDocs]) -> None:
    i = _achar(secoes, REGISTRO_SECOES[5], 2)
    if i is None:
        return
    campos = _campos(secoes[i].linhas)
    for item in CHECKLIST_ITENS:
        if _vazio(campos.get(_norm(item))):
            erros.append(
                ErroDocs("checklist", f"Item do checklist sem condição objetiva: {item} (Req. 10.5).")
            )


def _verificar_portabilidade(
    secoes: Sequence[_Secao], cenarios: Sequence[Cenario], erros: list[ErroDocs]
) -> None:
    multiplos = [c for c in cenarios if tem_multiplos_assistentes(c)]
    if not multiplos:
        erros.append(
            ErroDocs("portabilidade", "Nenhum cenário com a mesma entrada em 2 ou mais assistentes (Req. 10.7).")
        )
        return
    i = _achar(secoes, REGISTRO_SECOES[6], 2)
    if i is None:
        return
    corpo = "\n".join(_corpo(s) for s in [secoes[i], *_descendentes(secoes, i)])
    if _vazio(corpo):
        erros.append(ErroDocs("portabilidade", "A seção de portabilidade está vazia."))
    elif not any(c.id and c.id in corpo for c in multiplos):
        erros.append(
            ErroDocs("portabilidade", "A seção de portabilidade não cita nenhum cenário executado em 2 ou mais assistentes.")
        )


def verificar_registro(texto: str, raiz: Path | None = None) -> ResultadoDocs:
    """Verifica o Registro_de_Prompts conforme a convenção do docstring do módulo.

    Com `raiz`, confere também os links do índice contra os arquivos de `prompts/`.
    """
    erros: list[ErroDocs] = []
    secoes = _secoes(texto)
    for nome in REGISTRO_SECOES:
        if _achar(secoes, nome, 2) is None:
            erros.append(ErroDocs(f"secao:{nome}", f"Seção ausente no Registro: {nome}."))
    _verificar_indice_e_fichas(secoes, raiz, erros)
    _verificar_comparacao(secoes, erros)
    _verificar_licoes(secoes, erros)
    cenarios = _verificar_cenarios(secoes, texto, erros)
    _verificar_checklist_qualidade(secoes, erros)
    _verificar_portabilidade(secoes, cenarios, erros)
    return ResultadoDocs(tuple(erros))


# --------------------------------------------------------------------------- #
# Repositório
# --------------------------------------------------------------------------- #


def verificar_documentos(raiz: Path) -> ResultadoDocs:
    """Lê README, Registro e LICENSE da raiz e aplica todas as verificações."""
    raiz = Path(raiz)
    resultado = ResultadoDocs()
    readme = raiz / CAMINHO_README
    if readme.is_file():
        resultado = resultado.somar(verificar_readme(readme.read_text(encoding="utf-8"), raiz))
    else:
        resultado = resultado.somar(
            ResultadoDocs((ErroDocs("readme", "O arquivo README.md não existe."),)).somar(
                verificar_licenca_readme("", raiz)
            )
        )
    registro = raiz / CAMINHO_REGISTRO
    if registro.is_file():
        resultado = resultado.somar(verificar_registro(registro.read_text(encoding="utf-8"), raiz))
    else:
        resultado = resultado.somar(
            ResultadoDocs((ErroDocs("registro", f"O arquivo {CAMINHO_REGISTRO} não existe."),))
        )
    return resultado
