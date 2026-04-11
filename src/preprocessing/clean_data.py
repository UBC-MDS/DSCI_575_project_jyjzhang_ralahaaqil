from pathlib import Path
import sys
from typing import Any
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.preprocessing.helpers import read_parquet, filter_by_column, concat_columns, collapse_array_to_string, convert_nan_to_negative_one, convert_string_to_json, expand_json_to_columns

REVIEWS = {
    "path": PROJECT_ROOT / "data" / "raw" / "reviews.parquet",
    "columns_to_keep": ["title", "text", "parent_asin", "verified_purchase"],
    "columns_to_join": ["title", "text"],
    "filter_column": "verified_purchase",
    "filter_value": True,
    "new_column_name": "reviews_content",
}

METADATA = {
    "path": PROJECT_ROOT / "data" / "raw" / "metadata.parquet",
    "columns_to_keep": ["title", "average_rating", "rating_number", "features", "description", "store", "categories", "details", "parent_asin"],
    "collapsed_column_names": ["categories", "features", "description"],
    "columns_to_convert_nan_to_negative_one": ["average_rating", "rating_number"],
    "columns_to_convert_string_to_json": ["details"],
    "columns_to_expand_json_to_columns": [
    "Developed By",
    "Version",
    "Application Permissions",
    "Minimum Operating System",
    "Manufacturer",
    "Language",],
    "columns_to_join": ["developed_by", "version", "application_permissions", "minimum_operating_system", "manufacturer", "language", "features", "description", "store", "categories", "title"],
    "new_column_name": "metadata_content",
}

def clean_reviews(reviews: Path = REVIEWS["path"], 
                  columns_to_keep: list[str] = REVIEWS["columns_to_keep"], 
                  columns_to_join: list[str] = REVIEWS["columns_to_join"],
                  filter_column: str = REVIEWS["filter_column"],
                  filter_value: Any = REVIEWS["filter_value"],
                  new_column_name: str = REVIEWS["new_column_name"]) -> duckdb.DuckDBPyRelation:
    reviews = read_parquet(reviews, columns_to_keep)
    reviews = filter_by_column(reviews, filter_column, filter_value)
    reviews = concat_columns(reviews, columns_to_join, new_column_name=new_column_name)
    return reviews 

def clean_metadata(metadata: Path = METADATA["path"],
                  columns_to_keep: list[str] = METADATA["columns_to_keep"],
                  columns_to_convert_nan_to_negative_one: list[str] = METADATA["columns_to_convert_nan_to_negative_one"],
                  columns_to_convert_string_to_json: list[str] = METADATA["columns_to_convert_string_to_json"],
                  columns_to_expand_json_to_columns: list[str] = METADATA["columns_to_expand_json_to_columns"],
                  columns_to_join: list[str] = METADATA["columns_to_join"],
                  new_column_name: str = METADATA["new_column_name"]) -> duckdb.DuckDBPyRelation:
    metadata = read_parquet(metadata, columns_to_keep)
    metadata = collapse_array_to_string(metadata, METADATA["collapsed_column_names"])
    metadata = convert_nan_to_negative_one(metadata, columns_to_convert_nan_to_negative_one)
    metadata = convert_string_to_json(metadata, columns_to_convert_string_to_json)
    metadata = expand_json_to_columns(metadata, columns_to_expand_json_to_columns, json_column="details")
    metadata = concat_columns(metadata, columns_to_join, new_column_name=new_column_name)
    return metadata

def merge_reviews_and_metadata(reviews: duckdb.DuckDBPyRelation, metadata: duckdb.DuckDBPyRelation) -> duckdb.DuckDBPyRelation:
    joined = duckdb.sql("SELECT * FROM reviews LEFT JOIN metadata USING (parent_asin)")
    final = concat_columns(joined, ["reviews_content", "metadata_content"])
    return final

def main():
    # metadata = clean_metadata()
    # print(metadata)
    # reviews = clean_reviews()
    # print(reviews)
    merged = merge_reviews_and_metadata(clean_reviews(), clean_metadata())
    merged.write_parquet(str(PROJECT_ROOT / "data" / "processed" / "preprocessed_data.parquet"))
    print(f"Preprocessed data saved to {PROJECT_ROOT / 'data' / 'processed' / 'preprocessed_data.parquet'}")

if __name__ == "__main__":
    main()