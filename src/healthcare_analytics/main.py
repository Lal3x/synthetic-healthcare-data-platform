import argparse

from healthcare_analytics.bronze.ingest import load_bronze
from healthcare_analytics.gold.aggregate import load_gold
from healthcare_analytics.reset_db import reset_database
from healthcare_analytics.silver.transform import load_silver
from healthcare_analytics.utils.db import get_engine
from healthcare_analytics.utils.schema import create_schemas


def run_pipeline(reset_before: bool = False) -> None:
    """
    Executa a pipeline completa em ordem:
    schemas -> bronze -> silver -> gold.
    """
    engine = get_engine()

    if reset_before:
        reset_database(engine=engine, confirm=True)

    create_schemas(engine)
    load_bronze(engine)
    load_silver(engine)
    load_gold(engine)

    print("\nPipeline completa executada com sucesso.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Executa a pipeline de dados em camadas do projeto healthcare_analytics."
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Apaga os schemas bronze, silver e gold antes de executar a pipeline.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    run_pipeline(reset_before=args.reset)


if __name__ == "__main__":
    main()
