"""Generate assets/typewriter.svg — a letterhead page being typed on.

Usage: python3 scripts/gen_typewriter.py > assets/typewriter.svg

A sheet of cream paper with deckled edges: the name, tagline and affiliation
are printed as a letterhead (Playfair Display), and below a star-ornamented
rule rotating taglines are typed on an old typewriter (Special Elite). Each
character strikes with a small jolt in fresh blue ink that dries darker, at an
uneven human rhythm; finished lines are backspaced away.
"""
import random, sys

from svgtext import glyph, load, text_path

NAME = "Hong-Son (Saun) Nguyen"
TAGLINE = "Robotics · Artificial Intelligence · Social Intelligence"
AFFILIATION = ["M.S. Researcher @ National Cheng Kung University (NCKU), Taiwan",
               "Networked Robotic Systems Lab (NRSL)"]
LINES = [
    "Building robots that understand people — not just obstacles.",
    "Social Robot Navigation · Human–Robot Interaction",
    "Trajectory Prediction with Graphs + State-Space Models",
    "Social Behavior-Aware Robot Navigation via RL Policy",
]
FONT = "special-elite-latin-400-normal"
SIZE = 19

W, H = 860, 178
SX, SY, SW, SH = 2, 4, 856, 166       # the sheet, as wide as the painting above
RULE_Y = SY + 116
BASELINE = SY + 147                   # typed line
INK, FRESH, RIBBON = "#22263A", "#2A5599", "#B8432E"   # dried ink, wet ink, red ribbon caret
NAVY, BLUE, GRAPHITE, GOLD = "#13295A", "#2A5599", "#4A5068", "#C9962E"


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


# ---------------------------------------------------------------- paper
def paper_path():
    """Deckled sheet: gently uneven top and bottom, torn left and right ends."""
    r = random.Random(1888)
    x0, y0, x1, y1 = SX + 4, SY + 1, SX + SW - 4, SY + SH - 1
    pts = []
    x = x0
    while x < x1:                                   # top, left to right
        pts.append((x, y0 + r.uniform(-1.1, 1.1)))
        x += r.uniform(5, 11)
    y = y0
    while y < y1:                                   # right end, torn
        pts.append((x1 + r.uniform(-2.5, 3), y))
        y += r.uniform(2, 5)
    x = x1
    while x > x0:                                   # bottom, right to left
        pts.append((x, y1 + r.uniform(-1.1, 1.1)))
        x -= r.uniform(5, 11)
    y = y1
    while y > y0:                                   # left end, torn
        pts.append((x0 - r.uniform(-2.5, 3), y))
        y -= r.uniform(2, 5)
    return "M" + "L".join(f"{f1(px)} {f1(py)}" for px, py in pts) + "Z"


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


def star(x, y, r):
    k = r * .16
    return (f'<path transform="translate({f1(x)} {f1(y)})" d="M0 {-r}Q{k:.2f} {-k:.2f} {r} 0Q{k:.2f} {k:.2f} 0 {r}'
            f'Q{-k:.2f} {k:.2f} {-r} 0Q{-k:.2f} {-k:.2f} 0 {-r}Z" fill="#F4D35E" stroke="#B8862F" stroke-width=".6">'
            f'<animate attributeName="opacity" values="1;.4;1" dur="2.8s" repeatCount="indefinite"/></path>')


def letterhead():
    cx = W / 2

    def printed(font, text, size, baseline, tracking):
        # outlined at 4x with whole-unit coordinates, then scaled down (0.25px accuracy)
        return text_path(font, text, size * 4, cx * 4, baseline * 4, tracking * 4, coarse=True)
    name = printed("playfair-display-latin-700-normal", NAME, 30, SY + 40, .5)
    tag = printed("playfair-display-latin-400-italic", TAGLINE, 15, SY + 63, .3)
    aff = [printed("playfair-display-latin-400-normal", line, 11.5, SY + 84 + 14.5 * i, .35)
           for i, line in enumerate(AFFILIATION)]
    half = 130
    return (f'<g transform="scale(.25)"><path d="{name}" fill="{NAVY}" fill-opacity=".95"/>'
            f'<path d="{tag}" fill="{BLUE}" fill-opacity=".95"/>'
            + "".join(f'<path d="{d}" fill="{GRAPHITE}"/>' for d in aff) + '</g>'
            + f'<path d="M{f1(cx - half)} {RULE_Y}H{f1(cx - 14)}M{f1(cx + 14)} {RULE_Y}H{f1(cx + half)}" '
              f'stroke="{INK}" stroke-opacity=".45" stroke-width=".8"/>'
            + f'<circle cx="{f1(cx - half)}" cy="{RULE_Y}" r="1.2" fill="{INK}" fill-opacity=".45"/>'
              f'<circle cx="{f1(cx + half)}" cy="{RULE_Y}" r="1.2" fill="{INK}" fill-opacity=".45"/>'
            + star(cx, RULE_Y, 6))


load(FONT)
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t">
<title id="t">{NAME} — {TAGLINE} — {", ".join(AFFILIATION)}. {" / ".join(LINES)}</title>
<defs>
  <linearGradient id="paper" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FBF5E4"/><stop offset="1" stop-color="#EFE4C6"/></linearGradient>
  <linearGradient id="paperShade" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#A08655" stop-opacity=".16"/><stop offset=".05" stop-color="#A08655" stop-opacity="0"/><stop offset=".95" stop-color="#A08655" stop-opacity="0"/><stop offset="1" stop-color="#A08655" stop-opacity=".16"/></linearGradient>
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
{letterhead()}
<g fill="{INK}">{letters}</g>
<rect y="{f1(BASELINE - 16)}" width="2" height="19" rx="1" fill="{RIBBON}">
  <animate attributeName="x" calcMode="discrete" values="{caret_x}" keyTimes="{caret_k}" dur="{T:.2f}s" repeatCount="indefinite"/>
  <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.55;1" dur="1s" repeatCount="indefinite"/>
</rect>
</svg>
'''
sys.stdout.write(svg)
