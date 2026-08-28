import pandas as pd


def create_one_big_table(
    patients_df: pd.DataFrame, encounters_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Cria uma "One Big Table" (OBT) unindo pacientes e encontros.
    Granularidade: por encontro clínico.
    """
    print("Criando a One Big Table (OBT)...")

    obt = encounters_df.merge(
        patients_df,
        left_on="patient",
        right_on="id",
        how="left",
        suffixes=("_encounter", "_patient"),
    )

    obt = obt.rename(
        columns={
            "id_encounter": "encounter_id",
            "patient": "patient_id",
            "start": "encounter_start_date",
            "stop": "encounter_end_date",
            "description": "encounter_description",
            "id_patient": "patient_original_id",
        }
    )

    cols = [
        "encounter_id",
        "patient_id",
        "encounter_start_date",
        "encounter_end_date",
        "encounterclass",
        "encounter_description",
        "duration_hours",
        "total_claim_cost",
        "payer_coverage",
        "gender",
        "race",
        "ethnicity",
        "full_name",
    ]
    return obt[cols]


def create_patient_summary(
    patients_df: pd.DataFrame, encounters_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Cria tabela de resumo agregada por paciente: total de encontros,
    custo total, duração média.
    """
    print("Criando tabela de resumo por paciente...")

    encounters_agg = (
        encounters_df.groupby("patient")
        .agg(
            total_encounters=("id", "count"),
            total_claim_cost=("total_claim_cost", "sum"),
            avg_encounter_duration_hours=("duration_hours", "mean"),
        )
        .reset_index()
        .rename(columns={"patient": "id"})
    )

    patient_summary = patients_df.merge(encounters_agg, on="id", how="left")

    patient_summary = patient_summary.rename(columns={"id": "patient_id"}).fillna(0)

    # Remove colunas financeiras de renda, não fazem parte do escopo da gold
    patient_summary = patient_summary.drop(columns=["income"], errors="ignore")

    return patient_summary


def create_encounter_summary(encounters_df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria tabela de resumo agregada por tipo de encontro (encounterclass).
    """
    print("Criando tabela de resumo por tipo de encontro...")

    return (
        encounters_df.groupby("encounterclass")
        .agg(
            total_encounters=("id", "count"),
            avg_claim_cost=("total_claim_cost", "mean"),
            sum_claim_cost=("total_claim_cost", "sum"),
            avg_encounter_duration_hours=("duration_hours", "mean"),
        )
        .reset_index()
    )
