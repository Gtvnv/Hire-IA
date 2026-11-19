# Resumo das execuções

Gerado por `tools/executar_cenarios.py` em 2026-11-19 05:08:51 UTC. Assistente: Ollama. Parâmetros: temperature=0, seed=42, num_ctx=8192, num_predict=2500.

## Execuções

| ID | Prompt | Versão | Modelo | Duração (s) | Status | Descrição | Arquivo |
|---|---|---|---|---|---|---|---|
| EV01 | Avaliador | v1 | llama3.2:latest | 623.9 | concluída | Entrada A1 do Registro (comparação de versões) | [EV01.md](EV01.md) |
| EV02 | Avaliador | v1 | llama3.2:latest | 698.6 | concluída | Entrada A2 do Registro (comparação de versões) | [EV02.md](EV02.md) |
| EV03 | Avaliador | v1 | llama3.2:latest | 566.3 | concluída | Entrada A3 do Registro (comparação de versões) | [EV03.md](EV03.md) |
| EV04 | Avaliador | v2 | llama3.2:latest | 834.4 | concluída | Entrada A1 do Registro (comparação de versões) | [EV04.md](EV04.md) |
| EV05 | Avaliador | v2 | llama3.2:latest | 1209.6 | concluída | Entrada A2 do Registro (comparação de versões) | [EV05.md](EV05.md) |
| EV06 | Avaliador | v2 | llama3.2:latest | 1019.5 | concluída | Entrada A3 do Registro (comparação de versões) | [EV06.md](EV06.md) |
| EV07 | Gerador | v1 | llama3.2:latest | 377.8 | concluída | Banco para Desenvolvedor Backend Júnior | [EV07.md](EV07.md) |
| EV08 | Gerador | v1 | llama3.2:latest | 324.1 | concluída | Banco para Analista de Dados Pleno | [EV08.md](EV08.md) |
| EV09 | Avaliador | v2 | llama3.2:latest | 1144.3 | concluída | Resposta vazia (apenas espaços, tabs e quebras de linha) | [EV09.md](EV09.md) |
| EV10 | Avaliador | v2 | llama3.2:latest | 905.8 | concluída | Resposta fora de contexto | [EV10.md](EV10.md) |
| EV11 | Gerador | v1 | llama3.2:1b | 710.4 | concluída | Mesma entrada de EV07 (portabilidade) | [EV11.md](EV11.md) |
| EV12 | Avaliador | v2 | llama3.2:1b | 596.4 | concluída | Mesma entrada de EV05 (portabilidade) | [EV12.md](EV12.md) |

## Verificações automáticas

Resultados calculados por `tools/banco.validar_banco` (Gerador) e por `tools/feedback.calcular_nota_final` (Avaliador). "Não extraível" indica que a saída não seguiu o formato esperado para a extração.

| ID | Prompt | Modelo | Resultado da verificação |
|---|---|---|---|
| EV01 | Avaliador v1 | llama3.2:latest | notas extraídas [9, 8, 7, 6, 8]; nota final calculada = 7.8; nota final informada = 6.8; calcular_nota_final confere: não |
| EV02 | Avaliador v1 | llama3.2:latest | notas extraídas [5, 6, 4, 5, 5]; nota final calculada = 5.0; nota final informada = 4; calcular_nota_final confere: não |
| EV03 | Avaliador v1 | llama3.2:latest | notas extraídas [2, 3, 3, 4, 3]; nota final calculada = 2.9; nota final informada = 2.85; calcular_nota_final confere: não |
| EV04 | Avaliador v2 | llama3.2:latest | notas extraídas [9, 8, 7, 6, 8]; nota final calculada = 7.8; nota final informada = 6.8; calcular_nota_final confere: não |
| EV05 | Avaliador v2 | llama3.2:latest | notas extraídas [4, 5, 3, 4, 5]; nota final calculada = 4.2; nota final informada = 4.15; calcular_nota_final confere: não |
| EV06 | Avaliador v2 | llama3.2:latest | notas extraídas [4, 5, 3, 4, 5]; nota final calculada = 4.2; nota final informada = 4.15; calcular_nota_final confere: não |
| EV07 | Gerador v1 | llama3.2:latest | banco.validar_banco: inválido (0 perguntas lidas). Erros: Nenhuma tabela Markdown encontrada. |
| EV08 | Gerador v1 | llama3.2:latest | banco.validar_banco: inválido (0 perguntas lidas). Erros: Nenhuma tabela Markdown encontrada. |
| EV09 | Avaliador v2 | llama3.2:latest | feedback.resposta_em_branco(entrada) = verdadeiro; notas extraídas [4, 6, 3, 4, 5]; nota final calculada = 4.4; nota final informada = 3.75; calcular_nota_final confere: não |
| EV10 | Avaliador v2 | llama3.2:latest | notas extraídas [0, 0, 0, 0, 0]; nota final calculada = 0.0; nota final informada = 0; calcular_nota_final confere: sim |
| EV11 | Gerador v1 | llama3.2:1b | banco.validar_banco: inválido (0 perguntas lidas). Erros: Colunas inválidas. Esperado: número, pergunta, categoria, dificuldade, resposta de referência; encontrado: campo, regra. |
| EV12 | Avaliador v2 | llama3.2:1b | notas extraídas [6, 5, 4, 3, 2]; nota final calculada = 4.4; nota final informada = 6.8; calcular_nota_final confere: não |

## Observações calculadas a partir dos metadados e da saída

| ID | done_reason | prompt_eval_count | eval_count (num_predict=2500) | Linhas de tabela Markdown na saída |
|---|---|---|---|---|
| EV01 | stop | 3343 | 670 | 7 |
| EV02 | stop | 3235 | 611 | 7 |
| EV03 | stop | 3240 | 568 | 7 |
| EV04 | stop | 4276 | 691 | 7 |
| EV05 | stop | 4168 | 701 | 7 |
| EV06 | stop | 4173 | 610 | 7 |
| EV07 | stop | 2704 | 73 | 0 |
| EV08 | stop | 2696 | 75 | 0 |
| EV09 | stop | 4150 | 794 | 7 |
| EV10 | stop | 4179 | 378 | 7 |
| EV11 | stop | 2704 | 1283 | 13 |
| EV12 | stop | 4168 | 675 | 7 |
