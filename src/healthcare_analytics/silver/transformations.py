# src/healthcare_analytics/silver/transformations.py
import numpy as np
import pandas as pd


def transform_patients(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma os dados de pacientes para a camada silver:
    - Cria nome completo, status de vida (dead/alive)
    - Calcula diferença entre cobertura e despesas de saúde
    - Indica se o paciente ultrapassou a cobertura
    """
    print("Transformando dados de pacientes...")
    cols = [
        "id",
        "birthdate",
        "gender",
        "race",
        "ethnicity",
        "first",
        "last",
        "deathdate",
        "healthcare_expenses",
        "healthcare_coverage",
    ]
    patients = df[cols].copy()

    patients["full_name"] = (
        (patients["first"].fillna("") + " " + patients["last"].fillna(""))
        .str.strip()
        .replace(r"\s+", " ", regex=True)
    )

    patients["death"] = np.where(patients["deathdate"].notna(), "dead", "alive")

    coverage = pd.to_numeric(patients["healthcare_coverage"], errors="coerce").fillna(0)
    expenses = pd.to_numeric(patients["healthcare_expenses"], errors="coerce").fillna(0)
    patients["coverage_minus_expenses"] = coverage - expenses

    patients["over_expenses"] = np.where(patients["coverage_minus_expenses"] < 0, 1, 0)

    # patients["income"] = patients["income"].fillna(0)

    patients = patients.drop(columns=["first", "last"])

    return patients


def transform_encounters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma os dados de encontros clínicos para a camada silver:
    - Converte datas, calcula duração do encontro em horas
    """
    print("Transformando dados de encontros...")
    cols = [
        "id",
        "start",
        "stop",
        "patient",
        "encounterclass",
        "description",
        "base_encounter_cost",
        "total_claim_cost",
        "payer_coverage",
        "reasondescription",
    ]
    encounters = df[cols].copy()

    encounters = encounters.dropna(subset=["id", "patient"])

    encounters["start"] = pd.to_datetime(encounters["start"], errors="coerce")
    encounters["stop"] = pd.to_datetime(encounters["stop"], errors="coerce")

    encounters["duration_hours"] = (
        encounters["stop"] - encounters["start"]
    ).dt.total_seconds() / 3600

    return encounters


def transform_conditions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma os dados de condições de saúde para a camada silver:
    - Separa descrição da condição do tipo (texto entre parênteses)
    """
    print("Transformando dados de condições...")
    cols = ["start", "stop", "patient", "description"]
    conditions = df[cols].copy()

    conditions["condition"] = (
        conditions["description"].str.replace(r"\s*\(.*\)", "", regex=True).str.strip()
    )
    conditions["condition_type"] = conditions["description"].str.extract(r"\((.*?)\)")

    return conditions


def check_data_quality(df: pd.DataFrame, table_name: str) -> bool:
    """
    Verificações básicas de qualidade: DataFrame vazio, nulos em colunas
    críticas, valores negativos em custos.
    """
    print(f"\nVerificando qualidade dos dados: {table_name}")

    if df.empty:
        print(f"Alerta: DataFrame de {table_name} está vazio!")
        return False

    if table_name in ("patients", "encounters") and df["id"].isnull().any():
        print("Alerta: coluna 'id' contém valores nulos.")
        return False

    if table_name == "encounters":
        if (df["base_encounter_cost"] < 0).any():
            print("Alerta: 'base_encounter_cost' contém valores negativos.")
            return False
        if (df["total_claim_cost"] < 0).any():
            print("Alerta: 'total_claim_cost' contém valores negativos.")
            return False

    print(f"Qualidade de {table_name} OK.")
    return True
