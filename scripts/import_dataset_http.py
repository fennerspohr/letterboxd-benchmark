import argparse
import json
import time
from pathlib import Path

import requests


def main():
    parser = argparse.ArgumentParser(
        description="Importa filmes pela API HTTP, passando pelo Nginx."
    )
    parser.add_argument(
        "--size",
        type=int,
        choices=[20_000, 50_000],
        default=50_000,
        help="Quantidade de registros a importar.",
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="URL base da API/Nginx.",
    )
    args = parser.parse_args()

    source = Path(f"data/movies_{args.size}.jsonl")
    if not source.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {source}")

    url = f"{args.url.rstrip('/')}/movies"
    imported = 0
    failed = 0
    start = time.time()

    with source.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            original = json.loads(line)

            # Envia somente os campos aceitos por MovieCreate.
            movie = {
                key: original.get(key)
                for key in (
                    "name",
                    "date",
                    "tagline",
                    "description",
                    "minute",
                    "rating",
                )
            }

            try:
                response = requests.post(url, json=movie, timeout=30)

                if response.status_code == 201:
                    imported += 1
                else:
                    failed += 1
                    print(
                        f"Falha na linha {line_number}: "
                        f"HTTP {response.status_code} - {response.text[:300]}"
                    )

            except requests.RequestException as error:
                failed += 1
                print(f"Falha na linha {line_number}: {error}")

            processed = imported + failed
            if processed % 100 == 0:
                print(
                    f"Processados: {processed}/{args.size} | "
                    f"Importados: {imported} | Falhas: {failed}"
                )

    elapsed = time.time() - start

    print("\nImportação concluída.")
    print(f"Arquivo: {source}")
    print(f"Importados: {imported}")
    print(f"Falhas: {failed}")
    print(f"Tempo total: {elapsed:.2f} segundos")
    print(f"Taxa média: {imported / elapsed:.2f} filmes/s")


if __name__ == "__main__":
    main()
