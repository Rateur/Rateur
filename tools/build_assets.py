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
KICKER = "CHASSEUR DE PRIMES  //  DATA & IA"
ROLE = "Développeur IA · Master Expert IA & Data — EPSI Lyon"
PROMPT = "> alternance 2 ans · disponible maintenant"
COORDS = "SECTEUR LYON · 45.76°N  4.83°E"
EMAIL = "contact@valentinperies.fr"

STACK = [  # (catégorie, [(label, icône simple-icons ou None)])
    ("IA & ML", [("scikit-learn", "scikitlearn"), ("TensorFlow", "tensorflow"), ("Keras", "keras"),
                 ("MLflow", "mlflow"), ("LLM", None), ("MCP", "modelcontextprotocol"),
                 ("n8n", "n8n"), ("Ollama", "ollama")]),
    ("DATA", [("Python", "python"), ("Pandas", "pandas"), ("NumPy", "numpy"), ("Streamlit", "streamlit")]),
    ("BACK & MLOPS", [("FastAPI", "fastapi"), ("Flask", "flask"), ("SQL", None), ("SQLite", "sqlite"),
                      ("Docker", "docker"), ("CI/CD", "githubactions"), ("pytest", "pytest"),
                      ("Supabase", "supabase")]),
    ("INTERFACE", [("React", "react"), ("Next.js", "nextdotjs"), ("Three.js", "threedotjs"),
                   ("WebGL", "webgl")]),
]

MISSIONS = [  # id, nom, type, statut, (ligne1, ligne2), kpi, kpi_label, lien affiché
    ("01", "NUTRI-PREDICT", "FULL-STACK", "LIVRÉ",
     ("Prédit la variation de poids d'une portion.", "Projet de certification RNCP 2026."),
     "R² 0,985", "données simulées · régression lin. 0,959", "certification RNCP 2026"),
    ("02", "WILDAIPRINT", "VISION", "RE-TESTÉ",
     ("CNN + app. Fuite de données trouvée,", "corrigée, puis re-test sur 38 vraies photos."),
     "83 % » 26 %", "annoncé, puis mesuré sur un vrai jeu de test", "Rateur/WildAIprint-Modele-CNN"),
    ("03", "OBSERVATOIRE PARITÉ", "DATA", "DÉPLOYÉ",
     ("Temps de parole femmes / hommes à la TV.", "Open data, dataviz, site en ligne."),
     "33 / 35", "chaînes où les femmes parlent < 50 % (2020)", "opendata2025.netlify.app"),
    ("04", "IA DE FAMILLE", "IA LOCALE", "EN COURS",
     ("Assistant sur le NAS de la maison.", "Ollama, un RAG par personne."),
     "0 OCTET", "envoyé dans le cloud", "projet perso · réseau local"),
    ("05", "SEVENARTLIST", "FULL-STACK", "EN COURS",
     ("Trouver un film, voir où le regarder,", "suivre sa watchlist."),
     "NEXT.JS + SUPABASE", "front, auth et base de données", "Rateur/SevenArtList"),
    ("06", "MISSION SUIVANTE", "ALTERNANCE", "OUVERT",
     ("Votre équipe, vos données, deux ans.", "Lyon, hybride ou télétravail."),
     "VOTRE PROJET ICI", "écrivez-moi, je réponds vite", EMAIL),
]

SECTIONS = [  # fichier, session, titre, sous-titre
    ("title-transmission", "01", "TRANSMISSION", "qui est à bord"),
    ("title-missions", "02", "MISSIONS", "journal de bord"),
    ("title-radar", "03", "RADAR", "stack détectée"),
    ("title-signal", "04", "SIGNAL", "activité sur la grille"),
    ("title-soundtrack", "05", "BANDE-SON", "en écoute"),
]

FEATURE = {  # mission mise en avant (pleine largeur)
    "id": "07", "name": "SUMI", "type": "REACT", "status": "EN COURS",
    "lines": ("Mon nouveau projet, construit en React.", "Démo et détails à venir."),
    "kpi": "REACT", "kpi_label": "composants, hooks, état côté client", "link": "bientôt en ligne",
}
FEATURED_TECH = {"React"}

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
    W, H, P, C = 1280, 360, 13, 10
    cols, rows = 98, 27
    ox, oy = (W - (cols * P - 3)) / 2, (H - (rows * P - 3)) / 2
    cx = lambda c: ox + c * P
    cy = lambda r: oy + r * P
    rnd = random.Random(7)
    d = Doc(W, H, f"{NAME_1.title()} Périès, développeur IA à Lyon, en recherche d'alternance")
    d.defs.append(f'<clipPath id="card"><rect width="{W}" height="{H}" rx="16"/></clipPath>')
    d.defs.append('<linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="#0D1117" stop-opacity=".96"/>'
                  '<stop offset=".42" stop-color="#0D1117" stop-opacity=".82"/><stop offset=".62" stop-color="#0D1117" stop-opacity="0"/></linearGradient>')
    d.defs.append('<radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".6" stop-color="#000" stop-opacity="0"/>'
                  '<stop offset="1" stop-color="#000" stop-opacity=".55"/></radialGradient>')
    d.defs.append('<radialGradient id="bloom" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#72FF72" stop-opacity=".22"/>'
                  '<stop offset="1" stop-color="#72FF72" stop-opacity="0"/></radialGradient>')
    grid_pattern(d, P, C, ox, oy)
    d.add(f'<rect width="{W}" height="{H}" rx="16" fill="{BG}"/>', '<g clip-path="url(#card)">',
          f'<rect width="{W}" height="{H}" fill="url(#grid)"/>')

    def cell(c, r, lvl, extra="", op=1):
        return (f'<rect x="{cx(c):.1f}" y="{cy(r):.1f}" width="{C}" height="{C}" rx="2" fill="{G[lvl]}"'
                + (f' opacity="{op}"' if op != 1 else "") + f'{extra}/>')

    # Planète tramée + anneau
    pc, pr, R = 84, 8, 6.4
    planet, ring_back, ring_front = [], [], []
    lx, ly, lz = -.55, -.6, .58
    for c in range(int(pc - R - 1), int(pc + R + 2)):
        for r in range(int(pr - R - 1), int(pr + R + 2)):
            dx, dy = c - pc, r - pr
            if dx * dx + dy * dy <= R * R:
                nz = math.sqrt(max(0, 1 - (dx * dx + dy * dy) / (R * R)))
                lam = max(0, (dx / R) * lx + (dy / R) * ly + nz * lz)
                lvl = 1 + min(3, int(lam * 3.6 + rnd.random() * .5))
                if rnd.random() < .06: lvl = max(1, lvl - 2)
                planet.append(cell(c, r, lvl))
    tilt = math.radians(-14)
    seen = set()
    for i in range(720):
        a = i / 720 * 2 * math.pi
        x, y = 12.5 * math.cos(a), 2.6 * math.sin(a)
        xr, yr = x * math.cos(tilt) - y * math.sin(tilt), x * math.sin(tilt) + y * math.cos(tilt)
        c, r = round(pc + xr), round(pr + yr)
        if (c, r) in seen: continue
        seen.add((c, r))
        inside = (c - pc) ** 2 + (r - pr) ** 2 <= R * R
        front = math.sin(a) > 0
        if inside and not front: continue
        (ring_front if front else ring_back).append(cell(c, r, (1 if inside else 3) if front else 2))
    d.add(f'<circle cx="{cx(pc)+5}" cy="{cy(pr)+5}" r="140" fill="url(#bloom)"/>')
    d.add(*ring_back, *planet, *ring_front)

    # Étoiles qui scintillent (des contributions)
    occupied = seen | {(c, r) for c in range(77, 92) for r in range(0, 16)}
    for _ in range(95):
        c, r = rnd.randrange(cols), rnd.randrange(rows)
        if (c, r) in occupied: continue
        lvl = rnd.choice([1, 1, 1, 2, 2, 3, 4])
        if rnd.random() < .55:
            dur = rnd.uniform(2.5, 6)
            anim = (f'><animate attributeName="opacity" values="1;.15;1" dur="{dur:.1f}s" '
                    f'begin="-{rnd.uniform(0, dur):.1f}s" repeatCount="indefinite"/></rect>')
            d.add(cell(c, r, lvl)[:-2] + anim)
        else:
            d.add(cell(c, r, lvl))

    # Porte hyperespace + vaisseau original (sprite sur la grille)
    gate_c, gate_r = 47, 18
    gate = []
    for i in range(180):
        a = i / 180 * 2 * math.pi
        c, r = round(gate_c + 1.6 * math.cos(a)), round(gate_r + 6.2 * math.sin(a))
        if (c, r) not in gate: gate.append((c, r))
    step, n_steps = .11, 58
    T = step * n_steps + 1.6
    flash = (f'<animate attributeName="fill" values="{G[4]};{G[2]};{G[2]}" keyTimes="0;.25;1" '
             f'dur="{T:.2f}s" repeatCount="indefinite"/>')
    for c, r in gate:
        d.add(cell(c, r, 2)[:-2] + ">" + flash + "</rect>")

    SHIP = ["....33........",
            "..22444.......",
            "2222444444....",
            "111144444455R.",
            "2222444444....",
            "..22444.......",
            "....33........"]
    sprite = []
    for r, row in enumerate(SHIP):
        for c, ch in enumerate(row):
            if ch == ".": continue
            if ch == "R":
                sprite.append(f'<rect x="{c*P}" y="{r*P}" width="{C}" height="{C}" rx="2" fill="{INK}"/>')
            else:
                lvl = {"1": 2, "2": 2, "3": 3, "4": 4, "5": 4}[ch]
                fill = G[lvl] if ch != "5" else INK
                sprite.append(f'<rect x="{c*P}" y="{r*P}" width="{C}" height="{C}" rx="2" fill="{fill}"/>')
    start_c, ship_row = gate_c - 12, gate_r - 3
    vals = ";".join(f"{k*P} 0" for k in range(n_steps + 1)) + f";{n_steps*P} 0"
    kt = ";".join(f"{k*step/T:.4f}" for k in range(n_steps + 1)) + ";1"
    d.defs.append(f'<clipPath id="out"><rect x="{cx(gate_c)+4}" y="0" width="{W}" height="{H}"/></clipPath>')
    # Traînée : chaque cellule s'allume quand la tuyère passe, puis s'éteint (persistance phosphore)
    trail = []
    for k in range(n_steps):
        col = start_c + k + 1
        if col <= gate_c: continue
        t0 = k * step
        for dr, lvl, life in [(0, 4, 1.8), (-1, 3, 1.1), (1, 3, 1.1), (-2, 1, .6), (2, 1, .6)]:
            if abs(dr) == 2 and rnd.random() < .5: continue
            if abs(dr) == 1 and rnd.random() < .25: continue
            kt1, kt2 = .01, min(.98, life / T)
            trail.append(f'<rect x="{cx(col):.1f}" y="{cy(gate_r+dr):.1f}" width="{C}" height="{C}" rx="2" fill="{G[lvl]}" opacity="0">'
                         f'<animate attributeName="opacity" values="0;1;0;0" keyTimes="0;{kt1};{kt2:.3f};1" dur="{T:.2f}s" '
                         f'begin="{t0:.2f}s" repeatCount="indefinite"/></rect>')
    d.add('<g clip-path="url(#out)">', *trail,
          f'<g transform="translate({cx(start_c):.1f} {cy(ship_row):.1f})"><g>'
          f'<animateTransform attributeName="transform" type="translate" values="{vals}" keyTimes="{kt}" '
          f'calcMode="discrete" dur="{T:.2f}s" repeatCount="indefinite"/>' + "".join(sprite) + "</g></g></g>")

    # Voile de lisibilité + typographie façon générique jazz 70s
    d.add(f'<rect width="{W}" height="{H}" fill="url(#fade)"/>')
    X = 58
    g, _ = d.text(KICKER, X, 74, 13, MONO, G[3], ls=2.4)
    d.add(f'<g opacity="0">{g}<animate attributeName="opacity" from="0" to="1" begin=".1s" dur=".5s" fill="freeze"/></g>')
    g1, w1 = d.text(NAME_1, X, 170, 108, BEBAS, INK, ls=3)
    d.add(f'<g opacity="0" transform="translate(0 18)">{g1}'
          f'<animate attributeName="opacity" from="0" to="1" begin=".2s" dur=".6s" fill="freeze"/>'
          f'<animateTransform attributeName="transform" type="translate" from="0 18" to="0 0" begin=".2s" dur=".7s" fill="freeze" {EASE} keyTimes="0;1"/></g>')
    g2, w2 = d.text(NAME_2, X + 14, 278, 108, BEBAS, BG, ls=3)
    bw, by, bh = w2 + 30, 186, 104
    d.defs.append(f'<clipPath id="blk"><rect x="{X}" y="{by}" width="0" height="{bh}">'
                  f'<animate attributeName="width" from="0" to="{bw:.0f}" begin=".55s" dur=".6s" fill="freeze" {EASE} keyTimes="0;1"/></rect></clipPath>')
    d.add(f'<rect x="{X+9}" y="{by+9}" width="{bw:.0f}" height="{bh}" fill="none" stroke="{G[2]}" stroke-width="1.5" opacity="0">'
          f'<animate attributeName="opacity" from="0" to="1" begin="1.05s" dur=".4s" fill="freeze"/></rect>',
          f'<g clip-path="url(#blk)"><rect x="{X}" y="{by}" width="{bw:.0f}" height="{bh}" fill="{G[4]}"/>{g2}</g>')
    kx = X + max(w1, bw + 9) + 30
    d.add(d.vtext(KATAKANA, kx, 104, 17, JP, G[3], step=18.5,
                  extra='opacity="0"><animate attributeName="opacity" from="0" to=".9" begin="1.2s" dur=".8s" fill="freeze"/'))
    g, _ = d.text(ROLE, X, 324, 15.5, MONO, INK)
    d.add(f'<g opacity="0">{g}<animate attributeName="opacity" from="0" to="1" begin="1.1s" dur=".5s" fill="freeze"/></g>')
    # Ligne de prompt tapée lettre par lettre
    gp, wp = d.text(PROMPT, X, 350 - 2, 14, MONO, G[4])
    n = len(PROMPT)
    widths = [d.width(MONO, PROMPT[:i], 14) for i in range(n + 1)]
    d.defs.append(f'<clipPath id="typ"><rect x="{X-2}" y="330" width="0" height="24">'
                  f'<animate attributeName="width" values="{";".join(f"{w+2:.0f}" for w in widths)}" '
                  f'begin="1.6s" dur="{n*.045:.2f}s" calcMode="discrete" fill="freeze"/></rect></clipPath>')
    d.add(f'<g clip-path="url(#typ)">{gp}</g>')
    d.add(f'<rect x="{X+wp+5:.0f}" y="336" width="8" height="14" fill="{G[4]}" opacity="0">'
          f'<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;.01;.5;.51;1" dur="1.05s" begin="{1.6+n*.045:.2f}s" repeatCount="indefinite"/></rect>')

    # Détails : coordonnées + légende Less/More (clin d'œil à la grille GitHub)
    g, _ = d.text(COORDS, W - 40, 34, 11, MONO, DIM, ls=1.5, anchor="end")
    d.add(g)
    lx0 = W - 40 - 5 * 13 - 34
    g, _ = d.text("Less", lx0 - 6, H - 22, 11, MONO, DIM, anchor="end")
    d.add(g, *[f'<rect x="{lx0 + i*13}" y="{H-31}" width="10" height="10" rx="2" fill="{G[i]}" stroke="{EDGE}" stroke-width=".5"/>' for i in range(5)])
    g, _ = d.text("More", lx0 + 5 * 13 + 4, H - 22, 11, MONO, DIM)
    d.add(g)
    d.add(f'<rect width="{W}" height="{H}" fill="url(#vig)"/>', "</g>")
    scanlines(d, .09)
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
            for rf in [.40, .58, .76, .90, .49, .67, .83, .32]:
                bx, by = pol(a, R * rf)
                lx0 = bx + 14 if right else bx - 14 - lw
                b = (min(bx - 12, lx0) - 3, by - 13, max(bx + 12, lx0 + lw) + 3, by + 13)
                if lx0 < 10 or lx0 + lw > cx + R + 30: continue
                if math.hypot(bx - cx, by - cy) > R - 12: continue
                if not hit(b):
                    best = (bx, by, b); break
            if best is None:
                bx, by = pol(a, R * .6); best = (bx, by, (bx-12, by-12, bx+12, by+12))
            bx, by, b = best
            boxes.append(b)
            t = a / 360 * DUR
            begin = f"{t - DUR:.2f}s"
            ico = icon(slug, bx, by, 13, G[4]) if slug else cells_glyph(bx, by, 11, G[4])
            star = label in FEATURED_TECH
            gl, wl = d.text(label, bx + (14 if right else -14), by + 4, 13 if star else 11.5, MONO, AMBER if star else INK, anchor="start" if right else "end")
            if star:
                ico = icon(slug, bx, by, 15, AMBER)
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
    g, _ = d.text("CONTACTS DÉTECTÉS", X, 58, 12, MONO, G[3], ls=2.4); d.add(g)
    total = sum(len(i) for _, i in STACK)
    g, _ = d.text(f"{total:02d}", W - 44, 62, 30, BEBAS, G[4], anchor="end"); d.add(g)
    d.add(f'<line x1="{X}" y1="74" x2="{W-44}" y2="74" stroke="{EDGE}"/>')
    y = 108
    for (cat, items), (s0, s1) in zip(STACK, sectors):
        g, wc = d.text(cat, X, y, 24, BEBAS, INK, ls=1); d.add(g)
        g, _ = d.text(f"{s0:03d}°–{s1:03d}°", W - 44, y - 2, 11, MONO, DIM, anchor="end"); d.add(g)
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
        y += 40 + 18 * len(lines) + 12
    g, wv = d.text("balayage actif · tous systèmes nominaux", X + 14, H - 34, 11.5, MONO, DIM); d.add(g)
    d.add(f'<circle cx="{X+4}" cy="{H-38}" r="4" fill="{G[4]}"><animate attributeName="opacity" values="1;.2;1" dur="1.6s" repeatCount="indefinite"/></circle>')
    scanlines(d, .08)
    d.save("radar")


# ───────────────────────────── AVIS DE PRIME ─────────────────────────────
def build_bounty():
    W, H = 880, 290
    d = Doc(W, H, "Avis de prime : Valentin Périès cherche une alternance de 2 ans en IA et data, Lyon, hybride ou télétravail, disponible maintenant")
    frame(d)
    # bandeau
    d.add(f'<path d="M1 17a16 16 0 0 1 16-16h846a16 16 0 0 1 16 16v23H1z" fill="#0B1610"/>',
          f'<line x1="1" y1="40" x2="{W-1}" y2="40" stroke="{G[1]}"/>')
    g, _ = d.text("AVIS DE PRIME  N° 2026-LYN-01", 26, 26, 11.5, MONO, DIM, ls=2); d.add(g)
    g, w = d.text("TRANSMISSION ACTIVE", W - 26, 26, 11.5, MONO, G[4], ls=2, anchor="end"); d.add(g)
    d.add(f'<circle cx="{W-26-w-12:.0f}" cy="22" r="4" fill="{G[4]}"><animate attributeName="opacity" values="1;.15;1" dur="1.2s" repeatCount="indefinite"/></circle>')
    # identicon (style GitHub) généré depuis le pseudo
    h = hashlib.md5(b"Rateur").digest()
    P, C, X0, Y0 = 22, 18, 34, 66
    for r in range(7):
        for c in range(4):
            bit = (h[(r * 4 + c) % 16] >> (c % 8)) & 1
            lvl = 1 + (h[(r * 3 + c) % 16] % 4) if bit else 0
            for cc in {c, 6 - c}:
                d.add(f'<rect x="{X0+cc*P}" y="{Y0+r*P}" width="{C}" height="{C}" rx="3" fill="{G[lvl]}"/>')
    d.defs.append(f'<linearGradient id="sweep" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{G[4]}" stop-opacity="0"/>'
                  f'<stop offset="1" stop-color="{G[4]}" stop-opacity=".45"/></linearGradient>')
    d.defs.append(f'<clipPath id="idc"><rect x="{X0-4}" y="{Y0-4}" width="{7*P+4}" height="{7*P+4}"/></clipPath>')
    d.add(f'<rect clip-path="url(#idc)" x="{X0-6}" y="{Y0}" width="{7*P+8}" height="26" fill="url(#sweep)">'
          f'<animate attributeName="y" values="{Y0-26};{Y0+7*P};{Y0+7*P}" keyTimes="0;.7;1" dur="3.2s" repeatCount="indefinite"/></rect>',
          f'<rect x="{X0-10}" y="{Y0-10}" width="{7*P+16}" height="{7*P+16}" rx="6" fill="none" stroke="{G[1]}"/>')
    g, _ = d.text("ID : RATEUR", X0 + 7 * P / 2 - 2, Y0 + 7 * P + 34, 11.5, MONO, DIM, ls=2, anchor="middle"); d.add(g)
    # titre
    X = 250
    g, _ = d.text("CONTRAT RECHERCHÉ", X, 104, 50, BEBAS, INK, ls=2); d.add(g)
    g2, w2 = d.text("ALTERNANCE · 2 ANS", X + 12, 146, 30, BEBAS, BG, ls=2)
    d.add(f'<rect x="{X}" y="116" width="{w2+24:.0f}" height="38" fill="{G[4]}"/>', g2)
    rows = [("CHASSEUR", "Valentin Périès — développeur IA"),
            ("FORMATION", "Master Expert IA & Data Science · EPSI Lyon"),
            ("ZONE", "Lyon · hybride · télétravail"),
            ("DÉPART", "dès maintenant")]
    for i, (k, v) in enumerate(rows):
        y = 188 + i * 22
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
        g, _ = d.text(f"SESSION #{mid}", 24, 34, 11.5, MONO, DIM, ls=2); d.add(g)
        live = status in ("EN COURS", "OUVERT")
        col = AMBER if live else G[4]
        g, ws = d.text(status, W - 24, 34, 11.5, MONO, col, ls=1.5, anchor="end"); d.add(g)
        blink = f'<animate attributeName="opacity" values="1;.2;1" dur="1.4s" repeatCount="indefinite"/>' if live else ""
        d.add(f'<circle cx="{W-24-ws-10:.1f}" cy="30" r="3.6" fill="{col}">{blink}</circle>')
        g, wn = d.text(name, 24, 76, 36, BEBAS, INK, ls=1.2); d.add(g)
        g, _ = d.text(f"[{typ}]", 24 + wn + 12, 74, 11.5, MONO, G[3]); d.add(g)
        g, _ = d.text(l1, 24, 102, 12.5, MONO, "#B9CFBC"); d.add(g)
        g, _ = d.text(l2, 24, 120, 12.5, MONO, "#B9CFBC"); d.add(g)
        d.add(f'<line x1="24" y1="136" x2="{W-24}" y2="136" stroke="{EDGE}"/>')
        g, wk = d.text(kpi, 24, 172, 28, BEBAS, G[4], ls=1); d.add(g)
        g, _ = d.text(kpi_lbl, 24, 192, 10.5, MONO, DIM); d.add(g)
        clickable = link.startswith(("Rateur/", "opendata", "contact"))
        g, wl = d.text(link if len(link) < 34 else link[:31] + "…", W - 24 - (16 if clickable else 0), 168, 10.5, MONO,
                       G[3] if clickable else DIM, anchor="end")
        d.add(g)
        if clickable:
            d.add(arrow(W - 34, 160, 8, G[3]))
        # petite rangée de cellules : signature de la mission
        rnd = random.Random(mid)
        for i in range(12):
            d.add(f'<rect x="{W-24-12*9+i*9+1}" y="184" width="7" height="7" rx="1.5" fill="{G[rnd.choice([0,1,1,2,3,4])]}"/>')
        scanlines(d, .07)
        d.save(f"mission-{mid}")


def build_feature():
    f = FEATURE
    W, H = 880, 176
    d = Doc(W, H, f"Mission en avant : {f['name'].title()} — {' '.join(f['lines'])}")
    frame(d, 14, BG, AMBER)
    d.add(f'<rect x="1" y="1" width="150" height="{H-2}" rx="13" fill="#141008"/>',
          f'<line x1="151" y1="1" x2="151" y2="{H-1}" stroke="#3A2C12"/>')
    g, _ = d.text("NOUVEAU", 76, 52, 12, MONO, AMBER, ls=3, anchor="middle"); d.add(g)
    g, _ = d.text(f["id"], 76, 128, 72, BEBAS, AMBER, ls=2, anchor="middle"); d.add(g)
    g, _ = d.text("SESSION", 76, 152, 10.5, MONO, "#8A7344", ls=3, anchor="middle"); d.add(g)
    X = 180
    g, wn = d.text(f["name"], X, 70, 46, BEBAS, INK, ls=2); d.add(g)
    g, _ = d.text(f"[{f['type']}]", X + wn + 14, 66, 12, MONO, AMBER); d.add(g)
    g, ws = d.text(f["status"], W - 28, 38, 11.5, MONO, AMBER, ls=1.5, anchor="end"); d.add(g)
    d.add(f'<circle cx="{W-28-ws-10:.1f}" cy="34" r="3.6" fill="{AMBER}"><animate attributeName="opacity" values="1;.2;1" dur="1.4s" repeatCount="indefinite"/></circle>')
    for i, ln in enumerate(f["lines"]):
        g, _ = d.text(ln, X, 100 + i * 19, 13.5, MONO, "#B9CFBC"); d.add(g)
    d.add(icon("react", W - 110, 108, 64, AMBER).replace('fill="', 'opacity=".9" fill="'))
    d.add(f'<g><animateTransform attributeName="transform" type="rotate" from="0 {W-110} 108" to="360 {W-110} 108" dur="18s" repeatCount="indefinite"/>'
          f'<circle cx="{W-110}" cy="108" r="46" fill="none" stroke="{AMBER}" stroke-opacity=".5" stroke-dasharray="3 6"/></g>')
    g, _ = d.text(f["kpi_label"], X, 152, 11, MONO, DIM); d.add(g)
    g, _ = d.text(f["link"], W - 190, 152, 11, MONO, DIM, anchor="end"); d.add(g)
    scanlines(d, .07)
    d.save("mission-sumi")


# ───────────────────────────── TITRES DE SECTION ─────────────────────────────
def build_titles():
    W, H = 880, 64
    for fname, sess, title, sub in SECTIONS:
        d = Doc(W, H, f"{title.title()} — {sub}")
        frame(d, 12, BG, EDGE)
        g, _ = d.text(f"SESSION #{sess}", 22, 39, 11, MONO, DIM, ls=2.2); d.add(g)
        d.add(f'<rect x="124" y="16" width="4" height="32" fill="{G[4]}"/>')
        g, wt = d.text(title, 142, 47, 36, BEBAS, INK, ls=2.5); d.add(g)
        g, ws = d.text(f"// {sub}", W - 22, 39, 12, MONO, G[3], anchor="end"); d.add(g)
        x0, x1 = 142 + wt + 22, W - 22 - ws - 22
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


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    print("Génération des assets :")
    build_banner(); build_radar(); build_bounty(); build_missions(); build_feature(); build_titles(); build_buttons()
