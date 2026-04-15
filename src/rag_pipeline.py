from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings, ChatHuggingFace, HuggingFaceEndpoint
from langchain_community.vectorstores import FAISS
import os
from dotenv import load_dotenv
from transformers import pipeline, logging as transformers_logging
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import logging
from tqdm import tqdm
from functools import partialmethod

from src.helpers import read_preprocessed_parquet, convert_data_to_docs
from src.constants import (
    DEFAULT_PREPROCESSED_PARQUET,
    TOTAL_SIZE,
    OUTPUTS_DIR
)

os.environ["TRANSFORMERS_VERBOSITY"] = "error"
transformers_logging.set_verbosity_error()
logging.getLogger("transformers").setLevel(logging.ERROR)

tqdm.__init__ = partialmethod(tqdm.__init__, disable=True)

RAG_VECSTORE_PATH = OUTPUTS_DIR / "faiss_index"
LLM_REPO_ID = "openai/gpt-oss-safeguard-20b"
PROVIDER = "groq"

load_dotenv()
hf_token = os.getenv("HF_TOKEN")

def store_vectors(
        path: Path = DEFAULT_PREPROCESSED_PARQUET,
        output_path: Path = RAG_VECSTORE_PATH,
        total_size: int = TOTAL_SIZE,
        chunk = True,
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
        top_k: int = 5
):
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    vectorstore = FAISS.load_local(
        index_path, embeddings, allow_dangerous_deserialization=True
    )
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": top_k}
    )

    return retriever

def build_prompt():
    return ChatPromptTemplate.from_template(
        """
        You are a helpful Amazon shopping assistant for software products.
        Answer the question using ONLY the following context (real product reviews + metadata).
        Always cite the product ASIN and title when possible.

        Customer Reviews and Metadata:
        {context}
        
        Question:
        {input}
        
        Answer:
        """
    )

def build_context(docs):
    return "\n\n".join([
        f"Product ASIN: {doc.metadata.get('parent_asin', 'N/A')}\n"
        f"Title: {doc.metadata.get('product_title', '')}\n"
        f"Average Rating: {doc.metadata['average_rating']}/5]\n"
        f"Rating Number: {doc.metadata['rating_number']}/5]\n"
        f"Text: {doc.page_content}"
        for doc in docs
    ])

def build_language_model(
        repo_id: str = LLM_REPO_ID,
        max_new_tokens: int = 100
        ):
    llm_endpoint = HuggingFaceEndpoint(
        repo_id=repo_id,
        task="text-generation",
        max_new_tokens=max_new_tokens,
        provider=PROVIDER,
        huggingfacehub_api_token=hf_token
    )

    return ChatHuggingFace(llm=llm_endpoint)

def build_rag(
        query: str,
        vecstore_path: Path = RAG_VECSTORE_PATH,
        embed_model: str = "all-MiniLM-L6-v2",
        top_k: int = 5,
        llm_repo: str = LLM_REPO_ID,
        max_new_tokens: int = 100
):
    retriever = retrieve(
        index_path=vecstore_path,
        model_name=embed_model,
        top_k=top_k
    )
    llm = build_language_model(
        repo_id=llm_repo,
        max_new_tokens=max_new_tokens
    )
    
    rag_chain = (
        {
            "context": retriever | RunnableLambda(build_context),
            "input": RunnablePassthrough()
        }
        | build_prompt()
        | llm
        | StrOutputParser()
    )

    return rag_chain.invoke(query)
    


def main() -> None:
    print("Creating new vector store...")
    store_vectors(chunk=False)
    print(f"\nVector store saved to {RAG_VECSTORE_PATH}")

if __name__ == "__main__":
    main()