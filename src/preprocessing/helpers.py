import duckdb
from pathlib import Path
from typing import Any


def _sql_double_quoted_ident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def read_parquet(path: Path, columns: list[str]) -> duckdb.DuckDBPyRelation:
    """Load Parquet at path into DuckDB and return a relation with only the named columns."""
    data = duckdb.read_parquet(str(path))
    return duckdb.sql(f"SELECT {', '.join(columns)} FROM data")

def concat_columns(
    data: duckdb.DuckDBPyRelation,
    columns: list[str],
    *,
    separator: str = " ",
    new_column_name: str = "data_content",
) -> duckdb.DuckDBPyRelation:
    """Concatenate merge_columns with separator (nulls skipped); keep all other columns via EXCLUDE."""
    sep_lit = separator.replace("'", "''")
    idents = [_sql_double_quoted_ident(c) for c in columns]
    merge_expr = ", ".join(f"CAST({ident} AS VARCHAR)" for ident in idents)
    exclude = ", ".join(idents)
    alias = _sql_double_quoted_ident(new_column_name)
    return duckdb.sql(
        f"SELECT concat_ws('{sep_lit}', {merge_expr}) AS {alias}, * EXCLUDE ({exclude}) FROM data"
    )

def filter_by_column(data: duckdb.DuckDBPyRelation, column_name: str, value: Any) -> duckdb.DuckDBPyRelation:
    """Keep rows where column_name equals value."""
    return duckdb.sql(f"SELECT * FROM data WHERE {column_name} = {value}")

def collapse_array_to_string(
    data: duckdb.DuckDBPyRelation,
    column_names: list[str],
) -> duckdb.DuckDBPyRelation:
    """Turn each LIST/varchar[] column in column_names into varchar via array_to_string; keep all other columns via EXCLUDE."""
    idents = [_sql_double_quoted_ident(c) for c in column_names]
    collapsed = [f"array_to_string({ident}, ', ') AS {ident}" for ident in idents]
    exclude = ", ".join(idents)
    return duckdb.sql(
        f"SELECT {', '.join(collapsed)}, * EXCLUDE ({exclude}) FROM data"
    )

def convert_nan_to_negative_one(
    data: duckdb.DuckDBPyRelation, columns: list[str]
) -> duckdb.DuckDBPyRelation:
    """Replace NULL and NaN with -1 in the listed numeric columns; leave other columns unchanged."""
    replacements = ", ".join(
        f"CASE WHEN {c} IS NULL OR isnan({c}) THEN -1 ELSE {c} END AS {c}"
        for c in columns
    )
    return duckdb.sql(f"SELECT * REPLACE ({replacements}) FROM data")

def convert_string_to_json(
    data: duckdb.DuckDBPyRelation, columns: list[str]
) -> duckdb.DuckDBPyRelation:
    """Cast each listed column to JSON in place; leave other columns unchanged."""
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
    
def select_columns(
    data: duckdb.DuckDBPyRelation,
    columns: list[str],
) -> duckdb.DuckDBPyRelation:
    """Select only the listed columns"""
    idents = [_sql_double_quoted_ident(c) for c in columns]
    exclude = ", ".join(idents)
    return duckdb.sql(f"SELECT {', '.join(idents)} FROM data")

def duplicate_column(data: duckdb.DuckDBPyRelation, column_name: str, new_column_name: str) -> duckdb.DuckDBPyRelation:
    """Duplicate the column and rename it to the new column name"""
    return duckdb.sql(f"SELECT {column_name} AS {new_column_name}, * FROM data")

def concat_rows(
    data: duckdb.DuckDBPyRelation,
    id_column: str,
    content_column: str,
    *,
    separator: str = " ",
) -> duckdb.DuckDBPyRelation:
    """One row per id_column; content_column is string_agg of all values sharing that id (nulls skipped)."""
    id_ident = _sql_double_quoted_ident(id_column)
    content_ident = _sql_double_quoted_ident(content_column)
    sep_lit = separator.replace("'", "''")
    return duckdb.sql(
        f"SELECT {id_ident}, string_agg(CAST({content_ident} AS VARCHAR), '{sep_lit}') AS {content_ident} FROM data GROUP BY {id_ident}"
    )
