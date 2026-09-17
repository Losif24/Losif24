# Genera las piezas del perfil. Dos idiomas, una sola paleta: la de GitHub en oscuro.
#
# Criterio de diseño, para no volver a caer en la plantilla:
#   - Tipografía ELEGIDA, no la del sistema. Tres familias con un papel cada una:
#       Archivo Black  -> el nombre y las cifras. Lo que debe pesar.
#       Space Grotesk  -> títulos y texto corrido.
#       JetBrains Mono -> etiquetas pequeñas y datos.
#     Las tres van incrustadas en el SVG (base64), recortadas a los caracteres
#     que cada pieza usa: no dependen de la red ni de lo que tenga el visitante.
#   - El apellido va EN CONTORNO, sin relleno. Es el gesto de la pieza.
#   - Nada de pastillas ni emojis: el stack es una lista tipográfica.
#   - Las bandas no son todas iguales; cambian de altura, densidad y ritmo.
#   - El único color es el blanco: el contraste lo hacen el tamaño y el peso.
#
# Uso:  python assets/generate.py      (pide las cifras a GitHub si tienes `gh`)

import base64
import datetime
import io
import json
import os
import subprocess

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

NAME_FIRST, NAME_LAST = "JOSÉ", "DURÁN"
CITY = "BOGOTÁ · COLOMBIA"
ROLE = "SOFTWARE DEVELOPER"
USER = "Losif24"
RELEASE_REPOS = ["TradingTuff", "chimera-releases"]
FALLBACK = dict(releases=180, downloads=214, since=2022, tradingtuff=202, chimera=12)

COPY = {
    "en": dict(
        claim="I build things that ship: desktop apps, the backends behind them, and the plumbing in between.",
        disciplines=[("BACKEND", "Python · FastAPI · SQLite"),
                     ("DESKTOP", "C++17 · Qt 6 · WPF"),
                     ("SYSTEMS", "Win32 · ConPTY · WebSocket")],
        stack=[("DESKTOP", "C++17 · Qt 6 · C# / WPF · PySide6 · Win32 / ConPTY"),
               ("MOBILE", "Kotlin · Jetpack Compose · Material 3 · Android SDK"),
               ("BACKEND", "Python · FastAPI · SQLite · Supabase · WebSocket"),
               ("WEB", "TypeScript · React · HTML / CSS"),
               ("DELIVERY", "Git · CMake / MSBuild · Inno Setup · OpenCV")],
        open_label="OPEN ↗",
        stats=[("releases", "VERSIONS SHIPPED"), ("downloads", "INSTALLER DOWNLOADS"),
               ("since", "ON GITHUB SINCE")],
        asof="measured {d}",
        projects=[
            ("chimera", "01", "CHIMERA",
             "A desktop environment for reading someone else's codebase — or your own, six "
             "months later. It indexes the project and draws what depends on what.",
             "Python · Qt 6 · QML", "chimera", "RELEASES"),
            ("tradingtuff", "02", "TRADING TUFF",
             "A Windows terminal for reading a market in real time: live data, a chart engine "
             "written from scratch, and the context around the price in one screen.",
             "C++17 · Qt 6 · SQLite", "tradingtuff", "DOWNLOADS"),
        ],
    ),
    "es": dict(
        claim="Construyo cosas que se entregan: apps de escritorio, su backend y la fontanería del medio.",
        disciplines=[("BACKEND", "Python · FastAPI · SQLite"),
                     ("ESCRITORIO", "C++17 · Qt 6 · WPF"),
                     ("SISTEMAS", "Win32 · ConPTY · WebSocket")],
        stack=[("ESCRITORIO", "C++17 · Qt 6 · C# / WPF · PySide6 · Win32 / ConPTY"),
               ("MÓVIL", "Kotlin · Jetpack Compose · Material 3 · Android SDK"),
               ("BACKEND", "Python · FastAPI · SQLite · Supabase · WebSocket"),
               ("WEB", "TypeScript · React · HTML / CSS"),
               ("ENTREGA", "Git · CMake / MSBuild · Inno Setup · OpenCV")],
        open_label="ABRIR ↗",
        stats=[("releases", "VERSIONES PUBLICADAS"), ("downloads", "DESCARGAS"),
               ("since", "EN GITHUB DESDE")],
        asof="medido el {d}",
        projects=[
            ("chimera", "01", "CHIMERA",
             "Un entorno de escritorio para leer el código de otro — o el tuyo, seis meses "
             "después. Indexa el proyecto y dibuja de qué depende cada archivo.",
             "Python · Qt 6 · QML", "chimera", "VERSIONES"),
            ("tradingtuff", "02", "TRADING TUFF",
             "Una terminal de Windows para leer un mercado en vivo: datos en tiempo real, un "
             "motor de gráfico escrito desde cero y todo el contexto en una pantalla.",
             "C++17 · Qt 6 · SQLite", "tradingtuff", "DESCARGAS"),
        ],
    ),
}

BG, INK, MUTED, DIM, RULE = "#0D1117", "#FFFFFF", "#8B949E", "#5A626C", "#262C36"
XMLDECL = '<?xml version="1.0" encoding="UTF-8"?>'
W, M = 880, 56
HERE = os.path.dirname(os.path.abspath(__file__))
FONTDIR = os.path.join(HERE, "fonts")

# Cada papel tipográfico: su archivo, el peso al que se fija la variable, y el respaldo
# por si el visitante usa un navegador que no admite fuentes incrustadas en SVG.
FACES = {
    "display": dict(file="ArchivoBlack-Regular.ttf", wght=None, family="TuffDisplay",
                    fallback="'Arial Black', Impact, sans-serif"),
    "sans":    dict(file="SpaceGrotesk.ttf", wght=400, family="TuffSans",
                    fallback="'Segoe UI', Helvetica, Arial, sans-serif"),
    "sansb":   dict(file="SpaceGrotesk.ttf", wght=700, family="TuffSansBold",
                    fallback="'Segoe UI Semibold', Helvetica, Arial, sans-serif"),
    "mono":    dict(file="JetBrainsMono.ttf", wght=500, family="TuffMono",
                    fallback="Consolas, 'Liberation Mono', monospace"),
}

_used = {}          # papel -> caracteres usados en la pieza que se está construyendo
_cache = {}         # (papel, caracteres) -> base64, para no recortar dos veces lo mismo


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def embed(face_key, chars):
    """Recorta la fuente a esos caracteres y la devuelve en base64 woff2."""
    key = (face_key, chars)
    if key in _cache:
        return _cache[key]
    spec = FACES[face_key]
    font = TTFont(os.path.join(FONTDIR, spec["file"]))
    if spec["wght"] is not None and "fvar" in font:
        font = instancer.instantiateVariableFont(font, {"wght": spec["wght"]}, inplace=False)
    opts = subset.Options(layout_features=["*"], notdef_outline=True)
    opts.drop_tables += ["DSIG"]
    sub = subset.Subsetter(options=opts)
    sub.populate(text=chars)
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    _cache[key] = base64.b64encode(buf.getvalue()).decode("ascii")
    return _cache[key]


def fontcss():
    """Bloque @font-face con solo las familias que esta pieza usa de verdad."""
    rules = []
    for key in sorted(_used):
        chars = "".join(sorted(set(_used[key])))
        if not chars.strip():
            continue
        spec = FACES[key]
        rules.append(f"@font-face{{font-family:'{spec['family']}';font-style:normal;"
                     f"font-weight:400;src:url(data:font/woff2;base64,{embed(key, chars)}) "
                     f"format('woff2')}}")
    return f"<defs><style>{''.join(rules)}</style></defs>" if rules else ""


def txt(x, y, s, size, fill="none", face="sans", sp=None, anchor=None, opacity=None,
        stroke=None, sw=None):
    _used.setdefault(face, set()).update(s)
    spec = FACES[face]
    a = [f'x="{x}"', f'y="{y}"', f'font-family="{spec["family"]}, {spec["fallback"]}"',
         f'font-size="{size}"', f'fill="{fill}"']
    if sp is not None:
        a.append(f'letter-spacing="{sp}"')
    if anchor:
        a.append(f'text-anchor="{anchor}"')
    if opacity is not None:
        a.append(f'opacity="{opacity}"')
    if stroke:
        a.append(f'stroke="{stroke}" stroke-width="{sw}"')
    return f'<text {" ".join(a)}>{esc(s)}</text>'


def hline(x1, y, x2, color=RULE, w=1):
    return f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{color}" stroke-width="{w}"/>'


def start(h, label, texture=False):
    _used.clear()
    p = [XMLDECL,
         f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" '
         f'role="img" aria-label="{esc(label)}">',
         "@@FONTS@@"]
    if texture:
        # Rejilla a media tinta: da profundidad al negro plano sin meter un solo color.
        p.append('<defs><pattern id="g" width="28" height="28" patternUnits="userSpaceOnUse">'
                 f'<path d="M28 0H0V28" fill="none" stroke="{INK}" stroke-width="0.5" opacity="0.05"/>'
                 '</pattern></defs>')
    p.append(f'<rect width="{W}" height="{h}" fill="{BG}"/>')
    if texture:
        p.append(f'<rect width="{W}" height="{h}" fill="url(#g)"/>')
    return p


def end(p):
    p.append("</svg>")
    return "\n".join(p).replace("@@FONTS@@", fontcss())


def wrap(text, limit):
    lines, line = [], ""
    for word in text.split():
        probe = f"{line} {word}".strip()
        if len(probe) > limit:
            lines.append(line)
            line = word
        else:
            line = probe
    lines.append(line)
    return lines


def hero(c):
    H = 300
    right = W - M
    p = start(H, f"{NAME_FIRST} {NAME_LAST} — {ROLE}", texture=True)
    p.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" fill="none" stroke="{RULE}"/>')
    p.append(txt(M, 46, ROLE, 10, MUTED, "mono", sp=4))
    p.append(txt(right, 46, CITY, 10, MUTED, "mono", sp=2, anchor="end"))
    p.append(hline(M, 60, right))

    # El nombre en dos lineas: el apellido va en contorno. Ese hueco es el gesto de la pieza.
    p.append(txt(M, 152, NAME_FIRST, 76, INK, "display", sp=-2))
    p.append(txt(M, 228, NAME_LAST, 76, "none", "display", sp=-2, stroke=INK, sw=1.3))

    for i, (label, tech) in enumerate(c["disciplines"]):
        y = 118 + i * 48
        p.append(hline(560, y - 26, right))
        p.append(txt(right, y - 8, label, 9.5, MUTED, "mono", sp=2.6, anchor="end"))
        p.append(txt(right, y + 12, tech, 13, MUTED, "sans", anchor="end"))

    p.append(hline(M, 254, right))
    p.append(txt(M, 278, c["claim"], 13.5, MUTED, "sans"))
    return end(p)


def stack(c):
    ROW = 44
    H = 14 + len(c["stack"]) * ROW + 10
    p = start(H, "Stack")
    y = 14
    for i, (label, techs) in enumerate(c["stack"]):
        if i:
            p.append(hline(M, y, W - M))
        p.append(txt(M, y + 28, label, 9.5, MUTED, "mono", sp=2.8))
        p.append(txt(M + 152, y + 28, techs, 14.5, INK, "sans"))
        y += ROW
    return end(p)


def card(c, project, data):
    """Ficha de proyecto: ordinal al fondo, una cifra real a la derecha, toda ella pulsable."""
    _slug, num, title, desc, tech, metric_key, metric_label = project
    BOX, GAP = 132, 12
    right = W - M
    p = start(BOX + GAP, f"{title} — {desc}")
    p.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{BOX-1}" fill="none" stroke="{RULE}"/>')
    p.append(f'<rect x="0" y="0" width="3" height="{BOX}" fill="{INK}"/>')

    # El ordinal, enorme y casi invisible: da profundidad y marca el orden sin gritar.
    p.append(txt(M - 20, 122, num, 104, INK, "display", sp=-4, opacity=0.075))

    p.append(txt(M, 56, title, 23, INK, "sansb", sp=-0.4))
    for i, ln in enumerate(wrap(desc, 82)[:2]):
        p.append(txt(M, 84 + i * 18, ln, 13, MUTED, "sans"))
    p.append(txt(M, 121, tech, 10.5, MUTED, "mono", sp=1.2))

    p.append(hline(right - 150, 40, right))
    p.append(txt(right, 76, f"{data[metric_key]:,}".replace(",", " "), 26, INK, "display",
                 sp=-0.5, anchor="end"))
    p.append(txt(right, 94, metric_label, 9, MUTED, "mono", sp=2.2, anchor="end"))
    p.append(txt(right, 121, c["open_label"], 10, INK, "mono", sp=1.8, anchor="end"))
    return end(p)


def stats(c, data, stamp):
    H = 152
    p = start(H, "Numbers")
    p.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" fill="none" stroke="{RULE}"/>')
    col = (W - M * 2) / len(c["stats"])
    for i, (key, label) in enumerate(c["stats"]):
        x = M + i * col
        if i:
            p.append(f'<line x1="{x-28:.0f}" y1="38" x2="{x-28:.0f}" y2="104" '
                     f'stroke="{RULE}" stroke-width="1"/>')
        value = str(data[key]) if key == "since" else f"{data[key]:,}".replace(",", " ")
        p.append(txt(x, 86, value, 50, INK, "display", sp=-1.5))
        p.append(txt(x, 106, label, 9.5, MUTED, "mono", sp=2.4))
    p.append(hline(M, 122, W - M))
    p.append(txt(M, 140, c["asof"].format(d=stamp), 9, DIM, "mono", sp=1.2))
    return end(p)


def hairline():
    return (XMLDECL + f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="1" '
            f'viewBox="0 0 {W} 1"><rect width="{W}" height="1" fill="{RULE}"/></svg>')


def fetch():
    """Cifras reales desde GitHub; si `gh` no responde se usan las de FALLBACK."""
    try:
        out, total_rel, total_dl = {}, 0, 0
        for repo in RELEASE_REPOS:
            raw = subprocess.run(["gh", "api", "--paginate",
                                  f"repos/{USER}/{repo}/releases?per_page=100"],
                                 capture_output=True, text=True, check=True, timeout=120).stdout
            rel = dl = 0
            for chunk in raw.replace("][", "]\n[").split("\n"):
                if chunk.strip():
                    for r in json.loads(chunk):
                        rel += 1
                        dl += sum(a.get("download_count", 0) for a in r.get("assets", []))
            total_rel += rel
            total_dl += dl
            out["tradingtuff" if repo == "TradingTuff" else "chimera"] = (
                dl if repo == "TradingTuff" else rel)
        user = json.loads(subprocess.run(["gh", "api", f"users/{USER}"], capture_output=True,
                                         text=True, check=True, timeout=30).stdout)
        out.update(releases=total_rel, downloads=total_dl, since=int(user["created_at"][:4]))
        return out
    except Exception as exc:                      # noqa: BLE001 — sin red o sin gh, seguimos igual
        print("  (gh no respondió, uso las cifras guardadas:", exc, ")")
        return dict(FALLBACK)


def write(name, body):
    path = os.path.join(HERE, name)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(body + "\n")
    print(f"  {name:26} {os.path.getsize(path)/1024:6.1f} KB")


data = fetch()
stamp = datetime.date.today().strftime("%d/%m/%Y")
print("cifras:", data)
write("rule.svg", hairline())
for lang, c in COPY.items():
    write(f"hero-{lang}.svg", hero(c))
    write(f"stack-{lang}.svg", stack(c))
    write(f"stats-{lang}.svg", stats(c, data, stamp))
    for project in c["projects"]:
        write(f"card-{project[0]}-{lang}.svg", card(c, project, data))
