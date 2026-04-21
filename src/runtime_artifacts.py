"""Runtime bootstrap helpers for downloading app artifacts from S3."""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse

import boto3
from botocore import UNSIGNED
from botocore.client import Config

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACTS_S3_URI = os.getenv(
    "S3_ARTIFACTS_URI", "s3://mds-s3-ralah/575-project/"
)

S3_PREFIX_TO_LOCAL_ROOT = {
    "raw/": PROJECT_ROOT / "data" / "raw",
    "processed/": PROJECT_ROOT / "data" / "processed",
    "outputs/": PROJECT_ROOT / "outputs",
}

REQUIRED_LOCAL_FILES = (
    PROJECT_ROOT / "data" / "raw" / "reviews.parquet",
    PROJECT_ROOT / "data" / "processed" / "preprocessed_data.parquet",
    PROJECT_ROOT / "outputs" / "bm25_retriever.pkl",
    PROJECT_ROOT / "outputs" / "faiss_index" / "index.faiss",
    PROJECT_ROOT / "outputs" / "faiss_index" / "index.pkl",
)


def runtime_artifacts_present() -> bool:
    """Returns True when the files needed by the deployed app are present."""
    return all(path.is_file() for path in REQUIRED_LOCAL_FILES)


def _parse_s3_uri(s3_uri: str) -> tuple[str, str]:
    """Parses an S3 URI into bucket and normalized prefix."""
    parsed = urlparse(s3_uri)
    if parsed.scheme != "s3" or not parsed.netloc:
        raise ValueError(f"Invalid S3 URI: {s3_uri!r}")

    prefix = parsed.path.lstrip("/")
    if prefix and not prefix.endswith("/"):
        prefix += "/"

    return parsed.netloc, prefix


def _build_s3_client():
    """Builds an anonymous client for a public S3 bucket."""
    return boto3.client("s3", config=Config(signature_version=UNSIGNED))


def ensure_runtime_artifacts(
    s3_uri: str = DEFAULT_ARTIFACTS_S3_URI,
) -> dict[str, int | str]:
    """Syncs runtime data/index artifacts from S3 into the local project tree."""
    bucket, base_prefix = _parse_s3_uri(s3_uri)
    client = _build_s3_client()

    downloaded = 0
    skipped = 0

    for remote_prefix, local_root in S3_PREFIX_TO_LOCAL_ROOT.items():
        source_prefix = f"{base_prefix}{remote_prefix}"
        paginator = client.get_paginator("list_objects_v2")
        saw_files = False

        for page in paginator.paginate(Bucket=bucket, Prefix=source_prefix):
            for obj in page.get("Contents", []):
                key = obj["Key"]
                if key.endswith("/"):
                    continue

                saw_files = True
                relative_path = key[len(source_prefix) :]
                if not relative_path:
                    continue

                local_path = local_root / Path(relative_path)
                remote_size = int(obj.get("Size", -1))

                if local_path.is_file() and local_path.stat().st_size == remote_size:
                    skipped += 1
                    continue

                local_path.parent.mkdir(parents=True, exist_ok=True)
                client.download_file(bucket, key, str(local_path))
                downloaded += 1

        if not saw_files:
            raise FileNotFoundError(f"No S3 objects found under s3://{bucket}/{source_prefix}")

    missing = [
        str(path.relative_to(PROJECT_ROOT))
        for path in REQUIRED_LOCAL_FILES
        if not path.is_file()
    ]
    if missing:
        missing_str = ", ".join(missing)
        raise FileNotFoundError(
            f"Missing required runtime artifacts after S3 sync: {missing_str}"
        )

    return {
        "bucket": bucket,
        "prefix": base_prefix,
        "downloaded": downloaded,
        "skipped": skipped,
    }
