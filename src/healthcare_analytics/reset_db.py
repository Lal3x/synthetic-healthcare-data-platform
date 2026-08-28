import argparse

from sqlalchemy import text
from sqlalchemy.engine import Engine

from healthcare_analytics.config.settings import (
    SCHEMA_BRONZE,
    SCHEMA_GOLD,
    SCHEMA_SILVER,
)
from healthcare_analytics.utils.db import get_engine

DEFAULT_SCHEMAS = [SCHEMA_BRONZE, SCHEMA_SILVER, SCHEMA_GOLD]


def reset_database(
    engine: Engine | None = None,
    schemas: list[str] | None = None,
    confirm: bool = True,
) -> list[str]:
    """
    Remove todos os schemas configurados do banco, em cascata.
    Útil para reiniciar a pipeline do zero.
    """
    engine = engine or get_engine()
    schemas_to_drop = [schema for schema in (schemas or DEFAULT_SCHEMAS) if schema]

    if confirm:
        print(
            "ATENÇÃO: esta operação remove todos os dados dos schemas "
            f"{schemas_to_drop} com DROP SCHEMA ... CASCADE."
        )

    with engine.begin() as conn:
        for schema in schemas_to_drop:
            conn.execute(text(f"DROP SCHEMA IF EXISTS {schema} CASCADE"))
            print(f"Schema removido: {schema}")

    return schemas_to_drop


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Remove os schemas bronze, silver e gold do banco de dados."
    )
    parser.add_argument(
        "--schemas",
        nargs="*",
        default=DEFAULT_SCHEMAS,
        help="Lista opcional de schemas a serem removidos. Ex.: bronze silver gold",
    )
    parser.add_argument(
        "--no-confirm",
        action="store_true",
        help="Ignora a confirmação e executa imediatamente a remoção.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    reset_database(schemas=args.schemas, confirm=not args.no_confirm)


if __name__ == "__main__":
    main()
