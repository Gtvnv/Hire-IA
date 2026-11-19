"""Teste de propriedade: conformidade do arquivo de prompt (Req. 6.2, 6.4, 6.6, 6.7)."""

from hypothesis import given, settings, strategies as st

from tools.prompts_md import SECOES_PROMPT, VARIAVEIS_OBRIGATORIAS, validar_arquivo_prompt

_POOL = ["cargo", "senioridade", "tecnologias", "pergunta", "resposta", "nivel", "idioma"]

_palavra = st.text(alphabet="abcdefghijklmnopqrstuvwxyzáéíóúãõç", min_size=1, max_size=8)
_trecho = st.lists(_palavra, min_size=1, max_size=5).map(" ".join)

_EXEMPLO = (
    "Exemplo: Pergunta: o que é X? Resposta do candidato: Y. "
    "Feedback: Nota final 7. Pontos fortes: clareza."
)


@st.composite
def _arquivos(draw):
    # Seções: ausente, vazia ou preenchida.
    estado = {s: draw(st.sampled_from(["ok", "ok", "ok", "vazia", "ausente"])) for s in SECOES_PROMPT}
    formato_com_campo = draw(st.booleans())
    declaradas = draw(st.sets(st.sampled_from(_POOL)))
    if draw(st.booleans()):
        declaradas |= VARIAVEIS_OBRIGATORIAS
    usadas = draw(st.sets(st.sampled_from(_POOL)))
    if draw(st.booleans()):
        usadas = set(declaradas)
    sem_descricao = draw(st.sets(st.sampled_from(sorted(declaradas)))) if declaradas else set()
    avaliador = draw(st.booleans())
    com_exemplo = draw(st.booleans())

    linhas = ["# Prompt de teste", "", "## Variáveis", ""]
    for nome in sorted(declaradas):
        desc = "" if nome in sem_descricao else draw(_trecho)
        linhas.append(f"- `{{{{{nome}}}}}`: {desc}".rstrip() if not desc else f"- `{{{{{nome}}}}}`: {desc}")
    linhas += ["", "## Prompt v1", ""]
    # Preâmbulo (antes do primeiro ###): variáveis usadas e exemplo.
    linhas.append(" ".join(f"{{{{{n}}}}}" for n in sorted(usadas)))
    if com_exemplo:
        linhas.append(_EXEMPLO)
    for secao in SECOES_PROMPT:
        if estado[secao] == "ausente":
            continue
        linhas += ["", f"### {secao}", ""]
        if estado[secao] == "vazia":
            continue
        if secao == "Formato de saída":
            linhas.append(f"- **Nota:** {draw(_trecho)}" if formato_com_campo else draw(_trecho))
        else:
            linhas.append(draw(_trecho) + ".")
    md = "\n".join(linhas) + "\n"

    esperados = set()
    for secao, est in estado.items():
        if est != "ok":
            esperados.add(secao)
    if estado["Formato de saída"] == "ok" and not formato_com_campo:
        esperados.add("Formato de saída")
    if (usadas ^ declaradas) or (VARIAVEIS_OBRIGATORIAS - declaradas) or sem_descricao:
        esperados.add("Variáveis")
    if avaliador and not com_exemplo:
        esperados.add("Exemplo")
    return md, avaliador, esperados


# Feature: ia-entrevistador, Property 13: Conformidade do arquivo de prompt
# **Validates: Requirements 6.2, 6.4, 6.6, 6.7**
@settings(max_examples=200, deadline=None)
@given(_arquivos())
def test_prop_13_conformidade_do_arquivo_de_prompt(caso):
    md, avaliador, esperados = caso
    resultado = validar_arquivo_prompt(md, avaliador=avaliador)

    # Rejeita exatamente quando há alguma violação, apontando cada campo violado.
    assert resultado.valido == (not esperados)
    assert set(resultado.campos_invalidos) == esperados


# Feature: ia-entrevistador, Property 13: Conformidade do arquivo de prompt
# **Validates: Requirements 6.2, 6.4, 6.6, 6.7**
@settings(max_examples=100, deadline=None)
@given(
    extras=st.sets(st.sampled_from(["pergunta", "resposta", "nivel", "idioma"])),
    desc=_trecho,
    corpo=_trecho,
)
def test_prop_13_variavel_usada_e_nao_declarada_e_rejeitada(extras, desc, corpo):
    declaradas = sorted(VARIAVEIS_OBRIGATORIAS)
    md = "## Variáveis\n\n" + "\n".join(f"- `{{{{{n}}}}}`: {desc}" for n in declaradas)
    md += "\n\n## Prompt v1\n\n" + " ".join(f"{{{{{n}}}}}" for n in declaradas + sorted(extras))
    for secao in SECOES_PROMPT:
        md += f"\n\n### {secao}\n\n"
        md += f"- **Campo:** {corpo}" if secao == "Formato de saída" else corpo
    resultado = validar_arquivo_prompt(md, avaliador=False)

    assert resultado.valido == (not extras)
    for nome in extras:
        assert any(f"{{{{{nome}}}}}" in e.mensagem for e in resultado.erros)
