#!/usr/bin/env bash
# Live system stats for the eww widget in the wallpaper's title block. Prints one JSON object.
set -u
read -r _ u n s i _ < /proc/stat
prev=/tmp/claude-eww-cpu.$UID; now=$((u+n+s+i)); busy=$((u+n+s))
if [ -f "$prev" ]; then read -r pnow pbusy < "$prev"; d=$((now-pnow)); cpu=$(( d>0 ? (busy-pbusy)*100/d : 0 )); else cpu=0; fi
echo "$now $busy" > "$prev"
declare -A mi; while read -r k v _; do mi[${k%:}]=$v; done < /proc/meminfo
memu=$(( (mi[MemTotal]-mi[MemAvailable]) / 1048576 )); memt=$(( mi[MemTotal] / 1048576 ))
gtt=0; for f in /sys/class/drm/card*/device/mem_info_gtt_used; do [ -r "$f" ] && gtt=$(( $(cat "$f") / 1073741824 )) && break; done
load=$(cut -d' ' -f1-3 /proc/loadavg)
up=$(awk '{d=int($1/86400); h=int($1%86400/3600); m=int($1%3600/60); printf "%dd %02dh%02dm", d, h, m}' /proc/uptime)
disk=$(df -h / | awk 'NR==2 {print $3"/"$2}')
vpn=$(mullvad status 2>/dev/null | awk 'NR==1 && /^Connected/ {c=1} /Relay:/ && c {r=$2; sub(/-wg-.*|-ovpn-.*/, "", r); print r}'); vpn=${vpn:-off}
ip=$(ip -4 -o addr show scope global 2>/dev/null | awk '$2 ~ /^(wl|en|eth)/ {print $4; exit}' | cut -d/ -f1); ip=${ip:-none}
claude=$(pgrep -c -f '(^|/)claude( |$)'); codex=$(pgrep -c -f '(^|/)codex( |$)')
ff=$(pgrep -c 'Isolated')
temp=$(for z in /sys/class/thermal/thermal_zone*/temp; do cat "$z" 2>/dev/null; done | sort -n | tail -1); temp=$(( ${temp:-0} / 1000 ))
printf '{"cpu":%d,"temp":%d,"load":"%s","memu":%d,"memt":%d,"gtt":%d,"disk":"%s","up":"%s","vpn":"%s","ip":"%s","claude":%d,"codex":%d,"ff":%d,"host":"%s"}\n' \
  "$cpu" "$temp" "$load" "$memu" "$memt" "$gtt" "$disk" "$up" "$vpn" "$ip" "$claude" "$codex" "$ff" "$(hostname)"
