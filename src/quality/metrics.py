def calculate_quality(df):

    n = len(df)

    completeness = (
        df.notna().mean().mean()
    )

    uniqueness = (
        df["occurrenceID"].nunique() / n
        if n > 0 else 0
    )

    spatial_validity = (
        df["decimalLatitude"]
        .between(-90, 90)
        &
        df["decimalLongitude"]
        .between(-180, 180)
    ).mean()

    temporal_validity = (
        df["eventDate"].notna()
    ).mean()

    score = (
        0.30 * completeness +
        0.25 * uniqueness +
        0.25 * spatial_validity +
        0.20 * temporal_validity
    )

    return {
        "completeness": completeness,
        "uniqueness": uniqueness,
        "spatial_validity": spatial_validity,
        "temporal_validity": temporal_validity,
        "overall_score": score,
    }
