# Especificação SDD - TaskAnalyzer

**Projeto:** Bootcamp III - Fase 2  
**Estudante:** Matheus Costa Pessanha  
**Curso:** Ciência da Computação  
**Versão do contrato:** 1.1 (Fase 1 transposta + clarificações obrigatórias da Fase 2)

## 1. Propósito

O TaskAnalyzer analisa tarefas em memória e gera métricas objetivas de produtividade. Ele não persiste dados, não altera tarefas e não acessa banco de dados.

## 2. Entradas

Cada tarefa é representada por um mapeamento contendo:

| Campo | Tipo | Obrigatório | Regra |
|---|---|---:|---|
| `id_tarefa` | `int` | Sim | Inteiro maior que zero. |
| `data_criacao` | `datetime` | Sim | Marco mínimo para validação temporal. |
| `data_inicio` | `datetime` | Não | Quando informado, é usado como início do cálculo de duração. |
| `data_conclusao` | `datetime` | Para concluídas | Não pode ser anterior à criação nem ao início. |
| `prazo` | `datetime` | Sim | Data/hora limite de conclusão. |
| `prioridade` | `str` | Sim | `baixa`, `média` ou `alta`. |
| `status` | `str` | Sim | `concluída`, `pendente` ou `cancelada`. |

Datas com fuso são normalizadas para UTC. Para compatibilidade com o Test Harness da Fase 2, datetimes sem `tzinfo` são interpretados como UTC.

## 3. Saídas de `analyze_tasks`

A função retorna um dicionário com:

- `total_tarefas`: quantidade total de tarefas válidas recebidas;
- `total_concluidas`: quantidade de tarefas com status concluída;
- `total_pendentes`: quantidade de tarefas com status pendente;
- `tempo_medio_conclusao_horas`: média geral de conclusão em horas;
- `tempo_medio_conclusao_horas_por_prioridade`: médias para baixa, média e alta;
- `taxa_atraso_percentual`: percentual geral de tarefas concluídas após o prazo;
- `indicadores_por_prioridade`: totais, média e atraso agrupados por prioridade.

## 4. Regras de negócio

1. Apenas tarefas concluídas participam do cálculo de duração e atraso.
2. Se `data_inicio` estiver presente, a duração é `data_conclusao - data_inicio`.
3. Se `data_inicio` não estiver presente, usa-se `data_criacao` como fallback controlado.
4. Uma tarefa está atrasada quando `data_conclusao > prazo`.
5. Médias e percentuais são arredondados para duas casas decimais.
6. Se não houver tarefas concluídas, médias e taxas retornam `0.0`.
7. Entradas inválidas devem gerar `TaskValidationError` com código estável.

## 5. Códigos de erro

| Código | Nome | Condição |
|---|---|---|
| `TA-001` | `INVALID_TASK_ID` | ID ausente, inválido ou menor/igual a zero. |
| `TA-002` | `INVALID_ENUM_VALUE` | Prioridade ou status fora dos valores aceitos. |
| `TA-003` | `INVALID_DATE_ORDER` | Ordem temporal inconsistente. |
| `TA-004` | `MISSING_REQUIRED_FIELD` | Campo obrigatório ausente ou tipo temporal inválido. |

> O código `TA-005` da Fase 1 (ausência de concluídas) deixa de ser disparado nesta fase porque o enunciado da Fase 2 exige explicitamente retorno `0.0` para lista vazia ou apenas tarefas pendentes.

## 6. Cenário 1 - Sucesso

**DADO** um conjunto de tarefas válidas com diferentes prioridades, prazos e status;  
**QUANDO** `analyze_tasks` for executada;  
**ENTÃO** devem ser retornados corretamente `total_tarefas`, `total_concluidas`, `total_pendentes`, tempo médio geral e por prioridade e taxa de atraso.

## 7. Cenário 2 - Exceção/erro

**DADO** uma tarefa cuja `data_conclusao` seja anterior à `data_criacao`;  
**QUANDO** `analyze_tasks` for executada;  
**ENTÃO** deve ser lançada `TaskValidationError` com código `TA-003`.

## 8. Casos de borda

- Lista vazia: totais iguais a zero, médias e taxa iguais a `0.0`.
- Apenas pendentes: total de pendentes correto, médias e taxa iguais a `0.0`.
- Prioridade sem tarefas concluídas: média da prioridade igual a `0.0`.

## 9. Test Harness

O arquivo `tests/test_harness.py` traduz os cenários acima para testes automatizados com `pytest`. A suíte deve ser executada antes de qualquer homologação e todos os testes devem passar.
