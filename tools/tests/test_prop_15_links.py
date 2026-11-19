"""Teste de propriedade: links relativos do README (Req. 8.4, 8.8)."""

import tempfile
from pathlib import Path

from hypothesis import given, settings, strategies as st

from tools.docs_md import CAMINHO_REGISTRO, verificar_links_readme


@st.composite
def _cenario(draw):
    """Árvore de arquivos e README com links válidos, omitidos e quebrados."""
    n_prompts = draw(st.integers(0, 4))
    prompts = [f"prompts/prompt-{i}.md" for i in range(n_prompts)]
    linkar_prompts = [draw(st.booleans()) for _ in prompts]
    linkar_registro = draw(st.booleans())
    n_extras = draw(st.integers(0, 3))
    extras_ok = [f"docs/extra-{i}.md" for i in range(n_extras)]
    n_quebrados = draw(st.integers(0, 3))
    quebrados = [f"docs/inexistente-{i}.md" for i in range(n_quebrados)]
    # Externos e âncoras devem ser ignorados.
    ignorados = draw(
        st.lists(
            st.sampled_from(
                ["https://example.com/x.md", "mailto:a@b.com", "#secao", "http://x.org/y"]
            ),
            max_size=3,
        )
    )
    return prompts, linkar_prompts, linkar_registro, extras_ok, quebrados, ignorados


# Feature: ia-entrevistador, Property 15: Links relativos do README
# Validates: Requirements 8.4, 8.8
@settings(max_examples=100, deadline=None)
@given(_cenario())
def test_links_relativos_do_readme(cenario):
    prompts, linkar_prompts, linkar_registro, extras_ok, quebrados, ignorados = cenario
    with tempfile.TemporaryDirectory() as tmp:
        raiz = Path(tmp)
        for rel in [*prompts, *extras_ok, CAMINHO_REGISTRO]:
            arquivo = raiz / rel
            arquivo.parent.mkdir(parents=True, exist_ok=True)
            arquivo.write_text("# x\n", encoding="utf-8")

        alvos = [p for p, ok in zip(prompts, linkar_prompts) if ok]
        if linkar_registro:
            alvos.append(CAMINHO_REGISTRO)
        alvos += extras_ok + quebrados
        linhas = ["# Projeto", "", "Descrição."]
        linhas += [f"- [link {i}]({a})" for i, a in enumerate([*alvos, *ignorados])]
        texto = "\n".join(linhas) + "\n"

        resultado = verificar_links_readme(texto, raiz)

    faltando = [p for p, ok in zip(prompts, linkar_prompts) if not ok]
    if not linkar_registro:
        faltando.append(CAMINHO_REGISTRO)

    assert resultado.valido == (not quebrados and not faltando)
    campos = [e.campo for e in resultado.erros]
    assert campos.count("link") == len(quebrados)
    assert sorted(c for c in campos if c.startswith("link:")) == sorted(
        f"link:{f}" for f in faltando
    )
