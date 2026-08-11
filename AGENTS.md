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

### HID usage ranges (Adv360 only)

The Adv360 board defconfigs (`config/boards/arm/adv360/adv360_{left,right}_defconfig`) constrain which HID usages the firmware can physically emit. A binding outside the range is silently dropped — the host never sees an event, so it looks like the OS is ignoring the key.

| Setting | Ceiling | Consequence |
| :--- | :--- | :--- |
| `CONFIG_ZMK_HID_REPORT_TYPE_NKRO=y` | keyboard usage `0x67` (`KEYPAD_EQUAL`) | **F13-F24 (`0x68`+) and INTL keys are unreachable** |
| `+ CONFIG_ZMK_HID_KEYBOARD_EXTENDED_REPORT=y` | keyboard usage `0x97` (`LANG8`) | F13-F24 work. Breaks Android input — ZMK gives *no* input there |
| `CONFIG_ZMK_HID_CONSUMER_REPORT_USAGES_BASIC=y` | consumer usage `0xFF` | `C_AC_SEARCH` (`0x221`), `C_AC_DESKTOP_SHOW_ALL_WINDOWS` (`0x29F`) unreachable |
| `CONFIG_ZMK_HID_CONSUMER_REPORT_USAGES_FULL=y` | consumer usage `0xFFF` | Both work. Current setting |

**Rules**:
- Keep both halves' defconfigs in sync — edit `adv360_left_defconfig` *and* `adv360_right_defconfig`.
- After changing either setting, **unpair and re-pair on macOS**. The report descriptor changes shape and macOS caches the BLE HID report map; without a re-pair the old descriptor stays in force and the fix looks like it did nothing.
- The Silakka54 needs none of this: `lily58.conf` sets no HID options, so it inherits ZMK's defaults (HKRO, keyboard ceiling `0xFF`, consumer `FULL`), which cover every usage in the layout.

### Do Not Disturb is not a portable keycode

QMK's `MAC_DND` sends **Generic Desktop** usage `0x9B` (System Do Not Disturb) via `HSS()`. Do **not** port this as ZMK's `K_CANCEL`: that is **Keyboard/Keypad** usage `0x9B` (Keyboard Cancel) — same number, unrelated page, and macOS does nothing with it. ZMK cannot send it at all either way: `zmk_hid_press()` dispatches only `HID_USAGE_KEY` and `HID_USAGE_CONSUMER`, so there is no Generic Desktop report (which is also why `SYSTEM_POWER`/`SYSTEM_SLEEP` in `keys.h` are dead defines).

macOS stopped acting on the QMK version too, so **both** boards now bind plain `F13`, remapped host-side via Shortcuts.app ("Set Focus"). Note that F13 is what forces `CONFIG_ZMK_HID_KEYBOARD_EXTENDED_REPORT=y` above.

### ZMK version pinning (Silakka54)

The Silakka54 runs **nice!nano v2** controllers. Upstream ZMK has changed what the `board:` value in `build.yaml` *means* twice, silently, and both changes are load-bearing. Two upstream commits define the eras:

| Upstream commit | Date | What it did |
| :--- | :--- | :--- |
| `c06fa48c` ([#3060](https://github.com/zmkfirmware/zmk/pull/3060)) | 2025-12-10 | Zephyr 3.5 → 4.1 (LVGL 8 → 9); ported the nice!view code; **merged `nice_nano` + `nice_nano_v2` into one board with hardware revisions, default `2.0.0`** |
| `6690d535` ([#3145](https://github.com/zmkfirmware/zmk/pull/3145)) | 2026-02-12 | Moved to upstream Zephyr boards; board target became `nice_nano/nrf52840/zmk` and shield board-overlays were renamed to match |

Which gives three eras, and the correct `board:` differs in each:

| ZMK era | Correct `board:` | With `board: nice_nano` you get |
| :--- | :--- | :--- |
| before #3060 (incl. **v0.3.0**) | `nice_nano_v2` | builds, but targets **v1** hardware → **blank nice!view** |
| #3060 … #3145 | `nice_nano` | correct (revision defaults to `2.0.0`) |
| after #3145 (incl. current `main`) | `nice_nano@2//zmk` ← **current setting** | build fails: `undefined node label 'nice_view_spi'` |

The post-#3145 form is Zephyr hardware-model-v2 syntax, `board[@revision]/soc[/variant]`:

```
nice_nano@2//zmk
   │      │ │ └── variant: ZMK's additions to the upstream Zephyr board
   │      │ └──── soc: empty, the board has only one (nrf52840)
   │      └────── revision 2.0.0 = nice!nano v2
   └───────────── board name (vendor dir: nicekeyboards)
```

Zephyr normalises that to `nice_nano@2.0.0/nrf52840/zmk`, which is why the shield board-overlay is named `nice_nano_nrf52840_zmk.overlay`. Bare `nice_nano//zmk` would also work — it inherits `default: 2.0.0` from `board.yml` — but **state `@2` explicitly**: it was exactly an inherited default silently changing meaning that blanked the display. A v1 controller would be `nice_nano@1//zmk`.

To verify a build really got the revision you asked for, check the resolved config: revision 2.0.0 yields `CONFIG_ZMK_BATTERY_NRF_VDDH=y`, whereas 1.0.0 yields the voltage-divider driver instead.

**Why the wrong revision blanks the screen.** On pre-#3060 ZMK, `nice_nano` and `nice_nano_v2` are separate boards, and their DTS differ in exactly one functional way:

```diff
 EXT_POWER {
-    control-gpios = <&gpio0 13 GPIO_ACTIVE_LOW>;    // nice_nano   (v1)
+    control-gpios = <&gpio0 13 GPIO_ACTIVE_HIGH>;   // nice_nano_v2
+    init-delay-ms = <50>;
 };
```

`EXT_POWER` (P0.13) gates the **external VCC rail that powers the nice!view**. Running v1 firmware on v2 hardware inverts that pin, so the rail stays off and the display never powers up. Everything else looks perfectly healthy — the key matrix, USB and BLE are driven straight off the MCU and never touch that rail. A keyboard that types and pairs fine but shows nothing is the signature of this exact mistake, not of a display bug. (Battery reporting is also wrong in this state: v1 reads a voltage divider on ADC channel 2, v2 reads `zmk,battery-nrf-vddh`.)

**Rules**:
- Pin ZMK to a tag or a full commit SHA in *both* `config/west.yml` (`revision:`) and `.github/workflows/build.yml` (`uses: …@`). Keep the two in sync — mismatched refs fail the build.
- **Never track `main`.** Upstream's position ([#3157](https://github.com/zmkfirmware/zmk/issues/3157)) is that breaking changes are expected on `main` and users must pin; they explicitly declined to add a `nice_nano_v2` compatibility alias.
- When moving the pin across either boundary above, update `board:` in the same commit, and prefer the explicit `@2.0.0` revision so the name cannot quietly change meaning again.

### ZMK Studio
- **Enable**: Add `CONFIG_ZMK_STUDIO=y` to `lily58.conf`.
- **Unlock Key**: Map `&studio_unlock` to a **home-row outer** key on the utility layers — currently position **35** on `fn` and its mirror, position **24**, on `nf`. It must be a key that physically exists, so the inner thumbs are not an option.

## 3. Custom Behaviors & Mods

### Behaviors
- **Port**: Copy `hml`, `hmr`, `mlr`, `mll` definitions.
  - `mmr`/`mml` (mirror mod-taps) are no longer used by either board — the layout dropped those dual-function keys — but the names are kept here in case they come back.
  - QMK `MO(n)` is a plain `&mo n` and carries no `hold-trigger-key-positions`; only the `mll`/`mlr` mirror keys are hand-restricted. If `TT(n)` ever reappears upstream, note that ZMK has no equivalent and it needs a `<&mo>, <&tog>` hold-tap.
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
