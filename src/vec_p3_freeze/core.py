from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from .boards import BOARDS


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_board(board: str) -> str:
    if board not in BOARDS:
        raise ValueError(f"unknown board: {board}")
    return board.replace(":", "__")


def _slot_dir(bundle: Path, board: str, slot: int) -> Path:
    if slot not in {1, 2}:
        raise ValueError("slot must be 1 or 2")
    return bundle / safe_board(board) / f"slot_{slot}"


def freeze(
    bundle: Path,
    board: str,
    slot: int,
    source: Path,
    note: str = "",
) -> dict:
    if board not in BOARDS:
        raise ValueError(f"unknown board: {board}")
    source = source.resolve()
    if not source.is_file():
        raise FileNotFoundError(source)

    slot_dir = _slot_dir(bundle, board, slot)
    manifest_path = slot_dir / "manifest.json"
    if manifest_path.exists() or slot_dir.exists():
        raise FileExistsError(
            f"{board} slot {slot} already exists; refusing to overwrite"
        )

    slot_dir.mkdir(parents=True, exist_ok=False)
    destination = slot_dir / source.name
    shutil.copy2(source, destination)

    manifest = {
        "schema_version": 1,
        "board": board,
        "slot": slot,
        "source": str(source),
        "file": str(destination.relative_to(bundle)),
        "sha256": sha256_file(destination),
        "size_bytes": destination.stat().st_size,
        "frozen_utc": datetime.now(timezone.utc).isoformat(),
        "note": note,
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )

    destination.chmod(0o444)
    manifest_path.chmod(0o444)
    return manifest


def _manifests(bundle: Path) -> list[tuple[Path, dict]]:
    if not bundle.exists():
        return []
    rows: list[tuple[Path, dict]] = []
    for path in sorted(bundle.glob("**/manifest.json")):
        try:
            manifest = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid manifest JSON: {path}") from exc
        if not isinstance(manifest, dict):
            raise TypeError(f"invalid manifest object: {path}")
        rows.append((path, manifest))
    return rows


def verify(bundle: Path) -> list[dict]:
    results: list[dict] = []
    for manifest_path, manifest in _manifests(bundle):
        rel_file = Path(str(manifest.get("file", "")))
        artifact = bundle / rel_file
        status = "OK"
        actual = None

        if not artifact.is_file():
            status = "MISSING"
        else:
            actual = sha256_file(artifact)
            if actual != manifest.get("sha256"):
                status = "CHANGED"

        results.append(
            {
                "status": status,
                "board": manifest.get("board"),
                "slot": manifest.get("slot"),
                "file": str(rel_file),
                "expected_sha256": manifest.get("sha256"),
                "actual_sha256": actual,
                "manifest": str(manifest_path.relative_to(bundle)),
            }
        )
    return results


def checklist(bundle: Path) -> str:
    rows = _manifests(bundle)
    lines = [
        "# VEC P3 Submission Checklist",
        "",
        (
            "> Verify each frozen artifact immediately before upload. "
            "This bundle does not replace the official format validator."
        ),
        "",
        "| board | slot | file | SHA-256 | note |",
        "|---|---:|---|---|---|",
    ]
    for _, manifest in rows:
        note = str(manifest.get("note", "")).replace("|", "/").replace("\n", " ")
        lines.append(
            f"| {manifest.get('board', '')} | {manifest.get('slot', '')} | "
            f"{manifest.get('file', '')} | {manifest.get('sha256', '')} | "
            f"{note} |"
        )
    lines.extend(
        [
            "",
            "## Before upload",
            "",
            "1. Run the official/current VEC format validator on the frozen file.",
            "2. Run vec-p3-freeze verify --bundle <bundle> and require all rows = OK.",
            "3. Confirm the portal board matches the manifest board.",
            "4. Confirm the intended slot (1 or 2) before submitting.",
            "",
        ]
    )
    return "\n".join(lines)
