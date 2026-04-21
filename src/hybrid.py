import pickle

from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from src.constants import BM25_PICKLE_PATH


def hybrid_retrieval(query: str):
	"""Performs hybrid retrieval using BM25 and FAISS."""
    with BM25_PICKLE_PATH.open("rb") as f:
        bm25_retriever = pickle.load(f)

    model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = FAISS.load_local(
        "outputs/faiss_index", model, allow_dangerous_deserialization=True
    )

    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, vector_store.as_retriever()],
        weights=[0.4, 0.6],
    )
    return ensemble_retriever.invoke(query)
