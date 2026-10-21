# sdd-task-analyzer

Projeto cumulativo do **Bootcamp III** baseado em Spec-Driven Development (SDD), Test Harness, governança de contexto para IA, CI/CD e containerização.

## Objetivo

Analisar tarefas em memória e produzir métricas de produtividade, preservando o contrato técnico definido pelo SDD. A Fase 3 acrescenta automação de testes com GitHub Actions, execução reproduzível via Docker e governança ética com homologação humana.

## Estrutura final

```text
sdd-task-analyzer/
├── .github/
│   └── workflows/
│       └── ci.yml
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .gitignore
├── CONTEXT_RULES.md
├── specs/
│   ├── task_analyzer_spec.md
│   ├── system_design_document.md
│   ├── system_design_document.pdf
│   └── requirements.yaml
├── tests/
│   └── test_harness.py
├── src/
│   ├── __init__.py
│   └── task_analyzer.py
├── requirements.txt
└── README.md
```

## Requisitos

- Python 3.11+
- pytest
- Docker + Docker Compose (para validação containerizada)

## Testes locais

```bash
python -m pip install -r requirements.txt
python -m pytest tests/test_harness.py -v
```

Resultado esperado:

```text
8 passed
```

## CI/CD - GitHub Actions

O workflow `.github/workflows/ci.yml` é disparado em `push` e `pull_request` para `main` e `develop`. Ele:

1. faz checkout do código;
2. configura Python 3.11;
3. instala as dependências de `requirements.txt`;
4. executa `python -m pytest tests/test_harness.py -v`.

## Docker

Build e execução direta:

```bash
docker build -t sdd-task-analyzer .
docker run --rm sdd-task-analyzer
```

Ou com Docker Compose:

```bash
docker compose up --build --abort-on-container-exit
```

A imagem utiliza `python:3.11-slim`, mantendo o ambiente isolado e reproduzível.

## Governança de IA

Antes de qualquer geração ou alteração de código por IA, devem ser fornecidos:

- `CONTEXT_RULES.md`
- `specs/task_analyzer_spec.md`

A aprovação final depende de Test Harness 100% aprovado e revisão humana crítica (Critical-in-the-Loop).

## Autor

Matheus Costa Pessanha - Ciência da Computação - Bootcamp III.
