from pathlib import Path

import pandas as pd

from healthcare_analytics.bronze.readers import (
    add_execution_metadata,
    read_csv_lowercase,
    validate_not_empty,
)


def test_read_csv_lowercase_normaliza_colunas(tmp_path: Path):
    """Cria um CSV temporário com colunas maiúsculas/espaçadas e confere a normalização."""
    csv_path = tmp_path / "teste.csv"
    csv_path.write_text("Id, Nome ,IDADE\n1,João,30\n2,Maria,25\n")

    df = read_csv_lowercase(csv_path)

    assert list(df.columns) == ["id", "nome", "idade"]
    assert len(df) == 2


def test_read_csv_lowercase_arquivo_inexistente_retorna_vazio(tmp_path: Path):
    caminho_falso = tmp_path / "nao_existe.csv"
    df = read_csv_lowercase(caminho_falso)
    assert df.empty


def test_add_execution_metadata_adiciona_coluna():
    df = pd.DataFrame({"id": [1, 2]})
    result = add_execution_metadata(df)
    assert "execution_date" in result.columns
    assert len(result["execution_date"].unique()) == 1


def test_add_execution_metadata_nao_altera_df_original():
    """Garante que a função não modifica o DataFrame recebido (evita efeitos colaterais)."""
    df = pd.DataFrame({"id": [1, 2]})
    add_execution_metadata(df)
    assert "execution_date" not in df.columns


def test_validate_not_empty_com_dados_retorna_true():
    df = pd.DataFrame({"id": [1]})
    assert validate_not_empty(df, "arquivo.csv") is True


def test_validate_not_empty_vazio_retorna_false():
    df = pd.DataFrame()
    assert validate_not_empty(df, "arquivo.csv") is False
