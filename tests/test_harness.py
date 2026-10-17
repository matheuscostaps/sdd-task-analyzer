"""Test Harness do TaskAnalyzer baseado nos cenários de aceite da Fase 1/2."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from src.task_analyzer import TaskValidationError, analyze_tasks

UTC = timezone.utc


def _dt(day: int, hour: int) -> datetime:
    """Cria datetime UTC determinístico para os testes."""

    return datetime(2026, 10, day, hour, tzinfo=UTC)


def test_cenario_1_sucesso_metricas_corretas() -> None:
    """Cenário 1: calcula totais, médias e taxa de atraso corretamente."""

    tasks = [
        {
            "id_tarefa": 1,
            "data_criacao": _dt(1, 8),
            "data_inicio": _dt(1, 9),
            "data_conclusao": _dt(1, 11),
            "prazo": _dt(1, 12),
            "prioridade": "baixa",
            "status": "concluída",
        },
        {
            "id_tarefa": 2,
            "data_criacao": _dt(2, 8),
            "data_inicio": _dt(2, 8),
            "data_conclusao": _dt(2, 12),
            "prazo": _dt(2, 11),
            "prioridade": "alta",
            "status": "concluída",
        },
        {
            "id_tarefa": 3,
            "data_criacao": _dt(3, 8),
            "data_inicio": _dt(3, 8),
            "data_conclusao": _dt(3, 10),
            "prazo": _dt(3, 12),
            "prioridade": "alta",
            "status": "concluída",
        },
        {
            "id_tarefa": 4,
            "data_criacao": _dt(4, 8),
            "prazo": _dt(4, 18),
            "prioridade": "média",
            "status": "pendente",
        },
    ]

    result = analyze_tasks(tasks)

    assert result["total_tarefas"] == 4
    assert result["total_concluidas"] == 3
    assert result["total_pendentes"] == 1
    assert result["tempo_medio_conclusao_horas"] == 2.67
    assert result["tempo_medio_conclusao_horas_por_prioridade"] == {
        "baixa": 2.0,
        "média": 0.0,
        "alta": 3.0,
    }
    assert result["taxa_atraso_percentual"] == 33.33
    assert result["indicadores_por_prioridade"]["alta"][
        "taxa_atraso_percentual"
    ] == 50.0


def test_cenario_2_data_conclusao_anterior_criacao_dispara_erro() -> None:
    """Cenário 2: datas inconsistentes devem gerar TaskValidationError."""

    task = {
        "id_tarefa": 10,
        "data_criacao": _dt(10, 10),
        "data_conclusao": _dt(10, 9),
        "prazo": _dt(10, 18),
        "prioridade": "alta",
        "status": "concluída",
    }

    with pytest.raises(TaskValidationError, match="TA-003"):
        analyze_tasks([task])


def test_caso_borda_lista_vazia_retorna_zeros() -> None:
    """Lista vazia não deve causar divisão por zero."""

    result = analyze_tasks([])

    assert result["total_tarefas"] == 0
    assert result["total_concluidas"] == 0
    assert result["total_pendentes"] == 0
    assert result["tempo_medio_conclusao_horas"] == 0.0
    assert result["taxa_atraso_percentual"] == 0.0
    assert all(
        value == 0.0
        for value in result["tempo_medio_conclusao_horas_por_prioridade"].values()
    )


def test_caso_borda_apenas_pendentes_retorna_medias_zero() -> None:
    """Somente tarefas pendentes produzem médias 0.0 sem exceção."""

    tasks = [
        {
            "id_tarefa": 20,
            "data_criacao": _dt(12, 8),
            "prazo": _dt(12, 18),
            "prioridade": "baixa",
            "status": "pendente",
        },
        {
            "id_tarefa": 21,
            "data_criacao": _dt(13, 8),
            "prazo": _dt(13, 18),
            "prioridade": "alta",
            "status": "pendente",
        },
    ]

    result = analyze_tasks(tasks)

    assert result["total_tarefas"] == 2
    assert result["total_concluidas"] == 0
    assert result["total_pendentes"] == 2
    assert result["tempo_medio_conclusao_horas"] == 0.0
    assert result["taxa_atraso_percentual"] == 0.0


def test_data_inicio_opcional_usa_data_criacao_como_fallback() -> None:
    """Sem data_inicio, usa data_criacao no cálculo de duração."""

    task = {
        "id_tarefa": 30,
        "data_criacao": _dt(14, 8),
        "data_conclusao": _dt(14, 12),
        "prazo": _dt(14, 13),
        "prioridade": "média",
        "status": "concluída",
    }

    result = analyze_tasks([task])

    assert result["tempo_medio_conclusao_horas"] == 4.0
    assert result["taxa_atraso_percentual"] == 0.0


def test_id_invalido_dispara_ta001() -> None:
    """IDs não positivos devem ser rejeitados."""

    task = {
        "id_tarefa": 0,
        "data_criacao": _dt(15, 8),
        "prazo": _dt(15, 18),
        "prioridade": "baixa",
        "status": "pendente",
    }

    with pytest.raises(TaskValidationError, match="TA-001"):
        analyze_tasks([task])


def test_enum_invalido_dispara_ta002() -> None:
    """Prioridade fora do contrato deve ser rejeitada."""

    task = {
        "id_tarefa": 40,
        "data_criacao": _dt(16, 8),
        "prazo": _dt(16, 18),
        "prioridade": "urgente",
        "status": "pendente",
    }

    with pytest.raises(TaskValidationError, match="TA-002"):
        analyze_tasks([task])


def test_datetimes_naive_sao_interpretados_como_utc() -> None:
    """Compatibilidade: datetime sem tzinfo é tratado como UTC."""

    created = datetime(2026, 10, 17, 8)
    task = {
        "id_tarefa": 50,
        "data_criacao": created,
        "data_conclusao": created + timedelta(hours=3),
        "prazo": created + timedelta(hours=4),
        "prioridade": "alta",
        "status": "concluida",
    }

    result = analyze_tasks([task])

    assert result["tempo_medio_conclusao_horas"] == 3.0
    assert result["taxa_atraso_percentual"] == 0.0
