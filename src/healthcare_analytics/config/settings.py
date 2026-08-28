# src/healthcare_analytics/config/settings.py
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import URL

load_dotenv()


def get_env_var(
    nome: str, obrigatoria: bool = True, default: str | None = None
) -> str | None:
    """
    Busca uma variável de ambiente, com opção de ser obrigatória ou não.
    Levanta erro claro se for obrigatória e não estiver definida.
    """
    valor = os.getenv(nome, default)

    if obrigatoria and not valor:
        raise ValueError(f"Variável de ambiente obrigatória não encontrada: {nome}")

    return valor


def get_database_url() -> str:
    """Retorna a URL informada ou a monta com as configurações do Postgres."""
    database_url = get_env_var("DATABASE_URL", obrigatoria=False)

    if database_url:
        return database_url

    url = URL.create(
        drivername="postgresql+psycopg2",
        username=get_env_var("APP_DB_USER", obrigatoria=False, default="healthcare_analytics"),
        password=get_env_var("APP_DB_PASSWORD", obrigatoria=False, default="healthcare_analytics"),
        host=get_env_var("APP_DB_HOST", obrigatoria=False, default="localhost"),
        port=int(get_env_var("APP_DB_PORT", obrigatoria=False, default="5432")),
        database=get_env_var("APP_DB_NAME", obrigatoria=False, default="healthcare_analytics"),
    )

    return url.render_as_string(hide_password=False)


# Banco de dados
DATABASE_URL: str = get_database_url()

# Ambiente da aplicação (dev, staging, prod)
APP_ENV: str = get_env_var("APP_ENV", obrigatoria=False, default="dev")

# Nível de log
LOG_LEVEL: str = get_env_var("LOG_LEVEL", obrigatoria=False, default="INFO")

# Nomes dos schemas no Postgres
SCHEMA_BRONZE: str = get_env_var("SCHEMA_BRONZE", obrigatoria=False, default="bronze")
SCHEMA_SILVER: str = get_env_var("SCHEMA_SILVER", obrigatoria=False, default="silver")
SCHEMA_GOLD: str = get_env_var("SCHEMA_GOLD", obrigatoria=False, default="gold")

# Diretório de dados (landing zone dos CSVs brutos)
RAW_DATA_DIR: Path = Path(
    get_env_var("RAW_DATA_DIR", obrigatoria=False, default="data/raw")
)
