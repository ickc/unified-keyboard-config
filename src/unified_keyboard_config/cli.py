import argparse
import os
import sys
from pathlib import Path

from .patch import patch_keymap
from .pull import pull_source


def main():
    parser = argparse.ArgumentParser(description="Unified Keyboard Config CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Pull command
    pull_parser = subparsers.add_parser("pull", help="Pull latest Oryx layout")
    pull_parser.add_argument("submodule_path", type=Path, help="Path to the submodule")
    pull_parser.add_argument(
        "--layout-id", default=os.environ.get("ORYX_LAYOUT_ID"), help="Oryx Layout ID"
    )
    pull_parser.add_argument(
        "--geometry", default=os.environ.get("ORYX_GEOMETRY"), help="Keyboard geometry"
    )
    pull_parser.add_argument(
        "--patch", action="store_true", help="Apply patch after pulling"
    )

    # Patch command
    patch_parser = subparsers.add_parser("patch", help="Patch keymap file")
    patch_parser.add_argument(
        "keymap_path", type=Path, help="Path to the keymap.c file"
    )
    patch_parser.add_argument(
        "--geometry", default=os.environ.get("ORYX_GEOMETRY"), help="Keyboard geometry"
    )

    args = parser.parse_args()

    try:
        if args.command == "pull":
            pull_source(args.submodule_path, args.layout_id, args.geometry, args.patch)
        elif args.command == "patch":
            patch_keymap(args.keymap_path, args.geometry)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
