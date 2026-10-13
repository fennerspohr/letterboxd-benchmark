import argparse
import json
import os
from pathlib import Path

from pymongo import MongoClient, ReplaceOne
from pymongo.errors import BulkWriteError

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://admin:benchmark_local@localhost:27017/?authSource=admin",
)

DATABASE_NAME = "letterboxd"
COLLECTION_NAME = "movies"


def main():
    parser = argparse.ArgumentParser(
        description="Importa filmes para o MongoDB."
    )
    parser.add_argument(
        "--size",
        type=int,
        choices=[20_000, 50_000],
        default=50_000,
        help="Quantidade de registros a importar.",
    )
    args = parser.parse_args()

    source = Path(f"data/movies_{args.size}.jsonl")
    if not source.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {source}")

    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)

    try:
        client.admin.command("ping")
        collection = client[DATABASE_NAME][COLLECTION_NAME]

        # Limpa os dados anteriores para garantir o tamanho do experimento.
        collection.drop()

        operations = []
        imported = 0

        with source.open("r", encoding="utf-8") as file:
            for line in file:
                movie = json.loads(line)
                operations.append(
                    ReplaceOne({"_id": movie["_id"]}, movie, upsert=True)
                )

                if len(operations) >= 1000:
                    collection.bulk_write(operations, ordered=False)
                    imported += len(operations)
                    operations.clear()

        if operations:
            collection.bulk_write(operations, ordered=False)
            imported += len(operations)

        print(f"Arquivo: {source}")
        print(f"Documentos importados: {imported}")
        print(f"Documentos na coleção: {collection.count_documents({})}")

    except BulkWriteError as error:
        print("Erro durante a importação:")
        print(error.details)
        raise
    finally:
        client.close()


if __name__ == "__main__":
    main()
