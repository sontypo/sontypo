"""Generate assets/starry-nav.svg — human-aware navigation, after Van Gogh.

Usage: python3 scripts/gen_starry_nav.py > assets/starry-nav.svg
       python3 scripts/gen_starry_nav.py --cyclist > assets/starry-nav-cyclist.svg
       python3 scripts/gen_starry_nav.py --cyclist --frameless   (used by gen_hero.py)

Same robot/pedestrian simulation as gen_social_nav.py, re-staged as a night
plaza under a "Starry Night" sky: swirling brush-stroke vortices, haloed
stars, a swaying cypress and a lamp-lit square. The top-down simulation is
projected onto the ground plane with a simple perspective.
"""
import math, random, sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_social_nav  # noqa: E402
from gen_social_nav import (W, H, T, OFF, peds, STATIC, ped_pos, wrap_time,  # noqa: E402
                            robot_at, grid_times, f1, kt)

rng = random.Random(1889)

# optional oncoming cyclist: crosses once per loop (twice the walking span, so it
# spends the other half of the loop off-screen); the robot re-plans around it
CYCLIST = "--cyclist" in sys.argv
FRAMELESS = "--frameless" in sys.argv   # square corners, no border: for framing in gen_hero.py
if CYCLIST:
    peds.append(dict(id="c1", p0=(W + OFF, 168), v=(-2 * (W + 2 * OFF) / T, 0.0), phase=0.35))
    gen_social_nav.traj = gen_social_nav.simulate()
HORIZON = 178
N_KEY = 151

# Van Gogh palette
SKY = ["#0E1E45", "#13295A", "#1A3570", "#1F4386", "#2A5599", "#3767AE"]
SKY_L = ["#5B8BC9", "#7FA8D8", "#A9C7E8"]
CREAM = ["#F2EBC9", "#E9E4C9", "#DCE8F0"]
YELLOW = ["#F4D35E", "#E8C547", "#F7E7A1", "#FFF2B0"]
ORANGE = "#E89B2F"
GROUND = ["#1A3049", "#24425E", "#2E5470", "#1B2F4A", "#36607E", "#16263F"]
CYPRESS = ["#0B1A12", "#132A1A", "#1C3A24", "#24472B", "#3B5E2E", "#6B7F3A"]
GREEN = "#8BCC6A"

VORTICES = [(395, 80, 58, 1, 60), (538, 58, 36, -1, 44)]   # cx, cy, R, dir, period
STARS = [(158, 40, 8), (238, 116, 6), (272, 30, 5), (622, 126, 6),
         (668, 36, 8), (716, 96, 5), (318, 148, 4), (470, 150, 4)]
MOON = (796, 50, 20)


def i(v):
    return str(int(round(v)))


# ---------------------------------------------------------------- sky
def field(x, y):
    vx, vy = 1.0, 0.28 * math.sin(x / 55 + y / 33)
    for cx, cy, R, d, _ in VORTICES:
        dx, dy = x - cx, y - cy
        r = math.hypot(dx, dy) or 1
        w = 2.4 * math.exp(-((r - R) / (R * 0.75)) ** 2)
        vx += -dy / r * w * d + dx / r * w * 0.15
        vy += dx / r * w * d + dy / r * w * 0.15
    for sx, sy, sr in STARS + [MOON]:
        dx, dy = x - sx, y - sy
        r = math.hypot(dx, dy) or 1
        w = 1.6 * math.exp(-(r / (sr * 3.2)) ** 2)
        vx += -dy / r * w
        vy += dx / r * w
    n = math.hypot(vx, vy) or 1
    return vx / n, vy / n


def trace(x, y, steps=3, h=5.0):
    pts = [(x, y)]
    for _ in range(steps):
        ux, uy = field(x, y)
        x, y = x + ux * h, y + uy * h
        pts.append((x, y))
    return pts


def near_light(x, y):
    best = 99
    for sx, sy, sr in STARS + [MOON]:
        best = min(best, math.hypot(x - sx, y - sy) / sr)
    return best


def sky_strokes():
    out = []
    for gy in range(-4, HORIZON + 4, 8):
        for gx in range(-6, W + 6, 11):
            x, y = gx + rng.uniform(-4, 4), gy + rng.uniform(-3, 3)
            if any(math.hypot(x - cx, y - cy) < R + 1 for cx, cy, R, *_ in VORTICES):
                continue
            nl = near_light(x, y)
            if nl < 2.6:
                continue
            t = max(0.0, min(1.0, y / HORIZON))
            roll = rng.random()
            if nl < 5 and roll < 0.55:
                c = rng.choice(YELLOW[:3] + CREAM[:1])
            elif roll < 0.05:
                c = rng.choice(CREAM)
            elif roll < 0.30:
                c = rng.choice(SKY_L)
            else:
                lo = int(t * 3)
                c = SKY[min(len(SKY) - 1, lo + rng.randint(0, 2))]
            p = trace(x, y)
            out.append(f'<path d="M{i(p[0][0])} {i(p[0][1])}C{i(p[1][0])} {i(p[1][1])} '
                       f'{i(p[2][0])} {i(p[2][1])} {i(p[3][0])} {i(p[3][1])}" '
                       f'stroke="{c}" stroke-width="{rng.uniform(2.6, 3.8):.1f}"/>')
    return "".join(out)


def wind_ribbons():
    out = []
    for k, y0 in enumerate((22, 54, 100, 128, 158)):
        x, y = -20.0, float(y0)
        pts = [(x, y)]
        for _ in range(90):
            ux, uy = field(x, y)
            x, y = x + ux * 10, y + uy * 10
            pts.append((x, y))
            if x > W + 20:
                break
        d = "M" + " L".join(f"{i(px)} {i(py)}" for px, py in pts)
        c = CREAM[k % 3] if k % 2 == 0 else SKY_L[2]
        out.append(f'<path d="{d}" stroke="{c}" stroke-width="2.6" stroke-opacity=".55" '
                   f'stroke-dasharray="16 30" class="wind" style="animation-duration:{5 + k}s"/>')
    return "".join(out)


def vortex(cx, cy, R, d, period):
    strokes = []
    r = 5.0
    while r < R:
        n = max(4, int(2 * math.pi * r / 11))
        off = rng.uniform(0, 2 * math.pi)
        for j in range(n):
            a0 = off + j * 2 * math.pi / n
            a1 = a0 + min(0.9, 9.0 / r)
            x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
            x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
            fr = r / R
            roll = rng.random()
            if roll < 0.35 * (1 - fr) + 0.12:
                c = rng.choice(CREAM)
            elif roll < 0.7:
                c = rng.choice(SKY_L)
            else:
                c = rng.choice(SKY[3:])
            strokes.append(f'<path d="M{f1(x0)} {f1(y0)}A{f1(r)} {f1(r)} 0 0 1 {f1(x1)} {f1(y1)}" '
                           f'stroke="{c}" stroke-width="{rng.uniform(2.8, 4.0):.1f}"/>')
        r += 5.2
    # flowing spiral arm
    sp = []
    for k in range(160):
        a = k * 0.12
        rr = 4 + (R - 6) * k / 160
        sp.append((cx + rr * math.cos(a * d), cy + rr * math.sin(a * d)))
    spd = "M" + " L".join(f"{f1(x)} {f1(y)}" for x, y in sp)
    frm, to = (0, 360) if d > 0 else (360, 0)
    return (f'<g><animateTransform attributeName="transform" type="rotate" '
            f'from="{frm} {cx} {cy}" to="{to} {cx} {cy}" dur="{period}s" repeatCount="indefinite"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="url(#vortexBg)"/>'
            f'{"".join(strokes)}'
            f'<path d="{spd}" stroke="#FFF6DA" stroke-width="2.4" stroke-opacity=".75" '
            f'stroke-dasharray="12 9" class="wind" style="animation-duration:3s"/></g>')


def ring(cx, cy, r, color, width, dash, dur, rev=False):
    frm, to = (360, 0) if rev else (0, 360)
    return (f'<circle cx="{cx}" cy="{cy}" r="{f1(r)}" fill="none" stroke="{color}" '
            f'stroke-width="{width}" stroke-dasharray="{dash}" stroke-linecap="round">'
            f'<animateTransform attributeName="transform" type="rotate" '
            f'from="{frm} {cx} {cy}" to="{to} {cx} {cy}" dur="{dur}s" repeatCount="indefinite"/>'
            f'</circle>')


def star(cx, cy, s, k):
    dly = rng.uniform(0, 3)
    return (f'<g>'
            f'<circle cx="{cx}" cy="{cy}" r="{f1(s * 3.4)}" fill="url(#starGlow)">'
            f'<animate attributeName="r" values="{f1(s * 3.0)};{f1(s * 3.8)};{f1(s * 3.0)}" '
            f'dur="{3 + k % 3}s" begin="-{dly:.1f}s" repeatCount="indefinite"/></circle>'
            + ring(cx, cy, s * 2.7, SKY_L[1], 2.4, "3 6", 26 + k * 3, rev=k % 2 == 0)
            + ring(cx, cy, s * 2.0, YELLOW[1], 2.8, "5 4", 16 + k * 2, rev=k % 2 == 1)
            + ring(cx, cy, s * 1.35, YELLOW[2], 2.6, "4 3", 10 + k, rev=k % 2 == 0)
            + f'<circle cx="{cx}" cy="{cy}" r="{f1(s * 0.75)}" fill="#FFF8D6" stroke="{YELLOW[0]}" '
              f'stroke-width="1.5"><animate attributeName="fill-opacity" values="1;.7;1" '
              f'dur="{2 + k % 2}s" begin="-{dly:.1f}s" repeatCount="indefinite"/></circle></g>')


def moon():
    cx, cy, r = MOON
    crescent = (f'<path d="M{cx + r * 0.35} {cy - r * 0.94} A{r} {r} 0 1 0 {cx + r * 0.35} {cy + r * 0.94} '
                f'A{r * 0.8} {r * 0.8} 0 1 1 {cx + r * 0.35} {cy - r * 0.94}Z" fill="{YELLOW[0]}" '
                f'stroke="{ORANGE}" stroke-width="2"/>')
    return (f'<g><circle cx="{cx}" cy="{cy}" r="{r * 3}" fill="url(#moonGlow)">'
            f'<animate attributeName="r" values="{r * 2.8};{r * 3.3};{r * 2.8}" dur="5s" repeatCount="indefinite"/></circle>'
            + ring(cx, cy, r * 2.35, SKY_L[0], 3, "4 7", 40, rev=True)
            + ring(cx, cy, r * 1.85, ORANGE, 3.2, "7 5", 30)
            + ring(cx, cy, r * 1.4, YELLOW[1], 3.2, "6 4", 22, rev=True)
            + f'<circle cx="{cx}" cy="{cy}" r="{r * 1.08}" fill="{ORANGE}" fill-opacity=".22"/>'
            + crescent + '</g>')


# ---------------------------------------------------------------- land
def hills():
    def ridge(base, amp, freq, ph):
        pts = [(x, base - amp * (0.6 * math.sin(x / freq + ph) + 0.4 * math.sin(x / (freq * 0.37) + ph * 2)))
               for x in range(-10, W + 21, 20)]
        return pts

    out = []
    for base, amp, freq, ph, fill, stroke in ((160, 14, 120, 0.4, "#1F3D72", "#3A64A0"),
                                              (172, 9, 80, 2.1, "#172E57", "#2B5491")):
        pts = ridge(base, amp, freq, ph)
        d = "M" + " L".join(f"{x} {f1(y)}" for x, y in pts) + f" L{W + 20} {HORIZON + 6} L-10 {HORIZON + 6}Z"
        out.append(f'<path d="{d}" fill="{fill}"/>')
        for off in (4, 9):
            line = "M" + " L".join(f"{x} {f1(y + off)}" for x, y in pts)
            out.append(f'<path d="{line}" stroke="{stroke}" stroke-width="2.6" stroke-dasharray="9 7" '
                       f'stroke-dashoffset="{rng.randint(0, 15)}" stroke-opacity=".8"/>')
    return "".join(out)


def village():
    out = []
    x = 430
    while x < 790:
        w, h = rng.randint(14, 24), rng.randint(9, 16)
        base = HORIZON - 1 + rng.randint(-2, 2)
        roof = rng.randint(5, 9)
        out.append(f'<path d="M{x} {base}V{base - h}L{x + w / 2} {base - h - roof}L{x + w} {base - h}V{base}Z" '
                   f'fill="#14284A" stroke="#0A1328" stroke-width="1.4"/>')
        for _ in range(rng.randint(0, 2)):
            wx = x + rng.randint(3, w - 6)
            wy = base - rng.randint(4, h - 2)
            dur = rng.uniform(2.5, 6)
            out.append(f'<rect x="{wx}" y="{wy}" width="3.5" height="3.5" fill="{YELLOW[0]}">'
                       f'<animate attributeName="fill-opacity" values="1;.45;1;.9;1" dur="{dur:.1f}s" '
                       f'repeatCount="indefinite"/></rect>')
        x += w + rng.randint(2, 10)
        if 585 < x < 615:   # church
            out.append(f'<path d="M600 {HORIZON}V{HORIZON - 22}L607 {HORIZON - 52}L614 {HORIZON - 22}V{HORIZON}Z" '
                       f'fill="#14284A" stroke="#0A1328" stroke-width="1.6"/>'
                       f'<rect x="605" y="{HORIZON - 16}" width="4" height="6" fill="{YELLOW[1]}"/>')
            x = 620
    return "".join(out)


def ground_strokes():
    out = []
    for gy in range(HORIZON + 2, H + 6, 7):
        depth = (gy - HORIZON) / (H - HORIZON)
        step = int(10 + 8 * depth)
        for gx in range(-8, W + 8, step):
            x, y = gx + rng.uniform(-3, 3), gy + rng.uniform(-2, 2)
            ln = 7 + 9 * depth
            bend = rng.uniform(-2, 2)
            lamp = math.hypot((x - 742) / 1.0, (y - 262) * 3.5)
            if lamp < 110 and rng.random() < 0.7 * (1 - lamp / 110) + 0.1:
                c = rng.choice(YELLOW[:2] + ["#C9A240"])
            else:
                c = rng.choice(GROUND)
            out.append(f'<path d="M{i(x)} {i(y)}q{f1(ln / 2)} {f1(bend)} {f1(ln)} 0" stroke="{c}" '
                       f'stroke-width="{2.4 + 1.6 * depth:.1f}"/>')
    return "".join(out)


def lamp():
    x, top, base = 742, 204, 262
    return (f'<ellipse cx="{x}" cy="{base}" rx="110" ry="26" fill="url(#lampPool)"/>'
            f'<path d="M{x} {base}V{top + 6}" stroke="#0A1328" stroke-width="3"/>'
            f'<path d="M{x - 6} {top + 6}h12l-3 -10h-6z" fill="#0A1328"/>'
            f'<circle cx="{x}" cy="{top}" r="16" fill="url(#starGlow)">'
            f'<animate attributeName="r" values="14;19;14" dur="3.2s" repeatCount="indefinite"/></circle>'
            + ring(x, top, 10, YELLOW[1], 2.4, "4 4", 9)
            + ring(x, top, 15, ORANGE, 2.2, "3 6", 14, rev=True)
            + f'<circle cx="{x}" cy="{top}" r="3.5" fill="#FFF8D6"/>')


def cypress():
    cx, base, top = 74, 296, 6

    def half_width(y):
        u = (y - top) / (base - top)
        return 40 * u ** 0.8 * (1 + 0.18 * math.sin(y / 11))

    left = [(cx - half_width(y) + 4 * math.sin(y / 7), y) for y in range(top, base + 1, 6)]
    right = [(cx + half_width(y) + 4 * math.sin(y / 8 + 1), y) for y in range(base, top - 1, -6)]
    sil = "M" + " L".join(f"{f1(x)} {f1(y)}" for x, y in left + right) + "Z"
    out = [f'<path d="{sil}" fill="#0E2216"/>']
    weights = [0, 0, 1, 1, 1, 2, 2, 3, 4, 5]
    for _ in range(150):
        u = rng.uniform(-1, 1)
        y0 = rng.uniform(top + 30, base)
        span = rng.uniform(25, 70)
        y1 = max(top, y0 - span)
        ph, amp = rng.uniform(0, 6.28), rng.uniform(3, 8)
        pts = []
        for k in range(9):
            y = y0 + (y1 - y0) * k / 8
            x = cx + u * half_width(y) * 0.9 + amp * math.sin(y / 12 + ph) * (k / 8)
            pts.append((x, y))
        # curl the tip like a flame tongue
        tx, ty = pts[-1]
        pts.append((tx + (5 if u > 0 else -5), ty + 4))
        d = "M" + " L".join(f"{f1(x)} {f1(y)}" for x, y in pts)
        c = CYPRESS[rng.choice(weights)]
        out.append(f'<path d="{d}" stroke="{c}" stroke-width="{rng.uniform(2.8, 5):.1f}" stroke-linejoin="round"/>')
    return (f'<g filter="url(#paint)"><animateTransform attributeName="transform" type="rotate" '
            f'values="-1.4 {cx} {base};1.4 {cx} {base};-1.4 {cx} {base}" dur="7s" '
            f'calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1" repeatCount="indefinite"/>'
            + "".join(out) + '</g>')


# ---------------------------------------------------------------- agents
def project(x, y):
    d = y / 280.0
    return 430 + (x - 430) * (0.8 + 0.2 * d), HORIZON + 10 + d * 82, 0.7 + 0.7 * d


def fade(y):
    a = max(0.0, min(1.0, (y + 5) / 35))
    b = max(0.0, min(1.0, (305 - y) / 30))
    return a * b


def tracks(pos_fn, times):
    tr, sc, op = [], [], []
    for t in times:
        x, y = pos_fn(t)
        sx, sy, s = project(x, y)
        tr.append(f"{f1(sx)} {f1(sy)}")
        sc.append(f"{s:.2f}")
        op.append(f"{fade(y):.2f}")
    keys = ";".join(kt(t / T) for t in times)
    return (f'<animateTransform attributeName="transform" type="translate" dur="{f1(T)}s" '
            f'repeatCount="indefinite" values="{";".join(tr)}" keyTimes="{keys}"/>',
            f'<animateTransform attributeName="transform" type="scale" dur="{f1(T)}s" '
            f'repeatCount="indefinite" values="{";".join(sc)}" keyTimes="{keys}"/>',
            f'<animate attributeName="opacity" dur="{f1(T)}s" repeatCount="indefinite" '
            f'values="{";".join(op)}" keyTimes="{keys}"/>')


COATS = [("#2B3F6B", YELLOW[1]), ("#B07C2E", "#F2D27A"), ("#2F5A3A", "#9FCB7A"),
         ("#7A3B2E", "#E89B6F"), ("#3B2E5A", "#C79BD0"), ("#1F4A5E", "#9EC1E3")]


def person(coat, walking=True, hat=False, delay=0.0):
    c, hl = coat
    legs = ""
    for sgn, ph in ((1, 0.0), (-1, 0.45)):
        anim = (f'<animateTransform attributeName="transform" type="rotate" '
                f'values="{-16 * sgn} 0 -13;{16 * sgn} 0 -13;{-16 * sgn} 0 -13" dur=".9s" '
                f'begin="-{delay:.2f}s" repeatCount="indefinite"/>') if walking else ""
        legs += (f'<path d="M{sgn * 1.5} -13L{sgn * 2} 0" stroke="#0B1324" stroke-width="2.8" '
                 f'stroke-linecap="round">{anim}</path>')
    bob = (f'<animateTransform attributeName="transform" type="translate" values="0 0;0 -1;0 0" '
           f'dur=".45s" begin="-{delay:.2f}s" repeatCount="indefinite"/>') if walking else ""
    hat_el = (f'<path d="M-5.5 -32.5H5.5M-3.2 -33V-37.5H3.2V-33" stroke="#0B1324" stroke-width="1.8" '
              f'fill="#0B1324"/>') if hat else ""
    return (f'<ellipse cy="1" rx="8" ry="2.2" fill="#050B18" fill-opacity=".55"/>{legs}<g>{bob}'
            f'<path d="M-5.5 -12Q-6.5 -20 -4 -26.5L4 -26.5Q6.5 -20 5.5 -12Z" fill="{c}" '
            f'stroke="#0B1324" stroke-width="1"/>'
            f'<path d="M-2.5 -24Q-3.5 -18 -3 -13M1.5 -25Q2.5 -19 2 -13" stroke="{hl}" '
            f'stroke-width="1.1" stroke-opacity=".8" fill="none"/>'
            f'<circle cy="-30" r="4" fill="#E7B46A" stroke="#0B1324" stroke-width=".8"/>{hat_el}</g>')


def space_ring(rx=24, ry=7, cx=0):
    return (f'<ellipse cx="{cx}" rx="{rx}" ry="{ry}" fill="url(#spaceFill)" stroke="{YELLOW[1]}" '
            f'stroke-opacity=".55" stroke-width="1.6" class="flow"/>')


def prediction(dx, dy):
    out = []
    for m, (ax, ay, op) in enumerate(((dx, dy, .8), (dx * .9 + dy * .35, dy * .9 + dx * .35, .4),
                                      (dx * .9 - dy * .35, dy * .9 - dx * .35, .4))):
        for k in range(1, 5):
            out.append(f'<ellipse cx="{f1(ax * k)}" cy="{f1(ay * k)}" rx="{f1(3.4 - .4 * k)}" '
                       f'ry="{f1((3.4 - .4 * k) * .45)}" fill="{SKY_L[2]}" fill-opacity="{op * (1 - k * .18):.2f}"/>')
    return "".join(out)


def moving_person(p, idx):
    times = grid_times(N_KEY, [wrap_time(p)])
    tr, sc, op = tracks(lambda t: ped_pos(p, t), times)
    vx, vy = p["v"]
    if abs(vx) > abs(vy):
        pdx, pdy, flip = (11 if vx > 0 else -11), 0, vx < 0
    else:
        pdx, pdy, flip = 0, (5 if vy > 0 else -4), False
    body = person(COATS[idx % len(COATS)], hat=idx % 2 == 0, delay=idx * .3)
    if flip:
        body = f'<g transform="scale(-1 1)">{body}</g>'
    inner = space_ring() + prediction(pdx, pdy) + body
    if "partner" in p:
        dx, _ = p["partner"]
        mate = person(COATS[(idx + 3) % len(COATS)], delay=idx * .3 + .4)
        inner = (space_ring(rx=40, ry=10, cx=dx * .45) + prediction(pdx, pdy) + body
                 + f'<g transform="translate({f1(dx * .7)} 2)">{mate}</g>')
    return f'<g>{op}<g>{tr}<g>{sc}{inner}</g></g></g>'


def static_people():
    out = []
    for k, (x, y, a) in enumerate(STATIC):
        sx, sy, s = project(x, y)
        body = person(COATS[(k + 4) % len(COATS)], walking=False, hat=k == 0)
        if a == 180.0:
            body = f'<g transform="scale(-1 1)">{body}</g>'
        out.append(f'<g transform="translate({f1(sx)} {f1(sy)}) scale({s:.2f})">{body}</g>')
    cx, cy, s = project(473, 236)
    return (f'<g transform="translate({f1(cx)} {f1(cy)}) scale({s:.2f})">{space_ring(rx=34, ry=9)}</g>'
            + "".join(out))


def robot():
    times = grid_times(N_KEY)

    def pos(t):
        _, x, y, *_ = robot_at(t)
        return x, y
    tr, sc, _ = tracks(pos, times)
    return f'''<g><g>{tr}<g>{sc}<g transform="scale(1.3)">
    <path d="M14 -10L70 -26Q76 -10 70 6Z" fill="url(#beam)"/>
    <ellipse cy="1" rx="17" ry="2.6" fill="#050B18" fill-opacity=".55"/>
    <rect x="-14" y="-16" width="28" height="11" rx="3.5" fill="url(#robotBody)" stroke="#1E3314" stroke-width="1.2"/>
    <path d="M-11 -14.5Q0 -16.5 11 -14.5" stroke="#E4F5B8" stroke-width="1.4" fill="none"/>
    <rect x="10" y="-13" width="4" height="4" rx="1" fill="#FFF2B0"/>
    <g fill="#0E1626" stroke="{YELLOW[1]}" stroke-width="1.3">
      <circle cx="-8" cy="-4" r="4.2"/><circle cx="8" cy="-4" r="4.2"/>
    </g>
    <g stroke="{YELLOW[2]}" stroke-width="1">
      <path d="M-10.5 -4h5"><animateTransform attributeName="transform" type="rotate" from="0 -8 -4" to="360 -8 -4" dur=".8s" repeatCount="indefinite"/></path>
      <path d="M5.5 -4h5"><animateTransform attributeName="transform" type="rotate" from="0 8 -4" to="360 8 -4" dur=".8s" repeatCount="indefinite"/></path>
    </g>
    <path d="M1 -16V-23" stroke="#C9D1D9" stroke-width="1.6"/>
    <circle cx="1" cy="-26" r="10" fill="url(#starGlow)"><animate attributeName="r" values="8;12;8" dur="1.6s" repeatCount="indefinite"/></circle>
    {ring(1, -26, 6.5, YELLOW[1], 1.8, "3 3", 2)}
    {ring(1, -26, 9.5, GREEN, 1.6, "2 5", 3.2, rev=True)}
    <circle cx="1" cy="-26" r="3" fill="#FFF8D6" stroke="{GREEN}" stroke-width="1.2"/>
  </g></g></g></g>'''


def robot_trail():
    pts = []
    for t, x, y, *_ in [robot_at(k * 0.1) for k in range(int(T * 10) + 1)]:
        sx, sy, _ = project(x, y)
        pts.append((sx, sy))
    d = "M" + " L".join(f"{f1(x)} {f1(y)}" for x, y in pts)
    s, acc = [0.0], 0.0
    for a, b in zip(pts, pts[1:]):
        acc += math.hypot(b[0] - a[0], b[1] - a[1])
        s.append(acc)
    times = grid_times(N_KEY)
    offs = [f1(acc - s[min(int(round(t * 10)), len(s) - 1)]) for t in times]
    keys = ";".join(kt(t / T) for t in times)
    return (f'<path d="{d}" stroke="{YELLOW[2]}" stroke-opacity=".22" stroke-width="2" stroke-dasharray="3 7"/>'
            f'<path d="{d}" stroke="{YELLOW[1]}" stroke-opacity=".6" stroke-width="2.6" '
            f'stroke-dasharray="{f1(acc)}" stroke-dashoffset="{f1(acc)}">'
            f'<animate attributeName="stroke-dashoffset" dur="{f1(T)}s" repeatCount="indefinite" '
            f'values="{";".join(offs)}" keyTimes="{keys}"/></path>')


def _knee(hip, foot, thigh=8.0, shin=8.5, forward=1):
    hx, hy = hip
    fx, fy = foot
    d = min(math.hypot(fx - hx, fy - hy), thigh + shin - 0.01)
    a = math.atan2(fy - hy, fx - hx)
    cos_k = (thigh ** 2 + d ** 2 - shin ** 2) / (2 * thigh * d)
    k = math.acos(max(-1, min(1, cos_k)))
    return hx + thigh * math.cos(a - forward * k), hy + thigh * math.sin(a - forward * k)


def cyclist_figure():
    """Side view facing +x, ground contact at y=0."""
    rear, front, crank = (-12, -7.5), (12, -7.5), (0, -7.5)
    seat, bar = (-3.5, -18.5), (8.5, -20)
    hip, shoulder = (-3, -20), (4.5, -31)
    coat, coat_hl = "#C9962E", "#F4D35E"

    def wheel(cx, cy):
        spokes = "".join(f'<path d="M{f1(cx - 6.5 * math.cos(a))} {f1(cy - 6.5 * math.sin(a))}'
                         f'L{f1(cx + 6.5 * math.cos(a))} {f1(cy + 6.5 * math.sin(a))}"/>'
                         for a in (0, math.pi / 3, 2 * math.pi / 3))
        return (f'<circle cx="{cx}" cy="{cy}" r="7.5" stroke="#0B1324" stroke-width="2.2"/>'
                f'<circle cx="{cx}" cy="{cy}" r="7.5" stroke="{YELLOW[1]}" stroke-width=".9" '
                f'stroke-dasharray="3 3"/>'
                f'<g stroke="{CREAM[0]}" stroke-width=".7" stroke-opacity=".8">'
                f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" '
                f'to="360 {cx} {cy}" dur=".35s" repeatCount="indefinite"/>{spokes}</g>')

    def leg(phase):
        ds = []
        for k in range(13):
            a = phase + k * 2 * math.pi / 12
            foot = (crank[0] + 4.2 * math.cos(a), crank[1] + 4.2 * math.sin(a))
            kx, ky = _knee(hip, foot)
            ds.append(f"M{f1(hip[0])} {f1(hip[1])}L{f1(kx)} {f1(ky)}L{f1(foot[0])} {f1(foot[1])}")
        return (f'<path d="{ds[0]}" stroke="#0B1324" stroke-width="2.6" stroke-linejoin="round">'
                f'<animate attributeName="d" values="{";".join(ds)}" dur=".6s" repeatCount="indefinite"/></path>')

    scarf = ";".join(f"M3 -31Q-4 {f1(-31 + w)} -12 {f1(-29 + 2 * w)}" for w in (0, -2.5, 1.5, -1, 0))
    return (f'<ellipse cy="1" rx="22" ry="2.6" fill="#050B18" fill-opacity=".55"/>'
            f'<path d="M14 -16L62 -28Q68 -14 62 0Z" fill="url(#beam)"/>'
            + wheel(*rear) + wheel(*front)
            + leg(math.pi)
            + f'<path d="M{rear[0]} {rear[1]}L{crank[0]} {crank[1]}L{seat[0]} {seat[1]}L{rear[0]} {rear[1]}'
              f'M{crank[0]} {crank[1]}L{bar[0] - 1.5} {bar[1] + 2}L{seat[0]} {seat[1]}'
              f'M{bar[0] - 1.5} {bar[1] + 2}L{front[0]} {front[1]}M{bar[0] - 2} {bar[1]}H{bar[0] + 1.5}'
              f'M{seat[0] - 2.5} {seat[1]}H{seat[0] + 2}" stroke="#C8553D" stroke-width="1.9" '
              f'stroke-linejoin="round"/>'
              f'<circle cx="{front[0] + 1}" cy="-17.5" r="1.6" fill="#FFF2B0"/>'
            + leg(0)
            + f'<path d="M{hip[0] - 1.5} {hip[1] + 1}Q{hip[0] - 2} -27 {shoulder[0]} {shoulder[1]}'
              f'L{shoulder[0] + 3} {shoulder[1] + 3}Q{hip[0] + 3} -25 {hip[0] + 2.5} {hip[1] + 1}Z" '
              f'fill="{coat}" stroke="#0B1324" stroke-width="1"/>'
              f'<path d="M-1 -23Q1 -27 4 -29.5" stroke="{coat_hl}" stroke-width="1.1" stroke-opacity=".85"/>'
              f'<path d="M{shoulder[0] + 1} {shoulder[1] + 1.5}L{bar[0]} {bar[1]}" stroke="#0B1324" stroke-width="2.2"/>'
              f'<path d="M3 -31Q-4 -31 -12 -29" stroke="#C8553D" stroke-width="2.2">'
              f'<animate attributeName="d" values="{scarf}" dur=".8s" repeatCount="indefinite"/></path>'
              f'<circle cx="{shoulder[0] + 2.5}" cy="{shoulder[1] - 3.5}" r="4" fill="#E7B46A" stroke="#0B1324" stroke-width=".8"/>'
              f'<path d="M{shoulder[0] - 2} {shoulder[1] - 6}Q{shoulder[0] + 2.5} {shoulder[1] - 11} {shoulder[0] + 7} {shoulder[1] - 6}Z" '
              f'fill="#2B3F6B" stroke="#0B1324" stroke-width=".8"/>')


def moving_cyclist(p):
    times = grid_times(N_KEY, [wrap_time(p)])
    tr, sc, op = tracks(lambda t: ped_pos(p, t), times)
    flip = p["v"][0] < 0
    body = cyclist_figure()
    wind = "".join(f'<path d="M{-30 - 8 * k} {-12 - 7 * k}h-14" stroke="{CREAM[k % 3]}" stroke-width="1.8" '
                   f'stroke-opacity=".6" stroke-dasharray="6 5" class="wind" style="animation-duration:.6s"/>'
                   for k in range(3))
    inner = (f'<ellipse cx="6" rx="36" ry="8" fill="url(#spaceFill)" stroke="{YELLOW[1]}" '
             f'stroke-opacity=".55" stroke-width="1.6" class="flow"/>'
             + "".join(f'<ellipse cx="{f1(22 + 9 * k)}" rx="{f1(3.4 - .4 * k)}" ry="{f1((3.4 - .4 * k) * .45)}" '
                       f'fill="{SKY_L[2]}" fill-opacity="{.8 * (1 - k * .18):.2f}"/>' for k in range(1, 5))
             + wind + body)
    if flip:
        inner = f'<g transform="scale(-1 1)">{inner}</g>'
    return f'<g>{op}<g>{tr}<g>{sc}{inner}</g></g></g>'


def agents():
    by_id = {p["id"]: (k, p) for k, p in enumerate(peds)}

    def mp(pid):
        k, p = by_id[pid]
        return moving_person(p, k)
    # painter's order: far-to-near at the moments paths overlap
    cyc = moving_cyclist(by_id["c1"][1]) if CYCLIST else ""
    return mp("g1") + mp("p3") + cyc + robot() + mp("p1") + mp("p2") + static_people()


svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">
<title id="t">Human-aware navigation under a starry night{" — with a cyclist" if CYCLIST else ""}</title>
<desc id="d">A Van Gogh–style animated painting: under a swirling starry sky, a small robot crosses a lamp-lit plaza, predicting where people will walk{" — and making room for an oncoming cyclist" if CYCLIST else ""} while keeping clear of their personal space.</desc>
<defs>
  <clipPath id="clip"><rect width="{W}" height="{H}" rx="{0 if FRAMELESS else 14}"/></clipPath>
  <linearGradient id="skyBg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0B1838"/><stop offset=".6" stop-color="#1A3A78"/><stop offset="1" stop-color="#2B5596"/></linearGradient>
  <linearGradient id="groundBg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1B3150"/><stop offset="1" stop-color="#0C1729"/></linearGradient>
  <radialGradient id="vortexBg"><stop offset="0" stop-color="#7FA8D8"/><stop offset="1" stop-color="#2A5599"/></radialGradient>
  <radialGradient id="starGlow"><stop offset="0" stop-color="#FFF6C8" stop-opacity=".95"/><stop offset=".35" stop-color="#F4D35E" stop-opacity=".55"/><stop offset="1" stop-color="#F4D35E" stop-opacity="0"/></radialGradient>
  <radialGradient id="moonGlow"><stop offset="0" stop-color="#FCE9A8" stop-opacity=".9"/><stop offset=".4" stop-color="#E89B2F" stop-opacity=".45"/><stop offset="1" stop-color="#E89B2F" stop-opacity="0"/></radialGradient>
  <radialGradient id="lampPool"><stop offset="0" stop-color="#F4D35E" stop-opacity=".55"/><stop offset="1" stop-color="#F4D35E" stop-opacity="0"/></radialGradient>
  <radialGradient id="spaceFill"><stop offset="0" stop-color="#F4D35E" stop-opacity=".22"/><stop offset="1" stop-color="#F4D35E" stop-opacity="0"/></radialGradient>
  <linearGradient id="beam" x1="0" x2="1"><stop offset="0" stop-color="#FFF2B0" stop-opacity=".55"/><stop offset="1" stop-color="#FFF2B0" stop-opacity="0"/></linearGradient>
  <linearGradient id="robotBody" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#B9E89C"/><stop offset="1" stop-color="#5E9A44"/></linearGradient>
  <filter id="paint" x="-5%" y="-5%" width="110%" height="110%">
    <feTurbulence type="fractalNoise" baseFrequency=".035" numOctaves="2" seed="7" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="5" xChannelSelector="R" yChannelSelector="G"/>
  </filter>
  <style>
    .wind{{animation:wind 6s linear infinite}}
    @keyframes wind{{to{{stroke-dashoffset:-92}}}}
    .flow{{stroke-dasharray:5 4;animation:flow 1.4s linear infinite}}
    @keyframes flow{{to{{stroke-dashoffset:-18}}}}
  </style>
</defs>
<g clip-path="url(#clip)" fill="none" stroke-linecap="round">
  <rect width="{W}" height="{HORIZON + 4}" fill="url(#skyBg)"/>
  <g>{sky_strokes()}</g>
  <g>{wind_ribbons()}</g>
  {''.join(vortex(*v) for v in VORTICES)}
  {''.join(star(x, y, s, k) for k, (x, y, s) in enumerate(STARS))}
  {moon()}
  <g filter="url(#paint)">{hills()}</g>
  <g>{village()}</g>
  <rect y="{HORIZON}" width="{W}" height="{H - HORIZON}" fill="url(#groundBg)"/>
  <g>{ground_strokes()}</g>
  {lamp()}
  {robot_trail()}
  {agents()}
  {cypress()}
</g>
{"" if FRAMELESS else f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="none" stroke="#2A3550" stroke-width="2"/>'}
</svg>
'''
sys.stdout.write(svg)
