# Registro de Prompts

Registro dos prompts do projeto IA Entrevistador: índice, fichas com objetivo, técnica, versão atual e exemplos, e também comparação de versões, lições aprendidas, cenários de teste, checklist de qualidade e portabilidade entre assistentes.

Cada prompt fica em um arquivo próprio na pasta `prompts/`, com todas as suas versões. O texto completo de cada prompt está no arquivo indicado na ficha, sem truncamento.

> **Estado do registro:** todas as seções estão preenchidas. Os resultados vêm de 12 execuções reais (EV01 a EV12) em Ollama, modelos `llama3.2:latest` e `llama3.2:1b`, registradas em `docs/evidencias/` (ver [RESUMO.md](evidencias/RESUMO.md)). Pendências: nenhum cenário de fluxo (Simulador) foi executado, nenhuma execução usou um segundo assistente (a portabilidade entre assistentes não foi testada) e as correções das lições aprendidas ainda não estão nos prompts.

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

> **Estado: preenchido (tarefa 8.2) com execuções reais.** As seis execuções (EV01 a EV06) usaram Ollama, modelo `llama3.2:latest`, temperature 0, seed 42, em 2026-11-19, com a saída bruta em `docs/evidencias/`. As verificações automáticas estão em [RESUMO.md](evidencias/RESUMO.md) e usam `tools/feedback.calcular_nota_final`. O modelo é pequeno e local, então as conclusões valem para esta amostra de três entradas e não se generalizam.

- **Versão adotada:** v2
- **Motivo:** com base nas seis execuções, nenhuma versão calculou a nota final de forma confiável: nas duas, o valor informado coincidiu com o de `calcular_nota_final` (uma casa decimal) em 0 de 3 execuções (ver células abaixo). A v2 foi mantida porque seguiu o formato novo em 3 de 3 execuções (campo Autoverificação e faixa de âncora na justificativa) e acertou a soma em EV05 e EV06 (415 / 100), enquanto a v1 acertou só em EV03. Contra a v2: em EV04 a Autoverificação escreveu "Confere" sobre uma soma errada (680 em vez de 780), EV05 e EV06 receberam as mesmas notas para entradas diferentes (A3 fora do assunto ficou em 4,15, acima do 2,85 da v1) e nenhuma versão tratou A3 como "Resposta inválida" com nota 0. A diferença entre as versões é pequena e a amostra é de três entradas num modelo pequeno. A escolha da v2 é provisória e não prova que ela avalia melhor.
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

### v1: resultados reais

Execuções do Avaliador v1. "Calculada" é a nota de `calcular_nota_final` (uma casa decimal), conforme [RESUMO.md](evidencias/RESUMO.md).

- **Entrada 1:** A1 (forte), [EV01](evidencias/EV01.md). Notas extraídas 9, 8, 7, 6, 8. Informada 6,8 (a conta escrita soma 680; a soma correta é 780). Calculada 7,8. Não confere. A nota 6,8 é igual à do exemplo few-shot do prompt. Formato: tabela, cálculo, aviso e Pontos fortes presentes, mas a Verificação STAR veio com os quatro elementos "ausente" numa pergunta Técnica, onde deveria ser omitida. Resposta válida, sem "Resposta inválida".
- **Entrada 2:** A2 (fraca), [EV02](evidencias/EV02.md). Notas extraídas 5, 6, 4, 5, 5. Informada 4 (a conta escrita soma 400; a soma correta é 500). Calculada 5,0. Não confere. Formato: igual ao de EV01, com STAR indevida em pergunta Técnica e aviso presente. A justificativa de Correção técnica diz que a resposta está correta e depois diz que não explica a diferença.
- **Entrada 3:** A3 (fora do assunto), [EV03](evidencias/EV03.md). Notas extraídas 2, 3, 3, 4, 3. Informada 2,85 (soma 285, correta). Calculada 2,9. O tool marca "não confere" só porque o valor informado tem duas casas decimais e o arredondamento para uma casa dá 2,9. Não foi tratada como "Resposta inválida" e a nota não foi 0: o modelo avaliou a resposta como fraca e escreveu uma resposta sugerida. STAR indevida e aviso presentes.

### v2: resultados reais

Execuções do Avaliador v2, mesmas entradas e mesmos parâmetros.

- **Entrada 1:** A1 (forte), [EV04](evidencias/EV04.md). Notas extraídas 9, 8, 7, 6, 8, as mesmas de EV01. Informada 6,8 (a conta escrita soma 680; a soma correta é 780). Calculada 7,8. Não confere. O campo Autoverificação está presente, mas refaz a soma em ordem inversa com resultado errado (680) e termina com "Confere", ou seja, não detectou o erro. A justificativa cita faixa de âncora, porém com faixas incoerentes com a nota (nota 9 com "Faixa 7 a 8"). STAR indevida em pergunta Técnica, aviso presente, e a primeira linha perdeu o marcador de lista.
- **Entrada 2:** A2 (fraca), [EV05](evidencias/EV05.md). Notas extraídas 4, 5, 3, 4, 5. Informada 4,15 (soma 415, correta, e a Autoverificação confere de fato). Calculada 4,2. O tool marca "não confere" por causa das duas casas decimais, e o prompt pede uma casa. Campo Autoverificação e faixas de âncora presentes. STAR indevida e aviso presente. Em Pontos fortes o modelo escreveu "A resposta é parcial", o que não é um ponto forte.
- **Entrada 3:** A3 (fora do assunto), [EV06](evidencias/EV06.md). Notas extraídas 4, 5, 3, 4, 5, idênticas às de EV05 para uma entrada diferente. Informada 4,15 (soma correta). Calculada 4,2. Não foi tratada como "Resposta inválida" e a nota não foi 0. As justificativas dizem que a resposta não aborda a pergunta, mas dão 4 e 5 mesmo assim, e Pontos fortes diz "A resposta é clara". Campo Autoverificação e aviso presentes, STAR indevida.

### Leitura da comparação

- Soma ponderada: v1 acertou a soma escrita em 1 de 3 (EV03); v2 acertou em 2 de 3 (EV05, EV06). Nas duas versões, o valor informado igual ao de `calcular_nota_final` em uma casa decimal ocorreu em 0 de 3.
- Resposta inválida: A3 foi pontuada nas duas versões (2,9 na v1 e 4,2 na v2, calculadas). Nenhuma aplicou a regra de nota 0. A v2 deu uma nota maior que a v1 para a resposta fora do assunto e igual à da resposta fraca A2.
- Formato: todas as seis saídas trazem tabela, cálculo e aviso; todas trazem a Verificação STAR em pergunta Técnica, contra a instrução de omitir. A v2 traz Autoverificação e faixa de âncora nas três execuções.
- Limite: um modelo pequeno com temperature 0 e seed 42 produz uma única amostra por célula. Não há repetição que permita medir variação.

## Lições aprendidas

> **Estado: preenchido (tarefa 8.3).** As lições vêm das execuções EV01 a EV12 em Ollama ([RESUMO.md](evidencias/RESUMO.md)). Nenhuma das correções abaixo foi escrita em `prompts/`: todas estão **pendentes** e o campo Versão indica a versão do prompt em que a correção deve entrar. A única mudança já aplicada que aparece aqui é a Autoverificação da v2 do Avaliador, que não resolveu o problema.

### Lição 1: o Gerador pede variáveis que já estavam preenchidas

- **Problema:** em EV07 e EV08 (llama3.2:latest), com cargo, Senioridade e tecnologias preenchidos, o Gerador v1 não gerou o banco. A saída pediu "os valores" das variáveis (EV07 listou os próprios valores recebidos como se estivessem ausentes). Em EV11 (llama3.2:1b), a saída repetiu os Passos 1 a 5 do prompt e parou, sem tabela. As três execuções falham em `banco.validar_banco` (0 perguntas lidas).
- **Correção:** proposta, não aplicada. Reescrever o Passo 1 como condição verificável ("só peça valores se um campo estiver vazio; caso contrário, vá direto ao Passo 3") e colocar o exemplo de saída do Passo 3 no fim do prompt, perto da geração. Depois, repetir EV07, EV08 e EV11 para medir o efeito.
- **Versão:** v2
- **Situação:** pendente (Gerador está na v1; a v2 não existe).

### Lição 2: o Avaliador erra a soma ponderada e copia a nota do exemplo

- **Problema:** em 8 das 9 execuções do Avaliador com notas extraídas (EV01 a EV06, EV09, EV10 e EV12), a nota informada não confere com `calcular_nota_final`; só EV10 confere, com todas as notas 0. Em EV03, EV05 e EV06 o motivo é só o formato (duas casas decimais, quando o prompt pede uma); nas demais a soma está errada. Em EV01, EV04 e EV12 a nota final é 6,8, igual à do exemplo few-shot (em EV12, para notas que somam 435). Em EV01 e EV04 a soma escrita é 680 para notas que somam 780. Em EV09 a soma escrita é 375 para notas que somam 435. A Autoverificação da v2 escreveu "Confere" sobre a conta errada em EV04 e EV09.
- **Correção:** proposta, não aplicada. A tentativa da v2 (segunda conta em ordem inversa) não funcionou no modelo testado. Fazer o cálculo fora do modelo: o Avaliador devolve só as cinco notas e `tools/feedback.calcular_nota_final` calcula a nota final. Trocar os valores do exemplo few-shot por valores que não terminem em 6,8.
- **Versão:** v3
- **Situação:** pendente.

### Lição 3: resposta em branco ou fora do assunto não vira "Resposta inválida"

- **Problema:** em EV09 (resposta só com espaços, tabs e quebras de linha) o Avaliador v2 avaliou como se houvesse texto: notas 4, 6, 3, 4, 5, justificativas sobre trechos que não existem e nota 3,75, sem o bloco "Resposta inválida". Em EV10 (resposta sobre filme e lasanha) a nota foi 0, mas no formato de avaliação completo, com justificativa "Vazia." (a resposta não estava vazia), sem Status, sem Motivo e sem pedido de reenvio. A v1 e a v2 também pontuaram A3 (EV03: 2,9; EV06: 4,2).
- **Correção:** proposta, não aplicada. Fazer a checagem de resposta em branco antes de chamar o modelo (já existe `feedback.resposta_em_branco`, que retornou verdadeiro em EV09) e devolver o bloco "Resposta inválida" sem passar pelo Avaliador. Para resposta fora do assunto, pedir ao modelo uma classificação isolada (válida, parcial, inválida) antes da avaliação.
- **Versão:** v3
- **Situação:** pendente.

### Lição 4: a Verificação STAR aparece em pergunta Técnica

- **Problema:** o prompt diz para omitir a Verificação STAR fora de perguntas Comportamentais, mas ela aparece em 8 das 9 execuções do Avaliador (EV01 a EV06, EV09 e EV10 em perguntas Técnicas; EV12 não traz o campo). Em EV01 a v1 marca os quatro elementos como "ausente"; em EV10 escreve "Nenhuma informação". A v2 manteve o problema.
- **Correção:** proposta, não aplicada. Manter dois modelos de saída separados (Técnica/Situacional e Comportamental) em vez de uma regra de omissão no meio do formato, ou remover o campo da saída do modelo por pós-processamento.
- **Versão:** v3
- **Situação:** pendente.

## Cenários de teste

> **Estado: preenchido (tarefa 8.3) com execuções reais.** Os cinco cenários usam as execuções EV05 a EV12 (Ollama, `llama3.2:latest` e `llama3.2:1b`, temperature 0, seed 42, 2026-11-19), com a saída bruta em `docs/evidencias/`. Pendente: nenhum cenário de **fluxo** (Simulador de Entrevista) foi executado, e por isso não há cenário desse tipo aqui. As execuções EV01 a EV04 e EV06 não viraram cenário porque repetem o Perfil_da_Vaga de A2 e o Registro exige perfis distintos; elas estão na comparação de versões. Os critérios são os do [Checklist de qualidade](#checklist-de-qualidade). Quando a saída não traz o que o critério mede (por exemplo, sem tabela de perguntas), o critério fica reprovado.

### Cenário G1: Gerador, Desenvolvedor Backend Júnior

- **Cargo:** Desenvolvedor Backend
- **Senioridade:** Júnior
- **Tecnologias:** C#, ASP.NET Core, SQL Server
- **Tipo:** padrao
- **Checklist:**
  - [ ] Relevância das perguntas
  - [ ] Aderência à Senioridade
  - [ ] Formato de saída
  - [ ] Coerência das notas
  - [ ] Clareza do Feedback
- **Resultado:** reprovado
- **Itens reprovados:** Relevância das perguntas; Aderência à Senioridade; Formato de saída; Coerência das notas; Clareza do Feedback
- **Divergências:** nenhuma

#### Execução 1

- **Assistente:** Ollama
- **Modelo:** llama3.2:latest
- **Data:** 2026-11-19
- **Entrada:** Gerador v1 com cargo Desenvolvedor Backend, Senioridade Júnior, tecnologias C#, ASP.NET Core, SQL Server, idioma e descrição não informados. Evidência: [EV07](evidencias/EV07.md).
- **Saída:** o modelo respondeu "Passo 1. Variáveis sem valor" e pediu os valores de Desenvolvedor Backend, Júnior, C#, ASP.NET Core, SQL Server, idioma e descrição, que já estavam preenchidos. Sem tabela e sem verificação de contagem. `banco.validar_banco`: inválido, 0 perguntas lidas ("Nenhuma tabela Markdown encontrada").
- **Verificações:**
  - Relevância das perguntas: reprovado
  - Aderência à Senioridade: reprovado
  - Formato de saída: reprovado
  - Coerência das notas: reprovado
  - Clareza do Feedback: reprovado

#### Execução 2

- **Assistente:** Ollama
- **Modelo:** llama3.2:1b
- **Data:** 2026-11-19
- **Entrada:** a mesma de EV07: Gerador v1 com cargo Desenvolvedor Backend, Senioridade Júnior, tecnologias C#, ASP.NET Core, SQL Server, idioma e descrição não informados. Evidência: [EV11](evidencias/EV11.md).
- **Saída:** o modelo repetiu o texto dos Passos 1 a 5 do prompt (1283 tokens gerados) e parou, sem pergunta e sem tabela de perguntas. `banco.validar_banco`: inválido, 0 perguntas lidas ("Colunas inválidas", pois a única tabela lida foi a de regras do prompt, com as colunas campo e regra).
- **Verificações:**
  - Relevância das perguntas: reprovado
  - Aderência à Senioridade: reprovado
  - Formato de saída: reprovado
  - Coerência das notas: reprovado
  - Clareza do Feedback: reprovado

### Cenário G2: Gerador, Analista de Dados Pleno

- **Cargo:** Analista de Dados
- **Senioridade:** Pleno
- **Tecnologias:** SQL, Power BI, Python
- **Tipo:** padrao
- **Checklist:**
  - [ ] Relevância das perguntas
  - [ ] Aderência à Senioridade
  - [ ] Formato de saída
  - [ ] Coerência das notas
  - [ ] Clareza do Feedback
- **Resultado:** reprovado
- **Itens reprovados:** Relevância das perguntas; Aderência à Senioridade; Formato de saída; Coerência das notas; Clareza do Feedback

#### Execução 1

- **Assistente:** Ollama
- **Modelo:** llama3.2:latest
- **Data:** 2026-11-19
- **Entrada:** Gerador v1 com cargo Analista de Dados, Senioridade Pleno, tecnologias SQL, Power BI, Python, idioma e descrição não informados. Evidência: [EV08](evidencias/EV08.md).
- **Saída:** saudação e pedido dos valores de cargo, senioridade, tecnologias e idioma, todos já informados (exceto o idioma, que é opcional). Sem tabela e sem verificação de contagem. `banco.validar_banco`: inválido, 0 perguntas lidas.
- **Verificações:**
  - Relevância das perguntas: reprovado
  - Aderência à Senioridade: reprovado
  - Formato de saída: reprovado
  - Coerência das notas: reprovado
  - Clareza do Feedback: reprovado

### Cenário A2: Avaliador, resposta fraca de Desenvolvedor Back-end Pleno

- **Cargo:** Desenvolvedor Back-end
- **Senioridade:** Pleno
- **Tecnologias:** C#, SQL Server
- **Tipo:** padrao
- **Checklist:**
  - [ ] Relevância das perguntas
  - [x] Aderência à Senioridade
  - [ ] Formato de saída
  - [ ] Coerência das notas
  - [ ] Clareza do Feedback
- **Resultado:** reprovado
- **Itens reprovados:** Relevância das perguntas; Formato de saída; Coerência das notas; Clareza do Feedback
- **Divergências:**
  - Relevância das perguntas: reprovado em Ollama, modelo llama3.2:1b (aprovado em Ollama, modelo llama3.2:latest)

#### Execução 1

- **Assistente:** Ollama
- **Modelo:** llama3.2:latest
- **Data:** 2026-11-19
- **Entrada:** Avaliador v2, pergunta Técnica "Qual a diferença entre INNER JOIN e LEFT JOIN?" e resposta fraca A2: "O INNER JOIN junta tabelas e o LEFT JOIN também junta, só que de um jeito diferente. Os dois são usados em consultas." Evidência: [EV05](evidencias/EV05.md).
- **Saída:** tabela com notas 4, 5, 3, 4, 5 e faixas de âncora, cálculo, Autoverificação, nota final 4,15 (soma 415, correta), pontos de melhoria, resposta sugerida e aviso. A Verificação STAR aparece em pergunta Técnica. Em Pontos fortes consta "A resposta é parcial". `calcular_nota_final` dá 4,2 e marca "não confere" porque a nota informada tem duas casas decimais.
- **Verificações:**
  - Relevância das perguntas: aprovado
  - Aderência à Senioridade: aprovado
  - Formato de saída: reprovado
  - Coerência das notas: reprovado
  - Clareza do Feedback: reprovado

#### Execução 2

- **Assistente:** Ollama
- **Modelo:** llama3.2:1b
- **Data:** 2026-11-19
- **Entrada:** a mesma de EV05: Avaliador v2, pergunta Técnica "Qual a diferença entre INNER JOIN e LEFT JOIN?" e resposta fraca A2. Evidência: [EV12](evidencias/EV12.md).
- **Saída:** texto corrido com uma tabela de critérios (notas 6, 5, 4, 3, 2), sem Cálculo, sem Autoverificação, sem aviso e sem Verificação STAR. Informa nota final 6,8, igual à do exemplo few-shot. `calcular_nota_final` dá 4,4. A resposta sugerida abre com "Na API de pedidos", trecho do exemplo do prompt, e repete a mesma frase várias vezes.
- **Verificações:**
  - Relevância das perguntas: reprovado
  - Aderência à Senioridade: aprovado
  - Formato de saída: reprovado
  - Coerência das notas: reprovado
  - Clareza do Feedback: reprovado

### Cenário V1: Avaliador, resposta em branco de Engenheiro de Dados Sênior

- **Cargo:** Engenheiro de Dados
- **Senioridade:** Sênior
- **Tecnologias:** Python, Spark, Airflow
- **Tipo:** resposta-vazia
- **Checklist:**
  - [ ] Relevância das perguntas
  - [ ] Aderência à Senioridade
  - [ ] Formato de saída
  - [ ] Coerência das notas
  - [ ] Clareza do Feedback
- **Resultado:** reprovado
- **Itens reprovados:** Relevância das perguntas; Aderência à Senioridade; Formato de saída; Coerência das notas; Clareza do Feedback; comportamento esperado e observado divergem

#### Execução 1

- **Assistente:** Ollama
- **Modelo:** llama3.2:latest
- **Data:** 2026-11-19
- **Entrada:** Avaliador v2, pergunta Técnica "Como você garante a idempotência de um pipeline de dados em lote?" e resposta só com espaços, tabs e quebras de linha. Evidência: [EV09](evidencias/EV09.md).
- **Comportamento esperado:** bloco "Resposta inválida" (Status, Nota final 0, Motivo, Próximo passo pedindo o reenvio) e nenhuma avaliação dos critérios.
- **Comportamento observado:** o modelo avaliou como se houvesse resposta. Notas 4, 6, 3, 4, 5, justificativas sobre conteúdo que não existe, nota final 3,75 (soma escrita 375; a soma correta é 435 e `calcular_nota_final` dá 4,4), Autoverificação "Confere" sobre a conta errada, Verificação STAR com quatro "ausente" em pergunta Técnica e resposta sugerida circular. Sem "Resposta inválida" e sem pedido de reenvio. `feedback.resposta_em_branco` da entrada retorna verdadeiro.
- **Divergência de comportamento:** sim
- **Saída:** ver o comportamento observado e a saída bruta em EV09.
- **Verificações:**
  - Relevância das perguntas: reprovado
  - Aderência à Senioridade: reprovado
  - Formato de saída: reprovado
  - Coerência das notas: reprovado
  - Clareza do Feedback: reprovado

### Cenário F1: Avaliador, resposta fora de contexto de Analista de Dados Júnior

- **Cargo:** Analista de Dados
- **Senioridade:** Júnior
- **Tecnologias:** SQL, Power BI
- **Tipo:** fora-de-contexto
- **Checklist:**
  - [x] Relevância das perguntas
  - [x] Aderência à Senioridade
  - [ ] Formato de saída
  - [x] Coerência das notas
  - [ ] Clareza do Feedback
- **Resultado:** reprovado
- **Itens reprovados:** Formato de saída; Clareza do Feedback; comportamento esperado e observado divergem

#### Execução 1

- **Assistente:** Ollama
- **Modelo:** llama3.2:latest
- **Data:** 2026-11-19
- **Entrada:** Avaliador v2, pergunta Técnica "O que é uma chave primária em um banco de dados relacional?" e resposta "Ontem eu assisti a um filme de ficção científica muito bom e depois fui jantar com a minha família. A receita de lasanha estava ótima." Evidência: [EV10](evidencias/EV10.md).
- **Comportamento esperado:** bloco "Resposta inválida" (Status, Nota final 0, Motivo de a resposta não tratar da pergunta, Próximo passo pedindo o reenvio).
- **Comportamento observado:** nota final 0, mas no formato de avaliação completo. Os cinco critérios receberam 0 com a justificativa "Vazia.", embora a resposta não estivesse vazia. Não há Status, Motivo nem pedido de reenvio. O modelo escreveu uma resposta sugerida (correta e curta, adequada a Júnior) e uma Verificação STAR "Nenhuma informação" em pergunta Técnica. `calcular_nota_final` confere (0,0).
- **Divergência de comportamento:** sim
- **Saída:** ver o comportamento observado e a saída bruta em EV10.
- **Verificações:**
  - Relevância das perguntas: aprovado
  - Aderência à Senioridade: aprovado
  - Formato de saída: reprovado
  - Coerência das notas: aprovado
  - Clareza do Feedback: reprovado

## Checklist de qualidade

> **Estado: preenchido (tarefa 8.3).** Cada item vale para o Gerador e para o Avaliador. Um item é aprovado só se a condição for cumprida pela saída; se a saída não traz o que a condição mede, o item é reprovado.

- **Relevância das perguntas:** Gerador: as 10 perguntas tratam do cargo informado, as Técnicas usam ao menos uma das tecnologias informadas e nenhum tema se repete. Avaliador: o Feedback trata da pergunta e da resposta enviadas e não reproduz trechos do exemplo few-shot do prompt (como a nota 6,8 ou "API de pedidos").
- **Aderência à Senioridade:** Gerador: ao menos 5 das 10 perguntas têm a dificuldade predominante da Senioridade (Júnior: Básico; Pleno: Intermediário; Sênior: Avançado). Avaliador: para Pleno, Sênior e Especialista, os pontos de melhoria cobram trade-offs e exemplos reais; para Estagiário e Júnior, basta cobrar correção e clareza.
- **Formato de saída:** Gerador: `banco.validar_banco` aceita a tabela (cinco colunas, 10 linhas) e há o bloco de verificação de contagem. Avaliador: a saída traz a tabela de critérios, o Cálculo, a Nota final, Pontos fortes, Pontos de melhoria, Resposta sugerida e o Aviso; a Verificação STAR aparece só em pergunta Comportamental; resposta inválida usa o bloco Status, Nota final 0, Motivo, Próximo passo e Aviso.
- **Coerência das notas:** Gerador: as contagens do bloco de verificação coincidem com a tabela. Avaliador: a nota final informada é igual à de `tools/feedback.calcular_nota_final` (soma ponderada com pesos 30/20/20/15/15, uma casa decimal) e a Autoverificação não confirma uma soma errada.
- **Clareza do Feedback:** Gerador: a saída é utilizável sem edição (sem pedir dados já informados e sem repetir o texto do prompt). Avaliador: cada campo contém o que o nome pede (Pontos fortes listam qualidades da resposta, Pontos de melhoria listam ações), as justificativas citam o que a resposta de fato contém e, em resposta inválida, o Motivo é verdadeiro e há pedido de reenvio.

## Portabilidade entre assistentes

> **Estado: preenchido de forma parcial (tarefa 8.3).** Todas as execuções usaram um único assistente, o Ollama, em dois modelos (`llama3.2:latest` e `llama3.2:1b`). Dois modelos do mesmo assistente não são dois assistentes: **a portabilidade entre assistentes ainda não foi testada.** Pendente: repetir A2 e G1 em um segundo Assistente_de_IA (por exemplo, um assistente de chat na nuvem) com a mesma entrada. Enquanto isso não ocorre, a verificação de `tools/docs_md.py` que exige 2 assistentes distintos continua falhando.

O que as execuções mostram é a diferença entre modelos, com a mesma entrada, o mesmo prompt e os mesmos parâmetros (temperature 0, seed 42):

- **Cenário A2 (Avaliador v2, EV05 contra EV12):** em `llama3.2:latest`, Relevância e Aderência aprovadas; Formato, Coerência e Clareza reprovados. Em `llama3.2:1b`, só a Aderência foi aprovada. A Relevância foi reprovada por reproduzir o exemplo few-shot (nota 6,8 e "API de pedidos"). O Formato foi reprovado nos dois modelos, pela Verificação STAR em pergunta Técnica no `latest` e pela falta de Cálculo, Autoverificação e Aviso no `1b`. A Coerência foi reprovada nos dois: 4,15 informado contra 4,2 calculado no `latest` (só pelas casas decimais), e 6,8 informado contra 4,4 calculado no `1b`. Única divergência de critério: Relevância das perguntas.
- **Cenário G1 (Gerador v1, EV07 contra EV11):** os cinco critérios foram reprovados nos dois modelos, sem divergência, por causas diferentes: o `latest` pediu variáveis já preenchidas e o `1b` repetiu o texto do prompt. Nenhum dos dois gerou perguntas.

Conclusões e limites: o `llama3.2:1b` seguiu o formato pior que o `latest` no Avaliador e falhou igual no Gerador. Cada célula é uma única execução, sem repetição, e os dois modelos são da mesma família, de modo que isso não permite concluir nada sobre outros assistentes.
