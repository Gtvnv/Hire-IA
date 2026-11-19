# Registro de Prompts

Registro dos prompts do projeto IA Entrevistador: índice, fichas com objetivo, técnica, versão atual e exemplos, e (nas próximas tarefas) comparação de versões, lições aprendidas, cenários de teste, checklist de qualidade e portabilidade entre assistentes.

Cada prompt fica em um arquivo próprio na pasta `prompts/`, com todas as suas versões. O texto completo de cada prompt está no arquivo indicado na ficha, sem truncamento.

> **Estado do registro:** as seções "Índice de prompts" e "Fichas dos prompts" estão preenchidas. As demais seções são reservas e serão preenchidas com resultados de execuções reais nas tarefas 8.2 e 8.3. Nenhum resultado de execução foi registrado até agora.

## Índice de prompts

| Prompt | Papel no projeto | Versão atual | Arquivo |
|---|---|---|---|
| Gerador de Perguntas | Gerador_de_Perguntas | v1 | [prompts/gerador-de-perguntas.md](../prompts/gerador-de-perguntas.md) |
| Simulador de Entrevista | Simulador_de_Entrevista | v1 | [prompts/simulador-de-entrevista.md](../prompts/simulador-de-entrevista.md) |
| Avaliador de Respostas | Avaliador_de_Respostas | v1 | [prompts/avaliador-de-respostas.md](../prompts/avaliador-de-respostas.md) |

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
- **Versão atual:** v1
- **Texto completo:** [prompts/avaliador-de-respostas.md](../prompts/avaliador-de-respostas.md), seção "Prompt v1" (texto integral, sem truncamento).
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

> **Reservado para a tarefa 8.2.** Esta seção ainda não foi preenchida. Ela receberá a v1 e a v2 do Avaliador de Respostas, o resultado de cada versão para o mesmo conjunto de pelo menos 3 entradas de teste, a versão adotada e o motivo. Nenhum resultado foi registrado, porque a v2 ainda não existe e as execuções ainda não foram feitas.

## Lições aprendidas

> **Reservado para a tarefa 8.3.** Esta seção ainda não foi preenchida. Ela receberá ao menos 3 lições, cada uma com problema, correção e versão do prompt em que a correção foi aplicada, a partir de problemas realmente observados nas execuções.

## Cenários de teste

> **Reservado para a tarefa 8.3.** Esta seção ainda não foi preenchida. Ela receberá de 3 a 20 cenários com Perfis_da_Vaga distintos e ao menos 2 Senioridades, incluindo resposta vazia, resposta fora de contexto e cenários de fluxo. Cada execução registrará identificador, entrada, saída obtida, Assistente_de_IA, modelo, data e resultado por critério, conforme a convenção descrita em `tools/docs_md.py`. Os resultados devem vir de execuções reais feitas pelo usuário.

## Checklist de qualidade

> **Reservado para a tarefa 8.3.** Esta seção ainda não foi preenchida. Ela receberá os cinco itens (relevância das perguntas, aderência à Senioridade, formato de saída, coerência das notas e clareza do Feedback), cada um com uma condição objetiva de aprovação.

## Portabilidade entre assistentes

> **Reservado para a tarefa 8.3.** Esta seção ainda não foi preenchida. Ela citará ao menos 1 cenário executado com a mesma entrada em 2 ou mais Assistentes_de_IA, com o resultado dos critérios por execução e as divergências observadas, indicando o assistente e o modelo em que cada critério foi reprovado.
