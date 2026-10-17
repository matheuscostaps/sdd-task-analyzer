"""TaskAnalyzer: cálculo de métricas de produtividade de tarefas.

O módulo implementa o contrato definido na especificação SDD do projeto e não
realiza persistência de dados. Toda a análise ocorre em memória.
"""

from __future__ import annotations

from datetime import datetime, timezone
import logging
from typing import Any, Final, Mapping, Sequence
import unicodedata

LOGGER = logging.getLogger(__name__)

PRIORITIES: Final[tuple[str, ...]] = ("baixa", "média", "alta")
STATUSES: Final[tuple[str, ...]] = ("concluída", "pendente", "cancelada")


class TaskValidationError(ValueError):
    """Exceção lançada quando uma tarefa viola o contrato de entrada.

    Args:
        code: Código estável do erro conforme a especificação SDD.
        message: Descrição objetiva da violação encontrada.
    """

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")


def _canonical_text(value: object) -> str:
    """Normaliza texto para comparação sem depender de caixa ou acentuação.

    Args:
        value: Valor a ser normalizado.

    Returns:
        Texto em minúsculas, sem espaços nas pontas e sem acentos.
    """

    text = str(value).strip().casefold()
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(char for char in normalized if not unicodedata.combining(char))


def _normalize_priority(value: object) -> str:
    """Valida e devolve a prioridade no formato canônico do contrato."""

    mapping = {"baixa": "baixa", "media": "média", "alta": "alta"}
    key = _canonical_text(value)
    try:
        return mapping[key]
    except KeyError as exc:
        raise TaskValidationError(
            "TA-002",
            "prioridade deve ser baixa, média ou alta.",
        ) from exc


def _normalize_status(value: object) -> str:
    """Valida e devolve o status no formato canônico do contrato."""

    mapping = {
        "concluida": "concluída",
        "pendente": "pendente",
        "cancelada": "cancelada",
    }
    key = _canonical_text(value)
    try:
        return mapping[key]
    except KeyError as exc:
        raise TaskValidationError(
            "TA-002",
            "status deve ser concluída, pendente ou cancelada.",
        ) from exc


def _as_utc(value: object, field_name: str) -> datetime:
    """Valida um datetime e o normaliza para UTC.

    Datetimes sem informação de fuso são interpretados como UTC para manter a
    compatibilidade com o Test Harness da Fase 2.

    Args:
        value: Valor esperado como ``datetime``.
        field_name: Nome do campo para compor mensagens de erro.

    Returns:
        Data/hora normalizada para UTC.

    Raises:
        TaskValidationError: Se o valor não for ``datetime``.
    """

    if not isinstance(value, datetime):
        raise TaskValidationError(
            "TA-004",
            f"{field_name} deve ser informado como datetime.",
        )
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _validate_task(task: Mapping[str, Any]) -> dict[str, Any]:
    """Valida uma tarefa e devolve seus campos normalizados.

    Args:
        task: Mapeamento com os campos da tarefa.

    Returns:
        Dicionário validado e normalizado.

    Raises:
        TaskValidationError: Se qualquer regra do contrato for violada.
    """

    required = ("id_tarefa", "data_criacao", "prazo", "prioridade", "status")
    missing = [field for field in required if field not in task]
    if missing:
        raise TaskValidationError(
            "TA-004",
            f"campo(s) obrigatório(s) ausente(s): {', '.join(missing)}.",
        )

    task_id = task["id_tarefa"]
    if isinstance(task_id, bool) or not isinstance(task_id, int) or task_id <= 0:
        raise TaskValidationError(
            "TA-001",
            "id_tarefa deve ser um inteiro maior que zero.",
        )

    created_at = _as_utc(task["data_criacao"], "data_criacao")
    deadline = _as_utc(task["prazo"], "prazo")
    priority = _normalize_priority(task["prioridade"])
    status = _normalize_status(task["status"])

    started_at: datetime | None = None
    if task.get("data_inicio") is not None:
        started_at = _as_utc(task["data_inicio"], "data_inicio")
        if started_at < created_at:
            raise TaskValidationError(
                "TA-003",
                "data_inicio não pode ser anterior a data_criacao.",
            )

    completed_at: datetime | None = None
    if task.get("data_conclusao") is not None:
        completed_at = _as_utc(task["data_conclusao"], "data_conclusao")

    if status == "concluída" and completed_at is None:
        raise TaskValidationError(
            "TA-004",
            "data_conclusao é obrigatória para tarefas concluídas.",
        )

    if completed_at is not None:
        if completed_at < created_at:
            raise TaskValidationError(
                "TA-003",
                "data_conclusao não pode ser anterior a data_criacao.",
            )
        if started_at is not None and completed_at < started_at:
            raise TaskValidationError(
                "TA-003",
                "data_conclusao não pode ser anterior a data_inicio.",
            )

    return {
        "id_tarefa": task_id,
        "data_criacao": created_at,
        "data_inicio": started_at,
        "data_conclusao": completed_at,
        "prazo": deadline,
        "prioridade": priority,
        "status": status,
    }


def _mean(values: Sequence[float]) -> float:
    """Calcula média arredondada em duas casas, retornando 0.0 se vazia."""

    if not values:
        return 0.0
    return round(sum(values) / len(values), 2)


def _percentage(numerator: int, denominator: int) -> float:
    """Calcula percentual seguro contra divisão por zero."""

    if denominator == 0:
        return 0.0
    return round((numerator / denominator) * 100, 2)


def analyze_tasks(tasks: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Analisa tarefas e retorna métricas consolidadas e por prioridade.

    A duração de uma tarefa concluída é medida a partir de ``data_inicio``
    quando o campo estiver presente. Como ``data_inicio`` é opcional no contrato
    da Fase 1, ``data_criacao`` é utilizada como fallback controlado.

    Args:
        tasks: Sequência de tarefas seguindo o contrato SDD.

    Returns:
        Dicionário com totais, média geral de conclusão em horas, médias por
        prioridade, taxa de atraso geral e indicadores por prioridade.

    Raises:
        TaskValidationError: Se alguma tarefa violar o contrato de entrada.
    """

    if isinstance(tasks, (str, bytes)) or not isinstance(tasks, Sequence):
        raise TaskValidationError(
            "TA-004",
            "tasks deve ser uma sequência de tarefas.",
        )

    normalized_tasks = [_validate_task(task) for task in tasks]
    completed_tasks = [
        task for task in normalized_tasks if task["status"] == "concluída"
    ]

    durations: list[float] = []
    late_count = 0
    for task in completed_tasks:
        completed_at = task["data_conclusao"]
        if completed_at is None:
            continue
        started_at = task["data_inicio"] or task["data_criacao"]
        duration_hours = (completed_at - started_at).total_seconds() / 3600
        durations.append(duration_hours)
        if completed_at > task["prazo"]:
            late_count += 1

    averages_by_priority: dict[str, float] = {}
    indicators_by_priority: dict[str, dict[str, int | float]] = {}

    for priority in PRIORITIES:
        priority_tasks = [
            task for task in normalized_tasks if task["prioridade"] == priority
        ]
        priority_completed = [
            task for task in priority_tasks if task["status"] == "concluída"
        ]
        priority_durations: list[float] = []
        priority_late = 0

        for task in priority_completed:
            completed_at = task["data_conclusao"]
            if completed_at is None:
                continue
            started_at = task["data_inicio"] or task["data_criacao"]
            priority_durations.append(
                (completed_at - started_at).total_seconds() / 3600
            )
            if completed_at > task["prazo"]:
                priority_late += 1

        priority_average = _mean(priority_durations)
        averages_by_priority[priority] = priority_average
        indicators_by_priority[priority] = {
            "total_tarefas": len(priority_tasks),
            "total_concluidas": len(priority_completed),
            "total_pendentes": sum(
                task["status"] == "pendente" for task in priority_tasks
            ),
            "tempo_medio_conclusao_horas": priority_average,
            "taxa_atraso_percentual": _percentage(
                priority_late,
                len(priority_completed),
            ),
        }

    result: dict[str, Any] = {
        "total_tarefas": len(normalized_tasks),
        "total_concluidas": len(completed_tasks),
        "total_pendentes": sum(
            task["status"] == "pendente" for task in normalized_tasks
        ),
        "tempo_medio_conclusao_horas": _mean(durations),
        "tempo_medio_conclusao_horas_por_prioridade": averages_by_priority,
        "taxa_atraso_percentual": _percentage(late_count, len(completed_tasks)),
        "indicadores_por_prioridade": indicators_by_priority,
    }

    LOGGER.info(
        "TaskAnalyzer concluído: total=%d, concluídas=%d, pendentes=%d",
        result["total_tarefas"],
        result["total_concluidas"],
        result["total_pendentes"],
    )
    return result
