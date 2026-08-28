import pandas as pd
import pytest


@pytest.fixture
def sample_patients_df() -> pd.DataFrame:
    """DataFrame de pacientes de exemplo, no formato que sai da bronze."""
    return pd.DataFrame(
        {
            "id": [1, 2],
            "birthdate": ["1990-01-01", "1985-05-05"],
            "gender": ["M", "F"],
            "race": ["white", "black"],
            "ethnicity": ["nonhispanic", "hispanic"],
            "first": ["João", "Maria"],
            "last": ["Silva", "Souza"],
            "deathdate": [None, "2020-01-01"],
            "healthcare_expenses": [1000.0, 2000.0],
            "healthcare_coverage": [800.0, 1500.0],
        }
    )


@pytest.fixture
def sample_encounters_df() -> pd.DataFrame:
    """DataFrame de encontros clínicos de exemplo, no formato que sai da bronze."""
    return pd.DataFrame(
        {
            "id": [10, 11],
            "start": ["2023-01-01 08:00:00", "2023-01-02 09:00:00"],
            "stop": ["2023-01-01 10:00:00", "2023-01-02 09:30:00"],
            "patient": [1, 2],
            "encounterclass": ["ambulatory", "emergency"],
            "description": ["Consulta de rotina", "Atendimento de emergência"],
            "base_encounter_cost": [100.0, 250.0],
            "total_claim_cost": [300.0, 900.0],
            "payer_coverage": [200.0, 700.0],
            "reasondescription": [None, "Dor no peito"],
        }
    )


@pytest.fixture
def sample_conditions_df() -> pd.DataFrame:
    """DataFrame de condições de saúde de exemplo, no formato que sai da bronze."""
    return pd.DataFrame(
        {
            "start": ["2023-01-01", "2023-01-02"],
            "stop": [None, "2023-02-01"],
            "patient": [1, 2],
            "description": ["Hipertensão (disorder)", "Gripe"],
        }
    )
