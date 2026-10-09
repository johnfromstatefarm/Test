#!/usr/bin/env python3
"""Build a Pikmin 2 (USA, GPVE01) main.dol with the Pikmin limit raised to 300.

Uses the projectPiki/pikmin2 decompilation in non-matching (modding) mode. You must supply
your own game: extract it with Dolphin (see README.md). No game files are downloaded or shipped.

Usage:
    python build.py --dol path/to/extracted/sys/main.dol [--workdir pikmin2-decomp]

Needs: git, python 3.10+, ninja (pip install ninja). On Linux x86_64 the decomp downloads
wibo automatically; on macOS install wine-crossover (see the decomp's README).
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

DECOMP_URL = "https://github.com/projectPiki/pikmin2.git"
# The commit the patch was written against. Newer commits may still work; pass --rev to try.
DECOMP_REV = "ca3dcb68d10ad9e5077d35367030189302a9cece"
VERSION = "GPVE01"

HERE = Path(__file__).resolve().parent
PATCHES = sorted((HERE / "patches").glob("*.patch"))


def run(cmd, cwd=None):
    print("+", " ".join(str(c) for c in cmd), flush=True)
    subprocess.run([str(c) for c in cmd], cwd=cwd, check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dol", required=True, type=Path, help="your extracted sys/main.dol (USA retail)")
    ap.add_argument("--workdir", type=Path, default=HERE / "pikmin2-decomp", help="where to clone the decomp")
    ap.add_argument("--rev", default=DECOMP_REV, help="decomp commit to build")
    ap.add_argument("--out", type=Path, default=HERE / "out" / "main.dol", help="where to write the modded DOL")
    args = ap.parse_args()

    if not args.dol.is_file():
        sys.exit(f"main.dol not found: {args.dol}")
    if shutil.which("ninja") is None:
        sys.exit("ninja not found; install it with: pip install ninja")

    work = args.workdir.resolve()
    if not (work / ".git").exists():
        run(["git", "clone", DECOMP_URL, work])
    run(["git", "fetch", "origin", args.rev], cwd=work)
    run(["git", "checkout", "--force", args.rev], cwd=work)
    run(["git", "reset", "--hard"], cwd=work)  # drop any earlier patch application
    for patch in PATCHES:
        run(["git", "apply", "--whitespace=nowarn", patch], cwd=work)

    orig = work / "orig" / VERSION / "sys"
    orig.mkdir(parents=True, exist_ok=True)
    shutil.copy2(args.dol, orig / "main.dol")

    run([sys.executable, "configure.py", "--non-matching", "--version", VERSION], cwd=work)
    run(["ninja"], cwd=work)

    built = work / "build" / VERSION / "main.dol"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(built, args.out)
    print(f"\nDone: {args.out}\nReplace sys/main.dol in your extracted disc with it (see README.md).")


if __name__ == "__main__":
    main()
