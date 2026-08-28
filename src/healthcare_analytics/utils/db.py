from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from healthcare_analytics.config.settings import DATABASE_URL


def get_engine(echo: bool = False) -> Engine:
    """
    Cria e retorna uma engine do SQLAlchemy conectada ao Postgres.
    'pool_pre_ping=True' garante que a conexão está ativa antes de cada uso,
    evitando erros de conexão "caída" em execuções longas.
    """
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=echo)

        # Força um teste real de conexão (create_engine sozinho é lento e não garante que a conexão está ativa)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        return engine

    except SQLAlchemyError as e:
        print(f"Erro ao conectar com o banco de dados: {e}")
        raise


if __name__ == "__main__":
    engine = get_engine()
    print("Conexão com o banco estabelecida com sucesso.")
