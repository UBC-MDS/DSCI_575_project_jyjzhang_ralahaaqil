from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
import faiss
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
import json
import duckdb
import pandas as pd
from pathlib import Path
import argparse


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PREPROCESSED_PARQUET = PROJECT_ROOT / "data" / "processed" / "preprocessed_data.parquet"
BATCH_SIZE = 100_000
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

def parquet_to_documents(
    df: pd.DataFrame,
    content_column: str = "data_content",
    metadata_columns: list[str] = None
):
    if metadata_columns is None:
        metadata_columns = [col for col in df.columns if col != content_column]
    
    documents = []
    for idx, row in df.iterrows():
        metadata = {col: row[col] for col in metadata_columns}
        content = str(row[content_column])
        
        metadata_str = json.dumps(metadata, ensure_ascii=False, default=str)
        combined_content = f"Metadata: {metadata_str}\nContent: {content}"
        
        doc = Document(
            page_content=combined_content,
            metadata=metadata
        )
        documents.append(doc)
    
    return documents


def create_faiss_index(
    path: Path = DEFAULT_PREPROCESSED_PARQUET,
    index_path: str = "outputs/faiss_index",
    content_column: str = "data_content",
    metadata_columns: list[str] = [
        "parent_asin", "average_rating", "rating_number" # add product
        ],
    model_name: str = "all-MiniLM-L6-v2",
    batch_size: int = 100000,
    total_size: int = 4645281
):
    
    model = HuggingFaceEmbeddings(model_name=model_name)
    index = faiss.IndexFlatL2(384)
    
    vector_store = FAISS(
        embedding_function=model,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={},
    )
    
    for start in range(0, total_size, batch_size):

        print(f"Processing batch {start // batch_size + 1}")
        end = min(start + batch_size - 1, total_size - 1)
        
        batch_df = read_chunk(path=path, start=start, end=end)
        
        documents = parquet_to_documents(
            df=batch_df,
            content_column=content_column,
            metadata_columns=metadata_columns
        )
        ids = [doc.metadata["parent_asin"] for doc in documents]

        vector_store.add_documents(documents=documents, ids=ids)
        
    vector_store.save_local(index_path)
    print("FAISS index saved in {index_path}")

def faiss_search(
        query: str,
        index_path: str = "outputs/faiss_index",
        top_k: int = 5,
        model_name: str = "all-MiniLM-L6-v2"
):
    model = HuggingFaceEmbeddings(model_name=model_name)
    vector_store = FAISS.load_local(
        index_path, model, allow_dangerous_deserialization=True
    )

    results = vector_store.similarity_search_with_score(
        query, k=top_k
        )
    
    return results 

def main(sample: bool = False):
    if sample:
        create_faiss_index(total_size=500000)
    else:
        create_faiss_index()
    print("FAISS index created")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create BM25 shard pickles from preprocessed Parquet.")
    parser.add_argument(
        "--sample",
        action="store_true",
        help=f"Create index on 500000 rows instead of the full {TOTAL_SIZE:,}-row dataset.",
    )
    args = parser.parse_args()
    main(sample=args.sample)