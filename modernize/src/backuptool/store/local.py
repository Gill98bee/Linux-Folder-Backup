"""Local filesystem object store."""

from pathlib import Path
import shutil
from typing import Optional

from ..encrypt import Passphrase


class LocalStore:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path_for(self, object_id: str) -> Path:
        return self.root / object_id[:2] / object_id

    def exists(self, object_id: str) -> bool:
        return self._path_for(object_id).exists()

    def put_file(self, object_id: str, source: Path, encrypt_passphrase: Optional[Passphrase] = None):
        dest = self._path_for(object_id)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if encrypt_passphrase:
            # encrypt to a temporary path
            enc = dest.with_suffix('.enc')
            encrypt_passphrase.encrypt_file(source, enc)
            shutil.move(str(enc), str(dest))
        else:
            shutil.copy2(source, dest)

    def get_file(self, object_id: str, dest: Path, decrypt_passphrase: Optional[Passphrase] = None):
        src = self._path_for(object_id)
        if not src.exists():
            raise FileNotFoundError(src)
        if decrypt_passphrase:
            # write temporary and decrypt
            tmp = dest.with_suffix('.tmp')
            shutil.copy2(src, tmp)
            decrypt_passphrase.decrypt_file(tmp, dest)
            tmp.unlink()
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
