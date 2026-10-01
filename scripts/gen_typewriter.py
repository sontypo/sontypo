"""Generate assets/typewriter.svg — rotating taglines typed on an old typewriter.

Usage: python3 scripts/gen_typewriter.py > assets/typewriter.svg

Each character strikes with a small jolt and a gold flash that settles to
cream, at an uneven human rhythm; finished lines are backspaced away. Glyphs
are outlined from Special Elite (see svgtext.py) and defined once, then reused.
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
SX, SY, SW, SH = 2, 6, 856, 48        # strip, flush with the painting above
BASELINE = SY + SH / 2 + 6.5
GOLD, CREAM, FLASH = "#E8C547", "#F2EBC9", "#FFE27A"


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
            f'<animate attributeName="fill" values="{FLASH};{FLASH};{CREAM};{CREAM}" keyTimes="0;{kt(a)};{kt(a3)};1" '
            f'dur="{T:.2f}s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="translate" values="0 -2.2;0 -2.2;0 0;0 0" '
            f'keyTimes="0;{kt(a)};{kt(a2)};1" dur="{T:.2f}s" repeatCount="indefinite"/></use>')


letters = "".join(char_el(c, x, a, e) for c, x, a, e in chars if c != " ")

caret.sort(key=lambda p: p[0])
caret_x = ";".join(f1(x + 1) for _, x in caret)
caret_k = ";".join(kt(tt) for tt, _ in caret)


def brush_tile():
    r = random.Random(1890)
    tw, th = 120, 30
    dabs = []
    for y in range(3, th, 6):
        for x in range(0, tw, 12):
            xx, yy = x + r.uniform(-4, 4), y + r.uniform(-1.5, 1.5)
            c = r.choice(["#1F4386", "#2A5599", "#3767AE", "#16306A"])
            q = f1(r.uniform(-2, 2))
            for ox in (-tw, 0, tw):
                for oy in (-th, 0, th):
                    if -11 < xx + ox < tw + 1 and -3 < yy + oy < th + 3:
                        dabs.append(f'<path d="M{f1(xx + ox)} {f1(yy + oy)}q4.5 {q} 9 0" stroke="{c}"/>')
    return (f'<pattern id="enamel" width="{tw}" height="{th}" patternUnits="userSpaceOnUse">'
            f'<g fill="none" stroke-width="2.4" stroke-linecap="round">{"".join(dabs)}</g></pattern>')


def star(x, y, r, dur, delay):
    k = r * .16
    return (f'<path transform="translate({f1(x)} {f1(y)})" d="M0 {-r}Q{k:.2f} {-k:.2f} {r} 0Q{k:.2f} {k:.2f} 0 {r}'
            f'Q{-k:.2f} {k:.2f} {-r} 0Q{-k:.2f} {-k:.2f} 0 {-r}Z" fill="#F4D35E">'
            f'<animate attributeName="opacity" values="1;.35;1" dur="{dur}s" begin="-{delay}s" repeatCount="indefinite"/></path>')


load(FONT)
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t">
<title id="t">{" / ".join(LINES)}</title>
<defs>
  <linearGradient id="stripBg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1A3570"/><stop offset="1" stop-color="#0B1838"/></linearGradient>
  <linearGradient id="stripBevel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".12"/><stop offset=".3" stop-color="#fff" stop-opacity="0"/><stop offset=".8" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".3"/></linearGradient>
  {brush_tile()}
  {glyph_defs}
</defs>
<rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="10" fill="url(#stripBg)"/>
<rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="10" fill="url(#enamel)" fill-opacity=".4"/>
<rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="10" fill="url(#stripBevel)"/>
<rect x="{SX + .6}" y="{SY + .6}" width="{SW - 1.2}" height="{SH - 1.2}" rx="9.5" fill="none" stroke="#0A1328" stroke-width="1.2"/>
<rect x="{SX + 4.5}" y="{SY + 4.5}" width="{SW - 9}" height="{SH - 9}" rx="6.5" fill="none" stroke="{GOLD}" stroke-opacity=".75" stroke-width=".9"/>
{star(SX + 18, SY + SH / 2, 4.5, 2.6, .4)}{star(SX + SW - 18, SY + SH / 2, 4.5, 3.1, 1.3)}
<g fill="{CREAM}">{letters}</g>
<rect y="{f1(BASELINE - 16)}" width="2" height="19" rx="1" fill="{GOLD}">
  <animate attributeName="x" calcMode="discrete" values="{caret_x}" keyTimes="{caret_k}" dur="{T:.2f}s" repeatCount="indefinite"/>
  <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.55;1" dur="1s" repeatCount="indefinite"/>
</rect>
</svg>
'''
sys.stdout.write(svg)
