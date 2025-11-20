import re
from pathlib import Path


def patch_keymap(keymap_path: Path, geometry: str | None = None):
    """
    Patches the chordal_hold_layout in keymap.c.
    If geometry is provided, it must match 'moonlander'.
    """
    if geometry and geometry != "moonlander":
        raise ValueError(f"Expected geometry='moonlander', but got '{geometry}'")

    if not keymap_path.exists():
        raise FileNotFoundError(f"Could not find keymap.c at {keymap_path}")

    # Define the target layout string
    new_layout = """const char chordal_hold_layout[MATRIX_ROWS][MATRIX_COLS] PROGMEM = LAYOUT(
  'L', 'L', 'L', 'L', 'L', 'L', 'L', 'R', 'R', 'R', 'R', 'R', 'R', 'R',
  'L', 'L', 'L', 'L', 'L', 'L', 'L', 'R', 'R', 'R', 'R', 'R', 'R', 'R',
  'L', 'L', 'L', 'L', 'L', 'L', 'L', 'R', 'R', 'R', 'R', 'R', 'R', 'R',
  'L', 'L', 'L', 'L', 'L', 'L', 'R', 'R', 'R', 'R', 'R', 'R',
  'L', 'L', 'L', 'L', 'L', 'R', 'L', 'R', 'R', 'R', 'R', 'R',
                 'R', 'R', 'R', 'L', 'L', 'L'
);"""

    content = keymap_path.read_text(encoding="utf-8")

    # Regex to find the block
    # Matches: const char chordal_hold_layout[MATRIX_ROWS][MATRIX_COLS] PROGMEM = LAYOUT(...);
    # We use re.DOTALL so . matches newlines
    pattern = r"(const\s+char\s+chordal_hold_layout\[MATRIX_ROWS\]\[MATRIX_COLS\]\s+PROGMEM\s*=\s*LAYOUT\s*\(.*?\);)"

    match = re.search(pattern, content, re.DOTALL)
    if not match:
        raise RuntimeError("Could not find chordal_hold_layout block in keymap.c")

    # Replace the found block with the new layout
    # We use string slicing to ensure we replace exactly the match
    new_content = content[: match.start()] + new_layout + content[match.end() :]

    keymap_path.write_text(new_content, encoding="utf-8")
    print(f"Successfully patched {keymap_path}")
