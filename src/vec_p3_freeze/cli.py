from __future__ import annotations

import argparse
from pathlib import Path

from .core import checklist, freeze, verify


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Freeze scarce VEC P3 submission slots."
    )
    subparsers = parser.add_subparsers(
        dest="command_name",
        required=True,
    )

    freeze_parser = subparsers.add_parser("freeze")
    freeze_parser.add_argument(
        "--bundle",
        type=Path,
        default=Path("p3_bundle"),
    )
    freeze_parser.add_argument("--board", required=True)
    freeze_parser.add_argument("--slot", type=int, required=True)
    freeze_parser.add_argument("--file", type=Path, required=True)
    freeze_parser.add_argument("--note", default="")

    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument(
        "--bundle",
        type=Path,
        default=Path("p3_bundle"),
    )

    checklist_parser = subparsers.add_parser("checklist")
    checklist_parser.add_argument(
        "--bundle",
        type=Path,
        default=Path("p3_bundle"),
    )
    checklist_parser.add_argument("--out", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command_name == "freeze":
        manifest = freeze(
            args.bundle,
            args.board,
            args.slot,
            args.file,
            args.note,
        )
        print(manifest["sha256"], manifest["file"])
        return 0

    if args.command_name == "verify":
        rows = verify(args.bundle)
        for row in rows:
            print(
                row["status"],
                row["board"],
                row["slot"],
                row["file"],
            )
        return 1 if any(row["status"] != "OK" for row in rows) else 0

    text = checklist(args.bundle)
    output = args.out or args.bundle / "SUBMISSION_CHECKLIST.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
