"""Core orchestration for backups."""

import hashlib
import os
from pathlib import Path
import sqlite3
import shutil
import json
from datetime import datetime
from typing import Iterable, List

from .db import Catalog
from .store.local import LocalStore
from .encrypt import Passphrase


class BackupManager:
    def __init__(self, store_root: Path):
        self.store_root = Path(store_root)
        self.store_root.mkdir(parents=True, exist_ok=True)
        self.catalog = Catalog(self.store_root / "catalog.db")
        self.local_store = LocalStore(self.store_root / "objects")

    def _scan_files(self, source: Path) -> Iterable[Path]:
        for root, dirs, files in os.walk(source):
            for f in files:
                yield Path(root) / f

    def _file_id(self, path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as fh:
            while True:
                chunk = fh.read(8192)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()

    def create_snapshot(self, source: Path, name: str | None = None, passphrase: Passphrase | None = None, dry_run: bool = False) -> str | None:
        source = Path(source)
        if not source.exists():
            raise FileNotFoundError(source)
        files = list(self._scan_files(source))
        if dry_run:
            print(f"Dry run: {len(files)} files would be backed up from {source}")
            for p in files:
                print(f"  {p.relative_to(source)}")
            return None
        snapshot = {"name": name or source.name, "created_at": datetime.utcnow().isoformat()}
        snapshot_id = self.catalog.create_snapshot(snapshot)
        for p in files:
            fid = self._file_id(p)
            rel = p.relative_to(source)
            # store object if missing
            if not self.local_store.exists(fid):
                self.local_store.put_file(fid, p, encrypt_passphrase=passphrase)
            self.catalog.add_file(snapshot_id, str(rel), fid, p.stat().st_size)
        return snapshot_id

    def list_snapshots(self) -> List[dict]:
        return self.catalog.list_snapshots()

    def prune(self, keep_last: int = 30, keep_days: int = 90) -> int:
        return self.catalog.prune(keep_last, keep_days)

    def restore_snapshot(self, snapshot_id: str, target: Path, passphrase: Passphrase | None = None):
        files = self.catalog.files_for_snapshot(snapshot_id)
        target.mkdir(parents=True, exist_ok=True)
        for entry in files:
            rel = entry['path']
            fid = entry['file_id']
            dest = target / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            self.local_store.get_file(fid, dest, decrypt_passphrase=passphrase)

