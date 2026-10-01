"""Generate assets/hero.svg — the Van Gogh painting with a name plaque attached.

Usage: python3 scripts/gen_hero.py > assets/hero.svg

The cyclist version of the painting (gen_starry_nav.py) sits on top; a
night-blue enamel plaque with gold inlay overlaps its bottom edge. The
background is transparent so it sits on GitHub's light or dark theme. Text is
outlined from Playfair Display (see svgtext.py), so it renders the same
everywhere.
"""
import os, random, re, subprocess, sys

from svgtext import text_path

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = "Hong-Son (Saun) Nguyen"
TAGLINE = "Robotics · Artificial Intelligence · Social Intelligence"
AFFILIATION = ["M.S. Researcher @ National Cheng Kung University (NCKU), Taiwan",
               "Networked Robotic Systems Lab (NRSL)"]

PW, PH = 860, 280                     # painting
PL_W, PL_H = 520, 106                 # plaque
OVERLAP = 12                          # how far the plaque rides up over the painting
X, Y = (PW - PL_W) / 2, PH - OVERLAP
W, H = PW, Y + PL_H + 16

GOLD = "#E8C547"


def f1(v):
    s = f"{v:.1f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def painting():
    svg = subprocess.run([sys.executable, os.path.join(HERE, "gen_starry_nav.py"), "--cyclist"],
                         check=True, capture_output=True, text=True).stdout
    svg = re.sub(r"<title.*?</desc>\n", "", svg, flags=re.S)
    # inline as a group (not a nested <svg>) so it shares this document's animation timeline
    return re.sub(r"<svg [^>]*>", "<g>", svg, count=1).replace("</svg>", "</g>")


def soft_shadow(x, y, w, h, spread, steps=8, alpha=.05, rx=6):
    out = []
    for k in range(steps):
        g = spread * (k + 1) / steps
        out.append(f'<rect x="{f1(x - g)}" y="{f1(y - g * .4)}" width="{f1(w + 2 * g)}" height="{f1(h + 2 * g)}" '
                   f'rx="{f1(rx + g)}" fill="#000" fill-opacity="{alpha}"/>')
    return "".join(reversed(out))


def brush_tile():
    """Seamless tile of short night-blue brush dabs for the enamel."""
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


def inlaid(d, fill, key, shadow=.7):
    return (f'<defs><path id="txt_{key}" d="{d}"/></defs>'
            f'<use href="#txt_{key}" fill="#050B18" fill-opacity="{shadow}" transform="translate(0 1.2)"/>'
            f'<use href="#txt_{key}" fill="{fill}"/>')


cx = W / 2
name = text_path("playfair-display-latin-700-normal", NAME, 30, cx, Y + 37, tracking=.5)
tag = text_path("playfair-display-latin-400-italic", TAGLINE, 14.5, cx, Y + 58, tracking=.3)
aff = [text_path("playfair-display-latin-400-normal", line, 11, cx, Y + 79 + 14 * i, tracking=.35)
       for i, line in enumerate(AFFILIATION)]

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {f1(H)}" width="{W}" height="{f1(H)}" role="img" aria-labelledby="t d">
<title id="t">{NAME} — {TAGLINE}</title>
<desc id="d">A Van Gogh–style animated painting: under a swirling starry sky a small robot crosses a lamp-lit plaza, predicting where people will walk and making room for an oncoming cyclist. A night-blue plaque with gold lettering below reads "{NAME} — {TAGLINE} — {", ".join(AFFILIATION)}".</desc>
<defs>
  <linearGradient id="plaqueBg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1A3570"/><stop offset="1" stop-color="#0B1838"/></linearGradient>
  <linearGradient id="plaqueBevel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".14"/><stop offset=".22" stop-color="#fff" stop-opacity="0"/><stop offset=".8" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".35"/></linearGradient>
  <linearGradient id="goldText" x1="0" y1="{f1(Y + 14)}" x2="0" y2="{f1(Y + 40)}" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#FFF6C8"/><stop offset=".55" stop-color="#F4D35E"/><stop offset="1" stop-color="#D9A93A"/></linearGradient>
  <linearGradient id="glint" gradientUnits="userSpaceOnUse" x1="-200" y1="0" x2="0" y2="60">
    <stop offset="0" stop-color="#FFF2B0" stop-opacity="0"/><stop offset=".5" stop-color="#FFF2B0" stop-opacity=".22"/><stop offset="1" stop-color="#FFF2B0" stop-opacity="0"/>
    <animate attributeName="x1" values="-200;-200;{W + 200};{W + 200}" keyTimes="0;.55;.85;1" dur="7s" repeatCount="indefinite"/>
    <animate attributeName="x2" values="0;0;{W + 400};{W + 400}" keyTimes="0;.55;.85;1" dur="7s" repeatCount="indefinite"/>
  </linearGradient>
  {brush_tile()}
</defs>
{painting()}
<g fill="none" stroke-linecap="round">
  {soft_shadow(X, Y + 3, PL_W, PL_H, 10, alpha=.03)}
  <rect x="{f1(X)}" y="{Y}" width="{PL_W}" height="{PL_H}" rx="6" fill="url(#plaqueBg)"/>
  <rect x="{f1(X)}" y="{Y}" width="{PL_W}" height="{PL_H}" rx="6" fill="url(#enamel)" fill-opacity=".45"/>
  <rect x="{f1(X)}" y="{Y}" width="{PL_W}" height="{PL_H}" rx="6" fill="url(#plaqueBevel)"/>
  <rect x="{f1(X + .6)}" y="{Y + .6}" width="{PL_W - 1.2}" height="{PL_H - 1.2}" rx="5.5" stroke="#0A1328" stroke-width="1.2"/>
  <rect x="{f1(X + 5)}" y="{Y + 5}" width="{PL_W - 10}" height="{PL_H - 10}" rx="3" stroke="{GOLD}" stroke-opacity=".85" stroke-width="1"/>
  <rect x="{f1(X + 8)}" y="{Y + 8}" width="{PL_W - 16}" height="{PL_H - 16}" rx="2" stroke="{GOLD}" stroke-opacity=".4" stroke-width=".6"/>
  {star(X + 17, Y + 17, 4.5, 2.4, .2)}{star(X + PL_W - 17, Y + 17, 4.5, 2.9, 1.1)}{star(X + 17, Y + PL_H - 17, 4.5, 3.1, 1.7)}{star(X + PL_W - 17, Y + PL_H - 17, 4.5, 2.6, .6)}
  {inlaid(name, "url(#goldText)", "name")}
  {inlaid(tag, "#A9C7E8", "tag", .6)}
  {inlaid(aff[0], "#C9DAEE", "aff0", .55)}
  {inlaid(aff[1], "#C9DAEE", "aff1", .55)}
  <rect x="{f1(X)}" y="{Y}" width="{PL_W}" height="{PL_H}" rx="6" fill="url(#glint)"/>
</g>
</svg>
'''
sys.stdout.write(svg)
