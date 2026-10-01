"""Generate the Van Gogh–themed link buttons in assets/links/.

Usage: python3 scripts/gen_link_buttons.py

Icons: GitHub, LinkedIn and Globe from Bootstrap Icons (MIT, © The Bootstrap
Authors); Google Scholar from Simple Icons (CC0).
"""
import math, os, random

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "links")
W, H = 216, 56

BUTTONS = [
    ("portfolio", "Portfolio", "sontypo.github.io", 16,
     "M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8m7.5-6.923c-.67.204-1.335.82-1.887 1.855q-.215.403-.395.872c.705.157 1.472.257 2.282.287zM4.249 3.539q.214-.577.481-1.078a7 7 0 0 1 .597-.933A7 7 0 0 0 3.051 3.05q.544.277 1.198.49zM3.509 7.5c.036-1.07.188-2.087.436-3.008a9 9 0 0 1-1.565-.667A6.96 6.96 0 0 0 1.018 7.5zm1.4-2.741a12.3 12.3 0 0 0-.4 2.741H7.5V5.091c-.91-.03-1.783-.145-2.591-.332M8.5 5.09V7.5h2.99a12.3 12.3 0 0 0-.399-2.741c-.808.187-1.681.301-2.591.332zM4.51 8.5c.035.987.176 1.914.399 2.741A13.6 13.6 0 0 1 7.5 10.91V8.5zm3.99 0v2.409c.91.03 1.783.145 2.591.332.223-.827.364-1.754.4-2.741zm-3.282 3.696q.18.469.395.872c.552 1.035 1.218 1.65 1.887 1.855V11.91c-.81.03-1.577.13-2.282.287zm.11 2.276a7 7 0 0 1-.598-.933 9 9 0 0 1-.481-1.079 8.4 8.4 0 0 0-1.198.49 7 7 0 0 0 2.276 1.522zm-1.383-2.964A13.4 13.4 0 0 1 3.508 8.5h-2.49a6.96 6.96 0 0 0 1.362 3.675c.47-.258.995-.482 1.565-.667m6.728 2.964a7 7 0 0 0 2.275-1.521 8.4 8.4 0 0 0-1.197-.49 9 9 0 0 1-.481 1.078 7 7 0 0 1-.597.933M8.5 11.909v3.014c.67-.204 1.335-.82 1.887-1.855q.216-.403.395-.872A12.6 12.6 0 0 0 8.5 11.91zm3.555-.401c.57.185 1.095.409 1.565.667A6.96 6.96 0 0 0 14.982 8.5h-2.49a13.4 13.4 0 0 1-.437 3.008M14.982 7.5a6.96 6.96 0 0 0-1.362-3.675c-.47.258-.995.482-1.565.667.248.92.4 1.938.437 3.008zM11.27 2.461q.266.502.482 1.078a8.4 8.4 0 0 0 1.196-.49 7 7 0 0 0-2.275-1.52c.218.283.418.597.597.932m-.488 1.343a8 8 0 0 0-.395-.872C9.835 1.897 9.17 1.282 8.5 1.077V4.09c.81-.03 1.577-.13 2.282-.287z"),
    ("github", "GitHub", "@sontypo", 16,
     "M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8"),
    ("scholar", "Google Scholar", "Publications", 24,
     "M5.242 13.769L0 9.5 12 0l12 9.5-5.242 4.269C17.548 11.249 14.978 9.5 12 9.5c-2.977 0-5.548 1.748-6.758 4.269zM12 10a7 7 0 1 0 0 14 7 7 0 0 0 0-14z"),
    ("linkedin", "LinkedIn", "Let's connect", 16,
     "M0 1.146C0 .513.526 0 1.175 0h13.65C15.474 0 16 .513 16 1.146v13.708c0 .633-.526 1.146-1.175 1.146H1.175C.526 16 0 15.487 0 14.854zm4.943 12.248V6.169H2.542v7.225zm-1.2-8.212c.837 0 1.358-.554 1.358-1.248-.015-.709-.52-1.248-1.342-1.248S2.4 3.226 2.4 3.934c0 .694.521 1.248 1.327 1.248zm4.908 8.212V9.359c0-.216.016-.432.08-.586.173-.431.568-.878 1.232-.878.869 0 1.216.662 1.216 1.634v3.865h2.401V9.25c0-2.22-1.184-3.252-2.764-3.252-1.274 0-1.845.7-2.165 1.193v.025h-.016l.016-.025V6.169h-2.4c.03.678 0 7.225 0 7.225z"),
]

SKY = ["#1F4386", "#2A5599", "#3767AE", "#5B8BC9"]
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"


def brush_strokes(seed):
    """Short strokes flowing around a swirl on the right half of the button."""
    rng = random.Random(seed)
    cx, cy = 150, 30
    out = []
    for _ in range(46):
        x, y = rng.uniform(40, W + 4), rng.uniform(-2, H + 2)
        pts = [(x, y)]
        for _ in range(3):
            dx, dy = x - cx, y - cy
            r = math.hypot(dx, dy) or 1
            w = 1.6 * math.exp(-(r / 34) ** 2)
            vx, vy = 1 - dy / r * w, 0.2 * math.sin(x / 18) + dx / r * w
            n = math.hypot(vx, vy)
            x, y = x + vx / n * 4.5, y + vy / n * 4.5
            pts.append((x, y))
        d = f"M{pts[0][0]:.0f} {pts[0][1]:.0f}C" + " ".join(f"{px:.0f} {py:.0f}" for px, py in pts[1:])
        out.append(f'<path d="{d}" stroke="{rng.choice(SKY)}" stroke-width="{rng.uniform(2.2, 3.2):.1f}"/>')
    return "".join(out)


def button(key, title, subtitle, box, icon, seed):
    s = 19 / box   # icon scaled to ~19px
    off = 30 - box * s / 2
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{title}: {subtitle}">
<title>{title} — {subtitle}</title>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0E1E45"/><stop offset="1" stop-color="#1A3570"/></linearGradient>
  <radialGradient id="sun" cx=".4" cy=".35"><stop offset="0" stop-color="#FFF2B0"/><stop offset="1" stop-color="#E8C547"/></radialGradient>
  <radialGradient id="glow"><stop offset="0" stop-color="#F4D35E" stop-opacity=".45"/><stop offset="1" stop-color="#F4D35E" stop-opacity="0"/></radialGradient>
  <clipPath id="c"><rect width="{W}" height="{H}" rx="14"/></clipPath>
</defs>
<g clip-path="url(#c)" fill="none" stroke-linecap="round">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <g opacity=".55">{brush_strokes(seed)}</g>
  <circle cx="30" cy="28" r="27" fill="url(#glow)"/>
  <circle cx="30" cy="28" r="21" stroke="#F4D35E" stroke-opacity=".7" stroke-width="2" stroke-dasharray="4 4">
    <animateTransform attributeName="transform" type="rotate" from="0 30 28" to="360 30 28" dur="18s" repeatCount="indefinite"/>
  </circle>
  <circle cx="30" cy="28" r="16.5" fill="url(#sun)"/>
  <path transform="translate({off:.2f} {off - 2:.2f}) scale({s:.4f})" d="{icon}" fill="#0E1E45"/>
  <text x="60" y="26" font-family="{FONT}" font-size="15" font-weight="700" fill="#F2EBC9">{title}</text>
  <text x="60" y="42" font-family="{FONT}" font-size="11" fill="#A9C7E8">{subtitle}</text>
  <path d="M{W - 24} 34l7-7m-5 0h5v5" stroke="#F4D35E" stroke-width="1.8" stroke-linejoin="round"/>
  <g transform="translate({W - 14} 11)">
    <circle r="5" fill="url(#glow)"><animate attributeName="r" values="3;6;3" dur="{2.4 + seed * .37:.2f}s" repeatCount="indefinite"/></circle>
    <circle r="1.6" fill="#FFF2B0"/>
  </g>
</g>
<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="13.5" fill="none" stroke="#F4D35E" stroke-opacity=".45" stroke-width="1.5"/>
</svg>
'''


os.makedirs(OUT, exist_ok=True)
for n, (key, title, sub, box, icon) in enumerate(BUTTONS):
    with open(os.path.join(OUT, f"{key}.svg"), "w") as f:
        f.write(button(key, title, sub, box, icon, n + 1))
