import argparse
import logging
import os
from functools import partialmethod
from pathlib import Path

import faiss
from dotenv import load_dotenv
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from tqdm import tqdm
from transformers import logging as transformers_logging

from src.constants import (
    DEFAULT_PREPROCESSED_PARQUET,
    TOTAL_SIZE,
)
from src.helpers import convert_data_to_docs, read_preprocessed_parquet

os.environ["TRANSFORMERS_VERBOSITY"] = "error"
transformers_logging.set_verbosity_error()
logging.getLogger("transformers").setLevel(logging.ERROR)

tqdm.__init__ = partialmethod(tqdm.__init__, disable=True)

load_dotenv()
hf_token = os.getenv("HF_TOKEN")


def create_faiss_index(
    path: Path = DEFAULT_PREPROCESSED_PARQUET,
    index_path: str = "outputs/faiss_index",
    model_name: str = "all-MiniLM-L6-v2",
    total_size: int = TOTAL_SIZE,
):
	"""Creates a FAISS index from the preprocessed Parquet data and saves it to disk."""
    model = HuggingFaceEmbeddings(model_name=model_name)
    index = faiss.IndexFlatL2(384)

    vector_store = FAISS(
        embedding_function=model,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={},
    )

    data = read_preprocessed_parquet(size=total_size)
    docs = convert_data_to_docs(data)

    vector_store.add_documents(documents=docs)

    vector_store.save_local(index_path)
    print("FAISS index saved in {index_path}")


def faiss_search(
    query: str,
    index_path: str = "outputs/faiss_index",
    top_k: int = 5,
    model_name: str = "all-MiniLM-L6-v2",
):
	"""Performs a FAISS search on the query and returns the top-k results."""
    model = HuggingFaceEmbeddings(model_name=model_name)
    vector_store = FAISS.load_local(
        index_path, model, allow_dangerous_deserialization=True
    )

    results = vector_store.similarity_search_with_score(query, k=top_k)

    return results


def main(sample: bool = False):
    if sample:
        create_faiss_index(total_size=10000)
    else:
        create_faiss_index()
    print("FAISS index created")


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
