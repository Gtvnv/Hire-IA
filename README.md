# IA Entrevistador

O IA Entrevistador é um projeto de engenharia de prompt que usa IA generativa para simular entrevistas técnicas de emprego. Ele entrega três prompts versionados, em texto puro, que funcionam em qualquer assistente de IA baseado em conversa. Os prompts geram perguntas por cargo e senioridade, conduzem a entrevista em formato de diálogo e avaliam as respostas com uma Rubrica fixa, terminando em um relatório final com plano de estudo.

## Objetivo

Ajudar quem se prepara para um processo seletivo a treinar com perguntas próximas das reais, receber feedback estruturado e saber o que estudar. O projeto também documenta a evolução dos prompts (versões, testes e lições aprendidas), sem depender de um produto específico.

## Tags

- IA
- Engenharia de Prompt
- IA Generativa
- Assistentes de IA

## Funcionalidades

- **Perfil da vaga:** cargo, senioridade (Estagiário, Júnior, Pleno, Sênior ou Especialista), tecnologias, descrição da vaga opcional e idioma (português do Brasil por padrão).
- **Geração de perguntas:** banco com 10 perguntas em tabela Markdown, com categoria (Técnica, Comportamental ou Situacional), dificuldade ajustada à senioridade e resposta de referência. É possível pedir 5 perguntas novas, sem repetir temas.
- **Simulação de entrevista:** uma pergunta por mensagem, em linguagem formal, nos modos treino (Feedback após cada resposta) e realista (Feedback só no relatório). O comando "encerrar" finaliza a simulação.
- **Avaliação de respostas:** cinco critérios ponderados (Correção técnica, Clareza, Profundidade, Estrutura da resposta e Exemplos práticos), nota final com a conta exibida, pontos fortes, pontos de melhoria, resposta sugerida e verificação STAR para perguntas comportamentais.
- **Relatório final:** nota geral, nota por categoria, resumo, pontos fortes e de melhoria e plano de estudo de 1 a 5 tópicos.
- **Validador opcional:** scripts em Python que conferem a estrutura dos prompts, do Registro e deste README.

## Pré-requisitos

- Acesso a um assistente de IA generativa baseado em conversa (por exemplo, ChatGPT, Claude, Gemini ou Copilot, citados apenas como exemplo).
- Um editor de texto ou o navegador para abrir os arquivos de prompt e copiar o conteúdo.
- Opcional, para o validador: Python 3 e as dependências de `tools/requirements.txt` (pytest e hypothesis).

## Estrutura do repositório

```text
.
├── README.md
├── LICENSE
├── prompts/
│   ├── gerador-de-perguntas.md
│   ├── simulador-de-entrevista.md
│   └── avaliador-de-respostas.md
├── docs/
│   └── registro-de-prompts.md
└── tools/
    ├── validar_artefatos.py
    ├── requirements.txt
    └── tests/
```

- [prompts/gerador-de-perguntas.md](prompts/gerador-de-perguntas.md): Gerador_de_Perguntas.
- [prompts/simulador-de-entrevista.md](prompts/simulador-de-entrevista.md): Simulador_de_Entrevista.
- [prompts/avaliador-de-respostas.md](prompts/avaliador-de-respostas.md): Avaliador_de_Respostas.
- [docs/registro-de-prompts.md](docs/registro-de-prompts.md): Registro de Prompts, com fichas, versões, cenários de teste e lições aprendidas.
- `tools/`: validador determinístico e testes de propriedade (opcional).

## Como usar

1. Escolha o assistente de IA que você vai usar e abra uma conversa nova.
2. Abra [prompts/gerador-de-perguntas.md](prompts/gerador-de-perguntas.md) e copie o texto da seção "Prompt v1".
3. Cole o texto na conversa e informe os valores das variáveis `{{cargo}}`, `{{senioridade}}` e `{{tecnologias}}` (e, se quiser, a descrição da vaga e o idioma). Se faltar algum valor, o prompt pede o campo ausente.
4. Confira o banco de 10 perguntas gerado e revise as respostas de referência, principalmente as marcadas com "verificar em fonte oficial".
5. Abra [prompts/simulador-de-entrevista.md](prompts/simulador-de-entrevista.md), copie o texto da seção "Prompt v1" e cole em uma conversa nova.
6. Informe o perfil da vaga, o modo (treino ou realista) e cole o banco de perguntas gerado no passo 3.
7. Responda a uma pergunta por vez, como em uma entrevista real. Se a resposta for vazia ou fora do assunto, o prompt pede o reenvio para a mesma pergunta.
8. No modo treino, leia o Feedback exibido após cada resposta. No modo realista, os Feedbacks aparecem só no relatório.
9. Para avaliar uma resposta isoladamente, use [prompts/avaliador-de-respostas.md](prompts/avaliador-de-respostas.md) em uma conversa nova, informando a pergunta, a categoria e a resposta.
10. Digite "encerrar" quando quiser parar, ou responda à última pergunta, para receber o Relatório Final.
11. Se uma geração falhar, peça para tentar novamente. Você não precisa reenviar os dados já informados.
12. Use o plano de estudo do relatório para escolher os próximos temas e repita a simulação.

## Exemplo de sessão

O exemplo abaixo é ilustrativo. Ele reutiliza o exemplo few-shot de [prompts/avaliador-de-respostas.md](prompts/avaliador-de-respostas.md) e não é o resultado de uma execução real em um assistente de IA.

**Perfil da vaga:** Desenvolvedor Back-end, Pleno, tecnologias C# e SQL Server. Categoria da pergunta: Comportamental.

**Pergunta**

Conte sobre uma vez em que você precisou resolver um problema de desempenho em produção.

**Resposta do candidato**

"No meu último projeto, a API de pedidos começou a demorar mais de 8 segundos nos horários de pico. Fiquei responsável por descobrir a causa. Analisei os logs, encontrei uma consulta sem índice e criei o índice na tabela de pedidos. Depois disso o tempo caiu para menos de 1 segundo."

**Feedback**

- **Pergunta avaliada:** Conte sobre uma vez em que você precisou resolver um problema de desempenho em produção.

- **Notas por critério:**

| Critério | Peso | Nota (0 a 10) | Justificativa |
|---|---|---|---|
| Correção técnica | 30% | 8 | A causa apontada, uma consulta sem índice, e a solução com índice são coerentes com o problema descrito. Faltou mencionar como a consulta lenta foi identificada. |
| Clareza | 20% | 7 | A sequência "demorava 8 segundos, analisei os logs, criei o índice" é fácil de acompanhar. Algumas frases são muito curtas e omitem detalhes. |
| Profundidade | 20% | 6 | A resposta cita a causa, mas não discute alternativas, riscos de criar o índice em produção nem como evitar a recorrência. |
| Estrutura da resposta | 15% | 5 | Há problema, ação e resultado, mas o contexto inicial é breve e não há conclusão sobre o que foi aprendido. |
| Exemplos práticos | 15% | 7 | Os números "mais de 8 segundos" e "menos de 1 segundo" tornam o caso concreto e verificável. |

- **Cálculo:** (30 × 8 + 20 × 7 + 20 × 6 + 15 × 5 + 15 × 7) / 100 = (240 + 140 + 120 + 75 + 105) / 100 = 680 / 100 = 6,8.
- **Nota final:** 6,8
- **Pontos fortes:**
  - Apresenta resultado mensurável, com tempo de resposta antes e depois da correção.
  - Mostra iniciativa ao assumir a investigação do problema.
- **Pontos de melhoria:**
  - Explicar como a consulta sem índice foi identificada, por exemplo com plano de execução ou métricas.
  - Descrever o impacto no negócio e o que foi feito para evitar que o problema volte.
- **Resposta sugerida:** "Na API de pedidos, o tempo de resposta passou de 8 segundos nos horários de pico, o que afetava as vendas. Eu fiquei responsável pela investigação. Analisei logs e o plano de execução e identifiquei uma consulta sem índice na tabela de pedidos. Criei o índice em horário de baixo uso, validei em homologação e acompanhei as métricas. O tempo caiu para menos de 1 segundo. Depois, configurei um alerta de lentidão e passamos a revisar planos de execução nas revisões de código."
- **Verificação STAR:**
  - Situação: presente
  - Tarefa: presente
  - Ação: presente
  - Resultado: presente
- **Aviso:** Esta nota é uma estimativa de apoio ao estudo e não substitui a avaliação de um profissional.

## Técnicas de engenharia de prompt

| Prompt | Técnica principal | Técnicas complementares |
|---|---|---|
| [Gerador de Perguntas](prompts/gerador-de-perguntas.md) | Saída estruturada (tabela com colunas fixas e verificação de contagem) | Definição de papel, restrições explícitas |
| [Simulador de Entrevista](prompts/simulador-de-entrevista.md) | Restrições explícitas (regras de conduta e limites numéricos) | Definição de papel, saída estruturada |
| [Avaliador de Respostas](prompts/avaliador-de-respostas.md) | Few-shot (exemplo completo de avaliação) | Saída estruturada, restrições explícitas |

Os três prompts usam variáveis nomeadas no formato `{{nome}}`, seções fixas (papel, contexto, tarefa, restrições e formato de saída) e texto puro em Markdown, sem recursos exclusivos de um produto. O texto completo, as versões e os exemplos de cada prompt estão no [Registro de Prompts](docs/registro-de-prompts.md).

## Resultados e aprendizados

Os resultados dos testes dos prompts em assistentes de IA reais são registrados em [docs/registro-de-prompts.md](docs/registro-de-prompts.md) e ainda estão pendentes. Até o momento, nenhuma execução real foi registrada, então este README não afirma notas, taxas de acerto nem comparações entre assistentes. Os exemplos incluídos nos prompts e neste README são ilustrativos.

Quando as execuções forem feitas, o Registro trará a comparação entre as versões do Avaliador, as lições aprendidas e os cenários de teste, com assistente, modelo e data de cada execução.

## Limitações

- **Respostas incorretas:** a IA generativa pode produzir perguntas, respostas de referência e avaliações incorretas, incompletas ou inventadas. Confirme fatos técnicos em fontes oficiais.
- **Revisão humana:** revise as saídas antes de usá-las para estudar ou tomar decisões. A nota é uma estimativa de apoio ao estudo e não substitui a avaliação de um profissional.
- **Variação entre assistentes e modelos:** o comportamento e a qualidade das saídas podem mudar entre assistentes de IA e entre modelos. A mesma resposta avaliada duas vezes pode receber notas diferentes.

### Privacidade e Segurança

Não insira nos prompts dados pessoais sensíveis, como CPF, RG, endereço residencial, telefone, dados bancários, senhas ou chaves de API. Também não insira informações confidenciais de empregadores, como código-fonte proprietário, dados de clientes ou segredos comerciais. Os prompts instruem o assistente a ignorar esses dados e características pessoais (gênero, idade, origem, etnia, religião, orientação sexual, deficiência e estado civil) e a lembrar o usuário de não os informar. Lembre também que o conteúdo da conversa é tratado conforme as políticas do assistente de IA que você usa.

## Próximos passos

- Executar os cenários de teste em ao menos dois assistentes de IA e registrar os resultados no Registro de Prompts.
- Criar a v2 do Avaliador de Respostas e comparar com a v1 usando as mesmas entradas de teste.
- Registrar as lições aprendidas a partir dos problemas observados nas execuções.
- Atualizar a seção "Resultados e aprendizados" com os resultados reais.

## Licença

Este projeto está sob a licença MIT. O texto completo está no arquivo [LICENSE](LICENSE).
