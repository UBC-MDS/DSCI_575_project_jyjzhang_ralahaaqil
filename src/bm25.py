import argparse
import pickle
from heapq import nlargest
from pathlib import Path

from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

from src.constants import (
    BM25_PICKLE_PATH,
    TOTAL_SIZE,
)
from src.helpers import convert_data_to_docs, read_preprocessed_parquet


def create_bm25_pickle(
    output_path: Path = BM25_PICKLE_PATH,
    total_size: int = TOTAL_SIZE,
) -> None:
    """Build a BM25 retriever from preprocessed rows and save it as one pickle.

    Each row in the selected subset becomes a LangChain ``Document`` with ``page_content`` from ``data_content``
    and metadata from ``product``, ``parent_asin``, ``average_rating``, and ``rating_number``.
    """
    data = read_preprocessed_parquet(size=total_size)
    docs = convert_data_to_docs(data)

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


def main(sample: bool = False) -> None:
    print("======================== BUILDING BM25 INDEX ==========================")
    if sample:
        create_bm25_pickle(total_size=25000)
    else:
        create_bm25_pickle()
    print(f"\nBM25 index saved to {BM25_PICKLE_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create BM25 shard pickles from preprocessed Parquet."
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help=f"Create index on 10000 rows instead of the full {TOTAL_SIZE:,}-row dataset.",
    )
    args = parser.parse_args()
    main(sample=args.sample)
