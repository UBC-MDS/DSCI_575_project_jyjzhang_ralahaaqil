import argparse
from pathlib import Path
import gc
from heapq import nlargest

import duckdb
import pandas as pd
import pickle
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PREPROCESSED_PARQUET = PROJECT_ROOT / "data" / "processed" / "preprocessed_data.parquet"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
SHARD_SIZE = 100_000
TOTAL_SIZE = 4_645_281
SAMPLE_SIZE = 500_000


def read_chunk(path: Path = DEFAULT_PREPROCESSED_PARQUET, start: int = 0, end: int = SHARD_SIZE) -> pd.DataFrame:
    """Read ``end - start`` rows from Parquet using ``OFFSET start`` and ``LIMIT end - start``.

    Args:
        path: Parquet file to scan.
        start: Zero-based row offset (first row returned).
        end: Used with ``start`` so that exactly ``end - start`` rows are requested; must be >= ``start``.

    Returns:
        A DataFrame with up to ``end - start`` rows (fewer if the file ends early).

    Raises:
        ValueError: If ``end < start``.
    """
    if end < start:
        raise ValueError(f"end ({end}) must be >= start ({start})")
    return duckdb.sql(
        f"SELECT * FROM read_parquet('{path}') LIMIT {end - start} OFFSET {start}"
    ).df()


def create_shard(data: pd.DataFrame, filename: str) -> None:
    """Build a BM25 retriever from a chunk of preprocessed rows and save it as a pickle.

    Each row becomes a LangChain ``Document`` with ``page_content`` from ``data_content``
    and metadata from ``product``, ``parent_asin``, ``average_rating``, ``rating_number``,
    and ``review_text``.

    Args:
        data: DataFrame containing those columns.
        filename: Base name for the output file (``.pkl`` is appended).

    Returns:
        None
    """
    meta_cols = [
        "product",
        "parent_asin",
        "average_rating",
        "rating_number",
        "review_text",
    ]
    metas = data[meta_cols].to_dict("records")

    docs = [
        Document(page_content=pc, metadata=md)
        for pc, md in zip(data["data_content"], metas)
    ]

    retriever = BM25Retriever.from_documents(docs)
    OUTPUTS_DIR.mkdir(exist_ok=True)
    output_path = OUTPUTS_DIR / f"{filename}.pkl"
    with output_path.open("wb") as f:
        pickle.dump(retriever, f)
    del metas
    del docs
    del retriever

def create_all_shards(sample: bool = False):
    total_rows = SAMPLE_SIZE if sample else TOTAL_SIZE
    total_shards = total_rows // SHARD_SIZE
    for start in range(0, total_rows, SHARD_SIZE):
        print(f"Processing shard {start // SHARD_SIZE + 1} of {total_shards}")
        end = min(start + SHARD_SIZE - 1, total_rows - 1)
        data = read_chunk(start=start, end=end)
        create_shard(data, filename=f"bm25_shard_{start // SHARD_SIZE + 1}")
        del data
        
def search_all_shards(query: str, top_k: int = 5, per_shard_k: int | None = None) -> list[tuple[float, Document]]:
    if per_shard_k is None:
        per_shard_k = top_k

    all_shards = list(OUTPUTS_DIR.glob("*.pkl"))
    if not all_shards:
        raise FileNotFoundError(f"No shard pickles found in {OUTPUTS_DIR}")

    all_results: list[tuple[float, Document]] = []
    for shard in all_shards:
        print(f"Searching shard {shard}")
        with shard.open("rb") as f:
            retriever = pickle.load(f)

        query_tokens = retriever.preprocess_func(query)
        scores = retriever.vectorizer.get_scores(query_tokens)
        top_indices = nlargest(per_shard_k, range(len(scores)), key=lambda idx: scores[idx])

        for idx in top_indices:
            all_results.append((float(scores[idx]), retriever.docs[idx]))

        del scores
        del retriever
        gc.collect()

    all_results.sort(key=lambda item: item[0], reverse=True)
    return all_results[:top_k]

def main(sample: bool = False):
    print("======================== CREATING SHARDS ==========================")
    create_all_shards(sample=sample)
    print("\n\nAll shards created")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create BM25 shard pickles from preprocessed Parquet.")
    parser.add_argument(
        "--sample",
        action="store_true",
        help=f"Shard only the first {SAMPLE_SIZE:,} rows instead of the full {TOTAL_SIZE:,}-row dataset.",
    )
    args = parser.parse_args()
    main(sample=args.sample)