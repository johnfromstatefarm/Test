# Pikmin 2: 300 Pikmin limit (PC via Dolphin)

Raises Pikmin 2's field limit from **100 to 300** Pikmin. The mod is a source patch on the
[projectPiki/pikmin2](https://github.com/projectPiki/pikmin2) decompilation, and you play it on PC with the
[Dolphin](https://dolphin-emu.org/) emulator.

The approach follows the retro/decomp playbook in
[universal-modder](https://github.com/rehan-remade/universal-modder): a decomp exists, so edit the C++ source
and build it with your own dump as the asset source. Ship only patches, never game files.

> **Status: written but not tested.** The patch is small and targeted, but it hasn't been compiled or
> played yet. The build needs your own `main.dol`, and the network here blocked the compiler download. See
> [Known risks](#known-risks).

## About "bringing it to PC"

Pikmin 2 has no native PC port. The decompilation still builds a **GameCube** executable, and porting it to
PC would mean replacing its whole GameCube graphics, audio and input layer. On PC you run the modded game in
**Dolphin**, which handles it well: high resolution, widescreen, 60 FPS hacks, controller support and save
states.

## What the patch changes

`patches/0001-raise-pikmin-limit-to-300.patch`:

- `include/Game/Piki.h`: `MAX_PIKI_COUNT` goes from 100 to 300. One constant drives everything that matters:
  - the Pikmin object pool (`pikiMgr->alloc`);
  - the sprout pool;
  - one model instance per Pikmin;
  - the formation slots (`CPlate`);
  - the Onion's "field is full" check;
  - the HUD's "max on field" value;
  - the temporary Pikmin lists used by whistling, swapping, day end and cave exit.
- `src/plugProjectOgawaU/ogObjContena.cpp`: the Onion menu used that constant to count its layout panes.
  The pane names stop at `Piki_00`–`Piki_99`, so a cap of 300 would wrap around and count panes twice. The
  count is now pinned at 100. This only affects the little Pikmin icons in that menu.

Game behaviour, not part of the mod: the "100 Pikmin" cutscene still plays the first time the field fills
up, now at 300.

## Build it

You need: your own **Pikmin 2 USA (GPVE01)** disc dumped from your console, Dolphin, Git, Python 3.10+ and
`ninja` (`pip install ninja`). Linux x86_64 needs nothing else. On macOS, install wine-crossover (see the
decomp's README).

1. In Dolphin, right-click Pikmin 2 → **Properties** → **Filesystem**.
2. Right-click **Disc** → **Extract Entire Disc...** into a folder, e.g. `P2-extracted/`. That folder now
   holds `sys/main.dol` and `files/`.
3. Build:
   ```sh
   python build.py --dol P2-extracted/sys/main.dol
   ```
   This clones the decomp at a pinned commit, applies the patch, builds in `--non-matching` mode and writes
   `out/main.dol`.
4. Back up `P2-extracted/sys/main.dol`, then replace it with `out/main.dol`.

## Play it on PC

1. In Dolphin, open **File → Open...** and choose `P2-extracted/sys/main.dol`. Dolphin detects the
   extracted disc and boots the whole game from that folder.
2. **Recommended:** go to **Config → Advanced** and turn on **Enable Emulated Memory Size Override**, with
   MEM1 at 64 MB. The game gives its heap all the RAM it finds, and 300 Pikmin plus their models and AI need
   much more than a retail GameCube's 24 MB.
3. Optional: in **Config → Advanced**, raise **Emulated CPU Clock Override**. Pikmin AI is CPU-heavy and
   300 Pikmin can slow the game down.
4. **Back up your memory card or save file** (`Dolphin Emulator/GC/`) before you play.

## Known risks

- **Memory:** this is the most likely cause of a crash. Without the MEM1 override, a busy area with 300
  Pikmin can run out of heap. Turn the override on before suspecting anything else.
- **Performance:** expect slowdown in large fights and big groups. Raise the CPU clock override.
- **Untested limits:** the patch covers every use of the limit constant in the decomp. Some code might still
  assume 100 without using the constant. If something breaks, note where it happened.
- **Saves:** Pikmin counts are stored as plain integers, so saves should load in the unmodded game. Back
  them up anyway.

## Legal

This repo holds only a source patch and a build script. You must own the game and dump it yourself. Never
upload `main.dol`, ISOs or extracted files.
