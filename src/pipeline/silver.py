import pandas as pd

from src.darwin_core.taxonomy import (
    popular_to_scientific
)

from src.darwin_core.coordinates import (
    dms_to_decimal
)


def normalize_dataset(
    input_file: str,
    output_file: str
):

    df = pd.read_csv(
        input_file
    )


    # ========================================================
    # NORMALIZAÇÃO DOS NOMES DAS COLUNAS
    # ========================================================

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(
            " ",
            "_"
        )
    )


    # ========================================================
    # NORMALIZAÇÃO DE STRINGS
    # ========================================================

    for column in df.select_dtypes(
        include=["object"]
    ).columns:

        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
        )


    # ========================================================
    # NOME POPULAR -> NOME CIENTÍFICO
    # ========================================================

    if "nome_popular" in df.columns:

        df["nome_cientifico"] = (
            df["nome_popular"]
            .apply(
                popular_to_scientific
            )
        )


    # ========================================================
    # DATA
    # ========================================================

    if "data_observacao" in df.columns:

        df["data_observacao"] = (
            pd.to_datetime(
                df["data_observacao"],
                format="%d/%m/%Y",
                errors="coerce"
            )
        )


    # ========================================================
    # LATITUDE
    # ========================================================

    if "latitude" in df.columns:

        df["latitude_decimal"] = (
            df["latitude"]
            .apply(
                dms_to_decimal
            )
        )


    # ========================================================
    # LONGITUDE
    # ========================================================

    if "longitude" in df.columns:

        df["longitude_decimal"] = (
            df["longitude"]
            .apply(
                dms_to_decimal
            )
        )


    # ========================================================
    # QUANTIDADE
    # ========================================================

    if "quantidade" in df.columns:

        df["quantidade"] = pd.to_numeric(
            df["quantidade"],
            errors="coerce"
        )


    # ========================================================
    # SALVA SILVER
    # ========================================================

    df.to_parquet(
        output_file,
        index=False
    )


    return df
