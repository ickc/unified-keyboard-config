import os
import sys
from pathlib import Path

import defopt

from .patch import patch_keymap
from .pull import pull_source


def pull(
    submodule_path: Path,
    *,
    layout_id: str = "",
    geometry: str = "",
    patch: bool = False,
) -> None:
    """Pull latest Oryx layout.

    :param submodule_path: Path to the submodule
    :param layout_id: Oryx Layout ID (defaults to ORYX_LAYOUT_ID env var)
    :param geometry: Keyboard geometry (defaults to ORYX_GEOMETRY env var)
    :param patch: Apply patch after pulling
    """
    layout_id = layout_id or os.environ.get("ORYX_LAYOUT_ID")
    geometry = geometry or os.environ.get("ORYX_GEOMETRY")

    try:
        pull_source(submodule_path, layout_id, geometry, patch)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def patch(
    keymap_path: Path,
    *,
    geometry: str = "",
) -> None:
    """Patch keymap file.

    :param keymap_path: Path to the keymap.c file
    :param geometry: Keyboard geometry (defaults to ORYX_GEOMETRY env var)
    """
    geometry = geometry or os.environ.get("ORYX_GEOMETRY")

    try:
        patch_keymap(keymap_path, geometry)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Unified Keyboard Config CLI"""
    defopt.run([pull, patch])


if __name__ == "__main__":
    main()
