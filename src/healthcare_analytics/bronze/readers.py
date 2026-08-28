from datetime import datetime
from pathlib import Path

import pandas as pd


def read_csv_lowercase(path: Path) -> pd.DataFrame:
    """
    Lê um CSV e normaliza os nomes das colunas (minúsculas, sem espaços extras).
    Retorna DataFrame vazio se o arquivo não existir, em vez de quebrar o pipeline.
    """
    try:
        df = pd.read_csv(path, low_memory=False)
        df.columns = df.columns.str.strip().str.lower()
        return df
    except FileNotFoundError:
        print(f"Erro: arquivo não encontrado em {path}")
        return pd.DataFrame()


def add_execution_metadata(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adiciona coluna de metadado de carga: data de execução.
    Ajuda a rastrear quando cada linha entrou na camada bronze.
    """
    df = df.copy()
    df["execution_date"] = datetime.today().strftime("%Y-%m-%d")
    return df


def validate_not_empty(df: pd.DataFrame, nome_arquivo: str) -> bool:
    """
    Verifica se o DataFrame tem dados antes de tentar carregar no banco.
    Retorna True se válido (tem dados), False se vazio.
    """
    if df.empty:
        print(f"Aviso: {nome_arquivo} está vazio ou não encontrado. Pulando.")
        return False
    return True
