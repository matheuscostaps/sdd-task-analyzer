# sdd-task-analyzer

Projeto da **Fase 2 do Bootcamp III**: implementação do TaskAnalyzer orientada por especificação (SDD), governança de contexto para IA e validação por Test Harness com `pytest`.

## Objetivo

Analisar tarefas em memória e produzir métricas de produtividade, incluindo totais, tempo médio de conclusão e taxa de atraso, preservando o contrato técnico definido na Fase 1 e as clarificações obrigatórias da Fase 2.

## Estrutura

```text
sdd-task-analyzer/
├── README.md
├── CONTEXT_RULES.md
├── .gitignore
├── requirements.txt
├── specs/
│   └── task_analyzer_spec.md
├── tests/
│   └── test_harness.py
└── src/
    └── task_analyzer.py
```

## Requisitos

- Python 3.11+
- pytest 8.x

## Instalação

```bash
python -m venv .venv
```

No Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

No Linux/macOS:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Executar testes

Na raiz do projeto:

```bash
python -m pytest -q
```

Resultado esperado desta versão:

```text
8 passed
```

## Contrato e governança

Antes de solicitar alterações a um assistente de IA, devem ser fornecidos como contexto:

- `CONTEXT_RULES.md`
- `specs/task_analyzer_spec.md`

O código só deve ser homologado após a execução bem-sucedida de toda a suíte de testes e revisão humana de aderência ao contrato.

## Estratégia Git/GitHub

Branches preparadas no histórico local:

- `main`
- `feature/sdd-specification`
- `feature/task-analyzer-impl`
- `feature/test-harness`

A branch `feature/test-harness` deve ser enviada ao GitHub e utilizada para abrir o Pull Request obrigatório para `main`. Após revisão humana e confirmação dos testes, o PR pode ser merged.

## Autor

Matheus Costa Pessanha - Ciência da Computação - Bootcamp III.
