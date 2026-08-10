# Adv360 to Lily58 Porting Guide

This guide documents the rules and logic used to port the `adv360.keymap` to `lily58.keymap`. Use this when updating the Lily58 configuration based on future Adv360 changes.

## 0. Why "Lily58" and not "Silakka54"

The keyboard in `submodule/Silakka54-ZMK` is **physically a Silakka54**, but it is driven by the **Lily58 shield** in ZMK. As far as the software in this repo is concerned, it *is* a Lily58 — which is why every file is named `lily58.*`:

- `config/lily58.keymap`, `config/lily58.conf`
- build targets `lily58_left` / `lily58_right` in `build.yaml`
- all key positions below are **Lily58 shield indices (0-57)**

The Lily58 has **58 keys**; the Silakka54 has **54**. The 4 Lily58 positions with no physical Silakka54 key are hardwired to `&none` on *every* layer:

| Lily58 position | Where | Physically present on Silakka54? |
| :--- | :--- | :--- |
| **42**, **43** | Bottom row (row 3), inner column each side | No |
| **53**, **54** | Thumb cluster, innermost key each side | No |

**Rule**: never bind anything to positions 42, 43, 53, 54 — the key does not exist on the hardware and the binding is unreachable. Always write `&none` there, including on mirrored and utility layers.

Full Lily58 position map used throughout this guide:

| Row | Left | Right |
| :--- | :--- | :--- |
| Number row | 0-5 | 6-11 |
| Top row | 12-17 | 18-23 |
| Home row | 24-29 | 30-35 |
| Bottom row | 36-42 (**42 = dead**) | 43-49 (**43 = dead**) |
| Thumbs | 50-53 (**53 = dead**) | 54-57 (**54 = dead**) |

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
The Adv360 thumb cluster is complex. The Lily58 shield has 4 thumb keys per side, but only **3 per side are physically present on the Silakka54** (see Section 0).

Only the Adv360's **bottom thumb row** is carried over — positions **65 66 67** (left) and **68 69 70** (right). Every other Adv360 thumb key (35 36 / 37 38, 52 / 53) is dropped.

#### The `ABC DEF -> CAB EFD` shuffle

Label the Adv360 bottom thumb row symbolically, in position order:

```
Adv360:   A  B  C     D  E  F
          65 66 67    68 69 70
```

The Lily58 thumbs do **not** take these in order. Shuffle them:

```
ABC DEF  ->  CAB EFD
```

| Symbol | Adv360 | Lily58 | Notes |
| :--- | :--- | :--- | :--- |
| **C** | 67 | **50** | leftmost |
| **A** | 65 | **51** | |
| **B** | 66 | **52** | |
| — | — | **53** | **Dead — always `&none`** |
| — | — | **54** | **Dead — always `&none`** |
| **E** | 69 | **55** | |
| **F** | 70 | **56** | |
| **D** | 68 | **57** | rightmost |

**Why**: the Silakka54 thumb keys sit physically closer together than the Adv360's, so keeping **AB** and **EF** adjacent and in order preserves the physical correspondence for the keys that get used constantly (Space/Tab, Enter/Backspace). **C** and **D** are the lesser-used outer keys (the layer keys), so they are the ones that get moved to the far ends.

- **Inner Keys**: Positions 53 and 54 have no physical key on the Silakka54. Bind `&none` on every layer — do **not** park utility bindings there.

### Reaching the mirror layer (`esab`)

The Adv360 enters the mirror layer with a **one-shot layer** key, `&sl 1`, bound to its mod-row inner keys (positions **35** and **38**). Both of those are dropped by the rules above, and after the thumb shuffle all six live Silakka54 thumbs are taken — so `&sl 1` has nowhere to go.

**Rule**: on the Silakka54 only, **Space and Backspace on the thumb row double as the mirror key on hold**:

- position **51** (`A`, Space) → `&mll 1 SPACE`
- position **56** (`F`, Backspace) → `&mlr 1 BACKSPACE`

This is a deliberate divergence — momentary (`&mo` via `mll`/`mlr`) rather than the Adv360's one-shot — and it is how this board reached the mirror layer before the shuffle too. The same-side `hold-trigger-key-positions` on `mll`/`mlr` are what make one-handed mirrored typing work.

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
- **Unlock Key**: Map `&studio_unlock` to a **home-row outer** key on the utility layers — currently position **35** on `fn` and its mirror, position **24**, on `nf`. It must be a key that physically exists, so the inner thumbs are not an option.

## 3. Custom Behaviors & Mods

### Behaviors
- **Port**: Copy `hml`, `hmr`, `mlr`, `mll`, `ltt` definitions.
  - `ltt` is the stand-in for QMK's `TT(n)`, which ZMK has no equivalent for: a hold-tap of `<&mo>, <&tog>`, so hold = momentary and tap = toggle. It differs from QMK in that a *single* tap toggles (QMK's `TAPPING_TOGGLE` defaults to 5).
  - `mmr`/`mml` (mirror mod-taps) are no longer used by either board — the layout dropped those dual-function keys — but the names are kept here in case they come back.
- **Update Triggers**: The `hold-trigger-key-positions` must be recalculated for Lily58 key indices.
  - **Left Hand Indices**: 0-5, 12-17, 24-29, 36-42, 50-53 (Thumbs).
  - **Right Hand Indices**: 6-11, 18-23, 30-35, 43-49, 54-57 (Thumbs).
  - *Note*: 42, 43, 53 and 54 are dead keys (Section 0) — listing them is harmless but pointless.
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
4. **Fix Thumbs**: Take the Adv360 bottom thumb row only and apply the `ABC DEF -> CAB EFD` shuffle. Drop every other Adv360 thumb key, then restore mirror-layer access on Space/Backspace.
5. **Apply Mods**: Wrap Bottom Row keys with `&hml`/`&hmr`.
6. **Mirror Check**: If layer is mirrored/flipped, swap the modifier sides in the Mod-Taps.
7. **Sanitize**: Search/Replace `&stp`, `&bl`, `&rgb` with `&none`.
