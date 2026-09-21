#!/usr/bin/env python3
"""Nix snowflake as an engineering drawing. Geometry from nixos-artwork/logo/nix-snowflake-white.svg."""
import math, sys

# One lambda (pointing up), centre-origin, y down, artwork px units.
L = [(98.0,-5.4),(-24.2,-217.0),(32.0,-217.5),(64.6,-160.6),(97.4,-217.2),(125.3,-217.2),(139.6,-192.5),(92.8,-112.0),(126.0,-54.2)]
R_TIP, R_APEX, FOOT_Y = 250.7, 97.8, 217.2

SCHEMES = {
  'amber':   dict(bg='#100c08', line='#ffb000', text='#e6e2d6', faint='rgba(255,176,0,0.28)', grid='rgba(255,176,0,0.07)', fill='rgba(255,176,0,0.06)'),
  'vandyke': dict(bg='#3b2410', line='#f3e6cf', text='#fff6e6', faint='rgba(243,230,207,0.35)', grid='rgba(243,230,207,0.09)', fill='rgba(243,230,207,0.05)'),
  'blueprint': dict(bg='#0f2a4a', line='#ffffff', text='#ffffff', faint='rgba(255,255,255,0.35)', grid='rgba(255,255,255,0.08)', fill='rgba(255,255,255,0.05)'),
}
W, H = 2560, 1440
FONT = "'3270 Nerd Font Mono','IBM 3270','Share Tech Mono',monospace"

def rot(p, deg):
    r = math.radians(deg); c, s = math.cos(r), math.sin(r)
    return (p[0]*c - p[1]*s, p[0]*s + p[1]*c)

def poly(pts, cx, cy, sc, **kw):
    d = ' '.join(f'{cx+x*sc:.1f},{cy+y*sc:.1f}' for x, y in pts)
    attrs = ' '.join(f'{k.replace("_","-")}="{v}"' for k, v in kw.items())
    return f'<polygon points="{d}" {attrs}/>'

def flake(cx, cy, sc, C):
    out = []
    for k in range(6):
        out.append(poly([rot(p, 60*k) for p in L], cx, cy, sc, fill=C['fill'], stroke=C['line'], stroke_width=2.2, stroke_linejoin='round'))
    return '\n'.join(out)

def text(x, y, s, C, size=20, anchor='start', fill=None, rotate=0, weight='normal'):
    tr = f' transform="rotate({rotate} {x} {y})"' if rotate else ''
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{fill or C["text"]}" font-weight="{weight}"{tr}>{s}</text>'

def line(x1, y1, x2, y2, C, w=1.2, dash=None, col=None, marker=''):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col or C["line"]}" stroke-width="{w}"{d}{marker}/>'

ARROWS = ' marker-start="url(#a)" marker-end="url(#a)"'

def hdim(x1, x2, y, label, C, ext_from=None, above=True, size=20):
    """Horizontal dimension between x1 and x2 at height y; extension lines from ext_from (y of feature)."""
    s = []
    if ext_from is not None:
        g = 6 if ext_from > y else -6
        for x in (x1, x2): s.append(line(x, ext_from - g, x, y - (14 if above else -14) * (1 if ext_from > y else -1), C, .9, col=C['faint']))
    s.append(line(x1, y, x2, y, C, 1.2, marker=ARROWS))
    s.append(text((x1+x2)/2, y - 7 if above else y + 24, label, C, size, 'middle'))
    return '\n'.join(s)

def vdim(y1, y2, x, label, C, ext_from=None, size=20, left=False):
    s = []
    if ext_from is not None:
        g = 6 if ext_from < x else -6
        for y in (y1, y2): s.append(line(ext_from + g, y, x + (14 if ext_from < x else -14), y, C, .9, col=C['faint']))
    s.append(line(x, y1, x, y2, C, 1.2, marker=ARROWS))
    s.append(text(x - 8 if left else x + 8, (y1+y2)/2 + 7, label, C, size, 'end' if left else 'start'))
    return '\n'.join(s)

def leader(x1, y1, x2, y2, x3, label, C, size=20):
    return (line(x1, y1, x2, y2, C, 1.2, marker=' marker-start="url(#dot)"') + line(x2, y2, x3, y2, C, 1.2)
            + text(x3 + (8 if x3 > x2 else -8), y2 + 7, label, C, size, 'start' if x3 > x2 else 'end'))

def circle(cx, cy, r, C, w=1, dash=None, col=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="none" stroke="{col or C["line"]}" stroke-width="{w}"{d}/>'

def arc(cx, cy, r, a1, a2, C, w=1.2, marker=ARROWS):
    p1 = (cx + r*math.cos(math.radians(a1)), cy + r*math.sin(math.radians(a1)))
    p2 = (cx + r*math.cos(math.radians(a2)), cy + r*math.sin(math.radians(a2)))
    return f'<path d="M{p1[0]:.1f},{p1[1]:.1f} A{r:.1f},{r:.1f} 0 0 1 {p2[0]:.1f},{p2[1]:.1f}" fill="none" stroke="{C["line"]}" stroke-width="{w}"{marker}/>'

# ---------------------------------------------------------------------------
# The sheet: flake centred, a few dimensions, thin bottom band. The title
# block's lower area is left empty on purpose: an eww widget draws live system
# stats there (see STATS_BOX for the rectangle it must cover).
# ---------------------------------------------------------------------------
BAR = 26          # waybar height at the bottom, kept clear
def stats_box(): return (W - 680, H - BAR - 204, W - 48, H - BAR - 74)   # x0, y0, x1, y1 of the live-stats area

def build_minimal(scheme):
    global W, H
    C = SCHEMES[scheme]
    o = []
    bottom = H - BAR                      # last usable row
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}">')
    o.append(f'''<defs>
  <marker id="a" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="12" markerHeight="12" orient="auto-start-reverse" markerUnits="userSpaceOnUse"><path d="M0,1.5 L10,5 L0,8.5 z" fill="{C['line']}"/></marker>
  <marker id="dot" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="8" markerHeight="8" markerUnits="userSpaceOnUse"><circle cx="5" cy="5" r="4" fill="{C['line']}"/></marker>
  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="{C['grid']}" stroke-width="1"/></pattern>
</defs>''')
    o.append(f'<rect width="{W}" height="{H}" fill="{C["bg"]}"/>')
    o.append(f'<rect width="{W}" height="{bottom}" fill="url(#grid)"/>')
    # frame: outer hairline, inner heavy, zone ticks
    fx0, fy0, fx1, fy1 = 48, 48, W - 48, bottom - 48
    o.append(f'<rect x="20" y="20" width="{W-40}" height="{bottom-40}" fill="none" stroke="{C["line"]}" stroke-width="1"/>')
    o.append(f'<rect x="{fx0}" y="{fy0}" width="{fx1-fx0}" height="{fy1-fy0}" fill="none" stroke="{C["line"]}" stroke-width="2.5"/>')
    for i in range(8):
        x = fx0 + i*(fx1-fx0)/8
        o.append(line(x, 20, x, fy0, C, 1)); o.append(line(x, fy1, x, bottom-20, C, 1))
        o.append(text(x + (fx1-fx0)/16, 40, str(i+1), C, 16, 'middle')); o.append(text(x + (fx1-fx0)/16, bottom-27, str(i+1), C, 16, 'middle'))
    for i in range(6):
        y = fy0 + i*(fy1-fy0)/6
        o.append(line(20, y, fx0, y, C, 1)); o.append(line(fx1, y, W-20, y, C, 1))
        o.append(text(34, y + (fy1-fy0)/12 + 6, 'ABCDEF'[i], C, 16, 'middle')); o.append(text(W-34, y + (fy1-fy0)/12 + 6, 'ABCDEF'[i], C, 16, 'middle'))
    # closing ticks at the far edges so all four corners become little squares
    o.append(line(fx1, 20, fx1, fy0, C, 1)); o.append(line(fx1, fy1, fx1, bottom-20, C, 1))
    o.append(line(20, fy1, fx0, fy1, C, 1)); o.append(line(fx1, fy1, W-20, fy1, C, 1))
    for x, y1_, y2_ in ((W/2, 20, 60), (W/2, bottom-60, bottom-20)): o.append(line(x, y1_, x, y2_, C, 2))
    for y, x1_, x2_ in ((bottom/2, 20, 60), (bottom/2, W-60, W-20)): o.append(line(x1_, y, x2_, y, C, 2))

    # ---- the flake, centred ------------------------------------------------
    cx, cy, sc = W/2, (fy0 + fy1)/2 - 30, 1.35 * H / 1440
    R = R_TIP*sc
    for k in range(3):
        a = math.radians(60*k); r = R + 70
        o.append(line(cx - r*math.cos(a), cy - r*math.sin(a), cx + r*math.cos(a), cy + r*math.sin(a), C, 1, dash='18 6 3 6', col=C['faint']))
    o.append(circle(cx, cy, R, C, 1, dash='18 6 3 6', col=C['faint']))
    o.append(circle(cx, cy, R_APEX*sc, C, 1, dash='18 6 3 6', col=C['faint']))
    o.append(flake(cx, cy, sc, C))
    o.append(circle(cx, cy, 5, C, 1.5)); o.append(text(cx + 10, cy - 10, 'C', C, 18))
    # dimensions: tip circle (right), apex circle (left), 60° pitch, foot chain (top), 217.2 (left)
    a = math.radians(20); px, py = cx + R*math.cos(a), cy + R*math.sin(a)
    o.append(leader(px, py, px + 110, py - 40, px + 170, '&#8960;501.4', C))
    a = math.radians(200); px, py = cx + R_APEX*sc*math.cos(a), cy + R_APEX*sc*math.sin(a)
    o.append(leader(px, py, px - 150, py + 60, px - 210, '&#8960;195.6', C))
    o.append(arc(cx, cy, R + 40, 2, 58, C))
    a = math.radians(30); o.append(text(cx + (R + 62)*math.cos(a), cy + (R + 62)*math.sin(a) + 7, '60&#176;', C, 20, 'middle'))
    xd = cx - R - 110
    o.append(vdim(cy - FOOT_Y*sc, cy, xd, '217.2', C, ext_from=cx - 30, left=True))
    o.append(line(cx - 40, cy, xd - 14, cy, C, .9, col=C['faint']))
    yt = cy - FOOT_Y*sc; yd = yt - 60
    for x1_, x2_, lbl in ((-24.2, 32.0, '56.2'), (32.0, 97.4, '65.4'), (97.4, 125.3, '27.9')):
        o.append(hdim(cx + x1_*sc, cx + x2_*sc, yd, lbl, C, ext_from=yt))
    o.append(text(cx, cy + R + 110, '6&#215; &#955;  EQ. SP.  ROTATE ABOUT C', C, 17, 'middle', fill=C['line']))

    # ---- bottom band: two notes left, title block right ----------------------
    yb = fy1 - 186
    tx = stats_box()[0]
    o.append(line(tx - 20, yb, fx1, yb, C, 2))      # title block only, no notes column
    o.append(line(tx - 20, yb, tx - 20, fy1, C, 2))
    o.append(text(tx, yb + 38, 'NIX FLAKE', C, 34, weight='bold'))
    o.append(text(fx1 - 12, yb + 38, 'NIX-&#955;6-501  REV 2.4', C, 16, 'end'))
    o.append(line(tx, yb + 50, fx1 - 12, yb + 50, C, 1))
    o.append(text(tx, yb + 50 + 18, 'SYSTEM', C, 12, fill=C['line']))
    o.append('</svg>')
    return '\n'.join(o)

if __name__ == '__main__':
    for a in sys.argv[1:]:
        if a.startswith('--size='):
            W, H = (int(x) for x in a[7:].split('x'))
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    sys.stdout.write(build_minimal(args[0] if args else 'amber'))
