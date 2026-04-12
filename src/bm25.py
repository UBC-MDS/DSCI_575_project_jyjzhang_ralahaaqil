from pathlib import Path
from heapq import nlargest

import duckdb
import pandas as pd
import pickle
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PREPROCESSED_PARQUET = PROJECT_ROOT / "data" / "processed" / "preprocessed_data.parquet"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
BM25_PICKLE_PATH = OUTPUTS_DIR / "bm25_retriever.pkl"

META_COLS = [
    "product",
    "parent_asin",
    "average_rating",
    "rating_number",
]


def read_preprocessed_parquet(path: Path = DEFAULT_PREPROCESSED_PARQUET) -> pd.DataFrame:
    """Load the full preprocessed Parquet table."""
    return duckdb.read_parquet(str(path)).df()


def create_bm25_pickle(
    parquet_path: Path = DEFAULT_PREPROCESSED_PARQUET,
    output_path: Path = BM25_PICKLE_PATH,
) -> None:
    """Build a BM25 retriever from all preprocessed rows and save it as one pickle.

    Each row becomes a LangChain ``Document`` with ``page_content`` from ``data_content``
    and metadata from ``product``, ``parent_asin``, ``average_rating``, and ``rating_number``.
    """
    data = read_preprocessed_parquet(parquet_path)
    metas = data[META_COLS].to_dict("records")

    docs = [
        Document(page_content=pc, metadata=md)
        for pc, md in zip(data["data_content"], metas, strict=True)
    ]

    retriever = BM25Retriever.from_documents(docs)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as f:
        pickle.dump(retriever, f)


def search(
    query: str,
    top_k: int = 5,
    pickle_path: Path = BM25_PICKLE_PATH,
) -> list[tuple[Document, float]]:
    """Run BM25 on the single saved index and return the top ``top_k`` (document, score) pairs."""
    if not pickle_path.is_file():
        raise FileNotFoundError(f"No BM25 index found at {pickle_path}")

    with pickle_path.open("rb") as f:
        retriever = pickle.load(f)

    query_tokens = retriever.preprocess_func(query)
    scores = retriever.vectorizer.get_scores(query_tokens)
    top_indices = nlargest(top_k, range(len(scores)), key=lambda idx: scores[idx])

    return [(retriever.docs[idx], float(scores[idx])) for idx in top_indices]


def main() -> None:
    print("======================== BUILDING BM25 INDEX ==========================")
    create_bm25_pickle()
    print(f"\nBM25 index saved to {BM25_PICKLE_PATH}")


if __name__ == "__main__":
    main()
