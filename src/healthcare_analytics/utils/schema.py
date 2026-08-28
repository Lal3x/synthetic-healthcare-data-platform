from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import Engine

from healthcare_analytics.utils.db import get_engine

DDL_PATH = Path("sql/ddl/create_schemas.sql")


def create_schemas(engine: Engine | None = None) -> None:
    """
    Lê o script SQL de criação de schemas e executa no banco.
    Idempotente: usa 'IF NOT EXISTS', então pode rodar quantas vezes quiser.
    """
    engine = engine or get_engine()

    sql_script = DDL_PATH.read_text(encoding="utf-8")

    with engine.begin() as conn:
        for statement in sql_script.strip().split(";"):
            statement = statement.strip()
            if statement:
                conn.execute(text(statement))

    print("Schemas criados/verificados com sucesso: bronze, silver, gold")


if __name__ == "__main__":
    create_schemas()
