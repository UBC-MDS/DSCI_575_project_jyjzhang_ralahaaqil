from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PREPROCESSED_PARQUET = (
    PROJECT_ROOT / "data" / "processed" / "preprocessed_data.parquet"
)
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

BM25_PICKLE_PATH = OUTPUTS_DIR / "bm25_retriever.pkl"

META_COLS = [
    "product",
    "parent_asin",
    "average_rating",
    "rating_number",
]

TOTAL_SIZE = 84804
