from pathlib import Path

import duckdb
import pandas as pd
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.constants import DEFAULT_PREPROCESSED_PARQUET, META_COLS, TOTAL_SIZE


def read_preprocessed_parquet(
    path: Path = DEFAULT_PREPROCESSED_PARQUET,
    size: int = TOTAL_SIZE,
) -> pd.DataFrame:
    """Load the preprocessed Parquet table."""
    return duckdb.read_parquet(str(path)).limit(size).df()


def convert_data_to_docs(
        data: pd.DataFrame,
        chunk: bool = False,
        chunk_args: dict = {"chunk_size": 100, "chunk_overlap": 20}
        ) -> list[Document]:
    """Convert the data to a list of Document objects."""
    metas = data.loc[:, list(META_COLS)].to_dict(orient="records")

    docs = [
        Document(page_content=pc, metadata=md)
        for pc, md in zip(data["data_content"], metas, strict=True)
    ]

    if chunk:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_args["chunk_size"],
            chunk_overlap=chunk_args["chunk_overlap"]
        )
        docs = text_splitter.split_documents(docs)
    
    return docs