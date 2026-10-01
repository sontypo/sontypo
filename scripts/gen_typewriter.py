"""Generate assets/typewriter.svg — rotating taglines typed on an old typewriter.

Usage: python3 scripts/gen_typewriter.py > assets/typewriter.svg

Typed onto a strip of cream paper with torn ends. Each character strikes with
a small jolt in fresh blue-black ink that dries darker, at an uneven human
rhythm; finished lines are backspaced away. Glyphs are outlined from Special
Elite (see svgtext.py) and defined once, then reused.
"""
import random, sys

from svgtext import glyph, load

LINES = [
    "Building robots that understand people — not just obstacles.",
    "Social Robot Navigation · Human–Robot Interaction",
    "Trajectory Prediction with Graphs + State-Space Models",
    "Social Behavior-Aware Robot Navigation via RL Policy",
]
FONT = "special-elite-latin-400-normal"
SIZE = 19

W, H = 860, 60
SX, SY, SW, SH = 2, 6, 856, 48        # paper strip, flush with the painting above
BASELINE = SY + SH / 2 + 6.5
INK, FRESH, RIBBON = "#22263A", "#2A5599", "#B8432E"   # dried ink, wet ink, red ribbon caret


def f1(v):
    s = f"{v:.1f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def kt(t):
    return f"{t / T:.4f}".rstrip("0").rstrip(".") or "0"


# ---------------------------------------------------------------- timeline
rng = random.Random(1888)
t = 0.5
chars = []            # (char, x, appear, erase)
caret = [(0.0, None)]  # (time, x)
for line in LINES:
    width = sum(glyph(FONT, c, SIZE)[1] for c in line)
    x0 = W / 2 - width / 2
    if caret[0][1] is None:
        caret[0] = (0.0, x0)
    caret.append((t, x0))
    x, placed = x0, []
    for c in line:
        t += min(.16, max(.045, rng.gauss(.075, .022)))
        if rng.random() < .05:
            t += rng.uniform(.15, .3)          # a hesitation
        adv = glyph(FONT, c, SIZE)[1]
        placed.append([c, x, t, None])
        x += adv
        caret.append((t, x))
        if c in ".,—·–":
            t += .12
    t += 1.9                                     # read it
    for p in reversed(placed):
        t += .026
        p[3] = t
        caret.append((t, p[1]))
    chars += placed
    t += .45
T = t

# ---------------------------------------------------------------- glyphs
uniq = sorted({c for c, *_ in chars if c != " "})
gid = {c: f"g{i}" for i, c in enumerate(uniq)}
# glyphs are drawn at 4x and scaled down, so whole-unit rounding keeps 0.25px accuracy
glyph_defs = "".join(f'<path id="{gid[c]}" d="{glyph(FONT, c, SIZE * 4, coarse=True)[0]}" transform="scale(.25)"/>'
                     for c in uniq)


def char_el(c, x, a, e):
    ink = rng.uniform(.82, 1.0)
    dy = rng.uniform(-.6, .6)
    a2, a3 = min(a + .07, e - .01), min(a + .22, e - .01)
    return (f'<use href="#{gid[c]}" x="{f1(x)}" y="{f1(BASELINE + dy)}" opacity="0" fill-opacity="{ink:.2f}">'
            f'<animate attributeName="opacity" calcMode="discrete" values="0;1;0" keyTimes="0;{kt(a)};{kt(e)}" '
            f'dur="{T:.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="fill" values="{FRESH};{FRESH};{INK};{INK}" keyTimes="0;{kt(a)};{kt(a3)};1" '
            f'dur="{T:.2f}s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="translate" values="0 -2.2;0 -2.2;0 0;0 0" '
            f'keyTimes="0;{kt(a)};{kt(a2)};1" dur="{T:.2f}s" repeatCount="indefinite"/></use>')


letters = "".join(char_el(c, x, a, e) for c, x, a, e in chars if c != " ")

caret.sort(key=lambda p: p[0])
caret_x = ";".join(f1(x + 1) for _, x in caret)
caret_k = ";".join(kt(tt) for tt, _ in caret)


def torn_edge(x, top, bottom, sign, r):
    """Jagged vertical edge; sign=-1 for the left end, +1 for the right."""
    pts, y = [], top
    while y < bottom:
        pts.append((x + sign * r.uniform(-3, 2.5), y))
        y += r.uniform(2, 5)
    pts.append((x + sign * r.uniform(-3, 2.5), bottom))
    return pts


def paper_path():
    r = random.Random(1888)
    left = torn_edge(SX + 4, SY, SY + SH, -1, r)
    right = torn_edge(SX + SW - 4, SY, SY + SH, 1, r)
    pts = right + list(reversed(left))
    return "M" + "L".join(f"{f1(x)} {f1(y)}" for x, y in pts) + "Z"


def fibres():
    """Seamless tile of paper fibres and speckles."""
    r = random.Random(1890)
    tw, th = 96, 48
    out = []
    for _ in range(46):
        x, y = r.uniform(0, tw), r.uniform(0, th)
        ln, ang = r.uniform(2, 6), r.uniform(-.6, .6)
        c = r.choice(["#D9CBA6", "#E2D5B4", "#FFFFFF", "#CDBF99"])
        out.append(f'<path d="M{f1(x)} {f1(y)}l{f1(ln)} {f1(ln * ang)}" stroke="{c}" stroke-width=".7"/>')
    for _ in range(22):
        out.append(f'<circle cx="{f1(r.uniform(0, tw))}" cy="{f1(r.uniform(0, th))}" r=".45" '
                   f'fill="{r.choice(["#BFAF88", "#A89A78"])}"/>')
    return (f'<pattern id="fibres" width="{tw}" height="{th}" patternUnits="userSpaceOnUse">'
            f'<g fill="none" stroke-linecap="round" opacity=".7">{"".join(out)}</g></pattern>')


load(FONT)
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t">
<title id="t">{" / ".join(LINES)}</title>
<defs>
  <linearGradient id="paper" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FBF5E4"/><stop offset="1" stop-color="#EFE4C6"/></linearGradient>
  <linearGradient id="paperShade" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#A08655" stop-opacity=".18"/><stop offset=".06" stop-color="#A08655" stop-opacity="0"/><stop offset=".94" stop-color="#A08655" stop-opacity="0"/><stop offset="1" stop-color="#A08655" stop-opacity=".18"/></linearGradient>
  {fibres()}
  <path id="sheet" d="{paper_path()}"/>
  {glyph_defs}
</defs>
<g fill="#000">
  <use href="#sheet" fill-opacity=".05" transform="translate(0 3)"/>
  <use href="#sheet" fill-opacity=".05" transform="translate(0 1.5)"/>
</g>
<use href="#sheet" fill="url(#paper)"/>
<use href="#sheet" fill="url(#fibres)"/>
<use href="#sheet" fill="url(#paperShade)"/>
<use href="#sheet" fill="none" stroke="#D6C79F" stroke-width=".8"/>
<g fill="{INK}">{letters}</g>
<rect y="{f1(BASELINE - 16)}" width="2" height="19" rx="1" fill="{RIBBON}">
  <animate attributeName="x" calcMode="discrete" values="{caret_x}" keyTimes="{caret_k}" dur="{T:.2f}s" repeatCount="indefinite"/>
  <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.55;1" dur="1s" repeatCount="indefinite"/>
</rect>
</svg>
'''
sys.stdout.write(svg)
