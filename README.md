# unified-keyboard-config

This repository serves as the central source of truth for my programmable keyboard layouts, unifying development across different hardware and firmware ecosystems.

It acts as a monorepo containing submodules for specific implementations, currently:

* **`submodule/Adv360-Pro-ZMK`** (Kinesis Advantage 360 Pro)
* **`submodule/Moonlander-QMK`** (ZSA Moonlander)
* **`submodule/Silakka54-ZMK`** (Silakka54 QMK)

*Note: Due to inherent differences in firmware feature sets, the translation process is designed to be lossy/adaptive, prioritizing core layout consistency over 1:1 feature parity.*

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
-   CalVer is used to make git tag based on the `main` branch.
    -   firmware from GitHub Actions is uploaded to releases with the same tag.

# Silakka54 (ZMK)

Manually ported from Advantage 360 Pro layout.

Branches:

-   `main`: periodically merged from `dev`
    -   `dev`: active branch
-   CalVer is used to make git tag based on the `main` branch.
    -   firmware from GitHub Actions is uploaded to releases with the same tag.
