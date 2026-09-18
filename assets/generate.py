# Genera las piezas del stack y escribe el bloque Stack de los dos README.
#
# Criterio, después de haberme pasado de decorativo tres veces:
#   - El perfil es texto de Markdown. Sin cabecera: el nombre ya sale en la barra
#     lateral de GitHub, y una lámina oscura desentona con el fondo de la tarjeta.
#   - En el stack, icono y nombre van en UNA sola imagen por tecnología. Separados,
#     Chrome parte la línea entre la imagen y su nombre aunque haya un &nbsp; (lo manda
#     la especificación de CSS) y GitHub borra cualquier style que lo impediría.
#   - Iconos de Devicon y letras de JetBrains Mono, ambos convertidos a trazos: un <path>
#     se pinta igual en cualquier navegador. Un solo gris, apagado a propósito, que se
#     lee sobre el tema oscuro y sobre el claro.
#
# Uso:  python assets/generate.py

import hashlib
import math
import os
import re

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

# Una fila por área. Cada tecnología: (icono de Devicon o None, nombre).
# El nombre puede ser {"en": ..., "es": ...} cuando cambia con el idioma.
STACK = [
    ({"en": "Backend", "es": "Backend"}, [
        ("nodejs", "Node.js"), ("java", "Java"), ("spring", "Spring Boot"),
        ("python", "Python"), ("fastapi", "FastAPI"), (None, "REST"), (None, "WebSocket")]),
    ({"en": "Web", "es": "Web"}, [
        ("javascript", {"en": "JavaScript (ES modules)", "es": "JavaScript (módulos ES)"}),
        ("typescript", {"en": "TypeScript (basic)", "es": "TypeScript (básico)"}),
        ("react", "React"), ("nextjs", "Next.js")]),
    ({"en": "Desktop", "es": "Escritorio"}, [
        ("cplusplus", "C++17"), ("qt", "Qt 6 (Widgets, QML)"), ("csharp", "C# / .NET WPF"),
        ("electron", "Electron"), (None, "PySide6"), (None, "Win32 / ConPTY")]),
    ({"en": "Mobile", "es": "Móvil"}, [
        ("kotlin", "Kotlin"), ("jetpackcompose", "Jetpack Compose"),
        ("android", "Android SDK"), (None, "Material 3")]),
    ({"en": "Data", "es": "Datos"}, [
        ("mysql", "MySQL"), ("sqlite", "SQLite"), ("supabase", "Supabase"), ("dbeaver", "DBeaver")]),
    ({"en": "Delivery", "es": "Entrega"}, [
        ("git", "Git"), ("cmake", "CMake"), ("pm2", "PM2"), (None, "MSBuild"), (None, "Inno Setup")]),
    ({"en": "Architecture", "es": "Arquitectura"}, [
        (None, "MVC"), (None, "MVVM"), (None, "Clean Architecture")]),
]

# Clase de Devicon -> código del glifo en devicon.ttf (sacado de devicon.min.css).
DEVICON = {
    "nodejs": 0xED9E,        # nodejs-plain
    "java": 0xEA7F,          # java-plain
    "spring": 0xEC16,        # spring-plain
    "python": 0xEB9C,        # python-plain
    "fastapi": 0xE9EF,       # fastapi-plain
    "javascript": 0xEA81,    # javascript-plain
    "typescript": 0xEC63,    # typescript-plain
    "react": 0xEBBC,         # react-plain
    "nextjs": 0xEB14,        # nextjs-plain
    "cplusplus": 0xE99A,     # cplusplus-plain
    "qt": 0xEBA2,            # qt-plain
    "csharp": 0xE9A0,        # csharp-plain
    "electron": 0xE9D8,      # electron-original
    "kotlin": 0xEAB5,        # kotlin-plain
    "jetpackcompose": 0xEA8C,  # jetpackcompose-plain
    "android": 0xE90F,       # android-plain
    "mysql": 0xEAFD,         # mysql-plain
    "sqlite": 0xEC1E,        # sqlite-plain
    "supabase": 0xEC2E,      # supabase-plain
    "dbeaver": 0xE9B0,       # dbeaver-plain
    "git": 0xEA2D,           # git-plain
    "cmake": 0xE97A,         # cmake-plain
    "pm2": 0xECE5,           # pm2-plain
}

ITEM_INK = "#848D97"  # 5.6:1 sobre #0D1117 y 3.4:1 sobre blanco
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FONTDIR = os.path.join(HERE, "fonts")
STACKDIR = os.path.join(HERE, "stack")

# Geometría de cada pieza del stack. El README la pone con align="absmiddle", que
# centra la imagen en la línea base + media altura de x del texto (unos 4 px a 16 px):
# con 20 px de alto, la línea base del texto de GitHub cae a unos 13,5 px del borde superior.
ITEM_H, ITEM_BASE = 20, 13.5
ITEM_SIZE = 13.0      # px de JetBrains Mono
ICON_PX, ICON_GAP = 15.0, 6.0
ITEM_PAD_R = 14.0     # aire tras cada tecnología; el espacio del Markdown suma 4 px más
ICON_PAD = 0.04

def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def load_mono():
    font = TTFont(os.path.join(FONTDIR, "JetBrainsMono.ttf"))
    return instancer.instantiateVariableFont(font, {"wght": 400}, inplace=False)


def ntos(v):
    s = f"{v:.1f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


class Stack:
    """Convierte icono + nombre en una imagen de trazos."""

    def __init__(self):
        self.mono = load_mono()
        self.mono_glyphs = self.mono.getGlyphSet()
        self.mono_cmap = self.mono.getBestCmap()
        self.upem = self.mono["head"].unitsPerEm
        self.cap = self.mono["OS/2"].sCapHeight
        dev = TTFont(os.path.join(FONTDIR, "devicon.ttf"))
        self.dev_glyphs, self.dev_cmap = dev.getGlyphSet(), dev.getBestCmap()

    def item(self, icon, label):
        paths, x = [], 0.0
        if icon:
            g = self.dev_glyphs[self.dev_cmap[DEVICON[icon]]]
            bp = BoundsPen(self.dev_glyphs)
            g.draw(bp)
            x0, y0, x1, y1 = bp.bounds
            k = ICON_PX / (max(x1 - x0, y1 - y0) * (1 + 2 * ICON_PAD))
            # centrado sobre la mitad de las mayúsculas del nombre
            cy = ITEM_BASE - self.cap * ITEM_SIZE / self.upem / 2
            pen = SVGPathPen(self.dev_glyphs, ntos=ntos)
            g.draw(TransformPen(pen, (k, 0, 0, -k, ICON_PX / 2 - k * (x0 + x1) / 2,
                                      cy + k * (y0 + y1) / 2)))
            paths.append(pen.getCommands())
            x = ICON_PX + ICON_GAP
        s = ITEM_SIZE / self.upem
        pen = SVGPathPen(self.mono_glyphs, ntos=ntos)
        for ch in label:
            gname = self.mono_cmap[ord(ch)]
            self.mono_glyphs[gname].draw(TransformPen(pen, (s, 0, 0, -s, x, ITEM_BASE)))
            x += self.mono_glyphs[gname].width * s
        paths.append(pen.getCommands())
        w = math.ceil(x + ITEM_PAD_R)
        d = " ".join(p for p in paths if p)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{ITEM_H}" '
                f'viewBox="0 0 {w} {ITEM_H}" role="img" aria-label="{esc(label)}">'
                f'<path fill="{ITEM_INK}" d="{d}"/></svg>')


def slug(label):
    return re.sub(r"[^a-z0-9]+", "-", label.lower().replace("+", "p").replace("#", "sharp")
                  .replace("ó", "o").replace("á", "a")).strip("-")


def stack_markdown(lang, files):
    rows = []
    for area, items in STACK:
        imgs = []
        for icon, label in items:
            text = label[lang] if isinstance(label, dict) else label
            imgs.append(f'<img src="assets/stack/{files[(icon, text)]}" '
                        f'height="{ITEM_H}" align="absmiddle" alt="{esc(text)}">')
        rows.append(f"**{area[lang]}** &ensp;\n" + "\n".join(imgs))
    return "\n\n".join(rows)


def build_stack():
    st = Stack()
    os.makedirs(STACKDIR, exist_ok=True)
    for old in os.listdir(STACKDIR):
        os.remove(os.path.join(STACKDIR, old))
    files = {}
    for _, items in STACK:
        for icon, label in items:
            for text in (label.values() if isinstance(label, dict) else [label]):
                svg = st.item(icon, text) + "\n"
                # La huella va en el nombre: GitHub redirige /raw/ a una URL SIN la query,
                # así que un ?v=N no invalida la caché de 5 min; un nombre nuevo sí.
                name = f"{slug(text)}-{hashlib.sha1(svg.encode()).hexdigest()[:6]}.svg"
                files[(icon, text)] = name
                with open(os.path.join(STACKDIR, name), "w", encoding="utf-8", newline="\n") as f:
                    f.write(svg)
    total = sum(os.path.getsize(os.path.join(STACKDIR, n)) for n in set(files.values()))
    print(f"  stack/   {len(set(files.values()))} piezas   {total/1024:.1f} KB en total")

    # El bloque vive entre dos marcas en cada README; lo de fuera no se toca.
    for lang, readme in (("en", "README.md"), ("es", "README.es.md")):
        path = os.path.join(ROOT, readme)
        with open(path, encoding="utf-8") as f:
            doc = f.read()
        start, end = "<!-- stack:start -->", "<!-- stack:end -->"
        a, b = doc.index(start) + len(start), doc.index(end)
        doc = doc[:a] + "\n" + stack_markdown(lang, files) + "\n" + doc[b:]
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
        print(f"  {readme}   bloque Stack reescrito")


build_stack()
