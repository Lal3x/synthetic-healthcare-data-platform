import pandas as pd

from healthcare_analytics.silver.transformations import (
    check_data_quality,
    transform_conditions,
    transform_encounters,
    transform_patients,
)

# -------------------------------
# transform_patients
# -------------------------------


def test_transform_patients_cria_full_name(sample_patients_df):
    result = transform_patients(sample_patients_df)
    assert result.loc[0, "full_name"] == "João Silva"


def test_transform_patients_marca_death_corretamente(sample_patients_df):
    result = transform_patients(sample_patients_df)
    assert result.loc[0, "death"] == "alive"
    assert result.loc[1, "death"] == "dead"


def test_transform_patients_calcula_coverage_minus_expenses(sample_patients_df):
    result = transform_patients(sample_patients_df)
    # paciente 1: 800 - 1000 = -200
    assert result.loc[0, "coverage_minus_expenses"] == -200.0


def test_transform_patients_marca_over_expenses(sample_patients_df):
    result = transform_patients(sample_patients_df)
    # paciente 1 gastou mais do que a cobertura
    assert result.loc[0, "over_expenses"] == 1
    # paciente 2: 1500 - 2000 = -500, também acima
    assert result.loc[1, "over_expenses"] == 1


def test_transform_patients_remove_colunas_de_nome_originais(sample_patients_df):
    result = transform_patients(sample_patients_df)
    assert "first" not in result.columns
    assert "last" not in result.columns


def test_transform_patients_com_campos_nulos():
    """Garante que a função não quebra quando nome/custos vêm nulos."""
    df = pd.DataFrame(
        {
            "id": [1],
            "birthdate": ["1990-01-01"],
            "gender": ["M"],
            "race": ["white"],
            "ethnicity": ["nonhispanic"],
            "first": [None],
            "last": [None],
            "deathdate": [None],
            "healthcare_expenses": [None],
            "healthcare_coverage": [None],
        }
    )

    result = transform_patients(df)

    assert result.loc[0, "full_name"] == ""
    assert result.loc[0, "coverage_minus_expenses"] == 0.0
    assert result.loc[0, "over_expenses"] == 0


# -------------------------------
# transform_encounters
# -------------------------------


def test_transform_encounters_converte_datas(sample_encounters_df):
    result = transform_encounters(sample_encounters_df)
    assert pd.api.types.is_datetime64_any_dtype(result["start"])
    assert pd.api.types.is_datetime64_any_dtype(result["stop"])


def test_transform_encounters_calcula_duracao_em_horas(sample_encounters_df):
    result = transform_encounters(sample_encounters_df)
    # primeiro encontro: 08:00 até 10:00 = 2 horas
    assert result.loc[0, "duration_hours"] == 2.0


def test_transform_encounters_remove_linhas_sem_id_ou_patient(sample_encounters_df):
    df = sample_encounters_df.copy()
    df.loc[0, "id"] = None
    result = transform_encounters(df)
    assert len(result) == 1


# -------------------------------
# transform_conditions
# -------------------------------


def test_transform_conditions_separa_descricao_e_tipo(sample_conditions_df):
    result = transform_conditions(sample_conditions_df)
    assert result.loc[0, "condition"] == "Hipertensão"
    assert result.loc[0, "condition_type"] == "disorder"


def test_transform_conditions_sem_parenteses_nao_tem_tipo(sample_conditions_df):
    result = transform_conditions(sample_conditions_df)
    # "Gripe" não tem parênteses, então condition_type deve ser nulo
    assert pd.isna(result.loc[1, "condition_type"])


# -------------------------------
# check_data_quality
# -------------------------------


def test_check_data_quality_dataframe_vazio_falha():
    df = pd.DataFrame()
    assert check_data_quality(df, "patients") is False


def test_check_data_quality_id_nulo_falha():
    df = pd.DataFrame({"id": [1, None, 3]})
    assert check_data_quality(df, "patients") is False


def test_check_data_quality_custo_negativo_falha():
    df = pd.DataFrame(
        {
            "id": [1, 2],
            "base_encounter_cost": [100, -50],
            "total_claim_cost": [200, 300],
        }
    )
    assert check_data_quality(df, "encounters") is False


def test_check_data_quality_dados_validos_passa():
    df = pd.DataFrame(
        {
            "id": [1, 2],
            "base_encounter_cost": [100, 150],
            "total_claim_cost": [200, 300],
        }
    )
    assert check_data_quality(df, "encounters") is True
