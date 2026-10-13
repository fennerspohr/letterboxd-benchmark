import json
from pathlib import Path

import pandas as pd

SOURCE = Path("data/movies.csv")
OUTPUT_DIR = Path("data")
COLUMNS = ["id", "name", "date", "tagline", "description", "minute", "rating"]


def normalize_record(row):
    movie_id = int(row["id"])

    def optional_string(value):
        if pd.isna(value):
            return None
        return str(value).strip()

    def optional_int(value):
        if pd.isna(value):
            return None
        return int(value)

    def optional_float(value):
        if pd.isna(value):
            return None
        return float(value)

    return {
        "_id": movie_id,
        "name": optional_string(row["name"]),
        "date": optional_int(row["date"]),
        "tagline": optional_string(row["tagline"]),
        "description": optional_string(row["description"]),
        "minute": optional_int(row["minute"]),
        "rating": optional_float(row["rating"]),
    }


def main():
    if not SOURCE.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {SOURCE}. "
            "Verifique se movies.csv está na pasta data/."
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(
        SOURCE,
        usecols=COLUMNS,
        nrows=50_000,
    )

    # Remover registros sem identificador e duplicatas de ID.
    df = df.dropna(subset=["id"])
    df = df.drop_duplicates(subset=["id"], keep="first")

    records = [normalize_record(row) for _, row in df.iterrows()]

    if len(records) < 50_000:
        print(
            f"Aviso: foram encontrados apenas {len(records)} "
            "registros válidos nas primeiras 50 mil linhas."
        )

    for size in (50_000, 20_000):
        subset = records[:size]
        output_file = OUTPUT_DIR / f"movies_{size}.jsonl"

        with output_file.open("w", encoding="utf-8") as file:
            for record in subset:
                file.write(json.dumps(record, ensure_ascii=False) + "\n")

        print(f"{output_file}: {len(subset)} registros")

    print("Preparação concluída.")


if __name__ == "__main__":
    main()
