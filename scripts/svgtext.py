"""Outline text as SVG paths so it renders identically on every machine.

Fonts come from @fontsource on jsDelivr and are cached in
~/.cache/sontypo-readme-fonts: Playfair Display (SIL OFL 1.1) and
Special Elite (Apache 2.0).
"""
import os

FONT_URL = "https://cdn.jsdelivr.net/npm/@fontsource/{family}/files/{name}.woff"
FONT_CACHE = os.path.expanduser("~/.cache/sontypo-readme-fonts")
_fonts = {}


def _num(v):
    s = f"{v:.1f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def load(name):
    """name like 'playfair-display-latin-700-normal'."""
    if name not in _fonts:
        from fontTools.ttLib import TTFont
        path = os.path.join(FONT_CACHE, name + ".woff")
        if not os.path.exists(path):
            import urllib.request
            os.makedirs(FONT_CACHE, exist_ok=True)
            family = name.split("-latin-")[0]
            urllib.request.urlretrieve(FONT_URL.format(family=family, name=name), path)
        _fonts[name] = TTFont(path)
    return _fonts[name]


def glyph(font, ch, size, x=0.0, baseline=0.0, coarse=False):
    """(path data, advance) for one character; coarse rounds to whole units."""
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    f = load(font)
    gname = f.getBestCmap()[ord(ch)]
    sc = size / f["head"].unitsPerEm
    pen = SVGPathPen(f.getGlyphSet(), ntos=(lambda v: str(int(round(v)))) if coarse else _num)
    f.getGlyphSet()[gname].draw(TransformPen(pen, (sc, 0, 0, -sc, x, baseline)))
    return pen.getCommands(), f["hmtx"][gname][0] * sc


def advance(font, text, size, tracking=0.0):
    f = load(font)
    cmap, sc = f.getBestCmap(), size / f["head"].unitsPerEm
    return sum(f["hmtx"][cmap[ord(c)]][0] * sc + tracking for c in text) - tracking


def text_path(font, text, size, cx, baseline, tracking=0.0, coarse=False):
    """Whole string as one path, centred on cx."""
    x = cx - advance(font, text, size, tracking) / 2
    out = []
    for ch in text:
        d, a = glyph(font, ch, size, x, baseline, coarse)
        out.append(d)
        x += a + tracking
    return "".join(out)
