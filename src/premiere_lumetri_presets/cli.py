"""CLI for premiere-lumetri-presets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import LOOK_CATALOG, generate_lumetri_jsx


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="lumetri-gen", description="Generate Premiere Pro Lumetri ExtendScript presets.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List calibrated Lumetri looks as JSON.")

    jsx = sub.add_parser("jsx", help="Generate .jsx script for a look.")
    jsx.add_argument("look", choices=sorted(LOOK_CATALOG.keys()))
    jsx.add_argument("--track", type=int, default=2, help="0-based video track index (default: 2 for V3).")
    jsx.add_argument("-o", "--output", default="", help="Optional output .jsx file path.")

    args = parser.parse_args(argv)
    if args.command == "list":
        print(json.dumps({k: v.to_dict() for k, v in LOOK_CATALOG.items()}, indent=2))
        return 0

    script = generate_lumetri_jsx(args.look, video_track_index=args.track)
    if args.output:
        Path(args.output).write_text(script, encoding="utf-8", newline="\n")
    else:
        print(script, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
