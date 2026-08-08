"""S3-compatible object store (stub)."""

import boto3
from pathlib import Path
from typing import Optional


class S3Store:
    def __init__(self, bucket: str, prefix: str = ""):
        self.bucket = bucket
        self.prefix = prefix.rstrip("/")
        self.s3 = boto3.client("s3")

    def _key(self, object_id: str) -> str:
        return f"{self.prefix}/{object_id}" if self.prefix else object_id

    def put_file(self, object_id: str, source: Path):
        self.s3.upload_file(str(source), self.bucket, self._key(object_id))

    def get_file(self, object_id: str, dest: Path):
        dest.parent.mkdir(parents=True, exist_ok=True)
        self.s3.download_file(self.bucket, self._key(object_id), str(dest))
