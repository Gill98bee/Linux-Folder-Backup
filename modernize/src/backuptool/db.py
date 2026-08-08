"""Simple SQLite-backed catalog for snapshots and file index."""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List


class Catalog:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.conn = sqlite3.connect(str(self.path))
        self._init()

    def _init(self):
        cur = self.conn.cursor()
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS snapshots (
                id TEXT PRIMARY KEY,
                name TEXT,
                created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS files (
                snapshot_id TEXT,
                path TEXT,
                file_id TEXT,
                size INTEGER,
                FOREIGN KEY(snapshot_id) REFERENCES snapshots(id)
            );
            """
        )
        self.conn.commit()

    def create_snapshot(self, meta: dict) -> str:
        sid = hashlib_short_id()
        cur = self.conn.cursor()
        cur.execute("INSERT INTO snapshots (id, name, created_at) VALUES (?, ?, ?)", (sid, meta.get('name'), meta.get('created_at')))
        self.conn.commit()
        return sid

    def add_file(self, snapshot_id: str, path: str, file_id: str, size: int):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO files (snapshot_id, path, file_id, size) VALUES (?, ?, ?, ?)", (snapshot_id, path, file_id, size))
        self.conn.commit()

    def list_snapshots(self) -> List[dict]:
        cur = self.conn.cursor()
        cur.execute("SELECT id, name, created_at FROM snapshots ORDER BY created_at DESC")
        rows = cur.fetchall()
        return [{'id': r[0], 'name': r[1], 'created_at': r[2]} for r in rows]

    def files_for_snapshot(self, snapshot_id: str) -> List[dict]:
        cur = self.conn.cursor()
        cur.execute("SELECT path, file_id, size FROM files WHERE snapshot_id = ?", (snapshot_id,))
        return [{'path': r[0], 'file_id': r[1], 'size': r[2]} for r in cur.fetchall()]

    def prune(self, keep_last: int, keep_days: int) -> int:
        cur = self.conn.cursor()
        # compute cutoff
        cutoff = (datetime.utcnow() - timedelta(days=keep_days)).isoformat()
        # select snapshots to keep
        cur.execute("SELECT id FROM snapshots ORDER BY created_at DESC LIMIT ?", (keep_last,))
        keep_ids = {r[0] for r in cur.fetchall()}
        # select deletable
        cur.execute("SELECT id, created_at FROM snapshots")
        to_delete = []
        for sid, created in cur.fetchall():
            if sid in keep_ids:
                continue
            if created > cutoff:
                continue
            to_delete.append(sid)
        for sid in to_delete:
            cur.execute("DELETE FROM files WHERE snapshot_id = ?", (sid,))
            cur.execute("DELETE FROM snapshots WHERE id = ?", (sid,))
        self.conn.commit()
        return len(to_delete)


# small helper
import secrets

def hashlib_short_id() -> str:
    return secrets.token_hex(10)
