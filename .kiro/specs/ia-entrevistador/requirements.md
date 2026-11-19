# Requirements Document

## Introduction

O IA Entrevistador é um projeto de engenharia de prompt que utiliza IA generativa e técnicas de entrevistas técnicas para simular processos seletivos. O projeto entrega um conjunto documentado de prompts reutilizáveis em qualquer assistente de IA generativa baseado em conversa (por exemplo, ChatGPT, Claude, Gemini ou Copilot), sem depender de um produto específico, que geram perguntas relevantes por cargo e senioridade, conduzem uma simulação de entrevista, avaliam as respostas do candidato com feedback estruturado e orientam a preparação do usuário. O projeto também entrega a documentação completa (README) e o registro dos prompts, com as versões, os resultados e as lições aprendidas.

Tags do projeto: IA, Engenharia de Prompt, IA Generativa, Assistentes de IA.

## Glossary

- **IA_Entrevistador**: O conjunto de prompts, fluxos e documentos que compõem o projeto.
- **Assistente_de_IA**: Qualquer assistente de IA generativa baseado em conversa em que os prompts são executados (por exemplo, ChatGPT, Claude, Gemini ou Copilot, citados apenas como ilustração).
- **Usuário**: Pessoa que utiliza o IA_Entrevistador para se preparar para um processo seletivo.
- **Candidato_Simulado**: O papel assumido pelo Usuário durante a simulação de entrevista.
- **Entrevistador_Simulado**: O papel assumido pelo Assistente_de_IA durante a simulação, conduzido por um prompt de sistema.
- **Perfil_da_Vaga**: Conjunto de informações de entrada composto por cargo, senioridade, tecnologias e, opcionalmente, descrição da vaga.
- **Senioridade**: Nível de experiência do cargo, com os valores Estagiário, Júnior, Pleno, Sênior e Especialista.
- **Gerador_de_Perguntas**: Prompt que produz o Banco_de_Perguntas a partir do Perfil_da_Vaga.
- **Banco_de_Perguntas**: Lista de perguntas geradas, cada uma com categoria, nível de dificuldade e resposta de referência.
- **Categoria_da_Pergunta**: Classificação da pergunta em Técnica, Comportamental ou Situacional.
- **Simulador_de_Entrevista**: Prompt que conduz a entrevista pergunta a pergunta, no formato de diálogo.
- **Avaliador_de_Respostas**: Prompt que avalia a resposta do Candidato_Simulado e produz o Feedback.
- **Feedback**: Resultado da avaliação, contendo nota, pontos fortes, pontos de melhoria e resposta sugerida.
- **Rubrica**: Conjunto de critérios de avaliação com pesos, usado pelo Avaliador_de_Respostas.
- **Relatório_Final**: Resumo consolidado ao final da simulação, com nota geral e plano de estudo.
- **Registro_de_Prompts**: Documento que cataloga cada prompt do projeto, com objetivo, texto, técnica aplicada, exemplo de entrada e saída, e versões.
- **README**: Documento principal do repositório, que descreve o projeto e seu uso.
- **Técnica_de_Prompt**: Técnica de engenharia de prompt aplicada, como definição de papel, few-shot, cadeia de raciocínio, saída estruturada e restrições explícitas.

## Requirements

### Requirement 1: Perfil da Vaga

**User Story:** Como Usuário, quero informar o cargo, a senioridade e as tecnologias da vaga, para que o IA_Entrevistador adapte a entrevista ao meu objetivo.

#### Acceptance Criteria

1. WHEN o Usuário envia os dados da vaga, THE IA_Entrevistador SHALL definir o Perfil_da_Vaga com os campos cargo (1 a 100 caracteres), Senioridade, tecnologias (0 a 20 itens, cada um com 1 a 50 caracteres) e idioma da entrevista.
2. IF o valor informado para Senioridade for diferente de Estagiário, Júnior, Pleno, Sênior ou Especialista, THEN THE IA_Entrevistador SHALL rejeitar o valor, manter o Perfil_da_Vaga sem alteração e exibir ao Usuário uma mensagem de erro indicando os cinco valores aceitos.
3. WHERE o Usuário fornece a descrição da vaga (1 a 5.000 caracteres), THE Gerador_de_Perguntas SHALL usar a descrição da vaga como contexto adicional na geração das perguntas.
4. IF o Usuário omite o cargo ou a Senioridade, THEN THE Gerador_de_Perguntas SHALL não gerar perguntas e SHALL solicitar ao Usuário o preenchimento de cada campo ausente, preservando os demais campos já informados.
5. WHERE o Usuário não informa o idioma da entrevista, THE IA_Entrevistador SHALL conduzir a entrevista em português do Brasil.
6. IF o cargo, a descrição da vaga ou um item de tecnologias exceder o limite de caracteres, ou a lista de tecnologias exceder 20 itens, THEN THE IA_Entrevistador SHALL rejeitar o campo excedente, manter o Perfil_da_Vaga sem alteração e exibir ao Usuário uma única mensagem de erro que liste todos os campos excedentes, cada um com o respectivo limite excedido.

### Requirement 2: Geração de Perguntas por Cargo e Senioridade

**User Story:** Como Usuário, quero receber perguntas relevantes por cargo e senioridade, para que eu treine com perguntas próximas das reais.

#### Acceptance Criteria

1. WHEN o Perfil_da_Vaga é fornecido com cargo e Senioridade preenchidos, THE Gerador_de_Perguntas SHALL gerar um Banco_de_Perguntas com exatamente 10 perguntas.
2. THE Gerador_de_Perguntas SHALL classificar cada pergunta em exatamente uma Categoria_da_Pergunta (Técnica, Comportamental ou Situacional), e o Banco_de_Perguntas SHALL conter no mínimo 2 perguntas de cada categoria.
3. THE Gerador_de_Perguntas SHALL incluir em cada pergunta exatamente um nível de dificuldade (Básico, Intermediário ou Avançado) e uma resposta de referência não vazia com no máximo 1.000 caracteres.
4. THE Gerador_de_Perguntas SHALL ajustar a distribuição de dificuldade à Senioridade informada, de modo que no mínimo 5 das 10 perguntas tenham o nível Básico para Estagiário e Júnior, Intermediário para Pleno, e Avançado para Sênior e Especialista.
5. THE Gerador_de_Perguntas SHALL gerar perguntas sem repetição de tema dentro do mesmo Banco_de_Perguntas, de modo que não existam duas perguntas abordando o mesmo tema, conceito ou competência principal.
6. WHEN o Usuário solicita mais perguntas, THE Gerador_de_Perguntas SHALL gerar 5 novas perguntas, mantendo as regras de categoria, dificuldade, resposta de referência e Senioridade, que não repetem o tema de nenhuma pergunta já existente no Banco_de_Perguntas, e SHALL adicioná-las ao Banco_de_Perguntas preservando as perguntas anteriores.
7. THE Gerador_de_Perguntas SHALL entregar o Banco_de_Perguntas em formato de tabela Markdown, com uma linha por pergunta e as colunas número, pergunta, Categoria_da_Pergunta, dificuldade e resposta de referência.
8. IF o Perfil_da_Vaga não contém cargo ou Senioridade, THEN THE Gerador_de_Perguntas SHALL rejeitar a solicitação sem gerar perguntas, exibir uma mensagem de erro indicando os campos ausentes e preservar os dados já informados pelo Usuário.
9. IF a geração do Banco_de_Perguntas falha ou não produz 10 perguntas válidas em até 60 segundos, THEN THE Gerador_de_Perguntas SHALL exibir uma mensagem de erro indicando a falha e permitir que o Usuário tente novamente sem reenviar o Perfil_da_Vaga.

### Requirement 3: Simulação de Entrevista

**User Story:** Como Usuário, quero simular uma entrevista em formato de diálogo, para que eu pratique como em um processo seletivo real.

#### Acceptance Criteria

1. WHEN o Usuário inicia a simulação, THE Simulador_de_Entrevista SHALL apresentar o Entrevistador_Simulado (nome fictício e cargo) e fazer a primeira pergunta em até 10 segundos.
2. WHILE a simulação está em andamento, THE Simulador_de_Entrevista SHALL fazer exatamente uma pergunta por mensagem e aguardar a resposta do Candidato_Simulado antes de enviar a próxima.
3. WHEN o Candidato_Simulado responde, THE Simulador_de_Entrevista SHALL enviar a próxima pergunta em até 10 segundos, sendo permitida no máximo 1 pergunta de aprofundamento consecutiva sobre a mesma resposta.
4. WHILE a simulação está em andamento, THE Simulador_de_Entrevista SHALL redigir as mensagens do Entrevistador_Simulado em linguagem formal, sem gírias, emojis ou ofensas ao Candidato_Simulado.
5. WHEN o Usuário digita o comando "encerrar" (sem diferenciar maiúsculas de minúsculas), THE Simulador_de_Entrevista SHALL interromper as perguntas, finalizar a simulação e gerar o Relatório_Final com as respostas já fornecidas.
6. WHEN o Candidato_Simulado responde à última pergunta planejada, THE Simulador_de_Entrevista SHALL finalizar a simulação e gerar o Relatório_Final.
7. WHERE o Usuário escolhe o modo treino, THE Simulador_de_Entrevista SHALL exibir o Feedback da resposta imediatamente após cada resposta e antes da próxima pergunta.
8. WHERE o Usuário escolhe o modo realista, THE Simulador_de_Entrevista SHALL omitir o Feedback durante a simulação e exibi-lo somente no Relatório_Final.
9. IF o Usuário digita "encerrar" antes de responder a primeira pergunta, THEN THE Simulador_de_Entrevista SHALL finalizar a simulação sem gerar Relatório_Final e informar que não há respostas para avaliar.
10. IF o Simulador_de_Entrevista não consegue gerar a próxima pergunta ou o Relatório_Final em até 30 segundos, THEN THE Simulador_de_Entrevista SHALL exibir uma mensagem de erro indicando a falha, preservar as respostas já fornecidas e permitir ao Usuário tentar novamente.

### Requirement 4: Avaliação de Respostas com Feedback

**User Story:** Como Usuário, quero ter minhas respostas avaliadas com feedback claro, para que eu saiba o que melhorar.

#### Acceptance Criteria

1. WHEN o Candidato_Simulado envia uma resposta a uma pergunta, THE Avaliador_de_Respostas SHALL avaliar a resposta segundo a Rubrica e apresentar o resultado em até 30 segundos após o envio.
2. THE Rubrica SHALL conter os critérios Correção técnica, Clareza, Profundidade, Estrutura da resposta e Exemplos práticos, com pesos inteiros em porcentagem, cada peso maior que 0% e a soma igual a 100%.
3. THE Avaliador_de_Respostas SHALL atribuir uma nota inteira de 0 a 10 para cada critério da Rubrica e uma nota final ponderada de 0 a 10, arredondada para uma casa decimal.
4. THE Avaliador_de_Respostas SHALL incluir no Feedback ao menos um ponto forte, ao menos um ponto de melhoria e uma resposta sugerida, cada item com no mínimo 1 frase e no máximo 1.000 caracteres.
5. WHERE a pergunta é Comportamental, THE Avaliador_de_Respostas SHALL indicar no Feedback, para cada um dos quatro elementos do método STAR (Situação, Tarefa, Ação, Resultado), se o elemento está presente ou ausente na resposta.
6. IF a resposta do Candidato_Simulado está vazia, contém apenas espaços em branco ou não aborda o assunto da pergunta, THEN THE Avaliador_de_Respostas SHALL atribuir nota final 0, exibir uma mensagem indicando o motivo da nota 0, bloquear o avanço da simulação e solicitar o reenvio da resposta para a mesma pergunta, sem descartar a avaliação anterior e sem avançar para a próxima pergunta até que uma nova resposta seja enviada.
7. THE Avaliador_de_Respostas SHALL apresentar, para cada nota de critério, uma justificativa de 1 a 3 frases que cite ao menos um trecho ou aspecto específico da resposta avaliada.
8. WHEN a mesma resposta é avaliada duas vezes com o mesmo prompt, THE Avaliador_de_Respostas SHALL produzir notas finais com diferença máxima de 1 ponto.
9. IF a avaliação falhar por indisponibilidade do serviço de avaliação ou exceder 30 segundos, THEN THE Avaliador_de_Respostas SHALL exibir uma mensagem de erro indicando que a avaliação não foi concluída, preservar a resposta enviada e permitir reenviar a avaliação sem digitar a resposta novamente.

### Requirement 5: Relatório Final e Plano de Estudo

**User Story:** Como Usuário, quero um relatório final da simulação, para que eu tenha um plano de estudo direcionado.

#### Acceptance Criteria

1. WHEN a simulação termina, THE Simulador_de_Entrevista SHALL gerar o Relatório_Final em até 10 segundos, contendo a nota geral (média aritmética das notas de todas as perguntas respondidas, de 0 a 10, com uma casa decimal), a nota média por Categoria_da_Pergunta (de 0 a 10, com uma casa decimal, apenas para categorias com pelo menos uma pergunta respondida) e um resumo do desempenho com no máximo 1.000 caracteres.
2. WHEN o Relatório_Final é gerado com pelo menos três perguntas respondidas, THE Simulador_de_Entrevista SHALL listar exatamente três pontos fortes e exatamente três pontos de melhoria do Candidato_Simulado, cada um com no máximo 200 caracteres e vinculado a uma Categoria_da_Pergunta.
3. WHEN o Relatório_Final é gerado, THE Simulador_de_Entrevista SHALL incluir um plano de estudo com de 1 a 5 tópicos, ordenados da menor para a maior nota média da Categoria_da_Pergunta correspondente, e, em caso de empate de nota, na ordem alfabética do nome da categoria.
4. IF o Candidato_Simulado respondeu a menos de três perguntas, THEN THE Simulador_de_Entrevista SHALL marcar o Relatório_Final como parcial com uma indicação visível no início do relatório, listar apenas os pontos fortes e de melhoria que as respostas disponíveis sustentam (de 0 a 2 de cada tipo) e preservar a nota geral e as notas por categoria calculadas.
5. IF o Candidato_Simulado respondeu a zero perguntas quando a simulação termina, THEN THE Simulador_de_Entrevista SHALL exibir uma mensagem indicando que não há dados para gerar o Relatório_Final e não SHALL gerar nota geral, notas por categoria nem plano de estudo.
6. IF a geração do Relatório_Final falhar ou exceder 10 segundos, THEN THE Simulador_de_Entrevista SHALL exibir uma mensagem de erro indicando a falha, preservar as respostas e as notas da simulação e permitir até 3 novas tentativas de geração.

### Requirement 6: Engenharia de Prompt

**User Story:** Como desenvolvedor do projeto, quero prompts bem projetados com técnicas de engenharia de prompt, para que os resultados sejam consistentes e reutilizáveis.

#### Acceptance Criteria

1. THE IA_Entrevistador SHALL fornecer exatamente um prompt versionado para cada uma das 3 funções: Gerador_de_Perguntas, Simulador_de_Entrevista e Avaliador_de_Respostas, totalizando 3 prompts, cada um em um arquivo de texto próprio.
2. THE IA_Entrevistador SHALL definir em cada prompt 5 seções identificadas por título: papel do Assistente_de_IA, contexto, tarefa, restrições e formato de saída, sendo que cada seção contém ao menos 1 frase não vazia.
3. THE IA_Entrevistador SHALL aplicar em cada prompt ao menos 1 Técnica_de_Prompt (por exemplo: role prompting, few-shot, chain-of-thought, saída estruturada) e registrar o nome da técnica e o trecho do prompt em que ela é aplicada em uma seção de documentação do próprio prompt.
4. THE IA_Entrevistador SHALL parametrizar os prompts com variáveis nomeadas entre chaves duplas no formato {{nome_da_variavel}}, incluindo no mínimo {{cargo}}, {{senioridade}} e {{tecnologias}}, e SHALL listar, para cada prompt, todas as variáveis usadas com uma descrição de 1 linha cada.
5. IF um prompt contém uma variável {{nome}} sem valor fornecido no momento do uso, THEN THE IA_Entrevistador SHALL solicitar ao Usuário o valor da variável ausente antes de executar o prompt e SHALL manter inalterados os valores já informados.
6. THE Avaliador_de_Respostas SHALL ter um prompt com ao menos 1 exemplo completo de avaliação (few-shot), contendo pergunta, resposta do candidato e Feedback, no mesmo formato de saída definido para o prompt.
7. THE IA_Entrevistador SHALL definir em cada prompt um formato de saída estruturado, que seja uma tabela Markdown ou uma lista com campos fixos, com os nomes dos campos ou colunas enumerados no prompt.
8. IF o Usuário solicita um assunto fora do escopo de entrevistas de emprego, THEN THE Simulador_de_Entrevista SHALL responder em até 3 frases informando que o assunto está fora do escopo e SHALL retomar a simulação repetindo a última pergunta da entrevista ainda sem resposta, preservando o histórico da simulação.

### Requirement 7: Registro e Versionamento dos Prompts

**User Story:** Como desenvolvedor do projeto, quero documentar a evolução dos prompts, para que seja possível comparar versões e justificar as decisões.

#### Acceptance Criteria

1. THE Registro_de_Prompts SHALL conter, para cada prompt, os campos obrigatórios: objetivo (1 a 300 caracteres), texto completo do prompt sem truncamento, Técnica_de_Prompt aplicada (exatamente 1 nome por prompt, conforme definido no Glossário), exemplo de entrada (mínimo 1), exemplo de saída correspondente ao exemplo de entrada (mínimo 1) e identificador de versão no formato "vN" (N inteiro maior ou igual a 1).
2. WHEN um prompt é alterado, THE Registro_de_Prompts SHALL registrar uma nova versão com identificador incrementado em 1 em relação à anterior, data de alteração no formato AAAA-MM-DD, motivo da mudança (1 a 500 caracteres) e resultado observado (1 a 500 caracteres), preservando integralmente o texto das versões anteriores.
3. THE Registro_de_Prompts SHALL documentar ao menos 2 versões do prompt do Avaliador_de_Respostas, apresentando para cada versão o resultado obtido com o mesmo conjunto de entradas de teste (mínimo 3 entradas) e uma comparação textual indicando qual versão foi adotada e por quê.
4. THE Registro_de_Prompts SHALL conter uma seção de lições aprendidas com ao menos 3 entradas, cada uma indicando o problema encontrado, a correção aplicada e a versão do prompt em que a correção foi aplicada.
5. THE Registro_de_Prompts SHALL armazenar cada prompt em um arquivo próprio, com 1 prompt por arquivo, dentro da pasta de prompts do repositório, incluindo todas as versões desse prompt no mesmo arquivo.
6. IF um prompt ou uma versão não contiver algum dos campos obrigatórios definidos nos critérios 1 e 2, THEN THE Registro_de_Prompts SHALL ser considerado incompleto, e o campo ausente SHALL ser indicado na revisão da documentação antes da entrega.

### Requirement 8: Documentação do Projeto (README)

**User Story:** Como visitante do repositório, quero um README completo, para que eu entenda e use o projeto sem ajuda externa.

#### Acceptance Criteria

1. THE README SHALL conter, em títulos de seção distintos e nesta ordem, as seções: título e descrição, objetivo, tags, funcionalidades, pré-requisitos, estrutura do repositório, como usar, exemplo de sessão, técnicas de engenharia de prompt, resultados e aprendizados, limitações, próximos passos e licença.
2. THE README SHALL apresentar o passo a passo de uso em qualquer Assistente_de_IA em lista numerada, com no mínimo 5 e no máximo 15 passos, cobrindo desde a colagem do prompt em uma conversa nova até a obtenção do Relatório_Final, podendo citar assistentes específicos apenas como exemplo ilustrativo.
3. THE README SHALL incluir ao menos um exemplo completo de sessão contendo, nesta ordem, uma pergunta, a resposta do Candidato_Simulado e o Feedback correspondente, com o texto integral de cada um dos três itens.
4. THE README SHALL apresentar um link relativo para cada arquivo de prompt do repositório e um link relativo para o Registro_de_Prompts, cada um apontando para um arquivo existente no repositório.
5. THE README SHALL listar na seção de tags exatamente as tags IA, Engenharia de Prompt, IA Generativa e Assistentes de IA.
6. THE README SHALL estar integralmente escrito em português do Brasil, exceto nomes próprios, nomes de produtos e termos técnicos sem tradução consagrada.
7. THE README SHALL descrever, na seção de limitações, no mínimo as limitações de respostas incorretas da IA generativa, a necessidade de revisão humana das saídas antes de seu uso e a possibilidade de o comportamento e a qualidade das saídas variarem entre Assistentes_de_IA e entre modelos.
8. IF um link do README apontar para um arquivo inexistente no repositório, THEN THE README SHALL ser considerado não conforme a este requisito até que o link seja corrigido.
9. THE README SHALL declarar na seção de licença o nome da licença adotada e referenciar o arquivo de licença do repositório.

### Requirement 9: Segurança, Privacidade e Limitações

**User Story:** Como Usuário, quero que o projeto trate dados pessoais e limitações da IA com cuidado, para que eu use a ferramenta com segurança.

#### Acceptance Criteria

1. THE README SHALL conter uma seção intitulada "Privacidade e Segurança" que oriente o Usuário a não inserir nos prompts dados pessoais sensíveis (CPF, RG, endereço residencial, telefone, dados bancários, senhas, chaves de API) nem informações confidenciais de empregadores (código-fonte proprietário, dados de clientes, segredos comerciais).
2. WHEN o Avaliador_de_Respostas gera um Feedback com nota, THE Avaliador_de_Respostas SHALL incluir no Feedback um aviso de que a nota é uma estimativa de apoio ao estudo e não substitui a avaliação de um profissional, posicionado na mesma mensagem da nota e com no máximo 200 caracteres.
3. IF o Assistente_de_IA não tem segurança sobre um fato técnico ao gerar uma pergunta, THEN THE Gerador_de_Perguntas SHALL marcar a resposta de referência com o texto literal "verificar em fonte oficial" e manter a pergunta e a resposta de referência na saída.
4. THE IA_Entrevistador SHALL redigir perguntas e Feedbacks sem referência a gênero, idade, origem, etnia, religião, orientação sexual, deficiência ou estado civil do Usuário, e sem usar termos que pressuponham essas características.
5. IF o Usuário informar nos prompts uma característica pessoal listada no critério 4 ou um dado sensível listado no critério 1, THEN THE IA_Entrevistador SHALL ignorar esse dado na elaboração de perguntas e Feedbacks e incluir um lembrete de uma frase orientando a não inserir dados pessoais sensíveis.

### Requirement 10: Casos de Teste dos Prompts

**User Story:** Como desenvolvedor do projeto, quero casos de teste dos prompts, para que eu valide a qualidade das respostas do Assistente_de_IA.

#### Acceptance Criteria

1. THE Registro_de_Prompts SHALL conter no mínimo 3 e no máximo 20 cenários de teste, cada um com um Perfil_da_Vaga distinto dos demais, cobrindo no mínimo 2 Senioridades diferentes.
2. THE Registro_de_Prompts SHALL registrar para cada cenário de teste: um identificador único, a entrada fornecida ao Assistente_de_IA, a saída obtida, o nome do Assistente_de_IA e o modelo utilizados na execução, a data da execução, e o resultado (aprovado ou reprovado) da verificação de cada critério de aceitação aplicável ao prompt testado.
3. THE Registro_de_Prompts SHALL conter no mínimo 1 cenário de teste com resposta vazia (0 caracteres ou apenas espaços em branco) e no mínimo 1 cenário com resposta fora de contexto (sem relação com a pergunta feita), para validar o tratamento de erro do Avaliador_de_Respostas.
4. WHEN um cenário de teste de resposta vazia ou fora de contexto é executado, THE Registro_de_Prompts SHALL registrar o comportamento esperado (o Avaliador_de_Respostas sinaliza a resposta como inválida, em vez de atribuir uma nota como se fosse uma resposta válida) e o comportamento observado, marcando o cenário como reprovado se ambos divergirem.
5. THE Registro_de_Prompts SHALL conter um checklist de qualidade com os 5 itens: relevância das perguntas, aderência à Senioridade, formato de saída, coerência das notas e clareza do Feedback, cada um com uma condição objetiva de aprovação (verdadeiro ou falso) e um resultado marcado por cenário de teste.
6. IF um ou mais itens do checklist de qualidade forem marcados como reprovados em um cenário de teste, THEN THE Registro_de_Prompts SHALL registrar o cenário como reprovado e indicar quais itens falharam.
7. THE Registro_de_Prompts SHALL conter no mínimo 1 cenário de teste executado em pelo menos 2 Assistentes_de_IA diferentes com a mesma entrada, registrando para cada execução o resultado da verificação dos critérios de aceitação aplicáveis, para evidenciar a portabilidade dos prompts.
8. WHEN um mesmo cenário de teste é executado em 2 ou mais Assistentes_de_IA e os resultados da verificação divergem entre as execuções, THE Registro_de_Prompts SHALL registrar a divergência e indicar o Assistente_de_IA e o modelo em que cada critério foi reprovado.