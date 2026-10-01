from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from .boards import BOARDS


def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for part in iter(lambda:f.read(1024*1024),b''): h.update(part)
    return h.hexdigest()


def safe_board(board: str) -> str:
    if board not in BOARDS: raise ValueError(f'unknown board: {board}')
    return board.replace(':','__)
