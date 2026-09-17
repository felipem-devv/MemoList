"""Módulo de repetição espaçada SM-2 adaptado para listas ordenadas como unidade.

Apenas a nota subjetiva (grade q) escolhida pelo usuário afeta os parâmetros de agendamento.
As estatísticas de acertos/erros item a item são puramente informativas e não entram nesta fórmula.
"""

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass
class SRSResult:
    repetitions: int
    interval_days: int
    ease_factor: float
    next_review: date


def calculate_next_review(
    repetitions: int,
    interval_days: int,
    ease_factor: float,
    grade: int,
    base_date: date | None = None,
) -> SRSResult:
    """Calcula os novos parâmetros de repetição espaçada SM-2.

    Comportamento acordado (Opção B - Anki style com diferenciação inicial):
    - grade = 1: 'Errei' (repetitions=0, interval=1d, EF sofre penalidade padrão -0.54, min 1.30)
    - grade = 3: 'Difícil' (EF reduz -0.14, intervalos: 1d se rep=0, 3d se rep=1, max(I+1, round(I*1.2)) se rep>=2)
    - grade = 4: 'Bom' (EF estável, intervalos: 2d se rep=0, 6d se rep=1, max(I+1, round(I*EF)) se rep>=2)
    - grade = 5: 'Fácil' (EF aumenta +0.10, intervalos: 4d se rep=0, 8d se rep=1, max(I+1, round(I*EF*1.3)) se rep>=2)
    """
    if base_date is None:
        base_date = date.today()

    # 1. Atualização do Ease Factor (mínimo 1.30)
    # Fórmula padrão SM-2: EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    delta_ef = 0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02)
    new_ef = max(1.30, round(ease_factor + delta_ef, 2))

    # 2. Atualização de Repetições e Intervalo
    if grade < 3:
        # Falha (Errei): reseta ciclo de repetição para 0 e define intervalo para 1 dia
        new_repetitions = 0
        new_interval = 1
    else:
        # Sucesso
        if repetitions == 0:
            if grade == 3:
                new_interval = 1
            elif grade == 4:
                new_interval = 2
            else:  # grade == 5
                new_interval = 4
        elif repetitions == 1:
            if grade == 3:
                new_interval = 3
            elif grade == 4:
                new_interval = 6
            else:  # grade == 5
                new_interval = 8
        else:
            if grade == 3:
                new_interval = max(interval_days + 1, round(interval_days * 1.2))
            elif grade == 4:
                new_interval = max(interval_days + 1, round(interval_days * new_ef))
            else:  # grade == 5
                new_interval = max(interval_days + 1, round(interval_days * new_ef * 1.3))

        new_repetitions = repetitions + 1

    next_review_date = base_date + timedelta(days=new_interval)

    return SRSResult(
        repetitions=new_repetitions,
        interval_days=new_interval,
        ease_factor=new_ef,
        next_review=next_review_date,
    )


def preview_intervals(
    repetitions: int, interval_days: int, ease_factor: float
) -> dict[str, int]:
    """Retorna os dias de intervalo previstos para cada botão de avaliação final."""
    grades = {"errei": 1, "dificil": 3, "bom": 4, "facil": 5}
    return {
        key: calculate_next_review(repetitions, interval_days, ease_factor, g).interval_days
        for key, g in grades.items()
    }
