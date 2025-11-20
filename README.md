# unified-keyboard-config

This repository serves as the central source of truth for my programmable keyboard layouts, unifying development across different hardware and firmware ecosystems.

It acts as a monorepo containing submodules for specific implementations, currently:

* **`submodule/Adv360-Pro-ZMK`** (Kinesis Advantage 360 Pro)
* **`submodule/Moonlander-QMK`** (ZSA Moonlander)

### How it works

Instead of maintaining separate, drifting configuration files for each board, this repository utilizes a **High-Level Layout Abstraction**. Keymaps are defined in a universal, table-like data structure, which is then bidirectionally translated into the specific source code required by ZMK and QMK.

*Note: Due to inherent differences in firmware feature sets, the translation process is designed to be lossy/adaptive, prioritizing core layout consistency over 1:1 feature parity.*
