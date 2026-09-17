from langchain.tools import tool
import pandas as pd


@tool
def profile_dataset(path: str) -> dict:
    """
    Analisa estruturalmente um dataset CSV.

    Retorna colunas, tipos, nulos, cardinalidade
    e exemplos de valores.
    """

    df = pd.read_csv(path)

    profile = {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "missing_values": df.isna().sum().to_dict(),
        "unique_values": df.nunique().to_dict(),
        "sample": df.head(5).to_dict(orient="records"),
    }

    return profile
