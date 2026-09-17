import pandas as pd


REQUIRED_TERMS = [
    "occurrenceID",
    "scientificName",
    "eventDate",
    "decimalLatitude",
    "decimalLongitude",
]


def validate_darwin_core(df: pd.DataFrame):

    errors = []
    warnings = []

    # Campos obrigatórios
    for column in REQUIRED_TERMS:

        if column not in df.columns:

            errors.append(
                f"Missing required term: {column}"
            )

    # occurrenceID
    if "occurrenceID" in df.columns:

        duplicated = df["occurrenceID"].duplicated().sum()

        if duplicated > 0:

            errors.append(
                f"Duplicated occurrenceID: {duplicated}"
            )

    # latitude
    if "decimalLatitude" in df.columns:

        invalid = (
            ~df["decimalLatitude"]
            .between(-90, 90)
        ).sum()

        if invalid > 0:

            errors.append(
                f"Invalid latitude values: {invalid}"
            )

    # longitude
    if "decimalLongitude" in df.columns:

        invalid = (
            ~df["decimalLongitude"]
            .between(-180, 180)
        ).sum()

        if invalid > 0:

            errors.append(
                f"Invalid longitude values: {invalid}"
            )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }
