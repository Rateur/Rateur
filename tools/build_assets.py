#!/usr/bin/env python3
"""
Générateur des assets SVG du profil GitHub (DA : space western / phosphore vert).

    pip install fonttools
    python tools/build_assets.py

Tout le texte est converti en tracés (glyphes réutilisés via <use>) :
GitHub affiche les SVG comme des <img>, donc aucune police web ne se charge.
Pour changer un texte, un projet ou une techno : modifie les DONNÉES ci-dessous.
Polices : Bebas Neue, Share Tech Mono, DotGothic16 (SIL OFL). Icônes : Simple Icons (CC0).
"""
import json, math, random, hashlib, pathlib
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
FONTS = ROOT / "tools" / "fonts"
ICONS = json.loads((ROOT / "tools" / "icons.json").read_text())

# ───────────────────────────── DONNÉES ─────────────────────────────
NAME_1, NAME_2 = "VALENTIN", "PÉRIÈS"
KATAKANA = "ヴァランタン・ペリエス"
KICKER = "CHASSEUR DE PRIMES  ·  LYON"
ROLE = "Développeur data & full-stack"
PROMPT = "> alternance 2 ans · dès maintenant"
EMAIL = "contact@valentinperies.fr"

STACK = [  # (catégorie, [(label, icône simple-icons ou None)])
    ("ML", [("scikit-learn", "scikitlearn"), ("TensorFlow", "tensorflow"), ("Keras", "keras"),
                 ("MLflow", "mlflow"), ("MCP", "modelcontextprotocol"),
                 ("n8n", "n8n"), ("Ollama", "ollama")]),
    ("DATA", [("Python", "python"), ("Pandas", "pandas"), ("NumPy", "numpy"), ("Streamlit", "streamlit")]),
    ("BACK & OPS", [("FastAPI", "fastapi"), ("Rust", "rust"), ("Flask", "flask"), ("SQL", None), ("SQLite", "sqlite"),
                      ("Docker", "docker"), ("CI/CD", "githubactions"), ("pytest", "pytest"),
                      ("Supabase", "supabase")]),
    ("INTERFACE", [("Svelte", "svelte"), ("React", "react"), ("TypeScript", "typescript"), ("Next.js", "nextdotjs"),
                   ("Tauri", "tauri"), ("Three.js", "threedotjs"), ("WebGL", "webgl")]),
]

MISSIONS = [  # id, nom, type, statut, (ligne1, ligne2), kpi ("→" dessiné), légende, lien affiché
    ("01", "NUTRI-PREDICT", "FULL-STACK", "LIVRÉ",
     ("Prédit la variation de poids d'une portion.", ""),
     "R² 0,985", "données simulées", "certif RNCP 2026"),
    ("02", "WILDAIPRINT", "VISION", "RE-TESTÉ",
     ("Fuite de données trouvée et corrigée,", "re-testé sur 38 photos."),
     "83 % → 26 %", "annoncé, puis mesuré", "Rateur/WildAIprint-Modele-CNN"),
    ("03", "OBSERVATOIRE PARITÉ", "DATA", "EN LIGNE",
     ("Temps de parole femmes / hommes à la TV.", ""),
     "33 / 35", "chaînes sous les 50 % (2020)", "opendata2025.netlify.app"),
    ("04", "ASSISTANT FAMILLE", "LOCAL", "EN COURS",
     ("Répond sur les papiers de la maison.", "Tourne sur mon NAS."),
     "0 OCTET", "dans le cloud", "privé"),
    ("05", "SEVENARTLIST", "FULL-STACK", "EN COURS",
     ("Trouver un film, voir où le regarder,", "suivre sa watchlist."),
     "NEXT.JS + SUPABASE", "", "Rateur/SevenArtList"),
    ("06", "?", "", "OUVERT", ("", ""), "", "", EMAIL),
]

SECTIONS = [("title-missions", "MISSIONS"), ("title-radar", "RADAR"),
            ("title-signal", "SIGNAL"), ("title-soundtrack", "BANDE-SON")]

SUMI = {"name": "SUMI", "version": "v0.4.0 · MIT",
        "pitch": ("Une île en haut de l'écran Windows.", "L'heure, puis la musique."),
        "link": "rateur.github.io/sumi"}
FEATURED_TECH = {"Rust", "Tauri", "Svelte"}  # la stack de Sumi, en ambre
SUMI_LOGO = "M292 330H732A80 80 0 0 1 732 490H566C540 490 522.5 525.3 553.1 551A64 64 0 1 1 470.9 551C501.5 525.3 484 490 458 490H292A80 80 0 0 1 292 330Z"

BUTTONS = [  # fichier, titre, sous-titre, glyphe
    ("btn-portfolio", "PORTFOLIO", "valentinperies.fr", "globe"),
    ("btn-linkedin", "LINKEDIN", "in/valentin-peries", "in"),
    ("btn-email", "E-MAIL", "contact@…", "mail"),
    ("btn-instagram", "INSTAGRAM", "@valentin.peries", "instagram"),
]

# ───────────────────────────── PALETTE ─────────────────────────────
BG, PANEL, CELL, EDGE = "#0D1117", "#0A0E13", "#161B22", "#21262D"
G = ["#161B22", "#1A4B27", "#2EA043", "#42A852", "#72FF72"]  # niveaux de contribution 0→4
INK, DIM, AMBER = "#E3F5E1", "#6E8B74", "#FFB547"
EASE = 'calcMode="spline" keySplines=".2 .8 .2 1"'

# ───────────────────────────── TEXTE → TRACÉS ─────────────────────────────
class Face:
    def __init__(self, *files):
        self.fonts = []
        for f in files:
            t = TTFont(FONTS / f)
            self.fonts.append((t, t.getBestCmap(), t.getGlyphSet(), 1000 / t["head"].unitsPerEm))

    def lookup(self, ch):
        for i, (t, cmap, gs, k) in enumerate(self.fonts):
            if ord(ch) in cmap:
                return i, cmap[ord(ch)]
        raise KeyError(f"glyphe absent : {ch!r}")

    def advance(self, ch):
        i, g = self.lookup(ch)
        t, _, _, k = self.fonts[i]
        return t["hmtx"][g][0] * k

    def path(self, i, g):
        t, _, gs, k = self.fonts[i]
        pen = SVGPathPen(gs, ntos=lambda v: str(round(v)))
        gs[g].draw(TransformPen(pen, (k, 0, 0, -k, 0, 0)))
        return pen.getCommands()

BEBAS = Face("bebas-neue-latin-400-normal.woff", "share-tech-mono-latin-400-normal.woff")
MONO = Face("share-tech-mono-latin-400-normal.woff", "bebas-neue-latin-400-normal.woff")
JP = Face("dotgothic16-119-400-normal.woff")
INTER = Face("inter-latin-400-normal.woff")
INTER_B = Face("inter-latin-600-normal.woff")


class Doc:
    """Petit constructeur SVG : glyphes mutualisés dans <defs>."""
    def __init__(self, w, h, label):
        self.w, self.h, self.label = w, h, label
        self.defs, self.body, self.glyphs, self.css = [], [], {}, []

    def add(self, *parts):
        self.body.extend(parts)

    def gid(self, face, ch):
        i, g = face.lookup(ch)
        key = (id(face), i, g)
        if key not in self.glyphs:
            n = f"g{len(self.glyphs)}"
            self.glyphs[key] = n
            d = face.path(i, g)
            if d:
                self.defs.append(f'<path id="{n}" d="{d}"/>')
            else:
                self.glyphs[key] = None
        return self.glyphs[key]

    @staticmethod
    def width(face, s, size, ls=0):
        return sum(face.advance(c) for c in s) * size / 1000 + ls * max(len(s) - 1, 0)

    def text(self, s, x, y, size, face=MONO, fill=INK, ls=0, anchor="start", extra=""):
        w = self.width(face, s, size, ls)
        if anchor == "middle": x -= w / 2
        if anchor == "end": x -= w
        k = size / 1000
        cur, uses = 0.0, []
        for c in s:
            n = self.gid(face, c)
            if n:
                uses.append(f'<use href="#{n}" x="{cur:.0f}"/>')
            cur += face.advance(c) + ls / k
        return (f'<g transform="translate({x:.1f} {y:.1f}) scale({k:.4f})" fill="{fill}" {extra}>'
                + "".join(uses) + "</g>"), w

    def vtext(self, s, x, y, size, face=JP, fill=INK, step=None, extra=""):
        step = step or size * 1.05
        parts = []
        for j, c in enumerate(s):
            g, _ = self.text(c, x, y + j * step, size, face, fill, anchor="middle")
            parts.append(g)
        return f'<g {extra}>' + "".join(parts) + "</g>"

    def render(self):
        css = f"<style>{''.join(self.css)}</style>" if self.css else ""
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
                f'width="{self.w}" height="{self.h}" role="img" aria-label="{self.label}">'
                f'<title>{self.label}</title>{css}<defs>{"".join(self.defs)}</defs>'
                + "".join(self.body) + "</svg>\n")

    def save(self, name):
        p = OUT / f"{name}.svg"
        p.write_text(self.render(), encoding="utf-8")
        print(f"  {p.relative_to(ROOT)}  {p.stat().st_size/1024:.1f} Ko")


def frame(d, rx=16, fill=BG, stroke=EDGE):
    d.add(f'<rect x=".5" y=".5" width="{d.w-1}" height="{d.h-1}" rx="{rx}" fill="{fill}" stroke="{stroke}"/>')


def scanlines(d, op=.10):
    d.defs.append('<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">'
                  f'<rect width="4" height="1" fill="#000" opacity="{op}"/></pattern>')
    d.add(f'<rect width="{d.w}" height="{d.h}" rx="16" fill="url(#scan)" pointer-events="none"/>')


def grid_pattern(d, pitch=13, cell=10, ox=0, oy=0, pid="grid", fill=CELL):
    d.defs.append(f'<pattern id="{pid}" width="{pitch}" height="{pitch}" patternUnits="userSpaceOnUse" '
                  f'x="{ox}" y="{oy}"><rect width="{cell}" height="{cell}" rx="2" fill="{fill}"/></pattern>')


def icon(slug, x, y, size, fill):
    k = size / 24
    return f'<path transform="translate({x - size/2:.1f} {y - size/2:.1f}) scale({k:.3f})" d="{ICONS[slug]}" fill="{fill}"/>'


def cells_glyph(x, y, size, fill):
    """Pictogramme générique (2×2 cellules) pour une techno sans logo."""
    c, gap = size * .42, size * .16
    o = -size / 2
    return "".join(f'<rect x="{x+o+i*(c+gap):.1f}" y="{y+o+j*(c+gap):.1f}" width="{c:.1f}" height="{c:.1f}" rx="1" '
                   f'fill="{fill}" opacity="{1 if (i+j)%2==0 else .5}"/>' for i in range(2) for j in range(2))


def arrow(x, y, s, fill):
    """Flèche ↗ dessinée (absente des polices)."""
    return (f'<path d="M{x} {y+s} L{x+s} {y} M{x+s*.35} {y} H{x+s} V{y+s*.65}" stroke="{fill}" '
            f'stroke-width="{max(1.4, s*.16):.1f}" fill="none" stroke-linecap="square"/>')


# ───────────────────────────── BANNIÈRE ─────────────────────────────
def build_banner():
    W, H = 1280, 360
    rnd = random.Random(11)
    d = Doc(W, H, "Valentin Périès, développeur à Lyon, en recherche d'alternance de 2 ans")
    PX, PY, R, T = 985, 182, 146, 40  # planète : centre, rayon, période de rotation (s)
    d.defs += [
        f'<clipPath id="card"><rect width="{W}" height="{H}" rx="16"/></clipPath>',
        '<radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".6"/></radialGradient>',
        '<linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="#0D1117" stop-opacity=".97"/><stop offset=".38" stop-color="#0D1117" stop-opacity=".85"/><stop offset=".56" stop-color="#0D1117" stop-opacity="0"/></linearGradient>',
        f'<radialGradient id="shade" cx=".33" cy=".3" r=".8"><stop offset="0" stop-color="#0D1117" stop-opacity="0"/><stop offset=".55" stop-color="#0D1117" stop-opacity=".15"/><stop offset="1" stop-color="#050807" stop-opacity=".92"/></radialGradient>',
        f'<radialGradient id="atmo" cx=".5" cy=".5" r=".5"><stop offset=".62" stop-color="{G[4]}" stop-opacity=".16"/><stop offset=".72" stop-color="{G[4]}" stop-opacity=".05"/><stop offset="1" stop-color="{G[4]}" stop-opacity="0"/></radialGradient>',
        f'<radialGradient id="core" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#0C1A11"/><stop offset="1" stop-color="#070D09"/></radialGradient>',
        f'<linearGradient id="comet" x1="0" x2="1"><stop offset="0" stop-color="{G[4]}" stop-opacity="0"/><stop offset="1" stop-color="{INK}"/></linearGradient>',
    ]
    grid_pattern(d, 13, 10, 4.5, 6, "grid", "#121820")
    d.css.append(
        f".m{{animation:orb {T}s ease-in-out infinite,side {T}s step-end infinite}}"
        f"@keyframes orb{{0%{{transform:translateX(-{R}px)}}50%{{transform:translateX({R}px)}}100%{{transform:translateX(-{R}px)}}}}"
        "@keyframes side{0%{opacity:1}50%{opacity:.07}100%{opacity:1}}"
        ".eq{transform-box:fill-box;transform-origin:50% 100%;animation:eq 1.6s ease-in-out infinite alternate}"
        "@keyframes eq{0%{transform:scaleY(.2)}100%{transform:scaleY(1)}}"
        ".drift{animation:drift 140s linear infinite}.drift2{animation:drift 80s linear infinite}"
        f"@keyframes drift{{to{{transform:translateX(-{W}px)}}}}")
    d.add(f'<rect width="{W}" height="{H}" rx="16" fill="{BG}"/>', '<g clip-path="url(#card)">',
          f'<rect width="{W}" height="{H}" fill="url(#grid)" opacity=".55"/>')

    # étoiles en deux plans de parallaxe (bouclent sans couture)
    for cls, n, size, op in [("drift", 70, 1.6, .5), ("drift2", 34, 2.4, .85)]:
        pts = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.random()) for _ in range(n)]
        dots = "".join(f'<rect x="{x+ox:.0f}" y="{y:.0f}" width="{size}" height="{size}" fill="{INK if t>.8 else G[3]}" opacity="{op*(.5+t/2):.2f}"/>'
                       for ox in (0, W) for x, y, t in pts)
        d.add(f'<g class="{cls}">{dots}</g>')
    # étoile filante
    d.add(f'<g opacity="0"><animate attributeName="opacity" values="0;1;0;0" keyTimes="0;.02;.06;1" dur="11s" begin="3s" repeatCount="indefinite"/>'
          f'<g transform="rotate(14 640 40)"><rect y="38" width="90" height="1.6" fill="url(#comet)">'
          f'<animate attributeName="x" values="560;860;860" keyTimes="0;.06;1" dur="11s" begin="3s" repeatCount="indefinite"/></rect></g></g>')

    # anneau : moitié arrière
    tilt = -13
    ring = lambda a0, a1, rx, ry: f"M{PX + rx*math.cos(math.radians(a0)):.1f} {PY + ry*math.sin(math.radians(a0)):.1f}A{rx} {ry} 0 0 1 {PX + rx*math.cos(math.radians(a1)):.1f} {PY + ry*math.sin(math.radians(a1)):.1f}"
    def ring_layer(a0, a1, op):
        out = []
        for rx, ry, w, col, dash, sp in [(262, 56, 1, G[1], None, 0), (246, 51, 3.2, G[3], "3 7", 40), (228, 47, 2, G[2], "2 11", 26)]:
            st = f'stroke-dasharray="{dash}"' if dash else ""
            an = (f'<animate attributeName="stroke-dashoffset" from="0" to="-{sp*10}" dur="{T/2:.0f}s" repeatCount="indefinite"/>' if dash else "")
            out.append(f'<path d="{ring(a0, a1, rx, ry)}" fill="none" stroke="{col}" stroke-width="{w}" {st} opacity="{op}">{an}</path>')
        return f'<g transform="rotate({tilt} {PX} {PY})">' + "".join(out) + "</g>"
    d.add(f'<circle cx="{PX}" cy="{PY}" r="{R*1.55:.0f}" fill="url(#atmo)"/>', ring_layer(180, 360, .55))

    # planète : globe de cellules en rotation (chaque rangée = une latitude)
    d.add(f'<circle cx="{PX}" cy="{PY}" r="{R}" fill="url(#core)"/>')
    noise = lambda la, lo: (math.sin(lo*2+la*1.3)*1.2 + math.sin(lo*3-la*2.2+1.7)*.8 + math.sin(lo+la*2.6+.4)*.6)
    rows = []
    step = 5.4
    lat = -83.7
    while lat <= 83:
        c = math.cos(math.radians(lat))
        y = PY + R * math.sin(math.radians(lat))
        n = max(6, round(60 * c))
        sz = 3.8
        movers = []
        for j in range(n):
            lon = j / n * 2 * math.pi
            v = noise(math.radians(lat), lon)
            lvl = 4 if v > .95 else 3 if v > .35 else 1
            if abs(lat) > 68: lvl = 4 if rnd.random() < .7 else 3  # calottes
            delay = -(lon / (2 * math.pi)) * T
            q = sz if lvl > 1 else sz * .62
            movers.append(f'<g class="m" style="animation-delay:{delay:.2f}s"><rect x="{-q/2/c:.2f}" y="{-q/2:.2f}" width="{q/c:.2f}" height="{q:.2f}" rx="1" fill="{G[lvl if lvl > 1 else 2]}"/></g>')
        rows.append(f'<g transform="translate({PX} {y:.1f}) scale({c:.4f} 1)">' + "".join(movers) + "</g>")
        lat += step
    d.add(*rows, f'<circle cx="{PX}" cy="{PY}" r="{R+1}" fill="url(#shade)"/>',
          f'<circle cx="{PX}" cy="{PY}" r="{R+.5}" fill="none" stroke="{G[3]}" stroke-opacity=".35"/>')
    d.add(ring_layer(0, 180, 1))

    d.add(f'<rect width="{W}" height="{H}" fill="url(#fade)"/>')
    # typographie
    X = 58
    g, _ = d.text(KICKER, X, 76, 13, MONO, G[3], ls=2.6)
    d.add(f'<g opacity="0">{g}<animate attributeName="opacity" from="0" to="1" begin=".1s" dur=".5s" fill="freeze"/></g>')
    g1, w1 = d.text(NAME_1, X, 172, 108, BEBAS, INK, ls=3)
    d.add(f'<g opacity="0" transform="translate(0 18)">{g1}'
          f'<animate attributeName="opacity" from="0" to="1" begin=".2s" dur=".6s" fill="freeze"/>'
          f'<animateTransform attributeName="transform" type="translate" from="0 18" to="0 0" begin=".2s" dur=".7s" fill="freeze" {EASE} keyTimes="0;1"/></g>')
    g2, w2 = d.text(NAME_2, X + 14, 280, 108, BEBAS, BG, ls=3)
    bw, by, bh = w2 + 30, 188, 104
    d.defs.append(f'<clipPath id="blk"><rect x="{X}" y="{by}" width="0" height="{bh}">'
                  f'<animate attributeName="width" from="0" to="{bw:.0f}" begin=".55s" dur=".6s" fill="freeze" {EASE} keyTimes="0;1"/></rect></clipPath>')
    d.add(f'<rect x="{X+9}" y="{by+9}" width="{bw:.0f}" height="{bh}" fill="none" stroke="{G[2]}" stroke-width="1.5" opacity="0">'
          f'<animate attributeName="opacity" from="0" to="1" begin="1.05s" dur=".4s" fill="freeze"/></rect>',
          f'<g clip-path="url(#blk)"><rect x="{X}" y="{by}" width="{bw:.0f}" height="{bh}" fill="{G[4]}"/>{g2}</g>')
    kx = X + max(w1, bw + 9) + 30
    d.add(d.vtext(KATAKANA, kx, 106, 17, JP, G[3], step=18.5,
                  extra='opacity="0"><animate attributeName="opacity" from="0" to=".9" begin="1.2s" dur=".8s" fill="freeze"/'))
    g, _ = d.text(ROLE, X, 326, 15.5, MONO, INK)
    d.add(f'<g opacity="0">{g}<animate attributeName="opacity" from="0" to="1" begin="1.1s" dur=".5s" fill="freeze"/></g>')
    gp, wp = d.text(PROMPT, X, 348, 14, MONO, G[4])
    n = len(PROMPT)
    widths = [d.width(MONO, PROMPT[:i], 14) for i in range(n + 1)]
    d.defs.append(f'<clipPath id="typ"><rect x="{X-2}" y="332" width="0" height="24">'
                  f'<animate attributeName="width" values="{";".join(f"{w+2:.0f}" for w in widths)}" '
                  f'begin="1.6s" dur="{n*.045:.2f}s" calcMode="discrete" fill="freeze"/></rect></clipPath>')
    d.add(f'<g clip-path="url(#typ)">{gp}</g>',
          f'<rect x="{X+wp+5:.0f}" y="337" width="8" height="14" fill="{G[4]}" opacity="0">'
          f'<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;.01;.5;.51;1" dur="1.05s" begin="{1.6+n*.045:.2f}s" repeatCount="indefinite"/></rect>')
    d.add(f'<rect width="{W}" height="{H}" fill="url(#vig)"/>', "</g>")
    scanlines(d, .07)
    d.add(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="{EDGE}"/>')
    d.save("banner")


# ───────────────────────────── RADAR ─────────────────────────────
def build_radar():
    W, H = 880, 440
    cx, cy, R = 222, 220, 188
    DUR = 8.0
    d = Doc(W, H, "Stack technique : " + ", ".join(l for _, items in STACK for l, _ in items))
    frame(d)
    grid_pattern(d, 13, 10, 0, 0, "grid", "#121820")
    d.defs.append(f'<clipPath id="scope"><circle cx="{cx}" cy="{cy}" r="{R}"/></clipPath>')
    d.defs.append('<radialGradient id="crt" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#0F2416"/>'
                  '<stop offset=".75" stop-color="#08140C"/><stop offset="1" stop-color="#050B07"/></radialGradient>')
    d.add(f'<circle cx="{cx}" cy="{cy}" r="{R+14}" fill="#070B09" stroke="{EDGE}" stroke-width="2"/>',
          f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="url(#crt)"/>')
    pol = lambda a, r: (cx + r * math.sin(math.radians(a)), cy - r * math.cos(math.radians(a)))
    # graduation
    for a in range(0, 360, 5):
        L = 10 if a % 30 == 0 else 5
        x1, y1 = pol(a, R + 13); x2, y2 = pol(a, R + 13 - L)
        d.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{G[2] if a%30==0 else G[1]}" stroke-width="1.2"/>')
    for k in (0.25, .5, .75, 1):
        d.add(f'<circle cx="{cx}" cy="{cy}" r="{R*k:.1f}" fill="none" stroke="{G[1]}" stroke-width="{1.2 if k==1 else .8}"' + ('' if k == 1 else ' stroke-dasharray="2 4"') + '/>')
    for a in (0, 90, 45, 135):
        x1, y1 = pol(a, R); x2, y2 = pol(a + 180, R)
        d.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{G[1]}" stroke-width=".8" opacity="{1 if a%90==0 else .5}"/>')
    # Balayage (traînée = empilement de secteurs)
    wedges = []
    n = 22
    for i in range(n):
        a1, a2 = -60 + i * 60 / n, -60 + (i + 1) * 60 / n + .4
        p1, p2 = pol(a1, R), pol(a2, R)
        op = (i + 1) / n * .30
        wedges.append(f'<path d="M{cx} {cy}L{p1[0]:.1f} {p1[1]:.1f}A{R} {R} 0 0 1 {p2[0]:.1f} {p2[1]:.1f}Z" fill="{G[4]}" opacity="{op:.3f}"/>')
    lead = pol(0, R)
    d.add(f'<g clip-path="url(#scope)"><g>'
          f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="{DUR}s" repeatCount="indefinite"/>'
          + "".join(wedges) + f'<line x1="{cx}" y1="{cy}" x2="{lead[0]:.1f}" y2="{lead[1]:.1f}" stroke="{G[4]}" stroke-width="2"/></g></g>')
    # Blips : secteurs proportionnels au nombre de technos, placement sans collision des étiquettes
    total = sum(len(i) for _, i in STACK)
    sectors, acc = [], 0
    for _, items in STACK:
        span = round(360 * len(items) / total)
        sectors.append((acc, min(360, acc + span))); acc += span
    sectors[-1] = (sectors[-1][0], 360)
    boxes = []
    def hit(b):
        return any(not (b[2] < o[0] or b[0] > o[2] or b[3] < o[1] or b[1] > o[3]) for o in boxes)
    for (cat, items), (s0, s1) in zip(STACK, sectors):
        m = 7
        span = (s1 - s0 - 2 * m)
        for j, (label, slug) in enumerate(items):
            a = s0 + m + span * (j + .5) / len(items)
            right = a < 180
            lw = d.width(MONO, label, 11.5)
            best = None
            cands = [(a + da, rf, fl) for fl in (False, True) for da in (0, -3.5, 3.5, -7, 7, -10, 10) for rf in (.40, .58, .76, .90, .49, .67, .83, .32, .24)]
            for aa, rf, fl in cands:
                bx, by = pol(aa, R * rf)
                right = (aa < 180) != fl
                lx0 = bx + 14 if right else bx - 14 - lw
                b = (min(bx - 13, lx0) - 4, by - 14, max(bx + 13, lx0 + lw) + 4, by + 14)
                if lx0 < 30 or lx0 + lw > cx + R + 30: continue
                if math.hypot(bx - cx, by - cy) > R - 12: continue
                if not hit(b):
                    best = (bx, by, b, right, aa); break
            if best is None:
                print('  ! placement forcé :', label); bx, by = pol(a, R * .6); best = (bx, by, (bx-12, by-12, bx+12, by+12), a < 180, a)
            bx, by, b, right, a = best
            boxes.append(b)
            t = a / 360 * DUR
            begin = f"{t - DUR:.2f}s"
            ico = icon(slug, bx, by, 13, G[4]) if slug else cells_glyph(bx, by, 11, G[4])
            star = label in FEATURED_TECH
            gl, wl = d.text(label, bx + (14 if right else -14), by + 4, 13 if star else 11.5, MONO, AMBER if star else INK, anchor="start" if right else "end")
            if star:
                ico = icon(slug, bx, by, 14, AMBER)
                d.add(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="15" fill="none" stroke="{AMBER}" stroke-width="1" stroke-dasharray="2 3"><animateTransform attributeName="transform" type="rotate" from="0 {bx:.1f} {by:.1f}" to="360 {bx:.1f} {by:.1f}" dur="10s" repeatCount="indefinite"/></circle>')
            d.add(f'<g opacity=".3"><animate attributeName="opacity" values="1;.42;.28" keyTimes="0;.55;1" dur="{DUR}s" begin="{begin}" repeatCount="indefinite"/>'
                  f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="10" fill="none" stroke="{G[4]}" stroke-width="1.2" opacity="0">'
                  f'<animate attributeName="r" values="10;26;26" keyTimes="0;.2;1" dur="{DUR}s" begin="{begin}" repeatCount="indefinite"/>'
                  f'<animate attributeName="opacity" values=".9;0;0" keyTimes="0;.2;1" dur="{DUR}s" begin="{begin}" repeatCount="indefinite"/></circle>'
                  f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="10" fill="{PANEL}" stroke="{G[3]}" stroke-width="1"/>{ico}{gl}</g>')
    for a, txt in [(0, "000"), (90, "090"), (180, "180"), (270, "270")]:
        x, y = pol(a, R + 26)
        g, _ = d.text(txt, x, y + 4, 10, MONO, DIM, anchor="middle")
        d.add(g)
    d.add(f'<circle cx="{cx}" cy="{cy}" r="3" fill="{G[4]}"/>')

    # Panneau de lecture
    X = 476
    y = 92
    for (cat, items), (s0, s1) in zip(STACK, sectors):
        g, wc = d.text(cat, X, y, 24, BEBAS, INK, ls=1); d.add(g)
        line, lines = "", []
        for l, _ in items:
            cand = (line + " · " + l) if line else l
            if d.width(MONO, cand, 13) > W - 44 - X:
                lines.append(line); line = l
            else:
                line = cand
        lines.append(line)
        for k, ln in enumerate(lines):
            g, _ = d.text(ln, X, y + 22 + k * 18, 13, MONO, G[3]); d.add(g)
        y += 40 + 18 * len(lines) + 22
    scanlines(d, .08)
    d.save("radar")


# ───────────────────────────── AVIS DE PRIME ─────────────────────────────
def build_bounty():
    W, H = 880, 290
    d = Doc(W, H, "Avis de prime : Valentin Périès cherche une alternance de 2 ans, Lyon, hybride ou télétravail, dès maintenant")
    frame(d)
    # bandeau
    d.add(f'<path d="M1 17a16 16 0 0 1 16-16h846a16 16 0 0 1 16 16v23H1z" fill="#0B1610"/>',
          f'<line x1="1" y1="40" x2="{W-1}" y2="40" stroke="{G[1]}"/>')
    g, _ = d.text("AVIS DE PRIME  N° 2026-LYN-01", 26, 26, 11.5, MONO, DIM, ls=2); d.add(g)
    # identicon (style GitHub) généré depuis le pseudo
    h = hashlib.md5(b"Rateur").digest()
    P, C, X0, Y0 = 22, 18, 40, 76
    for r in range(7):
        for c in range(4):
            bit = (h[(r * 4 + c) % 16] >> (c % 8)) & 1
            lvl = 1 + (h[(r * 3 + c) % 16] % 4) if bit else 0
            for cc in {c, 6 - c}:
                d.add(f'<rect x="{X0+cc*P}" y="{Y0+r*P}" width="{C}" height="{C}" rx="3" fill="{G[lvl]}"/>')
    d.add(f'<rect x="{X0-10}" y="{Y0-10}" width="{7*P+16}" height="{7*P+16}" rx="6" fill="none" stroke="{G[1]}"/>')
    # titre
    X = 250
    g, _ = d.text("CONTRAT RECHERCHÉ", X, 104, 50, BEBAS, INK, ls=2); d.add(g)
    g2, w2 = d.text("ALTERNANCE · 2 ANS", X + 12, 146, 30, BEBAS, BG, ls=2)
    d.add(f'<rect x="{X}" y="116" width="{w2+24:.0f}" height="38" fill="{G[4]}"/>', g2)
    rows = [("FORMATION", "Bac+5 · EPSI Lyon"),
            ("ZONE", "Lyon · hybride · télétravail"),
            ("DÉPART", "dès maintenant")]
    for i, (k, v) in enumerate(rows):
        y = 196 + i * 24
        g, _ = d.text(k, X, y, 12, MONO, DIM, ls=1.5); d.add(g)
        g, _ = d.text(v, X + 104, y, 14, MONO, INK); d.add(g)
    g, w = d.text(EMAIL, W - 44, H - 22, 13, MONO, G[4], anchor="end"); d.add(g)
    d.add(arrow(W - 44 - w - 18, H - 32, 10, G[4]))
    # tampon
    sx, sy = 728, 148
    gs, ws = d.text("DISPONIBLE", 0, 15, 34, BEBAS, AMBER, ls=3, anchor="middle")
    d.add(f'<g transform="translate({sx} {sy}) rotate(-9)"><g opacity="0">'
          f'<animate attributeName="opacity" from="0" to=".92" begin=".9s" dur=".12s" fill="freeze"/>'
          f'<animateTransform attributeName="transform" type="scale" values="1.6;.96;1" keyTimes="0;.7;1" begin=".9s" dur=".35s" fill="freeze"/>'
          f'<rect x="{-ws/2-16:.0f}" y="-26" width="{ws+32:.0f}" height="54" rx="4" fill="none" stroke="{AMBER}" stroke-width="3"/>'
          f'<rect x="{-ws/2-10:.0f}" y="-20" width="{ws+20:.0f}" height="42" rx="2" fill="none" stroke="{AMBER}" stroke-width="1"/>'
          f'{gs}</g></g>')
    scanlines(d, .08)
    d.save("bounty")


# ───────────────────────────── CARTES MISSIONS ─────────────────────────────
def build_missions():
    W, H = 430, 214
    for mid, name, typ, status, (l1, l2), kpi, kpi_lbl, link in MISSIONS:
        d = Doc(W, H, f"Mission {mid} : {name.title()} — {l1} {l2}")
        open_slot = typ == "ALTERNANCE"
        frame(d, 14, BG, G[2] if open_slot else EDGE)
        if open_slot:
            d.add(f'<rect x="8" y="8" width="{W-16}" height="{H-16}" rx="10" fill="none" stroke="{G[1]}" stroke-dasharray="4 5"/>')
        g, _ = d.text(mid, 24, 36, 16, BEBAS, DIM, ls=2); d.add(g)
        live = status in ("EN COURS", "OUVERT")
        col = AMBER if live else G[4]
        g, ws = d.text(status, W - 24, 34, 11.5, MONO, col, ls=1.5, anchor="end"); d.add(g)
        blink = f'<animate attributeName="opacity" values="1;.2;1" dur="1.4s" repeatCount="indefinite"/>' if live else ""
        d.add(f'<circle cx="{W-24-ws-10:.1f}" cy="30" r="3.6" fill="{col}">{blink}</circle>')
        if name == "?":
            g, wn = d.text("?", 24, 150, 110, BEBAS, G[1]); d.add(g); wn = 0
        else:
            g, wn = d.text(name, 24, 76, 36, BEBAS, INK, ls=1.2); d.add(g)
        if typ:
            g, _ = d.text(f"[{typ}]", 24 + wn + 12, 74, 11.5, MONO, G[3]); d.add(g)
        for yy, ln in ((102, l1), (120, l2)):
            if ln:
                g, _ = d.text(ln, 24, yy, 12.5, MONO, "#B9CFBC"); d.add(g)
        if name != "?":
            d.add(f'<line x1="24" y1="136" x2="{W-24}" y2="136" stroke="{EDGE}"/>')
        if "→" in kpi:
            a_, b_ = [t.strip() for t in kpi.split("→")]
            g, wa = d.text(a_, 24, 172, 28, BEBAS, G[4], ls=1); d.add(g)
            d.add(f'<path d="M{24+wa+10:.0f} 162 h18 m-6 -6 l6 6 l-6 6" stroke="{G[4]}" stroke-width="2.2" fill="none"/>')
            g, _ = d.text(b_, 24 + wa + 38, 172, 28, BEBAS, G[4], ls=1); d.add(g)
        elif kpi:
            g, wk = d.text(kpi, 24, 172, 28, BEBAS, G[4], ls=1); d.add(g)
        if kpi_lbl:
            g, _ = d.text(kpi_lbl, 24, 192, 10.5, MONO, DIM); d.add(g)
        clickable = link.startswith(("Rateur/", "opendata", "contact"))
        g, wl = d.text(link if len(link) < 34 else link[:31] + "…", W - 24 - (16 if clickable else 0), 192, 10.5, MONO,
                       G[3] if clickable else DIM, anchor="end")
        d.add(g)
        if clickable:
            d.add(arrow(W - 34, 184, 8, G[3]))
        scanlines(d, .07)
        d.save(f"mission-{mid}")


def build_sumi():
    f = SUMI
    W, H, T = 880, 300, 15.0
    d = Doc(W, H, f"Sumi — {' '.join(f['pitch'])} {f['version']}")
    L = 300  # panneau gauche
    d.defs += [
        f'<clipPath id="card"><rect width="{W}" height="{H}" rx="14"/></clipPath>',
        f'<clipPath id="scene"><rect x="{L}" y="0" width="{W-L}" height="{H}"/></clipPath>',
        '<linearGradient id="paper" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#EFE6D2"/><stop offset="1" stop-color="#E2D4B6"/></linearGradient>',
        '<linearGradient id="gold" x1="0" x2="1"><stop offset="0" stop-color="#D8B25C" stop-opacity="0"/><stop offset=".25" stop-color="#D8B25C" stop-opacity=".55"/><stop offset=".75" stop-color="#D8B25C" stop-opacity=".45"/><stop offset="1" stop-color="#D8B25C" stop-opacity="0"/></linearGradient>',
        '<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" seed="4"/>'
        '<feColorMatrix values="0 0 0 0 .35  0 0 0 0 .28  0 0 0 0 .18  0 0 0 .16 0"/></filter>',
        '<filter id="brush" x="-5%" y="-20%" width="110%" height="140%"><feTurbulence type="fractalNoise" baseFrequency=".035 .09" numOctaves="3" seed="9"/>'
        '<feDisplacementMap in="SourceGraphic" scale="9"/><feGaussianBlur stdDeviation=".4"/></filter>',
        '<filter id="mist"><feGaussianBlur stdDeviation="7"/></filter>',
        '<filter id="shadow" x="-30%" y="-30%" width="160%" height="190%"><feDropShadow dx="0" dy="8" stdDeviation="9" flood-color="#2B1F0C" flood-opacity=".35"/></filter>',
    ]
    d.add('<g clip-path="url(#card)">', f'<rect width="{W}" height="{H}" fill="#0B0B0F"/>')

    # Scène : paravent à l'encre (crêtes procédurales, bandes d'or, brume, grain du papier)
    d.add('<g clip-path="url(#scene)">', f'<rect x="{L}" width="{W-L}" height="{H}" fill="url(#paper)"/>')
    rnd = random.Random(21)
    for y0, h in [(58, 26), (150, 20), (232, 30)]:
        d.add(f'<rect x="{L}" y="{y0}" width="{W-L}" height="{h}" fill="url(#gold)" filter="url(#mist)"/>')
    def ridge(base, amp, freq, ph, col, op, seed):
        r = random.Random(seed)
        pts = []
        for i in range(0, W - L + 21, 7):
            x = L + i
            y = base - amp * (math.sin(i * freq + ph) * .6 + math.sin(i * freq * 2.7 + ph * 1.9) * .3 + math.sin(i * freq * 6.1) * .12) - r.uniform(0, amp * .12)
            pts.append(f"{x} {y:.1f}")
        return f'<path d="M{L} {H+30} L' + " L".join(pts) + f' L{W} {H+30} Z" fill="{col}" opacity="{op}" filter="url(#brush)"/>'
    d.add(ridge(150, 70, .018, 1.2, "#6B6458", .28, 1), ridge(200, 60, .024, 3.1, "#4A443B", .42, 2),
          f'<rect x="{L}" y="176" width="{W-L}" height="40" fill="#EFE6D2" opacity=".55" filter="url(#mist)"/>',
          ridge(262, 46, .031, .4, "#2E2A24", .62, 3), ridge(300, 22, .05, 2.2, "#1C1A17", .7, 4))
    # bateau (deux traits d'encre) qui glisse
    d.add(f'<g opacity=".7"><path d="M0 0 h26 l-4 5 h-18 z M9 0 v-10" fill="#2E2A24" stroke="#2E2A24" stroke-width="1.2" transform="translate({L+40} 244)">'
          f'<animateTransform attributeName="transform" type="translate" values="{L+40} 244;{W-70} 244" dur="60s" repeatCount="indefinite"/></path></g>')
    for k in range(1, 4):  # panneaux du paravent
        x = L + k * (W - L) / 4
        d.add(f'<line x1="{x:.0f}" y1="0" x2="{x:.0f}" y2="{H}" stroke="#8C7A55" stroke-opacity=".28"/>')
    d.add(f'<rect x="{L}" width="{W-L}" height="{H}" filter="url(#grain)"/>')

    # L'île : repos → musique (aperçu) → panneau ouvert → compacte → repos (tailles de docs/design.md)
    cx, top = L + (W - L) / 2, 18
    pts = [(0, 132, 34, 17), (2.6, 132, 34, 17), (3.1, 300, 56, 28), (5.4, 300, 56, 28), (5.9, 360, 164, 34),
           (10.6, 360, 164, 34), (11.1, 200, 34, 17), (13.9, 200, 34, 17), (14.4, 132, 34, 17), (15, 132, 34, 17)]
    kt = ";".join(f"{t/T:.4f}" for t, *_ in pts)
    spl = ";".join([".3 .9 .25 1"] * (len(pts) - 1))
    an = lambda a, vals: (f'<animate attributeName="{a}" values="{";".join(vals)}" keyTimes="{kt}" dur="{T}s" '
                          f'calcMode="spline" keySplines="{spl}" repeatCount="indefinite"/>')
    d.add(f'<rect x="{cx-66}" y="{top}" width="132" height="34" rx="17" fill="#000" filter="url(#shadow)">'
          + an("x", [f"{cx-w/2:.1f}" for _, w, _, _ in pts]) + an("width", [str(w) for _, w, _, _ in pts])
          + an("height", [str(h) for _, _, h, _ in pts]) + an("rx", [str(r) for *_, r in pts]) + "</rect>")
    def phase(t0, t1, inner, fade=.25):
        k = lambda t: f"{max(0, min(1, t / T)):.4f}"
        return (f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" '
                f'keyTimes="0;{k(t0)};{k(t0+fade)};{k(t1-fade)};{k(t1)};1" dur="{T}s" repeatCount="indefinite"/>{inner}</g>')
    def art(x, y, s):
        r = max(4, s * .2)
        return (f'<g><clipPath id="a{int(x)}{int(y)}"><rect x="{x}" y="{y}" width="{s}" height="{s}" rx="{r:.1f}"/></clipPath>'
                f'<g clip-path="url(#a{int(x)}{int(y)})"><rect x="{x}" y="{y}" width="{s}" height="{s}" fill="#E7DCC3"/>'
                f'<rect x="{x}" y="{y+s*.25:.1f}" width="{s}" height="{s*.18:.1f}" fill="#D8B25C" opacity=".6"/>'
                f'<path d="M{x} {y+s} L{x} {y+s*.62:.1f} Q{x+s*.3:.1f} {y+s*.28:.1f} {x+s*.52:.1f} {y+s*.58:.1f} T{x+s} {y+s*.5:.1f} V{y+s} Z" fill="#3A352D" opacity=".8"/></g></g>')
    def bars(x, y, h, col="#F4F1EA"):
        out = ""
        for i, hh in enumerate([.5, .9, .65, 1, .55]):
            b = h * hh
            dur = .6 + i * .11
            out += (f'<rect x="{x+i*4.5:.1f}" y="{y-b/2:.1f}" width="2.6" height="{b:.1f}" rx="1.3" fill="{col}">'
                    f'<animate attributeName="height" values="{b:.1f};{b*.35:.1f};{b:.1f}" dur="{dur:.2f}s" repeatCount="indefinite"/>'
                    f'<animate attributeName="y" values="{y-b/2:.1f};{y-b*.175:.1f};{y-b/2:.1f}" dur="{dur:.2f}s" repeatCount="indefinite"/></rect>')
        return out
    # repos : l'heure
    g, _ = d.text("16:22", cx, top + 22.5, 14, INTER_B, "#F4F1EA", anchor="middle")
    d.add(phase(0, 2.8, g), phase(14.2, 15, g, .15))
    # aperçu : nouveau morceau
    x0 = cx - 150
    g1, _ = d.text("West Lake", x0 + 54, top + 25, 13, INTER_B, "#F4F1EA")
    g2, _ = d.text("Ink & Gold", x0 + 54, top + 41, 11.5, INTER, "#9A968E")
    d.add(phase(3.1, 5.6, art(x0 + 10, top + 8, 40) + g1 + g2 + bars(cx + 112, top + 28, 18)))
    # panneau ouvert : pochette, titres, progression, commandes
    x0 = cx - 180
    g1, _ = d.text("West Lake", x0 + 86, top + 38, 16, INTER_B, "#F4F1EA")
    g2, _ = d.text("Ink & Gold", x0 + 86, top + 58, 13, INTER, "#9A968E")
    t1, _ = d.text("1:02", x0 + 18, top + 101, 11.5, INTER, "#9A968E")
    t2, _ = d.text("-2:57", x0 + 342, top + 101, 11.5, INTER, "#9A968E", anchor="end")
    bx, bw = x0 + 54, 246
    prog = (f'<rect x="{bx}" y="{top+94}" width="{bw}" height="5" rx="2.5" fill="#2A2A2E"/>'
            f'<rect x="{bx}" y="{top+94}" width="64" height="5" rx="2.5" fill="#D9C3A0">'
            f'<animate attributeName="width" values="64;64;96;96" keyTimes="0;{5.9/T:.3f};{10.6/T:.3f};1" dur="{T}s" repeatCount="indefinite"/></rect>')
    cy2 = top + 134
    ctl = (f'<path d="M{cx-58} {cy2} l9 -7 v14 z M{cx-49} {cy2} l9 -7 v14 z" fill="#F4F1EA"/>'
           f'<rect x="{cx-7}" y="{cy2-9}" width="5" height="18" rx="1.5" fill="#F4F1EA"/><rect x="{cx+3}" y="{cy2-9}" width="5" height="18" rx="1.5" fill="#F4F1EA"/>'
           f'<path d="M{cx+58} {cy2} l-9 -7 v14 z M{cx+49} {cy2} l-9 -7 v14 z" fill="#F4F1EA"/>')
    d.add(phase(6.0, 10.6, art(x0 + 18, top + 16, 56) + g1 + g2 + bars(x0 + 318, top + 34, 16) + t1 + t2 + prog + ctl))
    # compacte : pochette à gauche, ondes à droite
    d.add(phase(11.2, 14.0, art(cx - 92, top + 6, 22) + bars(cx + 70, top + 17, 14)))
    # bulle de l'heure, 8 px à droite de l'île
    def bubble(t0, t1, island_w):
        bxc = cx + island_w / 2 + 8 + 17
        g, _ = d.text("16:22", bxc, top + 21, 9.5, INTER_B, "#F4F1EA", anchor="middle")
        return phase(t0, t1, f'<circle cx="{bxc}" cy="{top+17}" r="17" fill="#000" filter="url(#shadow)"/>' + g)
    d.add(bubble(3.2, 5.6, 300), bubble(6.0, 10.6, 360), bubble(11.2, 14.0, 200))
    d.add("</g>")

    # Panneau gauche
    X = 34
    d.add(f'<path transform="translate({X-2} 26) scale(.07)" d="{SUMI_LOGO}" fill="#F4F1EA"/>')
    g, _ = d.text("NOUVEAU", X + 86, 52, 11, MONO, AMBER, ls=3); d.add(g)
    g, wn = d.text(f["name"], X, 150, 82, BEBAS, "#F4F1EA", ls=3); d.add(g)
    for i, ln in enumerate(f["pitch"]):
        g, _ = d.text(ln, X, 186 + i * 20, 13, MONO, "#B8B3A8"); d.add(g)
    for i, (slug, lbl) in enumerate([("rust", "Rust"), ("tauri", "Tauri"), ("svelte", "Svelte")]):
        xx = X + i * 78
        d.add(icon(slug, xx + 7, 243, 13, AMBER))
        g, _ = d.text(lbl, xx + 19, 247, 11.5, MONO, AMBER); d.add(g)
    g, wl = d.text(f["link"], X, 276, 11, MONO, "#F4F1EA"); d.add(g)
    d.add(arrow(X + wl + 8, 267, 8, "#F4F1EA"))
    g, _ = d.text(f["version"], L - 24, 276, 11, MONO, "#6F6B63", anchor="end"); d.add(g)
    d.add("</g>", f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14" fill="none" stroke="{AMBER}" stroke-opacity=".7"/>')
    d.save("mission-sumi")


# ───────────────────────────── TITRES DE SECTION ─────────────────────────────
def build_titles():
    W, H = 880, 64
    for fname, title in SECTIONS:
        d = Doc(W, H, title.title())
        frame(d, 12, BG, EDGE)
        d.add(f'<rect x="22" y="16" width="4" height="32" fill="{G[4]}"/>')
        g, wt = d.text(title, 40, 47, 36, BEBAS, INK, ls=2.5); d.add(g)
        x0, x1 = 40 + wt + 24, W - 22
        n = int((x1 - x0) // 9)
        rnd = random.Random(fname)
        for i in range(max(0, n)):
            lvl = rnd.choice([0, 0, 1, 1, 2, 3]) if i < n - 6 else 4 - (n - 1 - i) // 2
            d.add(f'<rect x="{x0+i*9:.0f}" y="28" width="7" height="7" rx="1.5" fill="{G[max(0,min(4,lvl))]}"/>')
        d.save(fname)


# ───────────────────────────── BOUTONS ─────────────────────────────
def build_buttons():
    W, H = 212, 52
    for fname, title, sub, glyph in BUTTONS:
        d = Doc(W, H, title.title())
        frame(d, 10, BG, G[2])
        x, y = 28, 26
        d.add(f'<rect x="{x-14}" y="{y-14}" width="28" height="28" rx="6" fill="#0B1610" stroke="{G[1]}"/>')
        if glyph == "instagram":
            d.add(icon("instagram", x, y, 15, G[4]))
        elif glyph == "in":
            g, _ = d.text("in", x, y + 7, 21, BEBAS, G[4], anchor="middle"); d.add(g)
        elif glyph == "mail":
            d.add(f'<rect x="{x-8}" y="{y-6}" width="16" height="12" rx="1.5" fill="none" stroke="{G[4]}" stroke-width="1.6"/>'
                  f'<path d="M{x-8} {y-5}L{x} {y+1}L{x+8} {y-5}" fill="none" stroke="{G[4]}" stroke-width="1.6"/>')
        else:
            d.add(f'<circle cx="{x}" cy="{y}" r="8" fill="none" stroke="{G[4]}" stroke-width="1.6"/>'
                  f'<ellipse cx="{x}" cy="{y}" rx="3.4" ry="8" fill="none" stroke="{G[4]}" stroke-width="1.3"/>'
                  f'<line x1="{x-8}" y1="{y}" x2="{x+8}" y2="{y}" stroke="{G[4]}" stroke-width="1.3"/>')
        g, _ = d.text(title, 54, 27, 21, BEBAS, INK, ls=1.6); d.add(g)
        g, _ = d.text(sub, 54, 42, 10.5, MONO, G[3]); d.add(g)
        d.add(arrow(W - 24, 18, 8, DIM))
        d.save(fname)


def build_footer():
    W, H = 880, 70
    line = "See you space cowboy..."
    d = Doc(W, H, line)
    n = len(line)
    widths = [d.width(MONO, line[:i], 16) for i in range(n + 1)]
    x = W / 2 - widths[-1] / 2
    g, _ = d.text(line, x, 42, 16, MONO, G[4])
    T = 9.0
    vals = ";".join(f"{w:.0f}" for w in widths) + f";{widths[-1]:.0f};0"
    kt = ";".join(f"{i*.07/T:.4f}" for i in range(n + 1)) + ";.85;1"
    d.defs.append(f'<clipPath id="typ"><rect x="{x-2:.0f}" y="20" width="0" height="30"><animate attributeName="width" values="{vals}" keyTimes="{kt}" '
                  f'dur="{T}s" calcMode="discrete" repeatCount="indefinite"/></rect></clipPath>')
    cur = ";".join(f"{x+w+4:.0f}" for w in widths) + f";{x+widths[-1]+4:.0f};{x+4:.0f}"
    d.add(f'<g clip-path="url(#typ)">{g}</g>',
          f'<rect y="28" width="9" height="17" fill="{G[4]}"><animate attributeName="x" values="{cur}" keyTimes="{kt}" dur="{T}s" calcMode="discrete" repeatCount="indefinite"/>'
          f'<animate attributeName="opacity" values="1;0;1" dur="1s" calcMode="discrete" repeatCount="indefinite"/></rect>')
    d.save("footer")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    print("Génération des assets :")
    build_banner(); build_radar(); build_bounty(); build_missions(); build_sumi(); build_titles(); build_buttons(); build_footer()
