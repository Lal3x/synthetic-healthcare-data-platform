from unittest.mock import Mock, call

from healthcare_analytics import main


def test_run_pipeline_executa_etapas_na_ordem(monkeypatch):
    engine = object()
    events = Mock()
    monkeypatch.setattr(main, "get_engine", Mock(return_value=engine))
    monkeypatch.setattr(main, "create_schemas", lambda value: events("schemas", value))
    monkeypatch.setattr(main, "load_bronze", lambda value: events("bronze", value))
    monkeypatch.setattr(main, "load_silver", lambda value: events("silver", value))
    monkeypatch.setattr(main, "load_gold", lambda value: events("gold", value))

    main.run_pipeline()

    assert events.call_args_list == [
        call("schemas", engine),
        call("bronze", engine),
        call("silver", engine),
        call("gold", engine),
    ]


def test_run_pipeline_reseta_antes_das_etapas(monkeypatch):
    engine = object()
    reset = Mock()
    monkeypatch.setattr(main, "get_engine", Mock(return_value=engine))
    monkeypatch.setattr(main, "reset_database", reset)
    monkeypatch.setattr(main, "create_schemas", Mock())
    monkeypatch.setattr(main, "load_bronze", Mock())
    monkeypatch.setattr(main, "load_silver", Mock())
    monkeypatch.setattr(main, "load_gold", Mock())

    main.run_pipeline(reset_before=True)

    reset.assert_called_once_with(engine=engine, confirm=True)


def test_build_parser_reconhece_reset():
    args = main.build_parser().parse_args(["--reset"])
    assert args.reset is True
