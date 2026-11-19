"""Teste de propriedade: estrutura do Banco_de_Perguntas (Req. 2.1 a 2.4, 2.7)."""

from hypothesis import given, settings, strategies as st

from tools.banco import (
    CATEGORIAS,
    COLUNAS,
    DIFICULDADE_POR_SENIORIDADE,
    DIFICULDADES,
    RESPOSTA_MAX,
    TOTAL_INICIAL,
    validar_banco,
)

_texto = st.text(
    alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyzáçãéõ ABC0123456789?,."),
    min_size=1,
    max_size=40,
).filter(lambda s: s.strip() != "").map(str.strip)

_resposta = st.one_of(
    _texto,
    st.just("r" * RESPOSTA_MAX),  # limite exato permitido
)

_senioridade = st.sampled_from(sorted(DIFICULDADE_POR_SENIORIDADE))


def _renderizar(linhas, colunas=COLUNAS):
    saida = ["| " + " | ".join(colunas) + " |", "|" + "---|" * len(colunas)]
    for l in linhas:
        saida.append("| " + " | ".join(l) + " |")
    return "\n".join(saida)


@st.composite
def _bancos(draw, total=TOTAL_INICIAL, categorias=None, n_predominante=None, senioridade=None):
    """Gera linhas (como listas de 5 células) para uma Senioridade.

    Por padrão o banco é válido; os parâmetros permitem violar a distribuição.
    """
    senior = senioridade or draw(_senioridade)
    predominante = DIFICULDADE_POR_SENIORIDADE[senior]
    outras = [d for d in DIFICULDADES if d != predominante]

    if categorias is None:
        base = list(CATEGORIAS) * 2
        extra = draw(st.lists(st.sampled_from(CATEGORIAS), min_size=total - 6, max_size=total - 6))
        categorias = draw(st.permutations(base + extra))

    if n_predominante is None:
        n_predominante = draw(st.integers(5, total))
    dificuldades = [predominante] * n_predominante + [
        draw(st.sampled_from(outras)) for _ in range(total - n_predominante)
    ]
    dificuldades = draw(st.permutations(dificuldades))

    linhas = [
        [str(i), draw(_texto), categorias[i - 1], dificuldades[i - 1], draw(_resposta)]
        for i in range(1, total + 1)
    ]
    return senior, linhas


def _com_erro(resultado, trecho):
    return (not resultado.valido) and any(trecho in e for e in resultado.erros)


# Feature: ia-entrevistador, Property 3: Estrutura do Banco_de_Perguntas
# **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.7**
@settings(max_examples=100)
@given(_bancos())
def test_banco_valido_e_aceito(dados):
    senior, linhas = dados
    r = validar_banco(_renderizar(linhas), senior)
    assert r.valido, r.erros
    assert len(r.perguntas) == TOTAL_INICIAL


# Feature: ia-entrevistador, Property 3: Estrutura do Banco_de_Perguntas
# **Validates: Requirements 2.7**
@settings(max_examples=100)
@given(_bancos(), st.integers(0, 4), st.sampled_from(["trocar", "remover", "renomear"]))
def test_colunas_invalidas_sao_rejeitadas(dados, indice, modo):
    senior, linhas = dados
    colunas = list(COLUNAS)
    if modo == "trocar":
        colunas[indice], colunas[(indice + 1) % 5] = colunas[(indice + 1) % 5], colunas[indice]
    elif modo == "renomear":
        colunas[indice] = "xyz"
    else:
        del colunas[indice]
        linhas = [[c for j, c in enumerate(l) if j != indice] for l in linhas]
    r = validar_banco(_renderizar(linhas, colunas), senior)
    assert _com_erro(r, "Colunas inválidas")


# Feature: ia-entrevistador, Property 3: Estrutura do Banco_de_Perguntas
# **Validates: Requirements 2.1**
@settings(max_examples=100)
@given(st.data(), st.integers(6, 20).filter(lambda n: n != TOTAL_INICIAL))
def test_total_de_linhas_diferente_de_dez_e_rejeitado(data, total):
    senior, linhas = data.draw(_bancos(total=total))
    r = validar_banco(_renderizar(linhas), senior)
    assert _com_erro(r, f"esperado {TOTAL_INICIAL}")


# Feature: ia-entrevistador, Property 3: Estrutura do Banco_de_Perguntas
# **Validates: Requirements 2.2, 2.3**
@settings(max_examples=100)
@given(_bancos(), st.integers(0, TOTAL_INICIAL - 1), st.sampled_from(["categoria", "dificuldade"]),
       _texto.filter(lambda s: s not in CATEGORIAS and s not in DIFICULDADES))
def test_categoria_ou_dificuldade_fora_do_conjunto_e_rejeitada(dados, i, campo, invalido):
    senior, linhas = dados
    linhas[i][2 if campo == "categoria" else 3] = invalido
    r = validar_banco(_renderizar(linhas), senior)
    assert _com_erro(r, f"{campo} '{invalido}' inválida")


# Feature: ia-entrevistador, Property 3: Estrutura do Banco_de_Perguntas
# **Validates: Requirements 2.3**
@settings(max_examples=100)
@given(_bancos(), st.integers(0, TOTAL_INICIAL - 1), st.booleans(), st.integers(1, 300))
def test_resposta_vazia_ou_acima_do_limite_e_rejeitada(dados, i, vazia, excesso):
    senior, linhas = dados
    linhas[i][4] = "" if vazia else "r" * (RESPOSTA_MAX + excesso)
    r = validar_banco(_renderizar(linhas), senior)
    assert _com_erro(r, "resposta de referência vazia" if vazia else "excede")


# Feature: ia-entrevistador, Property 3: Estrutura do Banco_de_Perguntas
# **Validates: Requirements 2.2**
@st.composite
def _bancos_categoria_escassa(draw):
    escassa = draw(st.sampled_from(CATEGORIAS))
    qtd = draw(st.integers(0, 1))
    outras = [c for c in CATEGORIAS if c != escassa]
    # Mantém as outras categorias com pelo menos 2 cada.
    categorias = [escassa] * qtd + outras * 2
    categorias += [draw(st.sampled_from(outras)) for _ in range(TOTAL_INICIAL - len(categorias))]
    categorias = draw(st.permutations(categorias))
    senior, linhas = draw(_bancos(categorias=categorias))
    return escassa, qtd, senior, linhas


@settings(max_examples=100)
@given(_bancos_categoria_escassa())
def test_categoria_com_menos_de_duas_perguntas_e_rejeitada(dados):
    escassa, qtd, senior, linhas = dados
    r = validar_banco(_renderizar(linhas), senior)
    assert _com_erro(r, f"Categoria {escassa} tem {qtd} perguntas")


# Feature: ia-entrevistador, Property 3: Estrutura do Banco_de_Perguntas
# **Validates: Requirements 2.4**
@settings(max_examples=100)
@given(st.data(), _senioridade, st.integers(0, 4))
def test_dificuldade_predominante_abaixo_de_cinco_e_rejeitada(data, senior, qtd):
    _, linhas = data.draw(_bancos(n_predominante=qtd, senioridade=senior))
    r = validar_banco(_renderizar(linhas), senior)
    predominante = DIFICULDADE_POR_SENIORIDADE[senior]
    assert _com_erro(r, f"Dificuldade {predominante} tem {qtd} perguntas")


# Feature: ia-entrevistador, Property 3: Estrutura do Banco_de_Perguntas
# **Validates: Requirements 2.1, 2.7**
@settings(max_examples=100)
@given(_bancos(), st.integers(0, TOTAL_INICIAL - 1))
def test_numeracao_fora_de_sequencia_e_rejeitada(dados, i):
    senior, linhas = dados
    linhas[i][0] = str(i + 50)
    r = validar_banco(_renderizar(linhas), senior)
    assert _com_erro(r, "fora da sequência")
