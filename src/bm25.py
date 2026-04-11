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


def read_chunk(path: Path = DEFAULT_PREPROCESSED_PARQUET, start: int = 0, end: int = 10000) -> pd.DataFrame:
    if end < start:
        raise ValueError(f"end ({end}) must be >= start ({start})")
    limit = end - start + 1
    resolved = str(Path(path).expanduser().resolve())
    path_sql = resolved.replace("'", "''")
    return duckdb.sql(
        f"SELECT * FROM read_parquet('{path_sql}') LIMIT {limit} OFFSET {start}"
    ).df()


def create_shard(data: pd.DataFrame, filename: str) -> Path:
    meta_cols = ["parent_asin", "average_rating", "rating_number"]
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
    gc.collect()
    return output_path

def create_all_shards():
    total_rows = TOTAL_SIZE
    total_shards = total_rows // SHARD_SIZE
    for start in range(0, total_rows, SHARD_SIZE):
        print(f"Processing shard {start // SHARD_SIZE + 1} of {total_shards}")
        end = min(start + SHARD_SIZE - 1, total_rows - 1)
        data = read_chunk(start=start, end=end)
        output_path = create_shard(data, filename=f"bm25_shard_{start // SHARD_SIZE + 1}")
        print(f"Saved shard {start // SHARD_SIZE + 1} to {output_path}")
        del data
        gc.collect()
        
def search_all_shards(query: str, top_k: int = 5, per_shard_k: int | None = None) -> list[tuple[float, Document]]:
    if per_shard_k is None:
        per_shard_k = top_k

    all_shards = sorted(OUTPUTS_DIR.glob("*.pkl"))
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

def main():
    create_all_shards()
    print("All shards created")

if __name__ == "__main__":
    main()