from datetime import UTC, datetime
from pathlib import Path

from airflow.sdk import dag, task


@dag(
    dag_id="healthcare_pipeline",
    description="Executa o pipeline de dados bronze, silver e gold.",
    start_date=datetime(2026, 8, 22, tzinfo=UTC),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    tags=["healthcare_analytics", "etl"],
)
def healthcare_pipeline():
    @task
    def verificar_banco() -> None:
        from healthcare_analytics.utils.db import get_engine

        engine = get_engine()
        engine.dispose()

    @task
    def verificar_arquivos() -> None:
        from healthcare_analytics.bronze.ingest import FILES
        from healthcare_analytics.config.settings import RAW_DATA_DIR

        ausentes = [
            filename
            for filename in FILES.values()
            if not (Path(RAW_DATA_DIR) / filename).is_file()
        ]

        if ausentes:
            raise FileNotFoundError(f"Arquivos CSV ausentes: {', '.join(ausentes)}")

    @task
    def criar_schemas() -> None:
        from healthcare_analytics.utils.schema import create_schemas

        create_schemas()

    @task
    def carregar_bronze() -> None:
        from healthcare_analytics.bronze.ingest import load_bronze

        load_bronze()

    @task
    def transformar_silver() -> None:
        from healthcare_analytics.silver.transform import load_silver

        load_silver()

    @task
    def agregar_gold() -> None:
        from healthcare_analytics.gold.aggregate import load_gold

        load_gold()

    banco = verificar_banco()
    arquivos = verificar_arquivos()
    schemas = criar_schemas()
    bronze = carregar_bronze()
    silver = transformar_silver()
    gold = agregar_gold()

    [banco, arquivos] >> schemas >> bronze >> silver >> gold


healthcare_pipeline()
