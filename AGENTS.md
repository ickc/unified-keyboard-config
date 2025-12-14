# Adv360 to Lily58 Porting Guide

This guide documents the rules and logic used to port the `adv360.keymap` to `lily58.keymap`. Use this when updating the Lily58 configuration based on future Adv360 changes.

## 1. Physical Layout Mapping

The Adv360 is larger than the Lily58. We map a subset of keys and drop the rest.

### Columns
- **Left Hand**:
  - Keep Adv360 Columns **0, 1, 2, 3, 4, 5**.
  - **Drop** Adv360 Columns **6, 7** (Inner/Center columns).
- **Right Hand**:
  - Keep Adv360 Columns **8, 9, 10, 11, 12, 13**.
  - **Drop** (implicitly, mirroring left).

### Rows
- **Standard Rows** (Numbers, Top, Home, Bottom): Keep as is (within kept columns).
- **Mod Row (Row 4)**: The Adv360 has a dedicated modifier row below "Z/X/C/V". **Drop this entire row**.
  - *Consequence*: Dedicated `Ctrl`, `Alt`, `Cmd` keys are lost. We replace this functionality with **Home Row Mods** (see Section 3).

### Thumb Cluster
The Adv360 thumb cluster is complex. The Lily58 has 4 thumb keys per side.

| Lily58 Key | Adv360 Equivalent | Function |
| :--- | :--- | :--- |
| **Outer 1** (Leftmost/Rightmost) | Adv360 Thumb 1 | Primary Thumb Layer 1 |
| **Outer 2** | Adv360 Thumb 2 | Primary Thumb Layer 2 |
| **Outer 3** | Adv360 Thumb 3 | Primary Thumb Layer 3 |
| **Inner** (Closest to OLED) | **None** (Dropped Adv360 Inner/Upper) | Used for **Utility/Unlock** or `&none` |

- **Rule**: Map the first 3 "Primary" Adv360 thumb bindings to Lily58's 3 Outer keys.
- **Inner Keys**: Use for `&studio_unlock` on utility layers (`fn`, `nf`). Set to `&none` on base layers if unused.

## 2. Configuration & Cleanups

### Required Removals
The Adv360 firmware has custom drivers not present in standard ZMK or the Lily58 board.
- **Remove Header**: `#include <dt-bindings/zmk/stp.h>`
- **Remove Header**: `#include <dt-bindings/zmk/backlight.h>` (Hardware mismatch)
- **Remove Header**: `#include <dt-bindings/zmk/rgb.h>` (Hardware mismatch)
- **Remove Behaviors**:
  - `&stp` (Service Technician Port)
  - `&bootloader` (Use `&sys_reset` if needed, or specific hardware bindings)
  - `&bl` (Backlight keys)
  - `&rgb_ug` (RGB keys)
  - `&studio_unlock` (Unless ZMK Studio is enabled, see below)

### ZMK Studio
- **Enable**: Add `CONFIG_ZMK_STUDIO=y` to `lily58.conf`.
- **Unlock Key**: Map `&studio_unlock` to the **Inner Thumb** keys on Utility Layers (`fn`, `nf`).

## 3. Custom Behaviors & Mods

### Behaviors
- **Port**: Copy `hml`, `hmr`, `mmr`, `mml`, `mlr`, `mll` definitions.
- **Update Triggers**: The `hold-trigger-key-positions` must be recalculated for Lily58 key indices.
  - **Left Hand Indices**: 0-5, 12-17, 24-29, 36-41, 50-53 (Thumbs).
  - **Right Hand Indices**: 6-11, 18-23, 30-35, 42-49, 54-57 (Thumbs).
  - *Note*: Ensure the list is accurate to the generated `lily58.keymap`.

### Bottom Row Mods
Since the dedicated Mod Row is dropped, we apply **Mod-Taps** to the Bottom Row keys (Z, X, C, V...).

- **Pattern**: `&hml MOD KEY` (Left) / `&hmr MOD KEY` (Right).
- **Mapping**:
  - `Z` / `/`: `Ctrl`
  - `X` / `.`: `Alt`
  - `C` / `,`: `Cmd` (Gui)
  - `V` / `M`: `Shift`
- **Mirrored Layers (`esab`, `nf`)**:
  - **Swap Modifiers**: Left Hand keys should trigger **Right Modifiers** (e.g., `&hml RCTRL Z`). Right Hand keys trigger Left Modifiers. This improves cross-hand ergonomic chording.

### Macros
- Copy `macros.dtsi` file entirely if unchanged, or append macros to `lily58.keymap`.

## 4. Porting Workflow
1. **Copy Layer**: Paste the Adv360 layer into `lily58.keymap`.
2. **Trim Columns**: Delete the inner columns (indices 6-7, 20-21 etc from Adv360 view).
3. **Delete Mod Row**: Remove the entire Row 4.
4. **Fix Thumbs**: Align the first 3 thumb keys to Lily58 Outer Thumbs. Handle the rest.
5. **Apply Mods**: Wrap Bottom Row keys with `&hml`/`&hmr`.
6. **Mirror Check**: If layer is mirrored/flipped, swap the modifier sides in the Mod-Taps.
7. **Sanitize**: Search/Replace `&stp`, `&bl`, `&rgb` with `&none`.
