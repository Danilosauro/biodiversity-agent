POPULAR_TO_SCIENTIFIC = {

    "onça-pintada":
        "Panthera onca",

    "anta":
        "Tapirus terrestris",

    "gambá-de-orelha-branca":
        "Didelphis albiventris",

    "carcará":
        "Caracara plancus",

    "tamanduá-bandeira":
        "Myrmecophaga tridactyla",

    "capivara":
        "Hydrochoerus hydrochaeris",

    "sagui-de-tufo-branco":
        "Callithrix jacchus",

    "tatu-bola":
        "Tolypeutes tricinctus",

    "beija-flor-tesoura":
        "Eupetula macroura",

    "raposa-do-campo":
        "Lycalopex vetulus",

    "lobo-guará":
        "Chrysocyon brachyurus",
}


def popular_to_scientific(
    popular_name: str
) -> str | None:

    if not popular_name:
        return None

    normalized = (
        popular_name
        .strip()
        .lower()
    )

    return POPULAR_TO_SCIENTIFIC.get(
        normalized
    )
