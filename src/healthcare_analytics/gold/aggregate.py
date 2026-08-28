# src/healthcare_analytics/gold/aggregate.py
import pandas as pd
from sqlalchemy.engine import Engine

from healthcare_analytics.config.settings import SCHEMA_GOLD, SCHEMA_SILVER
from healthcare_analytics.gold.aggregations import (
    create_encounter_summary,
    create_one_big_table,
    create_patient_summary,
)
from healthcare_analytics.utils.db import get_engine


def load_gold(engine: Engine | None = None) -> None:
    """
    Orquestra o ETL da camada gold: lê da silver, agrega, carrega na gold.
    """
    engine = engine or get_engine()

    try:
        print("Lendo dados da camada silver...")
        patients = pd.read_sql(f"SELECT * FROM {SCHEMA_SILVER}.patients", engine)
        encounters = pd.read_sql(f"SELECT * FROM {SCHEMA_SILVER}.encounters", engine)
        print("Extração concluída.")
    except Exception as e:
        print(f"Erro ao ler dados da camada silver: {e}")
        raise

    try:
        obt_df = create_one_big_table(patients, encounters)
        patient_summary_df = create_patient_summary(patients, encounters)
        encounter_summary_df = create_encounter_summary(encounters)
        print("\nTransformações para a camada gold concluídas.")
    except Exception as e:
        print(f"Erro durante as transformações para a camada gold: {e}")
        raise

    try:
        print("Carregando dados na camada gold...")
        obt_df.to_sql(
            "obt_encounters",
            engine,
            schema=SCHEMA_GOLD,
            if_exists="replace",
            index=False,
        )
        patient_summary_df.to_sql(
            "patient_summary",
            engine,
            schema=SCHEMA_GOLD,
            if_exists="replace",
            index=False,
        )
        encounter_summary_df.to_sql(
            "encounter_summary",
            engine,
            schema=SCHEMA_GOLD,
            if_exists="replace",
            index=False,
        )
        print("Carga gold concluída com sucesso.")
    except Exception as e:
        print(f"Erro ao carregar dados na camada gold: {e}")
        raise


if __name__ == "__main__":
    load_gold()
