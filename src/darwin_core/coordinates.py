import re


def dms_to_decimal(
    coordinate: str
) -> float:

    """
    Converte coordenada em graus/minutos/segundos
    para graus decimais.

    Exemplos:

    12°58'17"S
    -> -12.9713889

    38°30'05"W
    -> -38.5013889
    """

    if not isinstance(
        coordinate,
        str
    ):

        raise ValueError(
            "Coordinate must be a string."
        )

    pattern = (
        r"(\d+)[°]\s*"
        r"(\d+)['′]\s*"
        r"([\d.]+)[\"″]?\s*"
        r"([NSEW])"
    )

    match = re.match(
        pattern,
        coordinate.strip().upper()
    )

    if not match:

        raise ValueError(
            f"Invalid DMS coordinate: {coordinate}"
        )

    degrees = float(
        match.group(1)
    )

    minutes = float(
        match.group(2)
    )

    seconds = float(
        match.group(3)
    )

    direction = match.group(4)


    decimal = (
        degrees
        + minutes / 60
        + seconds / 3600
    )


    if direction in ["S", "W"]:

        decimal *= -1


    return decimal
