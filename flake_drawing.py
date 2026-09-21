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

def build(scheme):
    C = SCHEMES[scheme]
    o = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}">')
    o.append(f'''<defs>
  <marker id="a" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="12" markerHeight="12" orient="auto-start-reverse" markerUnits="userSpaceOnUse"><path d="M0,1.5 L10,5 L0,8.5 z" fill="{C['line']}"/></marker>
  <marker id="dot" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="8" markerHeight="8" markerUnits="userSpaceOnUse"><circle cx="5" cy="5" r="4" fill="{C['line']}"/></marker>
  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="{C['grid']}" stroke-width="1"/></pattern>
  <clipPath id="detA"><circle cx="1620" cy="400" r="230"/></clipPath>
</defs>''')
    o.append(f'<rect width="{W}" height="{H}" fill="{C["bg"]}"/>')
    o.append(f'<rect width="{W}" height="{H}" fill="url(#grid)"/>')
    # sheet frame + zones
    o.append(f'<rect x="20" y="20" width="{W-40}" height="{H-40}" fill="none" stroke="{C["line"]}" stroke-width="1"/>')
    o.append(f'<rect x="48" y="48" width="{W-96}" height="{H-96}" fill="none" stroke="{C["line"]}" stroke-width="2.5"/>')
    for i in range(8):
        x = 48 + i*(W-96)/8
        o.append(line(x, 20, x, 48, C, 1)); o.append(line(x, H-48, x, H-20, C, 1))
        o.append(text(x + (W-96)/16, 40, str(i+1), C, 16, 'middle')); o.append(text(x + (W-96)/16, H-27, str(i+1), C, 16, 'middle'))
    for i in range(6):
        y = 48 + i*(H-96)/6
        o.append(line(20, y, 48, y, C, 1)); o.append(line(W-48, y, W-20, y, C, 1))
        o.append(text(34, y + (H-96)/12 + 6, 'ABCDEF'[i], C, 16, 'middle')); o.append(text(W-34, y + (H-96)/12 + 6, 'ABCDEF'[i], C, 16, 'middle'))
    # centring marks
    for x, y1, y2 in ((W/2, 20, 60), (W/2, H-60, H-20)): o.append(line(x, y1, x, y2, C, 2))
    for y, x1, x2 in ((H/2, 20, 60), (H/2, W-60, W-20)): o.append(line(x1, y, x2, y, C, 2))

    # ---- main view --------------------------------------------------------
    cx, cy, sc = 780, 600, 1.5
    o.append(f'<g id="main">')
    # centrelines through tips (dash-dot) and hexagon construction
    for k in range(3):
        a = math.radians(60*k)
        r = R_TIP*sc + 70
        o.append(line(cx - r*math.cos(a), cy - r*math.sin(a), cx + r*math.cos(a), cy + r*math.sin(a), C, 1, dash='18 6 3 6', col=C['faint']))
    hexpts = [(R_TIP*math.cos(math.radians(60*k)), R_TIP*math.sin(math.radians(60*k))) for k in range(6)]
    o.append(poly(hexpts, cx, cy, sc, fill='none', stroke=C['faint'], stroke_width=1, stroke_dasharray='6 5'))
    o.append(circle(cx, cy, R_TIP*sc, C, 1, dash='18 6 3 6', col=C['faint']))
    o.append(circle(cx, cy, R_APEX*sc, C, 1, dash='18 6 3 6', col=C['faint']))
    o.append(flake(cx, cy, sc, C))
    o.append(circle(cx, cy, 5, C, 1.5)); o.append(text(cx + 10, cy - 10, 'C', C, 18))
    # Ø tip circle, Ø apex circle: leaders
    a = math.radians(20); px, py = cx + R_TIP*sc*math.cos(a), cy + R_TIP*sc*math.sin(a)
    o.append(leader(px, py, px + 110, py - 40, px + 170, '&#8960;501.4  TIP CIRCLE', C))
    a = math.radians(-150); px, py = cx + R_APEX*sc*math.cos(a), cy + R_APEX*sc*math.sin(a)
    o.append(leader(px, py, px - 120, py - 130, px - 180, '&#8960;195.6  APEX CIRCLE', C))
    # 60° angular dimension between tips at 0° and 60°
    o.append(arc(cx, cy, R_TIP*sc + 40, 2, 58, C))
    a = math.radians(30); o.append(text(cx + (R_TIP*sc + 62)*math.cos(a), cy + (R_TIP*sc + 62)*math.sin(a) + 7, '60&#176; TYP', C, 20, 'middle'))
    # foot flat distance from centre (vertical dim on left)
    xd = cx - R_TIP*sc - 110
    o.append(vdim(cy - FOOT_Y*sc, cy, xd, '217.2', C, ext_from=cx - 30, left=True))
    o.append(line(cx - 40, cy, xd - 14, cy, C, .9, col=C['faint']))
    # top foot chain dims
    yt = cy - FOOT_Y*sc; yd = yt - 60
    for x1, x2, lbl in ((-24.2, 32.0, '56.2'), (32.0, 97.4, '65.4'), (97.4, 125.3, '27.9')):
        o.append(hdim(cx + x1*sc, cx + x2*sc, yd, lbl, C, ext_from=yt))
    o.append(hdim(cx - 24.2*sc, cx + 125.3*sc, yd - 44, '149.5', C))
    # detail A marker on the top foot
    o.append(circle(cx + 50*sc, yt + 45, 120, C, 1.2, dash='10 5'))
    o.append(line(cx + 50*sc + 85, yt + 45 - 85, cx + 50*sc + 170, yt + 45 - 150, C, 1.2))
    o.append(text(cx + 50*sc + 178, yt + 45 - 150 + 7, 'A', C, 26, weight='bold'))
    o.append(text(cx, cy + R_TIP*sc + 96, 'FRONT VIEW  1.5:1', C, 22, 'middle'))
    o.append(text(cx, cy + R_TIP*sc + 122, '6&#215; &#955;  EQ. SP. ON &#8960;501.4  ROTATE ABOUT C', C, 17, 'middle', fill=C['line']))
    o.append('</g>')

    # ---- detail A ---------------------------------------------------------
    dx, dy, ds = 1620, 400, 3.4
    ox, oy = dx - 50*ds, dy + (FOOT_Y - 12)*ds   # place the top foot region in the circle
    o.append(f'<g id="detailA">')
    o.append(f'<g clip-path="url(#detA)">')
    o.append(f'<rect x="{dx-240}" y="{dy-240}" width="480" height="480" fill="{C["bg"]}"/>')
    o.append(f'<rect x="{dx-240}" y="{dy-240}" width="480" height="480" fill="url(#grid)"/>')
    o.append(flake(ox, oy, ds, C))
    o.append('</g>')
    o.append(circle(dx, dy, 230, C, 1.5))
    fy = oy - FOOT_Y*ds
    # notch depth 56.6, chamfer 28.5 @ 60°, foot flat reference
    o.append(vdim(fy, oy - 160.6*ds, dx + 230 + 40, '56.6', C, ext_from=ox + 64.6*ds))
    xch = ox + 125.3*ds
    o.append(line(xch, fy, xch + 90, fy, C, .9, col=C['faint']))
    o.append(arc(xch, fy, 70, 0, 60, C))
    o.append(text(xch + 92, fy + 48, '60&#176;', C, 20))
    o.append(leader(ox + 132.5*ds, oy - 204.8*ds, ox + 165*ds, oy - 215*ds, ox + 190*ds, '28.5 CHAMFER', C))
    o.append(hdim(ox + 32.0*ds, ox + 97.4*ds, fy - 40, '65.4 NOTCH', C, ext_from=fy))
    o.append(text(dx, dy + 300, 'DETAIL A  3.4:1', C, 22, 'middle'))
    o.append(text(dx, dy + 326, 'FOOT, NOTCH AND CHAMFER, TYP. 6 PL.', C, 17, 'middle'))
    o.append('</g>')

    # ---- view B: single lambda ---------------------------------------------
    bx, by, bs = 2120, 820, 1.15
    o.append('<g id="viewB">')
    up = L
    o.append(poly(up, bx, by, bs, fill=C['fill'], stroke=C['line'], stroke_width=2.2, stroke_linejoin='round'))
    o.append(circle(bx, by, 4, C, 1.5)); o.append(text(bx + 8, by + 22, 'C', C, 16))
    # leg length 244.4 (aligned dim along the long leg, offset to the left)
    p1 = (bx + 98.0*bs, by - 5.4*bs); p2 = (bx - 24.2*bs, by - 217.0*bs)
    nx, ny = -0.866, -0.5  # normal pointing away from the body (left/up)
    off = 90
    q1 = (p1[0] + nx*off, p1[1] + ny*off); q2 = (p2[0] + nx*off, p2[1] + ny*off)
    o.append(line(p1[0] + nx*6, p1[1] + ny*6, q1[0] + nx*12, q1[1] + ny*12, C, .9, col=C['faint']))
    o.append(line(p2[0] + nx*6, p2[1] + ny*6, q2[0] + nx*12, q2[1] + ny*12, C, .9, col=C['faint']))
    o.append(line(q1[0], q1[1], q2[0], q2[1], C, 1.2, marker=ARROWS))
    mx, my = (q1[0]+q2[0])/2 + nx*16, (q1[1]+q2[1])/2 + ny*16
    o.append(text(mx, my, '244.4', C, 20, 'middle', rotate=-60))
    # leg angle 60° to the foot flat
    fx, fy2 = bx - 24.2*bs, by - 217.0*bs
    o.append(line(fx, fy2, fx - 110, fy2, C, .9, col=C['faint']))
    o.append(arc(fx, fy2, 80, 120, 180, C))
    o.append(text(fx - 120, fy2 + 60, '60&#176;', C, 20, 'end'))
    # apex radius
    o.append(line(bx, by, bx + 98.0*bs, by - 5.4*bs, C, 1, dash='18 6 3 6', col=C['faint']))
    o.append(text(bx + 40*bs, by + 24, 'R97.8', C, 17))
    o.append(text(bx, by + 60, 'VIEW B  1.15:1', C, 22, 'middle'))
    o.append(text(bx, by + 86, '&#955; ELEMENT, 9 VERTICES, QTY 6', C, 17, 'middle'))
    o.append('</g>')

    # ---- bottom band: notes, flake spec, title block --------------------------
    yb = 1150
    o.append(line(48, yb, W-48, yb, C, 2))
    # notes
    notes = ['NOTES', '1. ALL DIMENSIONS IN px, ARTWORK UNITS (viewBox 501.56). SCALE AS NOTED.',
             '2. &#955; ELEMENT IDENTICAL 6 PL. PATTERN BY ROTATION ABOUT C, 60&#176; PITCH.',
             '3. APEX OF EACH &#955; SITS 3&#176; BEHIND ITS TIP CENTRELINE. THIS IS INTENTIONAL.',
             '4. TOLERANCES PER flake.lock. UNPINNED INPUTS REJECTED AT INSPECTION.',
             '5. FINISH: REPRODUCIBLE. IDENTICAL OUTPUT FOR IDENTICAL INPUTS, ANY HOST.',
             '6. DO NOT SCALE DRAWING. DO NOT nix-collect-garbage WHILE IN SERVICE.']
    for i, n in enumerate(notes):
        o.append(text(70, yb + 34 + i*30, n, C, 19 if i else 20, weight='bold' if i == 0 else 'normal'))
    o.append(line(1000, yb, 1000, H-48, C, 2))
    # spec: flake schema as a parts list
    o.append(text(1020, yb + 34, 'PARTS LIST  flake.nix', C, 20, weight='bold'))
    rows = [('ITEM', 'QTY', 'PART', 'SPEC'),
            ('1', '1', 'description', 'string'),
            ('2', 'n', 'inputs.&lt;name&gt;', 'url + flake.lock rev'),
            ('3', '1', 'outputs', 'fn { self, inputs.. }'),
            ('4', '6', '&#955;', 'per VIEW B'),
            ('5', '1', 'flake.lock', 'narHash pinned')]
    for i, r in enumerate(rows):
        y = yb + 64 + i*28
        for j, (col, w) in enumerate(zip(r, (60, 60, 200, 280))):
            o.append(text(1020 + sum((60, 60, 200, 280)[:j]), y, col, C, 17, weight='bold' if i == 0 else 'normal'))
        if i == 0: o.append(line(1020, y + 8, 1640, y + 8, C, 1))
    o.append(line(1660, yb, 1660, H-48, C, 2))
    # title block
    tx = 1680
    o.append(text(tx, yb + 40, 'NIX FLAKE', C, 38, weight='bold'))
    o.append(text(tx, yb + 68, 'SNOWFLAKE, 6&#215; &#955;, ROTATIONAL PATTERN', C, 19))
    o.append(line(tx, yb + 84, W-60, yb + 84, C, 1))
    cells = [('DWG NO', 'NIX-&#955;6-501'), ('REV', '2.4'), ('SHEET', '1 / 1'),
             ('SCALE', '1.5:1 MAIN'), ('UNITS', 'px'), ('SIZE', '2560&#215;1440'),
             ('DRAWN', 'elsirion'), ('DATE', '2026-09-19'), ('CHECKED', 'nix flake check')]
    for i, (k, v) in enumerate(cells):
        col, row = i % 3, i // 3
        x = tx + col*280; y = yb + 108 + row*50
        o.append(text(x, y, k, C, 13, fill=C['line']))
        o.append(text(x, y + 24, v, C, 21))
    o.append(text(1020, H - 60, 'SOURCE GEOMETRY: nixos-artwork/logo/nix-snowflake  &#183;  CC-BY 4.0', C, 12, 'start', fill=C['line']))
    o.append('</svg>')
    return '\n'.join(o)

if __name__ == '__main__' and '--minimal' not in sys.argv:
    scheme = sys.argv[1] if len(sys.argv) > 1 else 'amber'
    sys.stdout.write(build(scheme))


# ---------------------------------------------------------------------------
# Minimal sheet: flake centred, a few dimensions, thin bottom band. The title
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

if __name__ == '__main__' and '--minimal' in sys.argv:
    for a in sys.argv[1:]:
        if a.startswith('--size='):
            W, H = (int(x) for x in a[7:].split('x'))
    scheme = [a for a in sys.argv[1:] if not a.startswith('--')][0]
    sys.stdout.write(build_minimal(scheme))
    sys.exit(0)
