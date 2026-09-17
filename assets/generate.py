# Genera la ÚNICA imagen del perfil: la cabecera.
#
# Criterio, después de haberme pasado de decorativo tres veces:
#   - Una sola pieza. Todo lo demás es texto de Markdown, que es lo que hace
#     un perfil de ingeniero de verdad: se selecciona, se busca, se lee en cualquier parte.
#   - Sin caja, sin borde, sin textura, sin trucos. El fondo es el de GitHub,
#     así que la pieza no parece una lámina pegada: parece la página.
#   - Margen izquierdo cero, para que el nombre quede alineado al milímetro con
#     el párrafo que va debajo. Eso es lo que se nota sin saber por qué.
#   - Dos fuentes, no tres. Space Grotesk y JetBrains Mono, ambas SIL OFL,
#     recortadas a los caracteres exactos e incrustadas: no dependen de la red.
#
# Uso:  python assets/generate.py

import base64
import io
import os

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

NAME = "José Durán"
LINES = {
    "en": "SOFTWARE DEVELOPER · BOGOTÁ, COLOMBIA",
    "es": "DESARROLLADOR DE SOFTWARE · BOGOTÁ, COLOMBIA",
}

BG, INK, MUTED = "#0D1117", "#E6EDF3", "#8B949E"
W, H = 880, 96
XMLDECL = '<?xml version="1.0" encoding="UTF-8"?>'
HERE = os.path.dirname(os.path.abspath(__file__))
FONTDIR = os.path.join(HERE, "fonts")

FACES = {
    "name": dict(file="SpaceGrotesk.ttf", wght=600, family="TuffName",
                 fallback="'Segoe UI', Helvetica, Arial, sans-serif"),
    "mono": dict(file="JetBrainsMono.ttf", wght=400, family="TuffMono",
                 fallback="Consolas, 'Liberation Mono', monospace"),
}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def embed(face_key, chars):
    """Recorta la fuente a esos caracteres y la devuelve en base64 woff2."""
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
    return base64.b64encode(buf.getvalue()).decode("ascii")


def header(lang):
    sub = LINES[lang]
    faces = {"name": NAME, "mono": sub}
    css = "".join(
        f"@font-face{{font-family:'{FACES[k]['family']}';font-style:normal;font-weight:400;"
        f"src:url(data:font/woff2;base64,{embed(k, ''.join(sorted(set(v))))}) format('woff2')}}"
        for k, v in faces.items())

    def txt(x, y, s, size, fill, face, sp=None):
        spec = FACES[face]
        a = [f'x="{x}"', f'y="{y}"',
             f'font-family="{spec["family"]}, {spec["fallback"]}"',
             f'font-size="{size}"', f'fill="{fill}"']
        if sp is not None:
            a.append(f'letter-spacing="{sp}"')
        return f'<text {" ".join(a)}>{esc(s)}</text>'

    return "\n".join([
        XMLDECL,
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-label="{esc(NAME)} — {esc(sub)}">',
        f"<defs><style>{css}</style></defs>",
        f'<rect width="{W}" height="{H}" fill="{BG}"/>',
        txt(0, 46, NAME, 38, INK, "name", sp=-0.8),
        txt(0, 74, sub, 10.5, MUTED, "mono", sp=2.6),
        "</svg>",
    ])


for lang in LINES:
    path = os.path.join(HERE, f"header-{lang}.svg")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(header(lang) + "\n")
    print(f"  header-{lang}.svg   {os.path.getsize(path)/1024:.1f} KB")
