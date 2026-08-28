# src/healthcare_analytics/bronze/ingest.py
from uuid import uuid4

import pandas as pd
from sqlalchemy import inspect, text
from sqlalchemy.engine import Connection, Engine

from healthcare_analytics.bronze.readers import (
    add_execution_metadata,
    read_csv_lowercase,
    validate_not_empty,
)
from healthcare_analytics.config.settings import RAW_DATA_DIR, SCHEMA_BRONZE
from healthcare_analytics.utils.db import get_engine
from healthcare_analytics.utils.schema import create_schemas

# Mapeia nomes das tabelas de destino para os nomes dos arquivos CSV de origem.
FILES = {
    "bronze_patients": "patients.csv",
    "bronze_encounters": "encounters.csv",
    "bronze_conditions": "conditions.csv",
}

NATURAL_KEYS = {
    "bronze_patients": ["id"],
    "bronze_encounters": ["id"],
    "bronze_conditions": ["patient", "encounter", "code", "start"],
}


def _quoted(connection: Connection, identifier: str) -> str:
    """Escapa identificadores SQL conhecidos pelo pipeline."""
    return connection.dialect.identifier_preparer.quote(identifier)


def upsert_dataframe(
    engine: Engine,
    dataframe: pd.DataFrame,
    schema: str,
    table_name: str,
    natural_keys: list[str],
) -> None:
    """Insere dados novos e atualiza somente registros que foram alterados."""
    missing_keys = set(natural_keys) - set(dataframe.columns)
    if missing_keys:
        raise ValueError(
            f"Colunas-chave ausentes em {table_name}: {sorted(missing_keys)}"
        )

    if dataframe[natural_keys].isnull().any().any():
        raise ValueError(f"{table_name} contém valores nulos em sua chave natural")

    dataframe = dataframe.drop_duplicates(subset=natural_keys, keep="last")
    staging_table = f"_staging_{table_name}_{uuid4().hex[:8]}"

    with engine.begin() as connection:
        if not inspect(connection).has_table(table_name, schema=schema):
            dataframe.head(0).to_sql(
                table_name, connection, schema=schema, if_exists="append", index=False
            )

        quoted_schema = _quoted(connection, schema)
        quoted_table = _quoted(connection, table_name)
        qualified_table = f"{quoted_schema}.{quoted_table}"
        key_columns = ", ".join(_quoted(connection, key) for key in natural_keys)
        index_name = _quoted(connection, f"uq_{table_name}_natural_key")

        connection.execute(
            text(
                f"CREATE UNIQUE INDEX IF NOT EXISTS {index_name} "
                f"ON {qualified_table} ({key_columns})"
            )
        )

        dataframe.to_sql(
            staging_table,
            connection,
            schema=schema,
            if_exists="replace",
            index=False,
        )

        quoted_columns = [_quoted(connection, column) for column in dataframe.columns]
        columns = ", ".join(quoted_columns)
        update_columns = [
            column for column in dataframe.columns if column not in natural_keys
        ]
        assignments = ", ".join(
            f"{_quoted(connection, column)} = EXCLUDED.{_quoted(connection, column)}"
            for column in update_columns
        )
        changed = " OR ".join(
            f"{qualified_table}.{_quoted(connection, column)} "
            f"IS DISTINCT FROM EXCLUDED.{_quoted(connection, column)}"
            for column in update_columns
            if column != "execution_date"
        )
        quoted_staging = _quoted(connection, staging_table)

        connection.execute(
            text(
                f"INSERT INTO {qualified_table} ({columns}) "
                f"SELECT {columns} FROM {quoted_schema}.{quoted_staging} "
                f"ON CONFLICT ({key_columns}) DO UPDATE SET {assignments} "
                f"WHERE {changed}"
            )
        )
        connection.execute(text(f"DROP TABLE {quoted_schema}.{quoted_staging}"))


def load_bronze(engine: Engine | None = None) -> None:
    """
    Lê os CSVs da landing zone (raw) e carrega no schema bronze do Postgres.
    Registros novos são inseridos e registros alterados são atualizados pela chave
    natural. Reprocessar o mesmo arquivo não duplica nem modifica os dados.
    """
    engine = engine or get_engine()

    for table_name, filename in FILES.items():
        path = RAW_DATA_DIR / filename
        print(f"Lendo {path}...")

        df = read_csv_lowercase(path)

        if not validate_not_empty(df, filename):
            raise ValueError(f"O arquivo {filename} está vazio ou não foi encontrado")

        df = add_execution_metadata(df)

        upsert_dataframe(
            engine=engine,
            dataframe=df,
            schema=SCHEMA_BRONZE,
            table_name=table_name,
            natural_keys=NATURAL_KEYS[table_name],
        )

        print(f"{len(df)} linhas processadas em {SCHEMA_BRONZE}.{table_name}")

    print("\nCarga bronze concluída.")


if __name__ == "__main__":
    create_schemas()
    load_bronze()
