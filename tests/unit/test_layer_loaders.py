from unittest.mock import Mock

import pandas as pd
import pytest

from healthcare_analytics.gold import aggregate
from healthcare_analytics.silver import transform


def test_load_silver_transforma_e_grava_tres_conjuntos(monkeypatch):
    source = pd.DataFrame({"id": [1]})
    transformed = pd.DataFrame({"id": [1], "valid": [True]})
    monkeypatch.setattr(transform.pd, "read_sql", Mock(return_value=source))
    monkeypatch.setattr(transform, "check_data_quality", Mock(return_value=True))
    monkeypatch.setattr(transform, "transform_patients", Mock(return_value=transformed))
    monkeypatch.setattr(
        transform, "transform_encounters", Mock(return_value=transformed)
    )
    monkeypatch.setattr(
        transform, "transform_conditions", Mock(return_value=transformed)
    )
    to_sql = Mock()
    monkeypatch.setattr(pd.DataFrame, "to_sql", to_sql)

    transform.load_silver(engine=Mock())

    assert transform.pd.read_sql.call_count == 3
    assert to_sql.call_count == 3


def test_load_silver_interrompe_quando_origem_e_invalida(monkeypatch):
    monkeypatch.setattr(
        transform.pd, "read_sql", Mock(return_value=pd.DataFrame({"id": [1]}))
    )
    monkeypatch.setattr(transform, "check_data_quality", Mock(return_value=False))
    transform_patients = Mock()
    monkeypatch.setattr(transform, "transform_patients", transform_patients)

    with pytest.raises(ValueError, match="Falha na qualidade"):
        transform.load_silver(engine=Mock())

    transform_patients.assert_not_called()


def test_load_gold_agrega_e_grava_tres_resultados(monkeypatch):
    source = pd.DataFrame({"id": [1]})
    result = pd.DataFrame({"metric": [1]})
    monkeypatch.setattr(aggregate.pd, "read_sql", Mock(return_value=source))
    monkeypatch.setattr(aggregate, "create_one_big_table", Mock(return_value=result))
    monkeypatch.setattr(aggregate, "create_patient_summary", Mock(return_value=result))
    monkeypatch.setattr(
        aggregate, "create_encounter_summary", Mock(return_value=result)
    )
    to_sql = Mock()
    monkeypatch.setattr(pd.DataFrame, "to_sql", to_sql)

    aggregate.load_gold(engine=Mock())

    assert aggregate.pd.read_sql.call_count == 2
    assert to_sql.call_count == 3
