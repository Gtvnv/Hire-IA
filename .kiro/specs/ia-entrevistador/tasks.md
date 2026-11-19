# Implementation Plan: IA Entrevistador

## Overview

O projeto entrega três prompts versionados, portáteis e reutilizáveis em qualquer Assistente_de_IA baseado em conversa (por exemplo, ChatGPT, Claude, Gemini ou Copilot, citados apenas como ilustração), o Registro de Prompts, o README, a LICENSE e, opcionalmente, um validador determinístico em Python (`tools/`) com testes de propriedade (Hypothesis). A implementação segue esta ordem: estrutura do repositório, prompts, validador, documentação (Registro e README) e validação final dos artefatos reais.

Linguagem do validador: Python (conforme o design). Prompts e documentação em português do Brasil. Os prompts são texto puro em Markdown, sem recursos exclusivos de um produto (plugins, ferramentas, anexos, memória persistente ou sintaxe proprietária).

## Tasks

- [x] 1. Estrutura do repositório e licença
  - [x] 1.1 Criar a estrutura de pastas e a LICENSE
    - Criar as pastas `prompts/`, `docs/` e `tools/tests/`
    - Criar o arquivo `LICENSE` com o texto integral da licença MIT
    - _Requirements: 6.1, 7.5, 8.9_

- [x] 2. Prompt do Avaliador_de_Respostas
  - [x] 2.1 Escrever `prompts/avaliador-de-respostas.md` (v1)
    - Seguir a anatomia do design: Metadados (técnica aplicada e trecho), Variáveis (com descrição de 1 linha), Prompt v1 (Papel, Contexto, Tarefa, Restrições, Formato de saída), Exemplos e Histórico de versões
    - Definir a Rubrica (Correção técnica 30%, Clareza 20%, Profundidade 20%, Estrutura da resposta 15%, Exemplos práticos 15%) e a fórmula da nota final com exibição da conta
    - Definir os campos fixos do Feedback, a verificação STAR para perguntas comportamentais e o aviso de até 200 caracteres
    - Tratar resposta vazia, em branco ou fora do assunto (nota 0, motivo, reenvio sem avançar) e falha de avaliação ("reavaliar" sem redigitar)
    - Incluir ao menos um exemplo completo (few-shot) com pergunta, resposta e Feedback
    - Incluir as restrições de viés e privacidade (Req. 9.4 e 9.5) e o pedido de valor para variáveis ausentes
    - Manter o prompt em texto puro/Markdown, sem recursos exclusivos de um produto, para que funcione em qualquer Assistente_de_IA
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 7.1, 8.7, 9.2, 9.4, 9.5_

- [x] 3. Prompt do Gerador_de_Perguntas
  - [x] 3.1 Escrever `prompts/gerador-de-perguntas.md` (v1)
    - Seguir a mesma anatomia de arquivo do design
    - Validar o Perfil_da_Vaga no prompt: limites de cargo, tecnologias e descrição, valores de Senioridade, mensagem única de erro com todos os campos inválidos ou ausentes, preservação dos dados informados e idioma padrão
    - Gerar 10 perguntas em tabela Markdown com as colunas `número, pergunta, categoria, dificuldade, resposta de referência`, mínimo de 2 por categoria, resposta de referência de até 1.000 caracteres e tabela de distribuição de dificuldade por Senioridade, com contagem antes da entrega
    - Cobrir "mais perguntas" (5 novas, sem repetir tema, banco completo preservado), marcação "verificar em fonte oficial", falha com "tentar novamente" e uso opcional da descrição da vaga
    - Incluir as restrições de viés e privacidade e o pedido de valor para variáveis ausentes
    - Manter o prompt em texto puro/Markdown, sem recursos exclusivos de um produto (portabilidade entre Assistentes_de_IA)
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 6.2, 6.3, 6.4, 6.5, 6.7, 7.1, 9.3, 9.4, 9.5_

- [x] 4. Prompt do Simulador_de_Entrevista
  - [x] 4.1 Escrever `prompts/simulador-de-entrevista.md` (v1)
    - Seguir a mesma anatomia de arquivo do design
    - Definir a apresentação do Entrevistador_Simulado, uma pergunta por mensagem, no máximo uma pergunta de aprofundamento consecutiva e linguagem formal sem gírias, emojis ou ofensas
    - Definir os modos treino e realista, o comando "encerrar" (sem diferenciar maiúsculas), o encerramento sem respostas e o estado interno resumido para retomada após falha
    - Embutir as regras de avaliação do Avaliador_de_Respostas (Rubrica, fórmula e formato do Feedback)
    - Definir o Relatório_Final: nota geral, nota por categoria, resumo de até 1.000 caracteres, 3 pontos fortes e 3 de melhoria (200 caracteres cada, com categoria), relatório parcial com menos de 3 respostas, mensagem de ausência de dados com 0 respostas, plano de estudo de 1 a 5 tópicos ordenado e até 3 novas tentativas em falha
    - Tratar assunto fora do escopo (até 3 frases e repetição da última pergunta), falha na geração e restrições de viés e privacidade
    - Manter o prompt em texto puro/Markdown, sem recursos exclusivos de um produto (portabilidade entre Assistentes_de_IA)
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 6.2, 6.3, 6.4, 6.5, 6.7, 6.8, 7.1, 9.4, 9.5_

- [~] 5. Checkpoint - Revisar os três prompts
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Validador de artefatos (opcional, em `tools/`)
  - [x] 6.1 Preparar o projeto Python e implementar `tools/perfil.py`
    - Criar `tools/requirements.txt` (pytest, hypothesis), `tools/__init__.py` e `tools/tests/__init__.py`
    - Implementar a função pura que valida o Perfil_da_Vaga e devolve a lista completa de campos inválidos ou ausentes, com o limite excedido ou os valores aceitos de Senioridade
    - _Requirements: 1.1, 1.2, 1.4, 1.6, 2.8_

  - [x] 6.2 Escrever teste de propriedade para a validação do perfil
    - **Property 1: Validação do Perfil_da_Vaga**
    - Arquivo `tools/tests/test_prop_01_perfil.py`, mínimo de 100 iterações, geradores em torno dos limites (0, 1, 100, 101, 5.000, 5.001 e 0 a 21 itens)
    - **Validates: Requirements 1.1, 1.2, 1.6**

  - [x] 6.3 Escrever teste de propriedade para campos obrigatórios ausentes
    - **Property 2: Campos obrigatórios ausentes são todos listados**
    - Arquivo `tools/tests/test_prop_02_ausentes.py`
    - **Validates: Requirements 1.4, 2.8**

  - [x] 6.4 Implementar `tools/banco.py`
    - Interpretar a tabela Markdown do Banco_de_Perguntas e validar colunas, categorias, dificuldades, resposta de referência (até 1.000 caracteres), mínimo de 2 por categoria e mínimo de 5 na dificuldade predominante da Senioridade
    - Implementar a verificação de expansão do banco (5 linhas a mais, anteriores inalteradas e na mesma ordem)
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.6, 2.7_

  - [x] 6.5 Escrever teste de propriedade para a estrutura do banco
    - **Property 3: Estrutura do Banco_de_Perguntas**
    - Arquivo `tools/tests/test_prop_03_banco.py`, com tabelas geradas que violam cada regra
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.7**

  - [x] 6.6 Escrever teste de propriedade para a expansão do banco
    - **Property 4: Expansão do banco preserva as perguntas**
    - Arquivo `tools/tests/test_prop_04_expansao.py`
    - **Validates: Requirements 2.6**

  - [x] 6.7 Implementar `tools/feedback.py`
    - Validar a Rubrica (cinco critérios, pesos inteiros maiores que 0 somando 100)
    - Calcular a nota final ponderada `round1(soma(peso × nota) / 100)` e conferir a nota informada
    - Validar a estrutura do Feedback (notas inteiras de 0 a 10, justificativas de 1 a 3 frases, pontos, resposta sugerida, STAR para Comportamental, aviso de até 200 caracteres)
    - Implementar a regra de resposta em branco (nota 0, motivo, reenvio sem avançar)
    - _Requirements: 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 9.2_

  - [x] 6.8 Escrever teste de propriedade para os pesos da Rubrica
    - **Property 5: Pesos da Rubrica**
    - Arquivo `tools/tests/test_prop_05_rubrica.py`
    - **Validates: Requirements 4.2**

  - [x] 6.9 Escrever teste de propriedade para a nota final ponderada
    - **Property 6: Nota final ponderada**
    - Arquivo `tools/tests/test_prop_06_nota_final.py`
    - **Validates: Requirements 4.3**

  - [x] 6.10 Escrever teste de propriedade para a estrutura do Feedback
    - **Property 7: Estrutura do Feedback**
    - Arquivo `tools/tests/test_prop_07_feedback.py`
    - **Validates: Requirements 4.4, 4.5, 4.7, 9.2**

  - [x] 6.11 Escrever teste de propriedade para resposta em branco
    - **Property 8: Resposta em branco recebe nota 0**
    - Arquivo `tools/tests/test_prop_08_resposta_branca.py`, com espaços, tabs e quebras de linha
    - **Validates: Requirements 4.6**

  - [x] 6.12 Implementar `tools/relatorio.py`
    - Calcular a nota geral e a nota média por categoria (apenas categorias com resposta), com uma casa decimal
    - Validar o conteúdo do relatório conforme o número de respostas (n ≥ 3, 0 < n < 3, n = 0)
    - Ordenar o plano de estudo por nota crescente e, em empate, por nome da categoria
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [x] 6.13 Escrever teste de propriedade para as notas do relatório
    - **Property 9: Notas do Relatório_Final**
    - Arquivo `tools/tests/test_prop_09_notas_relatorio.py`
    - **Validates: Requirements 5.1**

  - [x] 6.14 Escrever teste de propriedade para o conteúdo do relatório
    - **Property 10: Conteúdo do relatório conforme o número de respostas**
    - Arquivo `tools/tests/test_prop_10_conteudo_relatorio.py`, com n = 0, 1, 2, 3 ou mais
    - **Validates: Requirements 5.2, 5.4, 5.5**

  - [x] 6.15 Escrever teste de propriedade para a ordenação do plano de estudo
    - **Property 11: Ordenação do plano de estudo**
    - Arquivo `tools/tests/test_prop_11_plano_estudo.py`, incluindo empates
    - **Validates: Requirements 5.3**

  - [x] 6.16 Implementar `tools/transcricao.py`
    - Validar as mensagens do Entrevistador_Simulado: no máximo uma pergunta nova, nenhum emoji e no máximo uma pergunta de aprofundamento consecutiva
    - _Requirements: 3.2, 3.3, 3.4_

  - [x] 6.17 Escrever teste de propriedade para o formato das mensagens do entrevistador
    - **Property 12: Regras de formato das mensagens do entrevistador**
    - Arquivo `tools/tests/test_prop_12_transcricao.py`, com mensagens contendo emojis
    - **Validates: Requirements 3.2, 3.3, 3.4**

  - [x] 6.18 Implementar `tools/prompts_md.py`
    - Validar o arquivo de prompt: cinco seções não vazias, campos de saída por nome, conjunto de variáveis `{{nome}}` igual ao listado em Variáveis (com `{{cargo}}`, `{{senioridade}}` e `{{tecnologias}}`) e exemplo completo no Avaliador
    - Validar o histórico de versões (`v1..vk` sem lacunas, data AAAA-MM-DD, motivo e resultado de 1 a 500 caracteres, texto integral) e a imutabilidade das versões anteriores entre revisões
    - _Requirements: 6.2, 6.4, 6.6, 6.7, 7.1, 7.2_

  - [x] 6.19 Escrever teste de propriedade para a conformidade do arquivo de prompt
    - **Property 13: Conformidade do arquivo de prompt**
    - Arquivo `tools/tests/test_prop_13_prompt.py`, com seções faltando e variáveis usadas e não declaradas
    - **Validates: Requirements 6.2, 6.4, 6.6, 6.7**

  - [x] 6.20 Escrever teste de propriedade para o histórico de versões
    - **Property 14: Histórico de versões**
    - Arquivo `tools/tests/test_prop_14_versoes.py`, com lacunas e alterações de versões anteriores
    - **Validates: Requirements 7.1, 7.2**

  - [x] 6.21 Implementar `tools/docs_md.py`
    - Verificar os links relativos do README (arquivo existente, link para cada prompt e para o Registro_de_Prompts) e a ordem das seções do Req. 8.1
    - Verificar o Registro_de_Prompts (contagens de versões do Avaliador, lições aprendidas e cenários, cobertura de Senioridades, cenários de resposta vazia e fora de contexto, checklist de 5 itens)
    - Verificar que cada execução de cenário registra assistente e modelo não vazios, a presença de ao menos 1 cenário executado em 2 ou mais Assistentes_de_IA e o registro de divergências (com assistente e modelo em que cada critério foi reprovado)
    - Verificar as tags exatas do README (IA, Engenharia de Prompt, IA Generativa, Assistentes de IA) e a seção de portabilidade do Registro
    - Calcular o resultado de cada cenário de teste (reprovado se algum item ou verificação reprovar, listando os itens) e verificar a existência do arquivo `LICENSE`
    - _Requirements: 7.3, 7.4, 7.6, 8.1, 8.4, 8.5, 8.8, 8.9, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8_

  - [x] 6.22 Escrever teste de propriedade para os links relativos do README
    - **Property 15: Links relativos do README**
    - Arquivo `tools/tests/test_prop_15_links.py`, com árvores de arquivos temporárias e links quebrados
    - **Validates: Requirements 8.4, 8.8**

  - [x] 6.23 Escrever teste de propriedade para o resultado de cenário de teste
    - **Property 16: Resultado de cenário de teste**
    - Arquivo `tools/tests/test_prop_16_cenario.py`
    - **Validates: Requirements 10.4, 10.6**

  - [x] 6.24 Implementar a CLI `tools/validar_artefatos.py`
    - Ligar os módulos e executar sobre `prompts/`, README, `docs/registro-de-prompts.md` e `LICENSE`
    - Listar cada verificação como aprovada ou reprovada e, em reprovação, indicar o campo ausente; sair com código diferente de zero se houver reprovação
    - _Requirements: 6.1, 7.6, 8.1, 8.5, 9.1_

  - [x] 6.25 Escrever teste de propriedade para divergências entre assistentes
    - **Property 17: Divergências entre assistentes são registradas com assistente e modelo**
    - Arquivo `tools/tests/test_prop_17_divergencias.py`, com 2 ou mais execuções, nomes de assistente e modelo variados (incluindo vazios) e casos em que todos os resultados coincidem
    - **Validates: Requirements 10.2, 10.7, 10.8**

- [~] 7. Checkpoint - Validador e testes
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Registro de Prompts
  - [x] 8.1 Criar `docs/registro-de-prompts.md` com índice e fichas
    - Índice com links relativos para cada arquivo em `prompts/`
    - Reservar a seção de portabilidade entre Assistentes_de_IA (preenchida na tarefa 8.3)
    - Ficha por prompt: objetivo (1 a 300 caracteres), texto completo, técnica (exatamente uma), exemplo de entrada, exemplo de saída e versão atual `vN`
    - _Requirements: 7.1, 7.5_

  - [~] 8.2 Criar a v2 do Avaliador e registrar a comparação de versões
    - Adicionar a v2 em `prompts/avaliador-de-respostas.md`, preservando o texto da v1 e registrando data, motivo e resultado
    - Documentar no Registro o resultado das duas versões com o mesmo conjunto de pelo menos 3 entradas de teste e a comparação textual indicando a versão adotada e o motivo
    - _Requirements: 4.8, 7.2, 7.3_

  - [~] 8.3 Registrar lições aprendidas, cenários de teste e checklist de qualidade
    - Ao menos 3 lições aprendidas com problema, correção e versão
    - De 3 a 20 cenários com Perfil_da_Vaga distintos e ao menos 2 Senioridades, incluindo resposta vazia e resposta fora de contexto, mais cenários de fluxo (encerrar, modo treino e realista, fora de escopo, variável ausente, dado sensível)
    - Para cada execução de cada cenário: identificador, entrada, saída obtida, nome do Assistente_de_IA e modelo utilizados, data, resultado por critério e comportamento esperado e observado nos casos de resposta inválida
    - Incluir ao menos 1 cenário executado com a mesma entrada em 2 ou mais Assistentes_de_IA, registrando o resultado dos critérios por execução e as divergências, com o assistente e o modelo em que cada critério foi reprovado
    - Preencher a seção de portabilidade do Registro com esse cenário e as divergências observadas
    - Checklist de 5 itens (relevância, aderência à Senioridade, formato de saída, coerência das notas, clareza) com condição objetiva e resultado por cenário
    - _Requirements: 7.4, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8_

- [x] 9. README
  - [x] 9.1 Escrever o `README.md`
    - Seções na ordem do Req. 8.1: título e descrição, objetivo, tags (exatamente IA, Engenharia de Prompt, IA Generativa e Assistentes de IA), funcionalidades, pré-requisitos, estrutura do repositório, como usar (lista numerada de 5 a 15 passos, genérica e válida para qualquer Assistente_de_IA, podendo citar assistentes específicos apenas como exemplo), exemplo de sessão (pergunta, resposta e Feedback integrais), técnicas de engenharia de prompt, resultados e aprendizados, limitações, próximos passos e licença
    - Incluir links relativos para os três prompts e para o Registro_de_Prompts
    - Incluir em Limitações as respostas incorretas da IA generativa, a revisão humana e a variação de comportamento e qualidade entre assistentes e modelos, com a subseção "Privacidade e Segurança"
    - Declarar a licença MIT e referenciar o arquivo `LICENSE`
    - Escrever tudo em português do Brasil
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.9, 9.1_

- [ ] 10. Validação final dos artefatos
  - [~] 10.1 Executar o validador sobre os artefatos reais e corrigir as reprovações
    - Rodar `python tools/validar_artefatos.py` e ajustar prompts, README e Registro até que todas as verificações sejam aprovadas
    - _Requirements: 6.1, 6.2, 6.4, 7.6, 8.4, 8.8, 10.1, 10.3_

- [~] 11. Checkpoint final
  - Ensure all tests pass, ask the user if questions arise.

- [x] 12. Melhorias pós-entrega

  - [x] 12.1 Adicionar CI e higiene do repositório
    - Criar .github/workflows/ci.yml (push e pull_request): Python 3.12, `pip install -r tools/requirements.txt`, `pytest tools/tests -q` e, em passo separado com `continue-on-error: true`, `python tools/validar_artefatos.py` (seções 8.2/8.3 do Registro dependem de execuções reais)
    - Criar `.gitattributes` (LF) e `pytest.ini` (`testpaths = tools/tests`); remover os `.gitkeep` sem uso
    - Ajustar o README (nota sobre CI e como rodar os testes) sem quebrar as verificações do README

  - [x] 12.2 Ampliar a cobertura dos testes de propriedade
    - Em `test_prop_01_perfil.py`, gerar `cargo`/`senioridade` só com espaços e verificar que são reportados como ausentes
    - Em `test_prop_11_plano_estudo.py`, cobrir relatórios parciais (n = 1 e n = 2)
## Notes

- Tarefas marcadas com `*` são opcionais e podem ser puladas para um MVP mais rápido.
- A pasta `tools/` (tarefa 6) é opcional como um todo. Sem ela, a tarefa 10.1 passa a ser uma revisão manual com o checklist do Registro.
- Cada tarefa referencia requisitos específicos para rastreabilidade.
- Os testes de propriedade validam regras determinísticas do validador, não chamadas a Assistentes_de_IA.
- Execute os testes uma única vez, sem modo watch: `pytest tools/tests --hypothesis-seed=0`.
- Cenários manuais em Assistentes_de_IA (tarefa 8.3), incluindo o cenário em 2 ou mais assistentes, dependem da execução pelo usuário; os resultados registrados devem vir de execuções reais.
- Os prompts são texto puro em Markdown, sem recursos exclusivos de um produto, para serem portáteis entre Assistentes_de_IA.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["2.1", "3.1", "6.1"] },
    { "id": 2, "tasks": ["4.1", "6.2", "6.3", "6.4", "6.7", "6.12", "6.16", "6.18", "6.21"] },
    { "id": 3, "tasks": ["6.5", "6.6", "6.8", "6.9", "6.10", "6.11", "6.13", "6.14", "6.15", "6.17", "6.19", "6.20", "6.22", "6.23", "6.24", "6.25", "8.1"] },
    { "id": 4, "tasks": ["8.2", "9.1"] },
    { "id": 5, "tasks": ["8.3"] },
    { "id": 6, "tasks": ["10.1", "12.1", "12.2"] }
  ]
}
```
