from contextlib import nullcontext
from unittest.mock import Mock

from healthcare_analytics import reset_db


def test_reset_database_remove_schemas_informados():
    connection = Mock()
    engine = Mock()
    engine.begin.return_value = nullcontext(connection)

    result = reset_db.reset_database(
        engine=engine,
        schemas=["bronze", "", "gold"],
        confirm=False,
    )

    assert result == ["bronze", "gold"]
    assert connection.execute.call_count == 2
    statements = [str(item.args[0]) for item in connection.execute.call_args_list]
    assert statements == [
        "DROP SCHEMA IF EXISTS bronze CASCADE",
        "DROP SCHEMA IF EXISTS gold CASCADE",
    ]


def test_build_parser_reconhece_schemas_e_no_confirm():
    args = reset_db.build_parser().parse_args(
        ["--schemas", "bronze", "silver", "--no-confirm"]
    )

    assert args.schemas == ["bronze", "silver"]
    assert args.no_confirm is True
