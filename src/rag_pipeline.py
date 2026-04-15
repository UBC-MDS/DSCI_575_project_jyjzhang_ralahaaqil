import logging
import os
from functools import partialmethod
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from ollama import Client
from tqdm import tqdm
from transformers import logging as transformers_logging

from src.constants import DEFAULT_PREPROCESSED_PARQUET, OUTPUTS_DIR, TOTAL_SIZE
from src.helpers import convert_data_to_docs, read_preprocessed_parquet
from src.hybrid_retrieval import hybrid_retrieval

os.environ["TRANSFORMERS_VERBOSITY"] = "error"
transformers_logging.set_verbosity_error()
logging.getLogger("transformers").setLevel(logging.ERROR)

tqdm.__init__ = partialmethod(tqdm.__init__, disable=True)

RAG_VECSTORE_PATH = OUTPUTS_DIR / "faiss_index"
LLM_PROVIDER = "kimi-k2.5:cloud"

SYSTEM_PROMPT = """
You are a helpful Amazon shopping assistant for software products.
Answer the question using ONLY the following context (real product reviews + metadata).
Always cite the product ASIN and title when possible.
"""

load_dotenv()
ollama_token = os.getenv("OLLAMA_API_KEY")


def store_vectors(
    path: Path = DEFAULT_PREPROCESSED_PARQUET,
    output_path: Path = RAG_VECSTORE_PATH,
    total_size: int = TOTAL_SIZE,
    chunk=True,
    chunk_args: dict = {"chunk_size": 100, "chunk_overlap": 20},
    model_name: str = "all-MiniLM-L6-v2",
):
    print("Reading data...")
    data = read_preprocessed_parquet(path=path, size=total_size)
    print("Converting to documents...")
    docs = convert_data_to_docs(data, chunk=chunk, chunk_args=chunk_args)
    print("Storing vectors...")
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    vectorstore = FAISS.from_documents(docs, embeddings)
    vectorstore.save_local(output_path)


def retrieve(
    index_path: Path = RAG_VECSTORE_PATH,
    model_name: str = "all-MiniLM-L6-v2",
    top_k: int = 5,
):
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    vectorstore = FAISS.load_local(
        index_path, embeddings, allow_dangerous_deserialization=True
    )
    retriever = vectorstore.as_retriever(
        search_type="similarity", search_kwargs={"k": top_k}
    )

    return retriever


def build_prompt(context: str, input: str):
    return f"""
    Customer Reviews and Metadata:
    {context}

    Question:
    {input}

    Answer:
    """.strip()


def build_context(docs):
    return "\n\n".join(
        [
            f"Product ASIN: {doc.metadata.get('parent_asin', 'N/A')}\n"
            f"Title: {doc.metadata.get('product_title', '')}\n"
            f"Average Rating: {doc.metadata['average_rating']}/5]\n"
            f"Rating Number: {doc.metadata['rating_number']}/5]\n"
            f"Text: {doc.page_content}"
            for doc in docs
        ]
    )


def setup_client():
    client = Client(
        host="https://ollama.com",
        headers={"Authorization": f"Bearer {ollama_token}"},
    )
    return client


def ask_rag(query: str, hybrid: bool = False):
    if hybrid:
        docs = hybrid_retrieval(query)
    else:
        docs = retrieve().invoke(query)
    context = build_context(docs)
    prompt = build_prompt(context, query)
    client = setup_client()

    return client.generate(
        model=LLM_PROVIDER,
        prompt=prompt,
        system=SYSTEM_PROMPT,
        stream=False,
    ).response


def main() -> None:
    print("Creating new vector store...")
    store_vectors(chunk=False)
    print(f"\nVector store saved to {RAG_VECSTORE_PATH}")


if __name__ == "__main__":
    main()
