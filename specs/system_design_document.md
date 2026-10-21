# System Design Document - TaskAnalyzer

## 1. Visão geral

O TaskAnalyzer é um módulo Python que analisa tarefas em memória e produz métricas de produtividade. O desenho da solução é orientado pela especificação SDD e pelas regras persistentes de contexto para IA.

## 2. Componentes

- `src/task_analyzer.py`: lógica de negócio e validação.
- `tests/test_harness.py`: Test Harness automatizado com pytest.
- `CONTEXT_RULES.md`: guardrails de arquitetura, testes e interação com IA.
- `.github/workflows/ci.yml`: integração contínua no GitHub Actions.
- `Dockerfile`: empacotamento reproduzível em Python 3.11 slim.
- `docker-compose.yml`: orquestração do serviço de teste.

## 3. Fluxo de confiança

1. O contrato SDD define entradas, saídas, regras e cenários.
2. A IA só pode gerar ou alterar código dentro das CONTEXT_RULES.
3. O Test Harness verifica os cenários e casos de borda.
4. O GitHub Actions repete a validação automaticamente em push e Pull Request.
5. Um segundo job do workflow constrói a imagem Docker e executa a mesma suíte dentro do container.
6. O Docker opera como usuário não-root, sem rede durante os testes e com sistema de arquivos somente leitura.
7. A homologação humana precede a integração na branch principal.

## 4. Critérios de aceite final

- Todos os testes aprovados.
- Workflow CI concluído com sucesso.
- Execução Docker reproduzível.
- Nenhuma dependência fora de `requirements.txt`.
- Código aderente ao SDD e às CONTEXT_RULES.
- Alterações integradas por fluxo rastreável de Git/Pull Request.
