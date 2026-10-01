"""Generate assets/social-nav.svg — a robot doing human-aware navigation.

Usage: python3 scripts/gen_social_nav.py > assets/social-nav.svg

Pedestrians move on periodic constant-velocity paths; the robot is driven by a
simple anticipatory social-force controller. Positions are sampled and baked
into SMIL keyframes so the SVG loops seamlessly. The scene shows a social
costmap, multi-modal trajectory predictions, a dynamic interaction graph and
live telemetry.
"""
import math, sys

W, H = 860, 280
T = 12.0            # loop period (s)
DT = 0.02
N_KEY = 181         # keyframes per loop (agents)
N_EDGE = 121        # keyframes per loop (graph edges)
OFF = 60            # off-screen margin
PX_PER_M = 80       # telemetry scale

GREEN = "#8BCC6A"
GREEN_L = "#B9E89C"
PURPLE = "#C79BD0"
PURPLE_L = "#EBD7F0"
BLUE = "#BCD3EB"
AMBER = "#E3B341"
BG = "#0D1117"
PANEL = "#111823"
DOT = "#1F2A37"
TEXT = "#8B949E"
TEXT_L = "#C9D1D9"

LANE_Y = 150

# moving pedestrians — periodic over T, the wrap happens off-screen
peds = [
    dict(id="p1", p0=(W + OFF, LANE_Y - 4), v=(-(W + 2 * OFF) / T, 0.0), phase=0.0),   # head-on
    dict(id="p2", p0=(250, -OFF), v=(0.0, (H + 2 * OFF) / T), phase=0.38),            # crossing
    dict(id="g1", p0=(600, H + OFF), v=(0.0, -(H + 2 * OFF) / T), phase=0.32,         # walking group
         partner=(30, 6)),
    dict(id="p3", p0=(745, -OFF), v=(0.0, (H + 2 * OFF) / T), phase=0.66),            # crossing
]
# static conversational group (F-formation)
STATIC = [(452, 236, 0.0), (494, 236, 180.0)]
STATIC_C = (473, 236)


def ped_pos(p, t):
    f = (t / T + p["phase"]) % 1.0
    return (p["p0"][0] + p["v"][0] * T * f, p["p0"][1] + p["v"][1] * T * f)


def ped_center(p, t):
    x, y = ped_pos(p, t)
    if "partner" in p:
        x, y = x + p["partner"][0] / 2, y + p["partner"][1] / 2
    return x, y


def wrap_time(p):
    f0 = p["phase"] % 1.0
    return (1.0 - f0) * T if f0 > 0 else None


def ped_bodies(t):
    out = []
    for p in peds:
        x, y = ped_pos(p, t)
        out.append((x, y, p["v"]))
        if "partner" in p:
            dx, dy = p["partner"]
            out.append((x + dx, y + dy, p["v"]))
    out += [(sx, sy, (0.0, 0.0)) for sx, sy, _ in STATIC]
    return out


def simulate(v0=88.0, k_lat=1400.0, k_lane=0.6, damp=4.0):
    """Forward speed is modulated (yield/slow down), avoidance is lateral."""
    x, y, vy = -OFF + 10, float(LANE_Y), 0.0
    vx = v0
    traj = []
    t = 0.0
    while t <= T + 1e-9:
        traj.append((t, x, y, vx, vy))
        ay = -k_lane * (y - LANE_Y) - damp * vy
        slow = 1.0
        for px, py, pv in ped_bodies(t):
            for tau in (0.0, 0.6, 1.2):
                qx, qy = px + pv[0] * tau, py + pv[1] * tau
                rx, ry = (x + v0 * tau) - qx, y - qy
                if rx > 40 or rx < -150:   # only humans ahead matter
                    continue
                d = math.hypot(rx, ry) or 1e-3
                w = math.exp(-(d - 40) / 26) / (1 + tau)
                side = ry if abs(ry) > 4 else 1.0   # tie-break: pass on the right
                ay += k_lat * w * (1 if side > 0 else -1)
            dnow = math.hypot(x - px, y - py)
            slow = min(slow, max(0.45, (dnow - 30) / 70))
        vx = v0 * slow
        vy += ay * DT
        vy = max(-70, min(70, vy))
        x += vx * DT
        y += vy * DT
        y = min(max(y, 40), H - 40)
        t += DT
    return traj


traj = simulate()


def robot_at(t):
    i = min(max(int(round(t / DT)), 0), len(traj) - 1)
    return traj[i]


def on_screen(x, y, m=0):
    return -m < x < W + m and -m < y < H + m


def nearest(t):
    _, x, y, *_ = robot_at(t)
    return min(math.hypot(x - px, y - py) for px, py, _ in ped_bodies(t))


# ---------------------------------------------------------------- formatting
def f0(v):
    return str(int(round(v)))


def f1(v):
    s = f"{v:.1f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def kt(v):
    return f"{v:.4f}".rstrip("0").rstrip(".") or "0"


def grid_times(n, wraps=()):
    ts = [i * T / (n - 1) for i in range(n)]
    for w in wraps:
        if w is not None:
            ts += [w - 1e-3, w]
    return sorted(set(ts))


def anim(attr, values, times, extra=""):
    return (f'<animate attributeName="{attr}" dur="{f1(T)}s" repeatCount="indefinite" '
            f'values="{";".join(values)}" keyTimes="{";".join(kt(t / T) for t in times)}"{extra}/>')


def anim_translate(points, times):
    return (f'<animateTransform attributeName="transform" type="translate" dur="{f1(T)}s" '
            f'repeatCount="indefinite" values="{";".join(f"{f1(x)} {f1(y)}" for x, y in points)}" '
            f'keyTimes="{";".join(kt(t / T) for t in times)}"/>')


def discrete_slots(texts, slot, attrs):
    """Show texts[i] only during slot i (calcMode=discrete opacity)."""
    n = len(texts)
    out = []
    for i, txt in enumerate(texts):
        a, b = i / n, (i + 1) / n
        if i == 0:
            vals, kts = "1;0", f"0;{kt(b)}"
        elif i == n - 1:
            vals, kts = "0;1", f"0;{kt(a)}"
        else:
            vals, kts = "0;1;0", f"0;{kt(a)};{kt(b)}"
        out.append(f'<text {attrs} opacity="{1 if i == 0 else 0}">{txt}'
                   f'<animate attributeName="opacity" calcMode="discrete" dur="{f1(T)}s" '
                   f'repeatCount="indefinite" values="{vals}" keyTimes="{kts}"/></text>')
    return "".join(out)


# ---------------------------------------------------------------- pieces
def human_figure(angle, sway_delay=0.0):
    """Top-down person facing +x, rotated by angle (deg)."""
    return (f'<g transform="rotate({f1(angle)})"><g>'
            f'<animateTransform attributeName="transform" type="rotate" values="-7;7;-7" '
            f'dur="0.9s" begin="-{sway_delay:.2f}s" repeatCount="indefinite"/>'
            f'<ellipse rx="6.5" ry="11.5" fill="url(#body)"/>'
            f'<circle cx="1.5" r="6" fill="{PURPLE_L}"/>'
            f'<circle cx="1.5" r="6" fill="none" stroke="{BG}" stroke-opacity=".5"/>'
            f'</g></g>')


def prediction_fan(length, angle):
    L = length
    modes = [(0.0, 1.0, 2.2), (-0.32, 0.6, 1.5), (0.32, 0.6, 1.5)]
    out = [f'<g transform="rotate({f1(angle)})" fill="none" stroke-linecap="round">']
    for bend, op, w in modes:
        ex, ey = L * math.cos(bend), L * math.sin(bend)
        cx, cy = L * 0.55, ey * 0.15
        out.append(f'<path d="M10 0 Q{f1(cx)} {f1(cy)} {f1(ex)} {f1(ey)}" stroke="url(#pred)" '
                   f'stroke-opacity="{op}" stroke-width="{w}" class="flow"/>'
                   f'<circle cx="{f1(ex)}" cy="{f1(ey)}" r="2.6" fill="{BLUE}" '
                   f'fill-opacity="{op}" stroke="none"/>')
    out.append('</g>')
    return "".join(out)


def costmap(angle, rx=50, ry=34, shift=12):
    return (f'<ellipse cx="{shift}" rx="{rx}" ry="{ry}" fill="url(#heat)" '
            f'transform="rotate({f1(angle)})"/>')


def zone_ring(r=25, dur=9):
    return (f'<circle r="{r}" fill="none" stroke="{PURPLE}" stroke-opacity=".45" '
            f'stroke-dasharray="2 5"><animateTransform attributeName="transform" type="rotate" '
            f'from="0" to="360" dur="{dur}s" repeatCount="indefinite"/></circle>')


def moving_pedestrian(p, layer):
    wr = wrap_time(p)
    times = grid_times(N_KEY, [wr])
    pts = [ped_pos(p, t) for t in times]
    vx, vy = p["v"]
    ang = math.degrees(math.atan2(vy, vx))
    sp = math.hypot(vx, vy)
    if layer == "heat":
        inner = costmap(ang)
        if "partner" in p:
            dx, dy = p["partner"]
            inner = (f'<ellipse cx="{f1(dx / 2)}" cy="{f1(dy / 2)}" rx="56" ry="50" '
                     f'fill="url(#heat)"/>')
    elif layer == "pred":
        cx, cy = (p["partner"][0] / 2, p["partner"][1] / 2) if "partner" in p else (0, 0)
        inner = (f'<g transform="translate({f1(cx)} {f1(cy)})">'
                 f'{prediction_fan(max(70, sp * 1.8), ang)}</g>')
    else:
        inner = zone_ring() + human_figure(ang, sway_delay=p["phase"])
        if "partner" in p:
            dx, dy = p["partner"]
            inner = (f'<ellipse cx="{f1(dx / 2)}" cy="{f1(dy / 2)}" rx="38" ry="30" fill="none" '
                     f'stroke="{PURPLE}" stroke-opacity=".5" stroke-dasharray="6 4"/>'
                     + inner + f'<g transform="translate({dx} {dy})">'
                     f'{zone_ring(dur=11)}{human_figure(ang, sway_delay=p["phase"] + .45)}</g>')
    return f'<g>{anim_translate(pts, times)}{inner}</g>'


def static_group(layer):
    cx, cy = STATIC_C
    if layer == "heat":
        return f'<circle cx="{cx}" cy="{cy}" r="58" fill="url(#heat)"/>'
    out = [f'<circle cx="{cx}" cy="{cy}" r="34" fill="none" stroke="{PURPLE}" '
           f'stroke-opacity=".5" stroke-dasharray="6 4"/>',
           f'<circle cx="{cx}" cy="{cy}" r="5" fill="{PURPLE}" fill-opacity=".25"/>']
    for i, (sx, sy, a) in enumerate(STATIC):
        out.append(f'<g transform="translate({sx} {sy})">{zone_ring(r=18, dur=10 + i)}'
                   f'{human_figure(a, sway_delay=i * .3).replace("0.9s", "2.6s")}</g>')
    return "".join(out)


# graph nodes: id -> (position fn, wrap times)
nodes = {p["id"]: ((lambda t, p=p: ped_center(p, t)), [wrap_time(p)]) for p in peds}
nodes["s"] = ((lambda t: STATIC_C), [])


def robot_xy(t):
    _, x, y, *_ = robot_at(t)
    return x, y


def edge(a_fn, a_wr, b_fn, b_wr, radius, max_op, color, width, cls=""):
    times = grid_times(N_EDGE, a_wr + b_wr)
    xs1, ys1, xs2, ys2, ops = [], [], [], [], []
    for t in times:
        (x1, y1), (x2, y2) = a_fn(t), b_fn(t)
        d = math.hypot(x2 - x1, y2 - y1)
        vis = on_screen(x1, y1, -6) and on_screen(x2, y2, -6)
        op = max(0.0, 1 - d / radius) * max_op if vis else 0.0
        xs1.append(f0(x1)); ys1.append(f0(y1)); xs2.append(f0(x2)); ys2.append(f0(y2))
        ops.append(f"{op:.2f}".rstrip("0").rstrip(".") or "0")
    if not any(o != "0" for o in ops):
        return ""
    return (f'<line stroke="{color}" stroke-width="{width}" stroke-linecap="round" {cls}>'
            + anim("x1", xs1, times) + anim("y1", ys1, times)
            + anim("x2", xs2, times) + anim("y2", ys2, times)
            + anim("stroke-opacity", ops, times) + '</line>')


def graph_edges():
    ids = list(nodes)
    out = []
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            (fa, wa), (fb, wb) = nodes[ids[i]], nodes[ids[j]]
            out.append(edge(fa, wa, fb, wb, 300, .55, BLUE, 1, 'stroke-dasharray="1 4"'))
    for nid, (fn, wr) in nodes.items():
        out.append(edge(robot_xy, [], fn, wr, 230, .85, GREEN, 1.3,
                        'stroke-dasharray="4 4" class="flow"'))
    return "".join(out)


def robot_tracks(lag=0.0, n=N_KEY):
    times = grid_times(n)
    pts, rot = [], []
    for t in times:
        _, x, y, vx, vy = robot_at(t - lag) if t >= lag else robot_at(T + t - lag)
        if t < lag:   # wrapped: robot sits off-screen at the end of the loop
            x, y = robot_at(T)[1], robot_at(T)[2]
        pts.append((x, y))
        rot.append(f1(math.degrees(math.atan2(vy, vx)) if math.hypot(vx, vy) > 5 else 0))
    return pts, rot, times


def robot_path():
    pts = [(x, y) for (_, x, y, *_r) in traj[::5]]
    d = f"M{f1(pts[0][0])} {f1(pts[0][1])}" + "".join(
        f"L{f1(px)} {f1(py)}" for px, py in pts[1:])
    s, acc = [0.0], 0.0
    for a, b in zip(pts, pts[1:]):
        acc += math.hypot(b[0] - a[0], b[1] - a[1])
        s.append(acc)
    times = grid_times(N_KEY)
    offs = [f1(acc - s[min(int(round(t / (DT * 5))), len(s) - 1)]) for t in times]
    return d, acc, offs, times


def comet():
    out = []
    for k in range(1, 8):
        pts, _, times = robot_tracks(lag=0.07 * k, n=121)
        out.append(f'<circle r="{f1(6 - 0.6 * k)}" fill="{GREEN}" fill-opacity="{0.42 - 0.05 * k:.2f}">'
                   f'{anim_translate(pts, times)}</circle>')
    return "".join(out)


def robot():
    pts, rot, times = robot_tracks()
    return f'''<g>{anim_translate(pts, times)}
    <circle r="46" fill="url(#halo)"/>
    <g><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="1.6s" repeatCount="indefinite"/>
      <path d="M0 0L84 0A84 84 0 0 1 59.4 59.4Z" fill="url(#sweep)"/>
      <line x2="84" stroke="{GREEN_L}" stroke-opacity=".7" stroke-width="1.2"/>
    </g>
    <circle r="84" fill="none" stroke="{GREEN}" stroke-opacity=".22" stroke-dasharray="1 7">
      <animateTransform attributeName="transform" type="rotate" from="360" to="0" dur="14s" repeatCount="indefinite"/>
    </circle>
    <circle r="20" fill="none" stroke="{GREEN}" stroke-width="1.2">
      <animate attributeName="r" values="18;60" dur="1.6s" repeatCount="indefinite"/>
      <animate attributeName="stroke-opacity" values=".55;0" dur="1.6s" repeatCount="indefinite"/>
    </circle>
    <g><animateTransform attributeName="transform" type="rotate" dur="{f1(T)}s" repeatCount="indefinite" values="{";".join(rot)}" keyTimes="{";".join(kt(t / T) for t in times)}"/>
      <rect x="-14" y="-17" width="11" height="6" rx="2" fill="#26302A"/>
      <rect x="5" y="-17" width="11" height="6" rx="2" fill="#26302A"/>
      <rect x="-14" y="11" width="11" height="6" rx="2" fill="#26302A"/>
      <rect x="5" y="11" width="11" height="6" rx="2" fill="#26302A"/>
      <rect x="-17" y="-12" width="35" height="24" rx="6" fill="url(#chassis)" stroke="{GREEN_L}" stroke-opacity=".6"/>
      <rect x="14" y="-9" width="3" height="18" rx="1.5" fill="{GREEN_L}"/>
      <circle cx="-2" r="6.5" fill="{BG}" stroke="{GREEN}" stroke-width="1.5"/>
      <circle cx="-2" r="2.6" fill="{GREEN_L}"><animate attributeName="fill-opacity" values="1;.35;1" dur="0.8s" repeatCount="indefinite"/></circle>
      <path d="M22 -5L30 0L22 5Z" fill="{GREEN}" fill-opacity=".9"/>
    </g>
  </g>'''


def telemetry():
    n = 48
    slots = [(i + 0.5) * T / n for i in range(n)]
    d_txt, v_txt, mode_txt, bar_w, bar_c = [], [], [], [], []
    for t in slots:
        _, x, y, vx, vy = robot_at(t)
        if on_screen(x, y):
            d = nearest(t) / PX_PER_M
            v = math.hypot(vx, vy) / PX_PER_M
            d_txt.append(f"{d:.2f} m")
            v_txt.append(f"{v:.2f} m/s")
            mode_txt.append("YIELD" if d < 1.4 else ("AVOID" if abs(vy) > 22 else "CRUISE"))
        else:
            d_txt.append("-- m"); v_txt.append("-- m/s"); mode_txt.append("IDLE")
    times = grid_times(N_EDGE)
    for t in times:
        _, x, y, *_ = robot_at(t)
        d = nearest(t) / PX_PER_M if on_screen(x, y) else 3.0
        bar_w.append(f0(min(d / 3.0, 1.0) * 64))
        bar_c.append(AMBER if d < 1.4 else GREEN)
    x0, y0 = W - 232, H - 44
    mode_els = []
    for i, m in enumerate(mode_txt):
        color = {"YIELD": AMBER, "AVOID": BLUE, "CRUISE": GREEN}.get(m, TEXT)
        mode_els.append(f'<tspan fill="{color}">{m}</tspan>')
    return f'''<g transform="translate({x0} {y0})" class="mono">
    <rect width="214" height="32" rx="7" fill="{PANEL}" fill-opacity=".9" stroke="#30363D"/>
    <text x="10" y="13" fill="{TEXT}" font-size="8.5">v</text>
    {discrete_slots(v_txt, T / 48, f'x="20" y="13" fill="{TEXT_L}" font-size="9.5"')}
    <text x="10" y="26" fill="{TEXT}" font-size="8.5">d<tspan font-size="6.5" dy="2">min</tspan></text>
    {discrete_slots(d_txt, T / 48, f'x="34" y="26" fill="{TEXT_L}" font-size="9.5"')}
    <rect x="90" y="20" width="64" height="5" rx="2.5" fill="#21262D"/>
    <rect x="90" y="20" height="5" rx="2.5">{anim("width", bar_w, times)}{anim("fill", bar_c, times, ' calcMode="discrete"')}</rect>
    <text x="90" y="13" fill="{TEXT}" font-size="8.5">mode</text>
    {discrete_slots(mode_els, T / 48, 'x="118" y="13" font-size="9.5"')}
    <text x="204" y="26" fill="{TEXT}" font-size="8" text-anchor="end">clear</text>
  </g>'''


def hud_steps():
    words = ["PERCEIVE", "PREDICT", "PLAN"]
    out = []
    for i, w in enumerate(words):
        vals = ";".join(GREEN if j == i else TEXT for j in range(3)) + ";" + (GREEN if i == 0 else TEXT)
        out.append(f'<tspan fill="{TEXT}">{w}<animate attributeName="fill" calcMode="discrete" '
                   f'values="{vals}" keyTimes="0;.3333;.6667;1" dur="2.4s" repeatCount="indefinite"/></tspan>')
        if i < 2:
            out.append(f'<tspan fill="#484F58"> → </tspan>')
    return "".join(out)


if __name__ == "__main__":
    min_d = min(nearest(t) for (t, x, y, *_r) in traj if on_screen(x, y, 20))
    exit_t = next((r[0] for r in traj if r[1] > W + 30), None)
    print(f"robot exits at t={exit_t}, min clearance={min_d:.1f}px", file=sys.stderr)
    path_d, path_len, offs, path_times = robot_path()

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">
    <title id="t">Human-aware robot navigation</title>
    <desc id="d">A mobile robot scans with LiDAR, builds a social costmap, predicts multi-modal pedestrian trajectories over a dynamic interaction graph, and yields personal space while crossing a crowd.</desc>
    <defs>
      <clipPath id="clip"><rect width="{W}" height="{H}" rx="14"/></clipPath>
      <pattern id="dots" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="10" cy="10" r="1" fill="{DOT}"/></pattern>
      <pattern id="major" width="80" height="80" patternUnits="userSpaceOnUse"><path d="M80 0H0V80" fill="none" stroke="{DOT}" stroke-opacity=".6"/></pattern>
      <radialGradient id="heat"><stop offset="0" stop-color="{PURPLE}" stop-opacity=".55"/><stop offset=".45" stop-color="#8A5F94" stop-opacity=".28"/><stop offset="1" stop-color="#442D47" stop-opacity="0"/></radialGradient>
      <radialGradient id="halo"><stop offset="0" stop-color="{GREEN}" stop-opacity=".38"/><stop offset="1" stop-color="{GREEN}" stop-opacity="0"/></radialGradient>
      <radialGradient id="sweep" cx="0" cy="0" r="84" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{GREEN}" stop-opacity=".5"/><stop offset="1" stop-color="{GREEN}" stop-opacity="0"/></radialGradient>
      <radialGradient id="vignette" cx=".5" cy=".5" r=".75"><stop offset=".55" stop-color="{BG}" stop-opacity="0"/><stop offset="1" stop-color="{BG}" stop-opacity=".85"/></radialGradient>
      <linearGradient id="chassis" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{GREEN_L}"/><stop offset="1" stop-color="#5E9A44"/></linearGradient>
      <radialGradient id="body" cx=".4" cy=".4"><stop offset="0" stop-color="{PURPLE_L}"/><stop offset="1" stop-color="#8A5F94"/></radialGradient>
      <linearGradient id="pred" x1="0" x2="1"><stop offset="0" stop-color="{BLUE}" stop-opacity=".9"/><stop offset="1" stop-color="{BLUE}" stop-opacity=".15"/></linearGradient>
      <linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="{BG}"/><stop offset=".05" stop-color="{BG}" stop-opacity="0"/><stop offset=".95" stop-color="{BG}" stop-opacity="0"/><stop offset="1" stop-color="{BG}"/></linearGradient>
      <style>
        .flow{{stroke-dasharray:3 5;animation:flow .9s linear infinite}}
        @keyframes flow{{to{{stroke-dashoffset:-16}}}}
        .mono{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-weight:600;letter-spacing:.06em}}
      </style>
    </defs>
    <g clip-path="url(#clip)">
      <rect width="{W}" height="{H}" fill="{BG}"/>
      <rect width="{W}" height="{H}" fill="url(#dots)"/>
      <rect width="{W}" height="{H}" fill="url(#major)"/>

      <!-- social costmap -->
      <g>{''.join(moving_pedestrian(p, "heat") for p in peds)}{static_group("heat")}</g>

      <!-- robot path: plan + executed trail -->
      <path d="{path_d}" fill="none" stroke="{GREEN}" stroke-opacity=".16" stroke-width="1.5" stroke-dasharray="2 6"/>
      <path d="{path_d}" fill="none" stroke="{GREEN}" stroke-opacity=".55" stroke-width="2" stroke-linecap="round" stroke-dasharray="{f1(path_len)}" stroke-dashoffset="{f1(path_len)}">{anim("stroke-dashoffset", offs, path_times)}</path>

      <!-- dynamic interaction graph -->
      <g>{graph_edges()}</g>

      <!-- multi-modal trajectory predictions -->
      <g>{''.join(moving_pedestrian(p, "pred") for p in peds)}</g>

      <!-- humans -->
      <g>{''.join(moving_pedestrian(p, "body") for p in peds)}{static_group("body")}</g>

      <!-- robot -->
      <g>{comet()}</g>
      {robot()}

      <rect width="{W}" height="{H}" fill="url(#vignette)"/>
      <rect width="{W}" height="{H}" fill="url(#fade)"/>

      <!-- HUD -->
      <g class="mono" font-size="10.5">
        <rect x="12" y="11" width="232" height="24" rx="7" fill="{PANEL}" fill-opacity=".9" stroke="#30363D"/>
        <circle cx="26" cy="23" r="4" fill="{GREEN}"><animate attributeName="fill-opacity" values="1;.2;1" dur="1.6s" repeatCount="indefinite"/></circle>
        <circle cx="26" cy="23" r="4" fill="none" stroke="{GREEN}"><animate attributeName="r" values="4;10" dur="1.6s" repeatCount="indefinite"/><animate attributeName="stroke-opacity" values=".8;0" dur="1.6s" repeatCount="indefinite"/></circle>
        <text x="38" y="27" fill="{GREEN}">SOCIAL_NAV</text><text x="112" y="27" fill="{TEXT}">// human-aware</text>
        <rect x="{W - 248}" y="11" width="236" height="24" rx="7" fill="{PANEL}" fill-opacity=".9" stroke="#30363D"/>
        <text x="{W - 130}" y="27" text-anchor="middle">{hud_steps()}</text>
      </g>
      <g class="mono" font-size="9" fill="{TEXT}" transform="translate(12 {H - 50})">
        <rect width="346" height="38" rx="7" fill="{PANEL}" fill-opacity=".9" stroke="#30363D"/>
        <g transform="translate(12 15)">
          <rect x="0" y="-6" width="11" height="8" rx="2" fill="{GREEN}"/><text x="16" y="1">robot</text>
          <circle cx="62" cy="-2" r="4" fill="{PURPLE}"/><text x="70" y="1">human</text>
          <circle cx="121" cy="-2" r="6" fill="url(#heat)"/><circle cx="121" cy="-2" r="2" fill="{PURPLE}" fill-opacity=".6"/><text x="131" y="1">social costmap</text>
          <path d="M0 13H12" stroke="{BLUE}" stroke-dasharray="2 2"/><text x="16" y="16">multi-modal prediction</text>
          <path d="M150 13H162" stroke="{GREEN}" stroke-dasharray="3 2"/><path d="M168 13H180" stroke="{BLUE}" stroke-dasharray="1 2"/><text x="186" y="16">interaction graph</text>
        </g>
      </g>
      {telemetry()}
    </g>
    <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="none" stroke="#30363D"/>
    </svg>
    '''
    sys.stdout.write(svg)
