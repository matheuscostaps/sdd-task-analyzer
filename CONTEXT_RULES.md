# CONTEXT_RULES - TaskAnalyzer

Estas regras devem ser fornecidas ao assistente de IA antes de qualquer solicitação de implementação. Elas funcionam como guardrails persistentes para manter o código aderente ao contrato SDD.

## 1. Diretrizes arquiteturais obrigatórias

- Usar Python 3.11 ou superior.
- Usar type hints em todas as funções e parâmetros.
- Seguir PEP 8 e princípios de código limpo.
- Manter funções pequenas, coesas e com responsabilidade única.
- Usar docstrings no padrão Google em módulos, classes e funções.
- Utilizar o módulo padrão `logging` para logs estruturados.
- Tratar exceções de forma específica e com mensagens claras.
- Usar nomes de variáveis e funções descritivos.
- Separar responsabilidades e evitar scripts monolíticos.
- Toda nova funcionalidade deve possuir teste correspondente.

## 2. Proibições explícitas

- Não utilizar bibliotecas externas não autorizadas.
- Não alterar, remover ou reinterpretar os cenários de aceite fornecidos.
- Não modificar a estrutura de pastas definida na especificação.
- Não persistir dados em arquivos ou bancos de dados.
- Não alterar assinatura, nome ou parâmetros de funções públicas sem autorização.
- Não gerar código sem testes correspondentes.
- Não inserir código duplicado ou desnecessário.
- Não assumir comportamentos que não estejam documentados.
- Não retornar estruturas incompatíveis com o contrato.
- Não ignorar falhas de teste para concluir a implementação.

## 3. Regras de interação com IA

- Fornecer `CONTEXT_RULES.md` e `specs/task_analyzer_spec.md` como contexto antes da geração do código.
- Solicitar que a IA confirme as restrições antes de implementar.
- Revisar criticamente todo código gerado.
- Executar o Test Harness após mudanças de comportamento.
- Rejeitar qualquer resposta que viole o contrato, os testes ou estas regras.

## 4. Regra de precedência da Fase 2

Quando o enunciado da Fase 2 explicitar um requisito operacional de teste que complemente a especificação da Fase 1, ele deve ser tratado como clarificação do contrato para esta entrega. Em especial:

- `analyze_tasks` deve retornar `total_tarefas`, `total_concluidas`, `total_pendentes`, `tempo_medio_conclusao_horas` e `taxa_atraso_percentual`.
- A média de conclusão também deve ser verificável por prioridade.
- Lista vazia ou conjunto contendo apenas tarefas pendentes deve retornar médias `0.0`, sem divisão por zero e sem exceção não tratada.
- `data_conclusao < data_criacao` deve disparar `TaskValidationError`.

## 5. Governança da Fase 3 - DevOps e Containerização

- O workflow de CI deve executar a mesma suíte `tests/test_harness.py` usada na homologação local.
- O ambiente de CI deve usar Python 3.11 ou superior e instalar somente dependências declaradas em `requirements.txt`.
- O Docker deve usar imagem oficial Python 3.11 slim e não deve introduzir bibliotecas não autorizadas.
- O container deve executar os testes como comportamento padrão de validação desta entrega.
- Falha no pytest, no GitHub Actions ou no ambiente Docker bloqueia a homologação final.
- A IA não pode alterar o contrato para fazer os testes passarem; qualquer conflito deve ser resolvido por revisão humana do SDD, do enunciado e das CONTEXT_RULES.
