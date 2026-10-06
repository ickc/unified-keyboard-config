# unified-keyboard-config

This repository serves as the central source of truth for my programmable keyboard layouts, unifying development across different hardware and firmware ecosystems.

It acts as a monorepo containing submodules for specific implementations, currently:

* **`submodule/Adv360-Pro-ZMK`** (Kinesis Advantage 360 Pro, ZMK)
* **`submodule/Moonlander-Mk1-QMK`** (ZSA Moonlander, QMK)
* **`submodule/Silakka54-ZMK`** (Silakka54, ZMK — driven by the Lily58 shield, see [AGENTS.md](AGENTS.md))

*Note: Due to inherent differences in firmware feature sets, the translation process is designed to be lossy/adaptive, prioritizing core layout consistency over 1:1 feature parity.*

# Quickstart

```sh
git clone --recurse-submodules git@github.com:ickc/unified-keyboard-config.git
# or, in an existing clone:
pixi run submodule-init
```

Tasks:

| Task | Purpose |
| :--- | :--- |
| `pixi run submodule-init` | `git submodule update --init --recursive` after a plain clone |
| `pixi run submodule-update` | pull each submodule to the tip of its tracked branch |
| `pixi run update-moonlander` | pull the latest layout from ORYX, patch it, and commit inside the submodule |
| `pixi run patch-moonlander` | re-apply the `chordal_hold_layout` patch to an existing `keymap.c` |

The ORYX layout is selected by `ORYX_LAYOUT_ID` and `ORYX_GEOMETRY`, set in `[tool.pixi.activation.env]` in `pyproject.toml` and overridable per-invocation with `--layout-id` / `--geometry`.

Note that `update-moonlander` commits *inside* the submodule only — bumping the pointer in this repo (`git add submodule/Moonlander-Mk1-QMK && git commit`) is a separate, manual step.

# Layers

All three boards share the same 4 layers, in the same order:

| # | Name | Purpose |
| :--- | :--- | :--- |
| 0 | `base` | QWERTY |
| 1 | `esab` | `base` mirrored left-right, for one-handed typing |
| 2 | `fn` | F-keys, media, Bluetooth, mouse |
| 3 | `nf` | `fn` mirrored |

`shift-esab` (formerly layer 4, a pre-shifted copy of `esab`) was removed in the ORYX yXxz0 layout. It was reached through the mirror mod-taps on the thumbs, which yXxz0 dropped to reduce dual-function keys. Shifted mirrored characters now come from holding Shift on `esab` like on any other layer. How `esab` is reached differs per board: a one-shot key (`OSL(1)` / `&sl 1`) on the Moonlander and Adv360, and holding Space or Backspace on the Silakka54 (see [AGENTS.md](AGENTS.md)).

# Releases

This repository is tagged with CalVer, and a release records the exact set of submodule commits that were current at that point. The submodule repositories carry their own tags of the same name, and it is those releases that hold the actual firmware artifacts — GitHub's source archive for this repository does **not** include submodule contents.

# ZSA Moonlander (QMK)

This acts as the primary source of modification.

1. Make changes in ORYX,
2. run `pixi run update-moonlander` to pull changes from ORYX and auto-apply custom patch to it,
3. download fimware at <https://github.com/ickc/Moonlander-Mk1-QMK/actions>.

Branches:

-   `main`: periodically merged from `dev`
    -   `dev`: active branch that pull changes (and patched) from ORYX.
-   CalVer is used to make git tag based on the `main` branch.
    -   firmware from GitHub Actions is uploaded to releases with the same tag.

# Kinesis Advantage 360 Pro (ZMK)

Manually ported from Moonlander layout.

Branches:

-   `main`: this tracks the upstream `KinesisCorporation/Adv360-Pro-ZMK:V3.0`.
    -   `release`: this branch off `main` and applied personalized changes (ported from ORYX).
        -   `dev`: this branch of `release` as development. Commits will be cleaned up before merging/squashing back to `release`. Upon updating `release`, if history diverges, delete the `dev` branch and create a new `dev` from `release`.
-   CalVer is used to make git tag based on the `release` branch (`main` tracks upstream, so it carries no personalized layout).
    -   firmware from GitHub Actions is uploaded to releases with the same tag.

# Silakka54 (ZMK)

Manually ported from Advantage 360 Pro layout. Physically a Silakka54, but flashed with the Lily58 shield — the config files are named `lily58.*` for that reason, and the 4 Lily58 keys absent from the Silakka54 are bound to `&none`. See [AGENTS.md](AGENTS.md).

Branches:

-   `main`: periodically merged from `dev`
    -   `dev`: active branch
-   CalVer is used to make git tag based on the `main` branch.
    -   firmware from GitHub Actions is uploaded to releases with the same tag.
