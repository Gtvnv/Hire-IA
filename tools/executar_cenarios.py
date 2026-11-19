"""Executa os prompts reais contra um servidor Ollama e grava evidências (tarefa 12.4).

Somente biblioteca padrão para a chamada HTTP (urllib). Lê o texto dos prompts em
``prompts/*.md`` (seções ``## Prompt vN``), preenche as variáveis ``{{nome}}``,
chama ``/api/chat`` com temperature 0 e seed fixa e salva, para cada execução, um
arquivo Markdown em ``docs/evidencias/`` com a entrada completa e a saída bruta,
sem edição. Ao final grava ``docs/evidencias/RESUMO.md`` com a tabela de execuções
e as verificações automáticas calculadas por ``tools/banco.py`` e
``tools/feedback.py``.

Uso: python tools/executar_cenarios.py [--url http://localhost:11434] [--somente ID,...]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from tools import banco, feedback  # noqa: E402
from tools.prompts_md import extrair_prompts  # noqa: E402

PASTA_PROMPTS = RAIZ / "prompts"
PASTA_EVIDENCIAS = RAIZ / "docs" / "evidencias"
ASSISTENTE = "Ollama"
MODELO_3B = "llama3.2:latest"
MODELO_1B = "llama3.2:1b"
SEED = 42
TEMPERATURA = 0
NUM_CTX = 8192
NUM_PREDICT = 2500
TIMEOUT_S = 3600

ARQUIVOS = {
    "Gerador": "gerador-de-perguntas.md",
    "Avaliador": "avaliador-de-respostas.md",
    "Simulador": "simulador-de-entrevista.md",
}

# ---------------------------------------------------------------- entradas

PERGUNTA_JOIN = "Qual a diferença entre INNER JOIN e LEFT JOIN?"

RESPOSTAS_A = {
    "A1": (
        "INNER JOIN devolve só as linhas com correspondência nas duas tabelas. LEFT JOIN "
        "devolve todas as linhas da tabela da esquerda e preenche com NULL as colunas da "
        "direita quando não há correspondência. Na prática, uso LEFT JOIN para listar "
        "clientes mesmo sem pedidos, e filtro por `pedido.Id IS NULL` para achar quem nunca "
        "comprou. Um cuidado é que um filtro na tabela da direita dentro do WHERE "
        "transforma o LEFT JOIN em INNER JOIN; nesse caso o filtro vai na cláusula ON. Em "
        "tabelas grandes, índices nas colunas de junção evitam varreduras completas."
    ),
    "A2": (
        "O INNER JOIN junta tabelas e o LEFT JOIN também junta, só que de um jeito "
        "diferente. Os dois são usados em consultas."
    ),
    "A3": (
        "Eu gosto de trabalhar em equipe e acho que a comunicação é a base de qualquer "
        "projeto. Também estou estudando inglês para crescer na carreira."
    ),
}

CONTEXTO_A = {
    "cargo": "Desenvolvedor Back-end",
    "senioridade": "Pleno",
    "tecnologias": "C#, SQL Server",
    "idioma": "não informado",
    "categoria": "Técnica",
    "pergunta": PERGUNTA_JOIN,
}


@dataclass
class Execucao:
    id: str
    prompt: str  # Gerador | Avaliador | Simulador
    versao: int
    modelo: str
    descricao: str
    variaveis: dict[str, str]
    # preenchidos na execução
    texto_entrada: str = ""
    saida: str = ""
    erro: str = ""
    inicio_utc: str = ""
    duracao_s: float = 0.0
    meta: dict = field(default_factory=dict)
    retentativa: bool = False

    @property
    def arquivo(self) -> str:
        return f"{self.id}.md"


def montar_execucoes() -> list[Execucao]:
    runs: list[Execucao] = []

    def add(prompt, versao, modelo, descricao, variaveis):
        runs.append(
            Execucao(f"EV{len(runs) + 1:02d}", prompt, versao, modelo, descricao, variaveis)
        )

    # (a) Avaliador v1 e v2 em A1, A2, A3 (llama3.2:latest)
    for versao in (1, 2):
        for aid, resposta in RESPOSTAS_A.items():
            add(
                "Avaliador", versao, MODELO_3B,
                f"Entrada {aid} do Registro (comparação de versões)",
                {**CONTEXTO_A, "resposta_do_candidato": resposta, "_entrada": aid},
            )

    # (b) cenários da tarefa 8.3 (Avaliador v2, versão atual)
    add(
        "Gerador", 1, MODELO_3B, "Banco para Desenvolvedor Backend Júnior",
        {"cargo": "Desenvolvedor Backend", "senioridade": "Júnior",
         "tecnologias": "C#, ASP.NET Core, SQL Server", "idioma": "não informado",
         "descricao_da_vaga": "não informada", "_entrada": "G1"},
    )
    add(
        "Gerador", 1, MODELO_3B, "Banco para Analista de Dados Pleno",
        {"cargo": "Analista de Dados", "senioridade": "Pleno",
         "tecnologias": "SQL, Power BI, Python", "idioma": "não informado",
         "descricao_da_vaga": "não informada", "_entrada": "G2"},
    )
    add(
        "Avaliador", 2, MODELO_3B, "Resposta vazia (apenas espaços, tabs e quebras de linha)",
        {"cargo": "Engenheiro de Dados", "senioridade": "Sênior",
         "tecnologias": "Python, Spark, Airflow", "idioma": "não informado",
         "categoria": "Técnica",
         "pergunta": "Como você garante a idempotência de um pipeline de dados em lote?",
         "resposta_do_candidato": "   \n\t  \n   ", "_entrada": "V1"},
    )
    add(
        "Avaliador", 2, MODELO_3B, "Resposta fora de contexto",
        {"cargo": "Analista de Dados", "senioridade": "Júnior",
         "tecnologias": "SQL, Power BI", "idioma": "não informado",
         "categoria": "Técnica",
         "pergunta": "O que é uma chave primária em um banco de dados relacional?",
         "resposta_do_candidato": (
             "Ontem eu assisti a um filme de ficção científica muito bom e depois "
             "fui jantar com a minha família. A receita de lasanha estava ótima."
         ),
         "_entrada": "F1"},
    )

    # (c) portabilidade: mesma entrada em llama3.2:1b
    g1 = runs[6]
    add("Gerador", 1, MODELO_1B, f"Mesma entrada de {g1.id} (portabilidade)", dict(g1.variaveis))
    a2 = runs[4]  # A2 v2? índice 3..5 = A1..A3 v2 -> A2 v2 é runs[4]
    add("Avaliador", 2, MODELO_1B, f"Mesma entrada de {a2.id} (portabilidade)", dict(a2.variaveis))
    return runs


# ----------------------------------------------------------------- prompt

_RE_VAR = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


def texto_do_prompt(nome: str, versao: int) -> str:
    md = (PASTA_PROMPTS / ARQUIVOS[nome]).read_text(encoding="utf-8")
    prompts = extrair_prompts(md)
    if versao not in prompts:
        raise KeyError(f"{ARQUIVOS[nome]} não tem '## Prompt v{versao}'")
    return prompts[versao]


def preencher(texto: str, variaveis: dict[str, str]) -> str:
    def troca(m: re.Match[str]) -> str:
        return variaveis.get(m.group(1), m.group(0))

    return _RE_VAR.sub(troca, texto)


# ----------------------------------------------------------------- ollama

def _http_json(url: str, corpo: dict | None, timeout: float) -> dict:
    dados = None if corpo is None else json.dumps(corpo).encode("utf-8")
    req = urllib.request.Request(
        url, data=dados, headers={"Content-Type": "application/json"},
        method="GET" if corpo is None else "POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (URL do operador)
        return json.loads(resp.read().decode("utf-8"))


def esperar_servidor(base: str, tentativas: int = 60) -> None:
    ultimo = None
    for _ in range(tentativas):
        try:
            _http_json(f"{base}/api/tags", None, 10)
            return
        except Exception as exc:  # noqa: BLE001
            ultimo = exc
            time.sleep(5)
    raise RuntimeError(f"Ollama indisponível em {base}: {ultimo}")


def digests(base: str) -> dict[str, str]:
    try:
        tags = _http_json(f"{base}/api/tags", None, 30)
    except Exception:  # noqa: BLE001
        return {}
    return {m["name"]: m.get("digest", "") for m in tags.get("models", [])}


def executar(run: Execucao, base: str, mapa_digest: dict[str, str]) -> None:
    run.texto_entrada = preencher(texto_do_prompt(run.prompt, run.versao), run.variaveis)
    run.meta["digest"] = mapa_digest.get(run.modelo, "")
    corpo = {
        "model": run.modelo,
        "messages": [{"role": "user", "content": run.texto_entrada}],
        "stream": False,
        "options": {
            "temperature": TEMPERATURA, "seed": SEED,
            "num_ctx": NUM_CTX, "num_predict": NUM_PREDICT,
        },
    }
    run.inicio_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    t0 = time.monotonic()
    try:
        resp = _http_json(f"{base}/api/chat", corpo, TIMEOUT_S)
        run.saida = resp.get("message", {}).get("content", "")
        run.meta["done_reason"] = resp.get("done_reason", "")
        run.meta["prompt_eval_count"] = resp.get("prompt_eval_count")
        run.meta["eval_count"] = resp.get("eval_count")
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        run.erro = f"{type(exc).__name__}: {exc}"
    run.duracao_s = time.monotonic() - t0


# --------------------------------------------------------------- evidências

def _cerca(texto: str) -> str:
    maior = max((len(m) for m in re.findall(r"`+", texto)), default=0)
    return "`" * max(3, maior + 1)


def _bloco(texto: str) -> str:
    c = _cerca(texto)
    return f"{c}text\n{texto}\n{c}"


def gravar_evidencia(run: Execucao) -> None:
    PASTA_EVIDENCIAS.mkdir(parents=True, exist_ok=True)
    vars_exibidas = {k: v for k, v in run.variaveis.items() if not k.startswith("_")}
    linhas = [
        f"# {run.id}: {run.prompt} v{run.versao} em {run.modelo}",
        "",
        f"- **Identificador:** {run.id}",
        f"- **Prompt e versão:** {run.prompt} v{run.versao} ({ARQUIVOS[run.prompt]})",
        f"- **Descrição:** {run.descricao}",
        f"- **Assistente de IA:** {ASSISTENTE}",
        f"- **Modelo (tag exata):** {run.modelo}",
        f"- **Digest do modelo (/api/tags):** {run.meta.get('digest') or 'indisponível'}",
        f"- **Data e hora (início, UTC):** {run.inicio_utc}",
        f"- **Duração:** {run.duracao_s:.1f} s",
        f"- **Parâmetros:** temperature={TEMPERATURA}, seed={SEED}, num_ctx={NUM_CTX}, "
        f"num_predict={NUM_PREDICT}, stream=false",
        f"- **Resposta do servidor:** done_reason={run.meta.get('done_reason', '')}, "
        f"prompt_eval_count={run.meta.get('prompt_eval_count')}, eval_count={run.meta.get('eval_count')}",
        f"- **Status da chamada:** {'FALHA: ' + run.erro if run.erro else 'concluída'}",
        *(["- **Retentativa:** sim. Este arquivo substitui uma tentativa anterior que falhou por "
           "timeout (~1817 s, done_reason vazio) com timeout menor; agora timeout=" + str(TIMEOUT_S) + " s."]
          if run.retentativa else []),
        "",
        "## Variáveis preenchidas",
        "",
        _bloco(json.dumps(vars_exibidas, ensure_ascii=False, indent=2)),
        "",
        "## Entrada completa (mensagem de usuário enviada, prompt já preenchido)",
        "",
        _bloco(run.texto_entrada),
        "",
        "## Saída bruta completa (sem edição)",
        "",
        _bloco(run.saida) if not run.erro else "(sem saída: a chamada falhou)",
        "",
    ]
    (PASTA_EVIDENCIAS / run.arquivo).write_text("\n".join(linhas), encoding="utf-8", newline="\n")


def carregar_evidencia(run: Execucao) -> None:
    """Recupera duração, status e saída de um EVxx.md já gravado (sem chamar o modelo)."""
    txt = (PASTA_EVIDENCIAS / run.arquivo).read_text(encoding="utf-8")
    m = re.search(r"\*\*Duração:\*\* ([\d.]+) s", txt)
    run.duracao_s = float(m.group(1)) if m else 0.0
    m = re.search(r"\*\*Status da chamada:\*\* FALHA: (.*)", txt)
    run.erro = m.group(1).strip() if m else ""
    m = re.search(r"(?<![\w])eval_count=(\w+)", txt)
    run.meta["eval_count"] = m.group(1) if m else None
    m = re.search(r"prompt_eval_count=(\w+)", txt)
    run.meta["prompt_eval_count"] = m.group(1) if m else None
    m = re.search(r"done_reason=(\w*)", txt)
    run.meta["done_reason"] = m.group(1) if m else ""
    cab = "## Saída bruta completa (sem edição)\n\n"
    if cab in txt and not run.erro:
        resto = txt.split(cab, 1)[1]
        primeira, corpo = resto.split("\n", 1)
        cerca = primeira[: len(primeira) - len("text")]
        run.saida = corpo.rsplit("\n" + cerca, 1)[0]


# ------------------------------------------------------ verificações automáticas

_CRITERIOS = tuple(feedback.RUBRICA_PADRAO)
_RE_NOTA_FINAL = re.compile(r"Nota final[^\d\n]{0,12}(\d+(?:[.,]\d+)?)", re.IGNORECASE)


def verificar_gerador(run: Execucao) -> str:
    if run.erro:
        return "não aplicável (chamada falhou)"
    res = banco.validar_banco(run.saida, run.variaveis["senioridade"])
    if res.valido:
        return f"banco.validar_banco: válido ({len(res.perguntas)} perguntas)"
    erros = "; ".join(res.erros[:6]) + (f"; (+{len(res.erros) - 6} erros)" if len(res.erros) > 6 else "")
    return f"banco.validar_banco: inválido ({len(res.perguntas)} perguntas lidas). Erros: {erros}"


def extrair_notas(saida: str) -> dict[str, int] | None:
    notas: dict[str, int] = {}
    for crit in _CRITERIOS:
        m = re.search(
            rf"\|\s*\**{re.escape(crit)}\**\s*\|\s*\d+\s*%?\s*\|\s*\**(\d+)\**(?:\s*/\s*10)?\s*\|",
            saida, re.IGNORECASE,
        )
        if not m:
            return None
        notas[crit] = int(m.group(1))
    return notas


def verificar_avaliador(run: Execucao) -> str:
    if run.erro:
        return "não aplicável (chamada falhou)"
    partes: list[str] = []
    entrada = run.variaveis.get("resposta_do_candidato", "")
    if feedback.resposta_em_branco(entrada):
        partes.append("feedback.resposta_em_branco(entrada) = verdadeiro")
    informada = _RE_NOTA_FINAL.search(run.saida)
    nota_txt = informada.group(1).replace(",", ".") if informada else None
    notas = extrair_notas(run.saida)
    if notas is None:
        partes.append("cinco notas por critério: não extraível")
        partes.append(f"nota final informada: {nota_txt}" if nota_txt else "nota final: não extraível")
        return "; ".join(partes)
    try:
        calculada = feedback.calcular_nota_final(feedback.RUBRICA_PADRAO, notas)
    except ValueError as exc:
        partes.append(f"notas extraídas {list(notas.values())} inválidas para o cálculo ({exc})")
        partes.append(f"nota final informada: {nota_txt}" if nota_txt else "nota final: não extraível")
        return "; ".join(partes)
    partes.append(f"notas extraídas {list(notas.values())}; nota final calculada = {calculada}")
    if nota_txt is None:
        partes.append("nota final informada: não extraível")
    else:
        ok = feedback.conferir_nota_final(feedback.RUBRICA_PADRAO, notas, nota_txt)
        partes.append(f"nota final informada = {nota_txt}; calcular_nota_final confere: {'sim' if ok else 'não'}")
    return "; ".join(partes)


def verificar(run: Execucao) -> str:
    if run.prompt == "Gerador":
        return verificar_gerador(run)
    if run.prompt == "Avaliador":
        return verificar_avaliador(run)
    return "sem verificação determinística aplicável"


def gravar_resumo(runs: list[Execucao]) -> None:
    linhas = [
        "# Resumo das execuções",
        "",
        f"Gerado por `tools/executar_cenarios.py` em {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}. "
        f"Assistente: {ASSISTENTE}. Parâmetros: temperature={TEMPERATURA}, seed={SEED}, "
        f"num_ctx={NUM_CTX}, num_predict={NUM_PREDICT}.",
        "",
        "## Execuções",
        "",
        "| ID | Prompt | Versão | Modelo | Duração (s) | Status | Descrição | Arquivo |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in runs:
        status = "falha" if r.erro else "concluída"
        linhas.append(
            f"| {r.id} | {r.prompt} | v{r.versao} | {r.modelo} | {r.duracao_s:.1f} | {status} | "
            f"{r.descricao} | [{r.arquivo}]({r.arquivo}) |"
        )
    linhas += [
        "",
        "## Verificações automáticas",
        "",
        "Resultados calculados por `tools/banco.validar_banco` (Gerador) e por "
        "`tools/feedback.calcular_nota_final` (Avaliador). \"Não extraível\" indica que a saída "
        "não seguiu o formato esperado para a extração.",
        "",
        "| ID | Prompt | Modelo | Resultado da verificação |",
        "|---|---|---|---|",
    ]
    for r in runs:
        resultado = verificar(r).replace("|", "\\|")
        linhas.append(f"| {r.id} | {r.prompt} v{r.versao} | {r.modelo} | {resultado} |")
    linhas += [
        "",
        "## Observações calculadas a partir dos metadados e da saída",
        "",
        "| ID | done_reason | prompt_eval_count | eval_count (num_predict=" + str(NUM_PREDICT) + ") | Linhas de tabela Markdown na saída |",
        "|---|---|---|---|---|",
    ]
    for r in runs:
        tabela = sum(1 for ln in r.saida.splitlines() if ln.strip().startswith("|"))
        linhas.append(
            f"| {r.id} | {r.meta.get('done_reason') or '(vazio)'} | {r.meta.get('prompt_eval_count')} | "
            f"{r.meta.get('eval_count')} | {tabela} |"
        )
    falhas = [r for r in runs if r.erro]
    if falhas:
        linhas += ["", "## Falhas de chamada", ""]
        linhas += [f"- {r.id}: {r.erro}" for r in falhas]
    linhas.append("")
    (PASTA_EVIDENCIAS / "RESUMO.md").write_text("\n".join(linhas), encoding="utf-8", newline="\n")


# --------------------------------------------------------------------- main

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", default=os.environ.get("OLLAMA_URL", "http://localhost:11434"))
    ap.add_argument("--ids", "--somente", dest="ids", default="", help="IDs separados por vírgula (ex.: EV11,EV12); retoma só essas execuções")
    ap.add_argument("--resumo", action="store_true", help="não chama o modelo: só regrava RESUMO.md a partir dos arquivos EVxx.md existentes")
    args = ap.parse_args(argv)
    base = args.url.rstrip("/")

    runs = montar_execucoes()
    if args.resumo:
        for r in runs:
            carregar_evidencia(r)
        gravar_resumo(runs)
        return 0
    if args.ids:
        alvo = {s.strip() for s in args.ids.split(",")}
        runs = [r for r in runs if r.id in alvo]
        for r in runs:
            if (PASTA_EVIDENCIAS / r.arquivo).exists():
                r.retentativa = True

    esperar_servidor(base)
    mapa = digests(base)
    for r in runs:
        print(f"[{r.id}] {r.prompt} v{r.versao} {r.modelo} - {r.descricao}", flush=True)
        executar(r, base, mapa)
        gravar_evidencia(r)
        print(f"[{r.id}] {'FALHA ' + r.erro if r.erro else 'ok'} em {r.duracao_s:.1f}s", flush=True)
    if not args.ids:
        gravar_resumo(runs)
    return 1 if any(r.erro for r in runs) else 0


if __name__ == "__main__":
    sys.exit(main())
