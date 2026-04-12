from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

REVIEWS = {
    "READ": {
        "path": PROJECT_ROOT / "data" / "raw" / "reviews.parquet",
        "columns_to_keep": ["title", "text", "parent_asin", "verified_purchase"],
    },
    "FILTER": {
        "column": "verified_purchase",
        "value": True,
    },
    "CONCAT": {
        "columns": ["title", "text"],
        "new_column_name": "reviews_content",
    },
    "DUPLICATE": {
        "column": "text",
        "new_column_name": "review_text",
    },
    "FINAL_COLUMNS": ["parent_asin", "reviews_content", "review_text"],
}

METADATA = {
    "READ": {
        "path": PROJECT_ROOT / "data" / "raw" / "metadata.parquet",
        "columns_to_keep": ["title", "average_rating", "rating_number", "features", "description", "store", "categories", "details", "parent_asin"],
    },
    "DUPLICATE": {
        "column": "title",
        "new_column_name": "product",
    },
    "COLLAPSE": {
        "columns": ["categories", "features", "description"],
    },
    "NAN_HANDLING": {
        "columns": ["average_rating", "rating_number"],
    },
    "STRING_TO_JSON": {
        "columns": ["details"],
    },
    "EXPAND_JSON": {
        "columns": ["Developed By", "Version", "Application Permissions", 
                    "Minimum Operating System", "Manufacturer", "Language"],
        "json_column": "details",
    },
    "CONCAT": {
        "columns": ["developed_by", "version", "application_permissions", "minimum_operating_system", 
                    "manufacturer", "language", "features", "description", "store", "categories", "title"],
        "new_column_name": "metadata_content",
    },
    "FINAL_COLUMNS": ["parent_asin", "product", "average_rating", "rating_number", "metadata_content"],
}