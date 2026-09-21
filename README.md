# Nix flake as an engineering drawing

Wallpaper generator: the Nix snowflake drawn as a dimensioned engineering sheet.
Amber phosphor, Van Dyke brown print, or blueprint colour schemes.

Geometry is extracted from the official logo in
[nixos-artwork](https://github.com/NixOS/nixos-artwork) (`logo/nix-snowflake-white.svg`),
so every dimension on the sheet is the real one: six lambdas on a Ø501.4 tip circle,
apexes on Ø195.6, foot flats at 217.2 from centre (exactly R·√3/2), 60° pitch.
Units are the artwork's own pixels.

## Sheets

- **full**: front view 1.5:1, detail A of a foot, view B of one lambda, notes,
  parts list reading `flake.nix` as a bill of materials, full title block.
- **minimal**: the flake centred with five dimensions and a title block whose
  lower field is left empty. It is sized for a live-stats widget
  (eww, see `STATS_BOX` in the script) to sit exactly in the "SYSTEM" field.
  The bottom 26 px are kept clear for a bar.

## Render

    ./render.sh            # everything into out/
    python3 flake_drawing.py amber > amber.svg
    python3 flake_drawing.py blueprint --minimal --size=2057x1371 > laptop.svg

Schemes: `amber`, `vandyke`, `blueprint`. Add one to `SCHEMES` in the script.
Text uses the 3270 Nerd Font with IBM 3270 / Share Tech Mono fallbacks; rasterise
with a font-aware renderer (`magick` via librsvg) on a machine that has one of them.

## Licence

Snowflake geometry: NixOS logo, CC-BY 4.0, NixOS contributors.
Everything else: MIT.
