import gc
from pathlib import Path

from datasets import load_dataset

DATASET = "Software"
DEBUG = False


def download_data():
    """Stores vectors in FAISS index to disk."""
    print("======================== DOWNLOADING DATA ==========================")
    Path("data/raw").mkdir(exist_ok=True)
    print("Created data/raw directory")

    if DEBUG:
        import psutil

        rss_mib = psutil.Process().memory_info().rss / (1024**2)
        print(f"DEBUG mode enabled — process RAM before download: {rss_mib:.1f} MiB")

    print(f"\n\nDownloading {DATASET} dataset...")
    dataset = load_dataset(
        "McAuley-Lab/Amazon-Reviews-2023",
        f"raw_review_{DATASET}",
        trust_remote_code=True,
    )
    dataset["full"].to_parquet("data/raw/reviews.parquet")
    print(f"\nDownloaded {DATASET} dataset reviews to data/raw/reviews.parquet")
    del dataset
    gc.collect()

    print(f"\n\nDownloading {DATASET} dataset metadata...")
    metadata = load_dataset(
        "McAuley-Lab/Amazon-Reviews-2023",
        f"raw_meta_{DATASET}",
        split="full",
        trust_remote_code=True,
    )
    metadata.to_parquet("data/raw/metadata.parquet")
    print(f"\nDownloaded {DATASET} dataset metadata to data/raw/metadata.parquet")
    del metadata
    gc.collect()

    if DEBUG:
        rss_mib = psutil.Process().memory_info().rss / (1024**2)
        print(f"DEBUG mode enabled — process RAM after download: {rss_mib:.1f} MiB")


if __name__ == "__main__":
    download_data()
