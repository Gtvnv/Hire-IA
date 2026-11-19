# Registro de Prompts

Registro dos prompts do projeto IA Entrevistador: índice, fichas com objetivo, técnica, versão atual e exemplos, e (nas próximas tarefas) comparação de versões, lições aprendidas, cenários de teste, checklist de qualidade e portabilidade entre assistentes.

Cada prompt fica em um arquivo próprio na pasta `prompts/`, com todas as suas versões. O texto completo de cada prompt está no arquivo indicado na ficha, sem truncamento.

> **Estado do registro:** as seções "Índice de prompts" e "Fichas dos prompts" estão preenchidas. As demais seções são reservas e serão preenchidas com resultados de execuções reais nas tarefas 8.2 e 8.3. Nenhum resultado de execução foi registrado até agora.

## Índice de prompts

| Prompt | Papel no projeto | Versão atual | Arquivo |
|---|---|---|---|
| Gerador de Perguntas | Gerador_de_Perguntas | v1 | [prompts/gerador-de-perguntas.md](../prompts/gerador-de-perguntas.md) |
| Simulador de Entrevista | Simulador_de_Entrevista | v1 | [prompts/simulador-de-entrevista.md](../prompts/simulador-de-entrevista.md) |
| Avaliador de Respostas | Avaliador_de_Respostas | v2 | [prompts/avaliador-de-respostas.md](../prompts/avaliador-de-respostas.md) |

## Fichas dos prompts

### Gerador de Perguntas

- **Objetivo:** gerar um Banco_de_Perguntas com 10 perguntas de entrevista, classificadas por categoria e dificuldade e com resposta de referência, adaptadas ao cargo e à Senioridade informados.
- **Técnica:** Saída estruturada
- **Versão atual:** v1
- **Texto completo:** [prompts/gerador-de-perguntas.md](../prompts/gerador-de-perguntas.md), seção "Prompt v1" (texto integral, sem truncamento).
- **Exemplo de entrada:**

  ```text
  Cargo: Desenvolvedor Backend
  Senioridade: Júnior
  Tecnologias: C#, ASP.NET Core, SQL Server
  Idioma: (não informado, usa português do Brasil)
  Descrição da vaga: (não informada)
  ```

- **Exemplo de saída:**

  ```text
  Tabela Markdown com as colunas: número | pergunta | categoria | dificuldade | resposta de referência
  (10 linhas), seguida da verificação de contagem:

  - Total de perguntas: 10
  - Técnica: 5 | Comportamental: 3 | Situacional: 2
  - Básico: 6 | Intermediário: 4 | Avançado: 0
  - Dificuldade predominante da Senioridade: Básico com 6 perguntas (mínimo 5 de 10)

  Exemplo da linha 1:
  | 1 | Qual é a diferença entre uma classe e uma struct em C#? | Técnica | Básico | Classe é tipo de referência, alocada no heap e com herança; struct é tipo de valor, copiada na atribuição, indicada para dados pequenos e imutáveis e sem herança de outras structs. |
  ```

  A saída completa, com as 10 linhas, está no "Exemplo 1" do arquivo do prompt. Esse exemplo é ilustrativo e foi escrito junto com o prompt; não é resultado de execução em um Assistente_de_IA.

### Simulador de Entrevista

- **Objetivo:** conduzir uma entrevista simulada em diálogo, uma pergunta por mensagem, a partir de um Banco_de_Perguntas, avaliar cada resposta com a Rubrica e encerrar com um Relatório_Final com nota geral, notas por categoria e plano de estudo.
- **Técnica:** Restrições explícitas
- **Versão atual:** v1
- **Texto completo:** [prompts/simulador-de-entrevista.md](../prompts/simulador-de-entrevista.md), seção "Prompt v1" (texto integral, sem truncamento).
- **Exemplo de entrada:**

  ```text
  Cargo: Analista de Dados
  Senioridade: Júnior
  Tecnologias: SQL, Power BI
  Modo: treino
  Banco_de_Perguntas: 10 perguntas; a pergunta 1 é "Qual é a diferença entre INNER JOIN e LEFT JOIN?" (Técnica, Básico)
  ```

- **Exemplo de saída:**

  ```text
  - Entrevistador: Boa tarde. Meu nome é Marina Duarte e sou Gerente de Dados nesta empresa. Conduzirei esta entrevista para a vaga de Analista de Dados. A simulação está no modo treino, ou seja, você receberá o Feedback após cada resposta. Se desejar finalizar, escreva "encerrar" a qualquer momento.
  - Pergunta 1 de 10: Qual é a diferença entre INNER JOIN e LEFT JOIN?
  ```

  Os exemplos de Feedback, Relatório_Final parcial, encerramento sem respostas e assunto fora do escopo estão na seção "Exemplos" do arquivo do prompt. Esses exemplos são ilustrativos e não são resultado de execução em um Assistente_de_IA.

### Avaliador de Respostas

- **Objetivo:** avaliar a resposta de um candidato a uma pergunta de entrevista segundo uma Rubrica fixa e devolver um Feedback estruturado, com notas por critério, nota final ponderada, pontos fortes, pontos de melhoria e resposta sugerida.
- **Técnica:** Few-shot
- **Versão atual:** v2
- **Texto completo:** [prompts/avaliador-de-respostas.md](../prompts/avaliador-de-respostas.md), seção "Prompt v2" (texto integral, sem truncamento).
- **Exemplo de entrada:**

  ```text
  Cargo: Desenvolvedor Back-end
  Senioridade: Pleno
  Tecnologias: C#, SQL Server
  Categoria: Comportamental
  Pergunta: Conte sobre uma vez em que você precisou resolver um problema de desempenho em produção.
  Resposta do candidato: "No meu último projeto, a API de pedidos começou a demorar mais de 8 segundos nos horários de pico. Fiquei responsável por descobrir a causa. Analisei os logs, encontrei uma consulta sem índice e criei o índice na tabela de pedidos. Depois disso o tempo caiu para menos de 1 segundo."
  ```

- **Exemplo de saída:**

  ```text
  - Pergunta avaliada: Conte sobre uma vez em que você precisou resolver um problema de desempenho em produção.
  - Notas por critério: Correção técnica 8, Clareza 7, Profundidade 6, Estrutura da resposta 5, Exemplos práticos 7
  - Cálculo: (30 × 8 + 20 × 7 + 20 × 6 + 15 × 5 + 15 × 7) / 100 = (240 + 140 + 120 + 75 + 105) / 100 = 680 / 100 = 6,8
  - Nota final: 6,8
  - Verificação STAR: Situação, Tarefa, Ação e Resultado presentes
  - Aviso: Esta nota é uma estimativa de apoio ao estudo e não substitui a avaliação de um profissional.
  ```

  O Feedback completo (tabela com justificativas, pontos fortes, pontos de melhoria e resposta sugerida) está na seção "Formato de saída" do arquivo do prompt. É o exemplo few-shot do prompt, ilustrativo e não resultado de execução.

## Comparação de versões do Avaliador

> **Estado: parcial (tarefa 8.2).** As descrições das versões e as entradas de teste estão definidas. As execuções reais ainda não foram feitas, então nenhum resultado, nota ou versão adotada está registrado. Todas as células de resultado abaixo estão marcadas como "pendente (execução real)".

### Versões comparadas

- **v1:** texto em [prompts/avaliador-de-respostas.md](../prompts/avaliador-de-respostas.md), seção "Prompt v1". Rubrica de cinco critérios com pesos 30/20/20/15/15, escala genérica única de 0 a 10 (cinco faixas), nota final ponderada com a conta mostrada, verificação STAR para perguntas Comportamentais, tratamento de resposta inválida (vazia, só espaços ou fora do assunto) e de falha de avaliação, e um exemplo few-shot.
- **v2:** texto na seção "Prompt v2" do mesmo arquivo. Mantém a Rubrica, os pesos e o few-shot da v1 e acrescenta: (1) tabela de âncoras numéricas por critério, com uma descrição por faixa de nota; (2) autoverificação da soma ponderada, com segunda conta em ordem inversa e campo "Autoverificação" no Feedback; (3) regras para resposta parcial e tangencial, com tetos de nota, separadas da resposta inválida (sem relação com a pergunta); (4) justificativa que cita a faixa de âncora usada; (5) restrições contra notas idênticas por padrão e contra copiar os valores do exemplo.

### Entradas de teste (mesmas para as duas versões)

Contexto comum a todas as entradas: Cargo Desenvolvedor Back-end, Senioridade Pleno, Tecnologias C# e SQL Server, idioma não informado (português do Brasil).

| ID | Tipo | Categoria | Pergunta | Resposta do candidato |
|---|---|---|---|---|
| A1 | Resposta forte | Técnica | Qual a diferença entre INNER JOIN e LEFT JOIN? | "INNER JOIN devolve só as linhas com correspondência nas duas tabelas. LEFT JOIN devolve todas as linhas da tabela da esquerda e preenche com NULL as colunas da direita quando não há correspondência. Na prática, uso LEFT JOIN para listar clientes mesmo sem pedidos, e filtro por `pedido.Id IS NULL` para achar quem nunca comprou. Um cuidado é que um filtro na tabela da direita dentro do WHERE transforma o LEFT JOIN em INNER JOIN; nesse caso o filtro vai na cláusula ON. Em tabelas grandes, índices nas colunas de junção evitam varreduras completas." |
| A2 | Resposta fraca | Técnica | Qual a diferença entre INNER JOIN e LEFT JOIN? | "O INNER JOIN junta tabelas e o LEFT JOIN também junta, só que de um jeito diferente. Os dois são usados em consultas." |
| A3 | Resposta fora do assunto | Técnica | Qual a diferença entre INNER JOIN e LEFT JOIN? | "Eu gosto de trabalhar em equipe e acho que a comunicação é a base de qualquer projeto. Também estou estudando inglês para crescer na carreira." |

Para uma quarta entrada opcional (parcial), usar a mesma pergunta com uma resposta que explica só o INNER JOIN. Ela não é obrigatória para a tarefa 8.2 e, se for usada, deve ser registrada como A4 com o texto exato executado.

### Resultados por versão

Preencher com a saída real de cada execução (nota final, notas por critério, se a conta confere, se o formato foi seguido). Informar também o Assistente_de_IA, o modelo e a data de cada execução.

| ID | Resultado v1 | Resultado v2 |
|---|---|---|
| A1 (forte) | pendente (execução real) | pendente (execução real) |
| A2 (fraca) | pendente (execução real) | pendente (execução real) |
| A3 (fora do assunto) | pendente (execução real) | pendente (execução real) |

### Versão adotada

Pendente (execução real). Depende dos resultados da tabela acima. O motivo da escolha será registrado aqui, com base nas execuções feitas pelo usuário.

## Lições aprendidas

> **Reservado para a tarefa 8.3.** Esta seção ainda não foi preenchida. Ela receberá ao menos 3 lições, cada uma com problema, correção e versão do prompt em que a correção foi aplicada, a partir de problemas realmente observados nas execuções.

## Cenários de teste

> **Reservado para a tarefa 8.3.** Esta seção ainda não foi preenchida. Ela receberá de 3 a 20 cenários com Perfis_da_Vaga distintos e ao menos 2 Senioridades, incluindo resposta vazia, resposta fora de contexto e cenários de fluxo. Cada execução registrará identificador, entrada, saída obtida, Assistente_de_IA, modelo, data e resultado por critério, conforme a convenção descrita em `tools/docs_md.py`. Os resultados devem vir de execuções reais feitas pelo usuário.

## Checklist de qualidade

> **Reservado para a tarefa 8.3.** Esta seção ainda não foi preenchida. Ela receberá os cinco itens (relevância das perguntas, aderência à Senioridade, formato de saída, coerência das notas e clareza do Feedback), cada um com uma condição objetiva de aprovação.

## Portabilidade entre assistentes

> **Reservado para a tarefa 8.3.** Esta seção ainda não foi preenchida. Ela citará ao menos 1 cenário executado com a mesma entrada em 2 ou mais Assistentes_de_IA, com o resultado dos critérios por execução e as divergências observadas, indicando o assistente e o modelo em que cada critério foi reprovado.
