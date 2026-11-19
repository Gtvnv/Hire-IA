"""Conformidade do arquivo de prompt e histórico de versões (Req. 6.2, 6.4, 6.6, 6.7, 7.1, 7.2).

Funções puras sobre o texto Markdown. Cada validação devolve todos os erros
de uma vez. Formato esperado (ver prompts/*.md):

- ``## Variáveis`` com itens ``- `{{nome}}`: descrição``;
- ``## Prompt vN`` com ``### Papel``, ``### Contexto``, ``### Tarefa``,
  ``### Restrições`` e ``### Formato de saída``;
- ``## Histórico de versões`` com blocos ``### vN`` e itens ``- **Data:**``,
  ``- **Motivo:**`` e ``- **Resultado:**`` (ou ``Resultado observado``).
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime
from typing import Mapping

SECOES_PROMPT = ("Papel", "Contexto", "Tarefa", "Restrições", "Formato de saída")
VARIAVEIS_OBRIGATORIAS = frozenset({"cargo", "senioridade", "tecnologias"})
ID_AVALIADOR = "avaliador-de-respostas"
CAMPO_MAX = 500

_RE_VAR_USO = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")
_RE_VAR_ITEM = re.compile(r"^\s*[-*]\s+`\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}`\s*:\s*(.*)$")
_RE_H2 = re.compile(r"^##\s+(.+?)\s*$")
_RE_H3 = re.compile(r"^###\s+(.+?)\s*$")
_RE_PROMPT_H2 = re.compile(r"^Prompt\s+v(\d+)$", re.IGNORECASE)
_RE_VERSAO_H3 = re.compile(r"^v(\d+)$", re.IGNORECASE)
_RE_CAMPO_SAIDA = re.compile(r"^\s*(?:[-*]\s+)?\*\*([^*\n]+?):\*\*", re.MULTILINE)
_RE_CAMPO_LISTA = re.compile(r"^\s*[-*]\s+([^:\n*`<]{2,60}):", re.MULTILINE)
_RE_CAMPO_TABELA = re.compile(r"^\s*\|[^|\n]+\|[^\n]*\|\s*\n\s*\|\s*:?-{3,}", re.MULTILINE)
_RE_ITEM_HIST = re.compile(r"^\s*[-*]\s+\*\*([^*\n]+?):\*\*\s*(.*)$")
_RE_DATA = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass(frozen=True)
class ErroPrompt:
    campo: str
    mensagem: str


@dataclass(frozen=True)
class ResultadoPrompt:
    erros: tuple[ErroPrompt, ...] = field(default_factory=tuple)

    @property
    def valido(self) -> bool:
        return not self.erros

    @property
    def campos_invalidos(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(e.campo for e in self.erros))


@dataclass(frozen=True)
class EntradaHistorico:
    versao: int
    data: str
    motivo: str
    resultado: str


# ---------------------------------------------------------------- parsing

def _norm(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFD", texto)
    sem_acento = "".join(c for c in sem_acento if unicodedata.category(c) != "Mn")
    return sem_acento.casefold().strip()


def _blocos(linhas: list[str], regex: re.Pattern[str]) -> list[tuple[str, list[str]]]:
    """Divide as linhas em blocos iniciados por um título que casa com regex."""
    blocos: list[tuple[str, list[str]]] = []
    atual: tuple[str, list[str]] | None = None
    em_codigo = False
    for linha in linhas:
        if linha.lstrip().startswith("```"):
            em_codigo = not em_codigo
        m = None if em_codigo else regex.match(linha)
        if m:
            atual = (m.group(1), [])
            blocos.append(atual)
        elif atual is not None:
            atual[1].append(linha)
    return blocos


def _h2(md: str) -> list[tuple[str, list[str]]]:
    return _blocos(md.splitlines(), _RE_H2)


def _secao_h2(md: str, titulo: str) -> list[str] | None:
    alvo = _norm(titulo)
    for t, corpo in _h2(md):
        if _norm(t) == alvo:
            return corpo
    return None


def extrair_variaveis_declaradas(md: str) -> dict[str, str]:
    """Variáveis da seção Variáveis: nome -> descrição (pode ser vazia)."""
    corpo = _secao_h2(md, "Variáveis") or []
    out: dict[str, str] = {}
    for linha in corpo:
        m = _RE_VAR_ITEM.match(linha)
        if m:
            out.setdefault(m.group(1), m.group(2).strip())
    return out


def extrair_prompts(md: str) -> dict[int, str]:
    """Texto integral de cada seção ``## Prompt vN`` (sem espaços nas pontas)."""
    out: dict[int, str] = {}
    for titulo, corpo in _h2(md):
        m = _RE_PROMPT_H2.match(titulo.strip())
        if m:
            out[int(m.group(1))] = "\n".join(corpo).strip()
    return out


def extrair_secoes_prompt(texto_prompt: str) -> dict[str, str]:
    """Subseções ``###`` de um prompt: título normalizado -> texto."""
    return {
        _norm(t): "\n".join(c).strip()
        for t, c in _blocos(texto_prompt.splitlines(), _RE_H3)
    }


def extrair_historico(md: str) -> list[tuple[int, dict[str, str]]]:
    """Blocos ``### vN`` do histórico: (versão, {campo normalizado: valor})."""
    corpo = _secao_h2(md, "Histórico de versões")
    if corpo is None:
        return []
    out: list[tuple[int, dict[str, str]]] = []
    for titulo, linhas in _blocos(corpo, _RE_H3):
        m = _RE_VERSAO_H3.match(titulo.strip())
        if not m:
            continue
        campos: dict[str, str] = {}
        ultimo: str | None = None
        for linha in linhas:
            mi = _RE_ITEM_HIST.match(linha)
            if mi:
                ultimo = _norm(mi.group(1))
                campos.setdefault(ultimo, mi.group(2).strip())
            elif ultimo and linha.startswith((" ", "\t")) and linha.strip():
                campos[ultimo] = (campos[ultimo] + " " + linha.strip()).strip()
            else:
                ultimo = None
        out.append((int(m.group(1)), campos))
    return out


def _identificador(md: str) -> str | None:
    m = re.search(r"\*\*Identificador:\*\*\s*(\S+)", md)
    return m.group(1) if m else None


# ------------------------------------------------------------ conformidade

def _tem_exemplo_completo(md: str, prompt: str) -> bool:
    texto = _norm(prompt + "\n" + (("\n".join(_secao_h2(md, "Exemplos") or []))))
    return all(
        chave in texto
        for chave in ("pergunta", "resposta do candidato", "nota final", "pontos fortes")
    )


def validar_arquivo_prompt(md: str, *, avaliador: bool | None = None) -> ResultadoPrompt:
    """Valida a conformidade estrutural do arquivo (Req. 6.2, 6.4, 6.6, 6.7).

    ``avaliador`` força ou dispensa a exigência de exemplo completo; por padrão
    é inferido do ``Identificador`` nos Metadados.
    """
    erros: list[ErroPrompt] = []
    prompts = extrair_prompts(md)
    if not prompts:
        return ResultadoPrompt((ErroPrompt("Prompt", "seção '## Prompt vN' ausente"),))
    versao = max(prompts)
    texto = prompts[versao]
    rotulo = f"Prompt v{versao}"

    secoes = extrair_secoes_prompt(texto)
    for nome in SECOES_PROMPT:
        corpo = secoes.get(_norm(nome))
        if corpo is None:
            erros.append(ErroPrompt(nome, f"seção '{nome}' ausente em {rotulo}"))
        elif not corpo.strip():
            erros.append(ErroPrompt(nome, f"seção '{nome}' vazia em {rotulo}"))

    formato = secoes.get(_norm("Formato de saída"), "")
    if formato.strip() and not (
        _RE_CAMPO_SAIDA.search(formato)
        or _RE_CAMPO_LISTA.search(formato)
        or _RE_CAMPO_TABELA.search(formato)
    ):
        erros.append(
            ErroPrompt(
                "Formato de saída",
                "nenhum campo de saída definido por nome (**Campo:**, '- Campo:' ou cabeçalho de tabela)",
            )
        )

    declaradas = extrair_variaveis_declaradas(md)
    usadas = set(_RE_VAR_USO.findall(texto))
    for nome in sorted(usadas - set(declaradas)):
        erros.append(ErroPrompt("Variáveis", f"variável {{{{{nome}}}}} usada e não declarada"))
    for nome in sorted(set(declaradas) - usadas):
        erros.append(ErroPrompt("Variáveis", f"variável {{{{{nome}}}}} declarada e não usada"))
    for nome in sorted(VARIAVEIS_OBRIGATORIAS - set(declaradas)):
        erros.append(ErroPrompt("Variáveis", f"variável obrigatória {{{{{nome}}}}} não declarada"))
    for nome, desc in declaradas.items():
        if not desc or "\n" in desc:
            erros.append(
                ErroPrompt("Variáveis", f"variável {{{{{nome}}}}} sem descrição de 1 linha")
            )

    exige_exemplo = avaliador if avaliador is not None else _identificador(md) == ID_AVALIADOR
    if exige_exemplo and not _tem_exemplo_completo(md, texto):
        erros.append(
            ErroPrompt("Exemplo", "exemplo completo (pergunta, resposta e Feedback) ausente")
        )
    return ResultadoPrompt(tuple(erros))


# ---------------------------------------------------------------- versões

def validar_historico_versoes(md: str) -> ResultadoPrompt:
    """Valida o histórico de versões (Req. 7.1, 7.2)."""
    erros: list[ErroPrompt] = []
    historico = extrair_historico(md)
    prompts = extrair_prompts(md)
    if not historico:
        return ResultadoPrompt((ErroPrompt("Histórico de versões", "nenhuma versão registrada"),))

    ids = [v for v, _ in historico]
    esperado = list(range(1, len(historico) + 1))
    if sorted(ids) != esperado:
        erros.append(
            ErroPrompt(
                "Histórico de versões",
                f"identificadores {['v%d' % i for i in ids]} não formam v1..v{len(historico)} sem lacunas",
            )
        )

    for versao, campos in historico:
        rot = f"v{versao}"
        data = campos.get("data", "")
        ok_data = bool(_RE_DATA.match(data))
        if ok_data:
            try:
                datetime.strptime(data, "%Y-%m-%d")
            except ValueError:
                ok_data = False
        if not ok_data:
            erros.append(ErroPrompt(f"{rot}.data", "data ausente ou fora do formato AAAA-MM-DD"))
        motivo = campos.get("motivo", "")
        if not 1 <= len(motivo) <= CAMPO_MAX:
            erros.append(ErroPrompt(f"{rot}.motivo", f"motivo deve ter de 1 a {CAMPO_MAX} caracteres"))
        resultado = campos.get("resultado", campos.get("resultado observado", ""))
        if not 1 <= len(resultado) <= CAMPO_MAX:
            erros.append(
                ErroPrompt(f"{rot}.resultado", f"resultado deve ter de 1 a {CAMPO_MAX} caracteres")
            )
        if not prompts.get(versao, "").strip():
            erros.append(ErroPrompt(f"{rot}.texto", f"texto integral '## Prompt {rot}' ausente ou vazio"))
    return ResultadoPrompt(tuple(erros))


def verificar_imutabilidade(anterior_md: str, novo_md: str) -> ResultadoPrompt:
    """Cada versão presente no arquivo anterior permanece idêntica no novo (Req. 7.2)."""
    antes = extrair_prompts(anterior_md)
    depois = extrair_prompts(novo_md)
    erros: list[ErroPrompt] = []
    for versao, texto in sorted(antes.items()):
        if versao not in depois:
            erros.append(ErroPrompt(f"v{versao}", f"versão v{versao} removida"))
        elif depois[versao] != texto:
            erros.append(ErroPrompt(f"v{versao}", f"texto da versão v{versao} foi alterado"))
    return ResultadoPrompt(tuple(erros))


def validar_prompt_completo(md: str, anterior_md: str | None = None) -> ResultadoPrompt:
    """Conformidade + histórico (+ imutabilidade, se houver revisão anterior)."""
    erros = list(validar_arquivo_prompt(md).erros) + list(validar_historico_versoes(md).erros)
    if anterior_md is not None:
        erros += list(verificar_imutabilidade(anterior_md, md).erros)
    return ResultadoPrompt(tuple(erros))
