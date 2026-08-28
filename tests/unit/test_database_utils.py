from contextlib import nullcontext
from unittest.mock import Mock

from sqlalchemy.exc import SQLAlchemyError

from healthcare_analytics.utils import db, schema


def test_get_engine_cria_engine_e_valida_conexao(monkeypatch):
    connection = Mock()
    engine = Mock()
    engine.connect.return_value = nullcontext(connection)
    create_engine = Mock(return_value=engine)
    monkeypatch.setattr(db, "create_engine", create_engine)

    result = db.get_engine(echo=True)

    assert result is engine
    create_engine.assert_called_once_with(
        db.DATABASE_URL, pool_pre_ping=True, echo=True
    )
    connection.execute.assert_called_once()


def test_get_engine_propaga_erro_de_conexao(monkeypatch):
    monkeypatch.setattr(
        db, "create_engine", Mock(side_effect=SQLAlchemyError("indisponível"))
    )

    try:
        db.get_engine()
    except SQLAlchemyError as error:
        assert "indisponível" in str(error)
    else:
        raise AssertionError("Era esperado um erro de conexão")


def test_create_schemas_executa_cada_comando_sql(monkeypatch, tmp_path):
    ddl = tmp_path / "schemas.sql"
    ddl.write_text("CREATE SCHEMA bronze; CREATE SCHEMA silver;", encoding="utf-8")
    monkeypatch.setattr(schema, "DDL_PATH", ddl)
    connection = Mock()
    engine = Mock()
    engine.begin.return_value = nullcontext(connection)

    schema.create_schemas(engine)

    assert connection.execute.call_count == 2
