from pathlib import Path
import shutil
import json
from datetime import datetime


def ingest_to_bronze(
    input_file: str,
    bronze_dir: str = "data/bronze"
):

    bronze = Path(bronze_dir)
    bronze.mkdir(parents=True, exist_ok=True)

    source = Path(input_file)

    destination = bronze / source.name

    shutil.copy2(source, destination)

    metadata = {
        "source_file": str(source),
        "bronze_file": str(destination),
        "ingestion_timestamp": datetime.utcnow().isoformat(),
        "size_bytes": source.stat().st_size,
    }

    with open(
        bronze / "metadata.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            metadata,
            f,
            indent=2,
            ensure_ascii=False
        )

    return destination
