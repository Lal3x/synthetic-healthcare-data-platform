import pandas as pd

from healthcare_analytics.gold.aggregations import (
    create_encounter_summary,
    create_one_big_table,
    create_patient_summary,
)


def _patients() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id": [1, 2, 3],
            "gender": ["F", "M", "F"],
            "race": ["white", "black", "asian"],
            "ethnicity": ["hispanic", "nonhispanic", "nonhispanic"],
            "full_name": ["Ana Silva", "João Souza", "Maria Lima"],
            "income": [1000, 2000, 3000],
        }
    )


def _encounters() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id": [10, 11, 12],
            "patient": [1, 1, 2],
            "start": pd.to_datetime(["2026-01-01", "2026-01-02", "2026-01-03"]),
            "stop": pd.to_datetime(
                ["2026-01-01 01:00", "2026-01-02 02:00", "2026-01-03 03:00"]
            ),
            "encounterclass": ["ambulatory", "ambulatory", "emergency"],
            "description": ["Consulta", "Retorno", "Urgência"],
            "duration_hours": [1.0, 2.0, 3.0],
            "total_claim_cost": [100.0, 200.0, 900.0],
            "payer_coverage": [80.0, 150.0, 700.0],
        }
    )


def test_create_one_big_table_une_paciente_e_atendimento():
    result = create_one_big_table(_patients(), _encounters())

    assert list(result["encounter_id"]) == [10, 11, 12]
    assert result.loc[0, "full_name"] == "Ana Silva"
    assert result.loc[2, "patient_id"] == 2


def test_create_patient_summary_agrega_e_preserva_paciente_sem_atendimento():
    result = create_patient_summary(_patients(), _encounters())

    ana = result.loc[result["patient_id"] == 1].iloc[0]
    maria = result.loc[result["patient_id"] == 3].iloc[0]
    assert ana["total_encounters"] == 2
    assert ana["total_claim_cost"] == 300.0
    assert maria["total_encounters"] == 0
    assert "income" not in result.columns


def test_create_encounter_summary_agrega_por_classe():
    result = create_encounter_summary(_encounters())

    ambulatory = result.loc[result["encounterclass"] == "ambulatory"].iloc[0]
    assert ambulatory["total_encounters"] == 2
    assert ambulatory["avg_claim_cost"] == 150.0
    assert ambulatory["sum_claim_cost"] == 300.0
