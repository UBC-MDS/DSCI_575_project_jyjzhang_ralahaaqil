import gc
from pathlib import Path
import sys
from typing import Any
import duckdb
import psutil

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEBUG = False

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.preprocessing.constants import REVIEWS, METADATA

from src.preprocessing.helpers import (read_parquet, filter_by_column, concat_columns, 
                                       collapse_array_to_string, convert_nan_to_negative_one, 
                                       convert_string_to_json, expand_json_to_columns, select_columns, duplicate_column)


def clean_reviews(params: dict[str, dict[str, Any]] = REVIEWS) -> duckdb.DuckDBPyRelation:
    print(f"Cleaning reviews...")
    reviews = read_parquet(params["READ"]["path"], params["READ"]["columns_to_keep"])
    reviews = filter_by_column(reviews, params["FILTER"]["column"], params["FILTER"]["value"])
    reviews = concat_columns(reviews, params["CONCAT"]["columns"], new_column_name=params["CONCAT"]["new_column_name"])
    reviews = select_columns(reviews, params["FINAL_COLUMNS"])
    return reviews 

def clean_metadata(params: dict[str, dict[str, Any]] = METADATA) -> duckdb.DuckDBPyRelation:
    print(f"Cleaning metadata...")
    metadata = read_parquet(params["READ"]["path"], params["READ"]["columns_to_keep"])
    metadata = duplicate_column(metadata, params["DUPLICATE"]["column"], params["DUPLICATE"]["new_column_name"])
    metadata = collapse_array_to_string(metadata, params["COLLAPSE"]["columns"])
    metadata = convert_nan_to_negative_one(metadata, params["NAN_HANDLING"]["columns"])
    metadata = convert_string_to_json(metadata, params["STRING_TO_JSON"]["columns"])
    metadata = expand_json_to_columns(metadata, params["EXPAND_JSON"]["columns"], 
                                      json_column=params["EXPAND_JSON"]["json_column"])
    metadata = concat_columns(metadata, params["CONCAT"]["columns"], new_column_name=params["CONCAT"]["new_column_name"])
    metadata = select_columns(metadata, params["FINAL_COLUMNS"])
    return metadata

def merge_reviews_and_metadata(reviews: duckdb.DuckDBPyRelation, metadata: duckdb.DuckDBPyRelation) -> duckdb.DuckDBPyRelation:
    print(f"Merging reviews and metadata...")
    joined = duckdb.sql("SELECT * FROM reviews LEFT JOIN metadata USING (parent_asin)")
    final = concat_columns(joined, ["reviews_content", "metadata_content"])
    return final

def main():
    print("======================== CLEANING DATA ==========================")
    if DEBUG:
        print(f"DEBUG mode enabled — process RAM before cleaning: {psutil.Process().memory_info().rss / (1024**2):.1f} MiB")
    
    merged = merge_reviews_and_metadata(clean_reviews(), clean_metadata())
    merged = select_columns(merged, ["parent_asin", "product", "average_rating", "rating_number", "data_content"])
    output_path = PROJECT_ROOT / "data" / "processed" / "preprocessed_data.parquet"
    print(f"Saving preprocessed data to {output_path}... (This may take a while)")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    merged.write_parquet(str(output_path))
    print(f"\nPreprocessed data saved to {output_path}")
    del merged
    gc.collect()
    duckdb.close()
    
    if DEBUG:
        print(f"DEBUG mode enabled — process RAM after cleaning: {psutil.Process().memory_info().rss / (1024**2):.1f} MiB")

if __name__ == "__main__":
    main()