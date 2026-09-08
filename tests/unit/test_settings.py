from healthcare_analytics.config import settings


def test_get_env_var_retorna_default(monkeypatch):
    monkeypatch.delenv("TESTE_MEDICINAL", raising=False)
    assert (
        settings.get_env_var("TESTE_MEDICINAL", obrigatoria=False, default="dev")
        == "dev"
    )


def test_get_env_var_obrigatoria_ausente(monkeypatch):
    monkeypatch.delenv("TESTE_MEDICINAL", raising=False)

    try:
        settings.get_env_var("TESTE_MEDICINAL")
    except ValueError as error:
        assert "TESTE_MEDICINAL" in str(error)
    else:
        raise AssertionError(
            "Era esperado ValueError para variável obrigatória ausente"
        )


def test_get_database_url_prioriza_url_completa(monkeypatch):
    expected = "postgresql+psycopg2://user:password@database:5432/app"
    monkeypatch.setenv("DATABASE_URL", expected)
    assert settings.get_database_url() == expected


def test_get_database_url_monta_url_com_variaveis_separadas(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("APP_DB_USER", "usuario")
    monkeypatch.setenv("APP_DB_PASSWORD", "senha")
    monkeypatch.setenv("APP_DB_HOST", "postgres-app")
    monkeypatch.setenv("APP_DB_PORT", "5432")
    monkeypatch.setenv("APP_DB_NAME", "healthcare_analytics")

    result = settings.get_database_url()

    assert (
        result
        == "postgresql+psycopg2://usuario:senha@postgres-app:5432/healthcare_analytics"
    )
