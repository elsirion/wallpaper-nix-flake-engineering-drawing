#!/usr/bin/env bash
# Render every scheme/size combination into out/. Needs python3 and ImageMagick (magick).
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p out
for s in amber vandyke blueprint; do
    python3 flake_drawing.py "$s" > "out/nix-flake-full-$s.svg"
    magick "out/nix-flake-full-$s.svg" "out/nix-flake-full-$s.png"
    python3 flake_drawing.py "$s" --minimal > "out/nix-flake-minimal-$s.svg"
    magick "out/nix-flake-minimal-$s.svg" "out/nix-flake-minimal-$s.png"
    # 14" laptop panel: 2057x1371 logical (2880x1920 @ 1.4)
    python3 flake_drawing.py "$s" --minimal --size=2057x1371 > "out/nix-flake-minimal-$s-edp.svg"
    magick -density 134 "out/nix-flake-minimal-$s-edp.svg" -resize 2880x1920! "out/nix-flake-minimal-$s-edp.png"
done
ls -la out
