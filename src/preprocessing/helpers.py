import duckdb
from pathlib import Path
from typing import Any

def read_parquet(path: Path, columns: list[str]) -> duckdb.DuckDBPyRelation:
    data = duckdb.read_parquet(str(path))
    return duckdb.sql(f"SELECT {', '.join(columns)} FROM data")

def join_columns(
    data: duckdb.DuckDBPyRelation,
    merge_columns: list[str],
    other_columns: list[str],
    *,
    separator: str = " ",
    new_column_name: str = "data_content",
) -> duckdb.DuckDBPyRelation:
    """Concatenate merge_columns with separator, skipping nulls; keep other_columns as-is."""
    sep_lit = separator.replace("'", "''")
    merge_expr = ", ".join(f"CAST({column} AS VARCHAR)" for column in merge_columns)
    tail = f", {', '.join(other_columns)}" if other_columns else ""
    return duckdb.sql(
        f"SELECT concat_ws('{sep_lit}', {merge_expr}) AS {new_column_name}{tail} FROM data"
    )

def filter_by_column(data: duckdb.DuckDBPyRelation, column_name: str, value: Any) -> duckdb.DuckDBPyRelation:
    return duckdb.sql(f"SELECT * FROM data WHERE {column_name} = {value}")

def collapse_array_to_string(
    data: duckdb.DuckDBPyRelation,
    column_names: list[str],
    other_columns: list[str] | None = None,
) -> duckdb.DuckDBPyRelation:
    """Turn each LIST/varchar[] column in column_names into a single varchar via array_to_string; keep other_columns as-is."""
    other = other_columns or []
    collapsed = [f"array_to_string({col}, ', ') AS {col}" for col in column_names]
    select_parts = [*other, *collapsed]
    return duckdb.sql(f"SELECT {', '.join(select_parts)} FROM data")

def convert_nan_to_negative_one(
    data: duckdb.DuckDBPyRelation, columns: list[str]
) -> duckdb.DuckDBPyRelation:
    replacements = ", ".join(
        f"CASE WHEN {c} IS NULL OR isnan({c}) THEN -1 ELSE {c} END AS {c}"
        for c in columns
    )
    return duckdb.sql(f"SELECT * REPLACE ({replacements}) FROM data")

def convert_string_to_json(
    data: duckdb.DuckDBPyRelation, columns: list[str]
) -> duckdb.DuckDBPyRelation:
    replacements = ", ".join(
        f"CAST({c} AS JSON) AS {c}"
        for c in columns
    )
    return duckdb.sql(f"SELECT * REPLACE ({replacements}) FROM data")

def expand_json_to_columns(
    data: duckdb.DuckDBPyRelation,
    keys: list[str],
    *,
    json_column: str = "details",
) -> duckdb.DuckDBPyRelation:
    """Expand selected JSON keys into plain-text columns; nulls become blank strings."""

    def json_path(key: str) -> str:
        inner = key.replace("\\", "\\\\").replace('"', '\\"')
        return f'$."{inner}"'

    def sql_alias(key: str) -> str:
        return key.lower().replace(" ", "_")

    j_expr = f"TRY_CAST({json_column} AS JSON)"
    extracts = []
    for key in keys:
        path_sql = json_path(key).replace("'", "''")
        raw_json = (
            f"COALESCE(NULLIF(CAST(json_extract({j_expr}, '{path_sql}') AS VARCHAR), 'null'), '')"
        )
        extracts.append(
            "CASE "
            f"WHEN {raw_json} = '' THEN '' "
            f"WHEN left({raw_json}, 1) = '[' AND right({raw_json}, 1) = ']' THEN "
            f"replace(replace(trim(both ']' from trim(both '[' from {raw_json})), '\",\"', ', '), '\"', '') "
            f"ELSE trim(both '\"' from {raw_json}) "
            f"END AS {sql_alias(key)}"
        )

    tail = ", ".join(extracts)
    return duckdb.sql(
        f"SELECT * EXCLUDE ({json_column}), {tail} FROM data"
    )