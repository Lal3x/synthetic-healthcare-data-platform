import pandas as pd
from sqlalchemy.engine import Engine

from healthcare_analytics.config.settings import SCHEMA_BRONZE, SCHEMA_SILVER
from healthcare_analytics.silver.transformations import (
    check_data_quality,
    transform_conditions,
    transform_encounters,
    transform_patients,
)
from healthcare_analytics.utils.db import get_engine


def load_silver(engine: Engine | None = None) -> None:
    """
    Orquestra o ETL da camada silver: lê da bronze, valida, transforma,
    valida de novo, e carrega na silver.
    """
    engine = engine or get_engine()

    try:
        print("Lendo dados da camada bronze...")
        patients = pd.read_sql(f"SELECT * FROM {SCHEMA_BRONZE}.bronze_patients", engine)
        encounters = pd.read_sql(
            f"SELECT * FROM {SCHEMA_BRONZE}.bronze_encounters", engine
        )
        conditions = pd.read_sql(
            f"SELECT * FROM {SCHEMA_BRONZE}.bronze_conditions", engine
        )
        print("Extração concluída.")
    except Exception as e:
        print(f"Erro na extração dos dados da bronze: {e}")
        raise

    if not all(
        [
            check_data_quality(patients, "patients"),
            check_data_quality(encounters, "encounters"),
            check_data_quality(conditions, "conditions"),
        ]
    ):
        raise ValueError("Falha na qualidade dos dados de origem (bronze)")

    try:
        patients_clean = transform_patients(patients)
        encounters_clean = transform_encounters(encounters)
        conditions_clean = transform_conditions(conditions)
        print("\nTransformações concluídas.")
    except Exception as e:
        print(f"Erro durante a transformação: {e}")
        raise

    if not all(
        [
            check_data_quality(patients_clean, "patients"),
            check_data_quality(encounters_clean, "encounters"),
            check_data_quality(conditions_clean, "conditions"),
        ]
    ):
        raise ValueError("Falha na qualidade dos dados transformados (silver)")

    print("\nCarregando dados na camada silver...")
    patients_clean.to_sql(
        "patients", engine, schema=SCHEMA_SILVER, if_exists="replace", index=False
    )
    encounters_clean.to_sql(
        "encounters", engine, schema=SCHEMA_SILVER, if_exists="replace", index=False
    )
    conditions_clean.to_sql(
        "conditions", engine, schema=SCHEMA_SILVER, if_exists="replace", index=False
    )
    print("Carga silver concluída com sucesso.")


if __name__ == "__main__":
    load_silver()
