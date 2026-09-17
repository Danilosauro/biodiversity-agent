import pandas as pd


def apply_mapping(
    df: pd.DataFrame,
    mapping: dict
) -> pd.DataFrame:

    output = pd.DataFrame(index=df.index)

    for source, target in mapping.items():

        if source not in df.columns:
            raise ValueError(
                f"Source column not found: {source}"
            )

        output[target] = df[source]

    return output
