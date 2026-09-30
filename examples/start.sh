#!/usr/bin/env bash
# Open the wallpaper stats widget on every active output (idempotent, safe under exec_always).
# Connector names change with dock/port (DP-4, DP-9, ...), so outputs are discovered at runtime,
# and a single listener keeps the widgets in sync on hotplug and mode/scale changes.
#
# Placement: each output's wallpaper (taken from swaybg's arguments) has a <name>.field.json sidecar
# (flake_drawing.py --field) with the sheet size and the stats field in sheet units. Mapping that
# through swaybg's fill scaling/cropping onto the output's logical size gives the window geometry,
# relative to the area the bar leaves free (the workspace rect), which is what layer-shell anchors to.
command -v eww >/dev/null || exit 0
eww daemon 2>/dev/null; sleep 1   # also lets a reload's fresh swaybg come up

png_size() { od -An -tu1 -j16 -N8 "$1" | awk 'NF == 8 {print $1*16777216+$2*65536+$3*256+$4, $5*16777216+$6*65536+$7*256+$8}'; }

# Prints "output x y w h scale" for every active output.
geometries() {
  local pid args=() i out='*' img mode field size outputs workspaces
  local -A imgs=() modes=()
  pid=$(pgrep -n swaybg) && mapfile -d '' args < "/proc/$pid/cmdline"
  for ((i = 1; i < ${#args[@]} - 1; i++)); do
    case ${args[i]} in
      -o) out=${args[i+1]} ;;
      -i) imgs[$out]=${args[i+1]} ;;
      -m) modes[$out]=${args[i+1]} ;;
    esac
  done
  outputs=$(swaymsg -t get_outputs); workspaces=$(swaymsg -t get_workspaces)
  for out in $(jq -r '.[] | select(.active) | .name' <<<"$outputs"); do
    img=${imgs[$out]:-${imgs['*']:-}}; mode=${modes[$out]:-${modes['*']:-}}
    field=${img%.*}.field.json
    if [[ -n $img && $mode == fill && -r $field ]] && size=$(png_size "$img") && [[ -n $size ]]; then
      jq -rn --arg out "$out" --arg size "$size" --argjson f "$(<"$field")" \
        --argjson outputs "$outputs" --argjson ws "$workspaces" '
        ($outputs[] | select(.name == $out) | .rect) as $o
        | ([$ws[] | select(.output == $out) | .rect] | first // $o) as $u
        | ($size | split(" ") | map(tonumber)) as [$iw, $ih]
        | ([$o.width / $iw, $o.height / $ih] | max) as $s          # fill: cover, centred, cropped
        | (($o.width - $iw * $s) / 2) as $ox | (($o.height - $ih * $s) / 2) as $oy
        | ($s * $iw / $f.size[0]) as $kx | ($s * $ih / $f.size[1]) as $ky   # logical px per sheet px
        | $f.field as [$x0, $y0, $x1, $y1]
        | [$out,
           ($u.x + $u.width - $o.x - $ox - $x1 * $kx | round),     # right margin inside the free area
           ($u.y + $u.height - $o.y - $oy - $y1 * $ky | round),    # bottom margin above the bar
           (($x1 - $x0) * $kx | round), (($y1 - $y0) * $ky | round),
           ($kx * 1000 | round / 1000)]
        | map(tostring) | join(" ")'
    else
      echo "$out 60 56 620 102 1"   # no sidecar: assume a 2560x1440-style sheet drawn at the output's size
    fi
  done
}

sync_windows() {
  local out x y w h scale open wanted=
  while read -r out x y w h scale; do
    eww open stats --screen "$out" --id "stats-$out" \
      --arg x="$x" --arg y="$y" --arg w="$w" --arg h="$h" --arg scale="$scale"
    wanted+="stats-$out"$'\n'
  done < <(geometries)
  open=$(eww active-windows | sed -n 's/^\(stats-[^:]*\):.*/\1/p')
  for id in $open; do grep -qx "$id" <<<"$wanted" || eww close "$id"; done
}
sync_windows

exec 9>"${XDG_RUNTIME_DIR:-/tmp}/eww-stats.lock"
flock -n 9 || exit 0
swaymsg -m -t subscribe '["output"]' | while read -r _; do sleep 1; sync_windows; done
