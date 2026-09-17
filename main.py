from pathlib import Path
import json

import pandas as pd

from src.pipeline.bronze import (
    ingest_to_bronze
)

from src.pipeline.silver import (
    normalize_dataset
)

from src.agent.agent import (
    analyze_dataset
)

from src.darwin_core.mapper import (
    apply_mapping
)

from src.darwin_core.validator import (
    validate_darwin_core
)

from src.quality.metrics import (
    calculate_quality
)


# ============================================================
# CONFIGURAÇÃO
# ============================================================

INPUT_FILE = (
    "examples/biodiversity_demo.csv"
)

BRONZE_DIR = (
    "data/bronze"
)

SILVER_FILE = (
    "data/silver/biodiversity.parquet"
)

GOLD_FILE = (
    "data/gold/darwin_core.csv"
)

QUALITY_FILE = (
    "reports/quality.json"
)

PLAN_FILE = (
    "logs/agent_plan.json"
)


# ============================================================
# DIRETÓRIOS
# ============================================================

def create_directories():

    directories = [

        "data/bronze",

        "data/silver",

        "data/gold",

        "logs",

        "reports",

    ]


    for directory in directories:

        Path(
            directory
        ).mkdir(
            parents=True,
            exist_ok=True
        )


# ============================================================
# CARREGAMENTO DO DATASET
# ============================================================

def load_dataset(
    file_path: str
) -> pd.DataFrame:
    """
    Carrega o dataset original.
    """

    path = Path(
        file_path
    )


    if not path.exists():

        raise FileNotFoundError(
            f"Dataset não encontrado: {file_path}"
        )


    if path.suffix.lower() != ".csv":

        raise ValueError(
            "Neste estágio do projeto o pipeline "
            "aceita somente arquivos CSV."
        )


    df = pd.read_csv(
        path
    )


    if df.empty:

        raise ValueError(
            "O dataset está vazio."
        )


    return df


# ============================================================
# PROFILING
# ============================================================

def profile_dataset(
    df: pd.DataFrame
) -> dict:
    """
    Produz informações estruturais para o agente.
    """

    profile = {

        "rows": len(df),

        "columns": len(
            df.columns
        ),

        "column_names": list(
            df.columns
        ),

        "dtypes": (
            df.dtypes
            .astype(str)
            .to_dict()
        ),

        "missing_values": (
            df.isna()
            .sum()
            .to_dict()
        ),

        "unique_values": (
            df.nunique()
            .to_dict()
        ),

    }


    return profile


# ============================================================
# SALVA PERFIL
# ============================================================

def save_profile(
    profile: dict
):

    profile_file = (
        "logs/dataset_profile.json"
    )


    with open(
        profile_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            profile,
            file,
            indent=2,
            ensure_ascii=False
        )


    return profile_file


# ============================================================
# SALVA PLANO DO AGENTE
# ============================================================

def save_agent_plan(
    plan
):

    with open(
        PLAN_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            plan.model_dump(),
            file,
            indent=2,
            ensure_ascii=False
        )


# ============================================================
# CONSTRÓI MAPEAMENTO
# ============================================================

def build_mapping(
    plan
) -> dict:
    """
    Converte o AgentPlan em um dicionário simples.

    Exemplo:

    {
        "nome_cientifico": "scientificName",
        "latitude_decimal": "decimalLatitude"
    }
    """

    mapping = {}


    for item in plan.mappings:

        source = (
            item.source_column
        )

        target = (
            item.darwin_core_term
        )


        mapping[source] = target


    return mapping


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

def main():

    print()
    print("=" * 70)
    print(" BIODIVERSITY AGENT")
    print("=" * 70)
    print()


    # ========================================================
    # PREPARAÇÃO
    # ========================================================

    create_directories()


    # ========================================================
    # 1. BRONZE
    # ========================================================

    print(
        "[1/6] Ingesting dataset into Bronze..."
    )


    bronze_file = (
        ingest_to_bronze(
            INPUT_FILE,
            BRONZE_DIR
        )
    )


    print(
        f"      Bronze: {bronze_file}"
    )


    # ========================================================
    # CARREGA BRONZE
    # ========================================================

    print()
    print(
        "      Loading Bronze dataset..."
    )


    df_bronze = load_dataset(
        str(bronze_file)
    )


    print(
        f"      Records: {len(df_bronze)}"
    )

    print(
        f"      Columns: {len(df_bronze.columns)}"
    )


    # ========================================================
    # 2. PROFILING + AGENTE
    # ========================================================

    print()
    print(
        "[2/6] Profiling dataset and running Llama 3.2..."
    )


    profile = profile_dataset(
        df_bronze
    )


    profile_file = save_profile(
        profile
    )


    print(
        f"      Profile: {profile_file}"
    )


    # --------------------------------------------------------
    # Colunas
    # --------------------------------------------------------

    columns = list(
        df_bronze.columns
    )


    print()
    print(
        "      Dataset columns:"
    )


    for column in columns:

        print(
            f"        - {column}"
        )


    # --------------------------------------------------------
    # Amostra
    # --------------------------------------------------------

    sample = (
        df_bronze
        .head(5)
        .to_dict(
            orient="records"
        )
    )


    # --------------------------------------------------------
    # Llama
    # --------------------------------------------------------

    plan = analyze_dataset(
        columns=columns,
        sample=sample
    )


    # --------------------------------------------------------
    # Salva plano
    # --------------------------------------------------------

    save_agent_plan(
        plan
    )


    print()
    print(
        f"      Agent plan: {PLAN_FILE}"
    )


    # --------------------------------------------------------
    # Decisão
    # --------------------------------------------------------

    print()
    print(
        "      Agent decision:"
    )


    print(
        f"      Accepted: {plan.accepted}"
    )


    print(
        f"      Reason: {plan.reason}"
    )


    # --------------------------------------------------------
    # Warnings
    # --------------------------------------------------------

    if plan.warnings:

        print()
        print(
            "      Warnings:"
        )


        for warning in plan.warnings:

            print(
                f"        - {warning}"
            )


    # --------------------------------------------------------
    # Rejeição
    # --------------------------------------------------------

    if not plan.accepted:

        raise RuntimeError(
            "O dataset foi rejeitado pelo agente.\n"
            f"Motivo: {plan.reason}"
        )


    # ========================================================
    # MAPEAMENTOS
    # ========================================================

    print()
    print(
        "      Proposed mappings:"
    )


    mapping = build_mapping(
        plan
    )


    for source, target in mapping.items():

        print(
            f"        {source} -> {target}"
        )


    if not mapping:

        raise RuntimeError(
            "O agente não produziu nenhum mapeamento."
        )


    # ========================================================
    # 3. SILVER
    # ========================================================

    print()
    print(
        "[3/6] Creating Silver dataset..."
    )


    normalize_dataset(
        str(bronze_file),
        SILVER_FILE
    )


    df_silver = pd.read_parquet(
        SILVER_FILE
    )


    print(
        f"      Silver: {SILVER_FILE}"
    )


    print(
        f"      Records: {len(df_silver)}"
    )


    # ========================================================
    # VALIDAÇÃO DAS TRANSFORMAÇÕES SILVER
    # ========================================================

    print()
    print(
        "      Checking transformed fields..."
    )


    # --------------------------------------------------------
    # Nome científico
    # --------------------------------------------------------

    if (
        "nome_popular" in df_silver.columns
        and "nome_cientifico" in df_silver.columns
    ):

        total_taxonomic = len(
            df_silver
        )


        successful_taxonomic = (
            df_silver[
                "nome_cientifico"
            ]
            .notna()
            .sum()
        )


        taxonomic_rate = (
            successful_taxonomic
            / total_taxonomic
            if total_taxonomic > 0
            else 0
        )


        print(
            "      Taxonomic conversion:"
            f" {successful_taxonomic}/"
            f"{total_taxonomic}"
            f" ({taxonomic_rate:.1%})"
        )


    # --------------------------------------------------------
    # Coordenadas
    # --------------------------------------------------------

    if (
        "latitude" in df_silver.columns
        and "latitude_decimal" in df_silver.columns
    ):

        valid_latitude = (
            df_silver[
                "latitude_decimal"
            ]
            .notna()
            .sum()
        )


        print(
            "      Latitude conversion:"
            f" {valid_latitude}/"
            f"{len(df_silver)}"
        )


    if (
        "longitude" in df_silver.columns
        and "longitude_decimal" in df_silver.columns
    ):

        valid_longitude = (
            df_silver[
                "longitude_decimal"
            ]
            .notna()
            .sum()
        )


        print(
            "      Longitude conversion:"
            f" {valid_longitude}/"
            f"{len(df_silver)}"
        )


    # ========================================================
    # 4. DARWIN CORE / GOLD
    # ========================================================

    print()
    print(
        "[4/6] Creating Darwin Core dataset..."
    )


    # --------------------------------------------------------
    # Mapeamento preferencial após transformação
    # --------------------------------------------------------

    transformed_mapping = {}

    for source, target in mapping.items():

        if (
            source == "nome_popular"
            and "nome_cientifico" in df_silver.columns
            and target == "scientificName"
        ):

            transformed_mapping[
                "nome_cientifico"
            ] = "scientificName"

            continue

        if (
            source == "latitude"
            and "latitude_decimal" in df_silver.columns
            and target == "decimalLatitude"
        ):

            transformed_mapping[
                "latitude_decimal"
            ] = "decimalLatitude"

            continue

        if (
            source == "longitude"
            and "longitude_decimal" in df_silver.columns
            and target == "decimalLongitude"
        ):

            transformed_mapping[
                "longitude_decimal"
            ] = "decimalLongitude"

            continue

        if source in df_silver.columns:

            transformed_mapping[
                source
            ] = target


        # ----------------------------------------------------
        # Nome popular
        # ----------------------------------------------------

        if (
            source == "nome_popular"
            and "nome_cientifico" in df_silver.columns
            and target == "scientificName"
        ):

            transformed_mapping[
                "nome_cientifico"
            ] = "scientificName"

            continue


        # ----------------------------------------------------
        # Latitude DMS
        # ----------------------------------------------------

        if (
            source == "latitude"
            and "latitude_decimal" in df_silver.columns
            and target == "decimalLatitude"
        ):

            transformed_mapping[
                "latitude_decimal"
            ] = "decimalLatitude"

            continue


        # ----------------------------------------------------
        # Longitude DMS
        # ----------------------------------------------------

        if (
            source == "longitude"
            and "longitude_decimal" in df_silver.columns
            and target == "decimalLongitude"
        ):

            transformed_mapping[
                "longitude_decimal"
            ] = "decimalLongitude"

            continue


        # ----------------------------------------------------
        # Mapeamento direto
        # ----------------------------------------------------

        if source in df_silver.columns:

            transformed_mapping[
                source
            ] = target


    print()
    print(
        "      Final mapping:"
    )


    for source, target in (
        transformed_mapping.items()
    ):

        print(
            f"        {source} -> {target}"
        )


    if not transformed_mapping:

        raise RuntimeError(
            "Nenhum mapeamento válido foi encontrado "
            "para o dataset Silver."
        )


    # --------------------------------------------------------
    # Aplica transformação
    # --------------------------------------------------------

    darwin_core = apply_mapping(
        df_silver,
        transformed_mapping
    )


    # ========================================================
    # VALIDAÇÃO DARWIN CORE
    # ========================================================

    print()
    print(
        "      Validating Darwin Core dataset..."
    )


    validation = (
        validate_darwin_core(
            darwin_core
        )
    )


    print()


    print(
        json.dumps(
            validation,
            indent=2,
            ensure_ascii=False
        )
    )


    if not validation["valid"]:

        raise RuntimeError(
            "A validação Darwin Core falhou."
        )


    # --------------------------------------------------------
    # GOLD
    # --------------------------------------------------------

    darwin_core.to_csv(
        GOLD_FILE,
        index=False
    )


    print()
    print(
        f"      Gold: {GOLD_FILE}"
    )


    # ========================================================
    # 5. QUALITY
    # ========================================================

    print()
    print(
        "[5/6] Calculating data quality..."
    )


    quality = (
        calculate_quality(
            darwin_core
        )
    )


    # --------------------------------------------------------
    # Indicadores adicionais
    # --------------------------------------------------------

    quality_report = {

        "dataset": {

            "input_file": INPUT_FILE,

            "bronze_file": str(
                bronze_file
            ),

            "silver_file": SILVER_FILE,

            "gold_file": GOLD_FILE,

            "records": len(
                darwin_core
            ),

        },


        "quality_metrics": quality,


        "darwin_core_validation": validation,


        "agent": {

            "accepted": plan.accepted,

            "reason": plan.reason,

            "warnings": plan.warnings,

            "cleaning_operations": (
                plan.cleaning_operations
            ),

            "validation_checks": (
                plan.validation_checks
            ),

        },


        "mapping": [

            {

                "source_column": (
                    item.source_column
                ),

                "darwin_core_term": (
                    item.darwin_core_term
                ),

                "confidence": (
                    item.confidence
                ),

                "justification": (
                    item.justification
                ),

            }

            for item in plan.mappings

        ],

    }


    # --------------------------------------------------------
    # Salva relatório de qualidade
    # --------------------------------------------------------

    with open(
        QUALITY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            quality_report,
            file,
            indent=2,
            ensure_ascii=False
        )


    print()
    print(
        f"      Quality report: {QUALITY_FILE}"
    )


    # ========================================================
    # 6. FINAL
    # ========================================================

    print()
    print(
        "[6/6] Pipeline completed."
    )


    print()
    print("=" * 70)
    print(" OUTPUTS")
    print("=" * 70)


    print(
        f"Bronze : {bronze_file}"
    )

    print(
        f"Silver : {SILVER_FILE}"
    )

    print(
        f"Gold   : {GOLD_FILE}"
    )

    print(
        f"Profile: {profile_file}"
    )

    print(
        f"Plan   : {PLAN_FILE}"
    )

    print(
        f"Quality: {QUALITY_FILE}"
    )


    print()
    print("=" * 70)
    print(" SUCCESS")
    print("=" * 70)
    print()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()
