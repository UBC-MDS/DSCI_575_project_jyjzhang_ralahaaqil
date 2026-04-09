from datasets import load_dataset

DATASET = "All_Beauty"

def download_data():
    print(f"Downloading {DATASET} dataset...")
    dataset = load_dataset("McAuley-Lab/Amazon-Reviews-2023", f"raw_review_{DATASET}", trust_remote_code=True)
    dataset['full'].to_parquet(f"data/raw/reviews.parquet")
    print(f"Downloaded {DATASET} dataset reviews to data/raw/reviews.parquet")
    
    metadata = load_dataset("McAuley-Lab/Amazon-Reviews-2023", f"raw_meta_{DATASET}", split="full", trust_remote_code=True)
    metadata.to_parquet(f"data/raw/metadata.parquet")
    print(f"Downloaded {DATASET} dataset metadata to data/raw/metadata.parquet")

if __name__ == "__main__":
    download_data()