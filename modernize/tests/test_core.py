from pathlib import Path
import tempfile
import os

from backuptool.core import BackupManager


def test_create_snapshot_and_list(tmp_path):
    # create sample tree
    src = tmp_path / "source"
    src.mkdir()
    f = src / "hello.txt"
    f.write_text("hello world")
    store = tmp_path / "store"
    mgr = BackupManager(store)
    sid = mgr.create_snapshot(src)
    snaps = mgr.list_snapshots()
    assert any(s['id'] == sid for s in snaps)
    # restore
    out = tmp_path / "restore"
    mgr.restore_snapshot(sid, out)
    assert (out / "hello.txt").read_text() == "hello world"
