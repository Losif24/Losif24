# Genera la portada, el stack, las fichas y las cifras del perfil. Dos idiomas.
# Una sola paleta: fondo negro, letras blancas. La banda y las cifras van invertidas.
# Uso:  python assets/generate.py       (pide las cifras a GitHub si tienes `gh`)

import datetime
import json
import os
import subprocess

NAME = "JOSÉ DURÁN"
CITY = "BOGOTÁ · COLOMBIA"
ROLE = "SOFTWARE DEVELOPER"
USER = "Losif24"
RELEASE_REPOS = ["TradingTuff", "chimera-releases"]

# Si `gh` no responde se usan estas, medidas el 17/09/2026.
FALLBACK = dict(releases=180, downloads=214, since=2022)

COPY = {
    "en": dict(
        claim="I build things that ship: desktop apps, the backends behind them, and the plumbing in between.",
        disciplines=[("01", "BACKEND", "Python · FastAPI · SQLite"),
                     ("02", "DESKTOP", "C++17 · Qt 6 · WPF"),
                     ("03", "SYSTEMS", "Win32 · ConPTY · WebSocket")],
        stack=[("DESKTOP", ["C++17", "Qt 6", "C# / WPF", "PySide6", "Win32 / ConPTY"]),
               ("MOBILE", ["Kotlin", "Jetpack Compose", "Material 3", "Android SDK"]),
               ("BACKEND", ["Python", "FastAPI", "SQLite", "Supabase", "WebSocket"]),
               ("WEB", ["TypeScript", "React", "HTML / CSS"]),
               ("DELIVERY", ["Git", "CMake / MSBuild", "Inno Setup", "OpenCV"])],
        open_label="OPEN ↗",
        stats=[("releases", "VERSIONS SHIPPED"), ("downloads", "INSTALLER DOWNLOADS"),
               ("since", "ON GITHUB SINCE")],
        asof="measured {d}",
        projects=[
            ("exodus", "01", "EXODUS",
             "TODO: una línea sobre qué hace, en tus palabras.",
             "TODO · tecnologías"),
            ("chimera", "02", "CHIMERA",
             "A desktop environment for reading someone else's codebase — or your own, six "
             "months later. It indexes the project and draws what depends on what.",
             "Python · Qt 6 · QML"),
            ("tradingtuff", "03", "TRADING TUFF",
             "A Windows terminal for reading a market in real time: live data, a chart engine "
             "written from scratch, and the context around the price in one screen.",
             "C++17 · Qt 6 · SQLite"),
        ],
    ),
    "es": dict(
        claim="Construyo cosas que se entregan: apps de escritorio, su backend y la fontanería del medio.",
        disciplines=[("01", "BACKEND", "Python · FastAPI · SQLite"),
                     ("02", "ESCRITORIO", "C++17 · Qt 6 · WPF"),
                     ("03", "SISTEMAS", "Win32 · ConPTY · WebSocket")],
        stack=[("ESCRITORIO", ["C++17", "Qt 6", "C# / WPF", "PySide6", "Win32 / ConPTY"]),
               ("MÓVIL", ["Kotlin", "Jetpack Compose", "Material 3", "Android SDK"]),
               ("BACKEND", ["Python", "FastAPI", "SQLite", "Supabase", "WebSocket"]),
               ("WEB", ["TypeScript", "React", "HTML / CSS"]),
               ("ENTREGA", ["Git", "CMake / MSBuild", "Inno Setup", "OpenCV"])],
        open_label="ABRIR ↗",
        stats=[("releases", "VERSIONES PUBLICADAS"), ("downloads", "DESCARGAS"),
               ("since", "EN GITHUB DESDE")],
        asof="medido el {d}",
        projects=[
            ("exodus", "01", "EXODUS",
             "TODO: una línea sobre qué hace, en tus palabras.",
             "TODO · tecnologías"),
            ("chimera", "02", "CHIMERA",
             "Un entorno de escritorio para leer el código de otro — o el tuyo, seis meses "
             "después. Indexa el proyecto y dibuja de qué depende cada archivo.",
             "Python · Qt 6 · QML"),
            ("tradingtuff", "03", "TRADING TUFF",
             "Una terminal de Windows para leer un mercado en vivo: datos en tiempo real, un "
             "motor de gráfico escrito desde cero y todo el contexto en una pantalla.",
             "C++17 · Qt 6 · SQLite"),
        ],
    ),
}

BG, INK, MUTED, RULE, CHIP = "#000000", "#FFFFFF", "#9A9A9A", "#2B2B2B", "#0E0E0E"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Consolas, 'Liberation Mono', monospace"
XMLDECL = '<?xml version="1.0" encoding="UTF-8"?>'
W, MARGIN = 880, 48
HERE = os.path.dirname(os.path.abspath(__file__))


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def txt(x, y, s, size, fill, family=SANS, weight=None, spacing=None, anchor=None, opacity=None):
    a = [f'x="{x}"', f'y="{y}"', f'font-family="{family}"', f'font-size="{size}"', f'fill="{fill}"']
    for cond, attr in ((weight, f'font-weight="{weight}"'), (spacing is not None, f'letter-spacing="{spacing}"'),
                       (anchor, f'text-anchor="{anchor}"'), (opacity is not None, f'opacity="{opacity}"')):
        if cond:
            a.append(attr)
    return f'<text {" ".join(a)}>{esc(s)}</text>'


def head(h, label):
    return [XMLDECL,
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" '
            f'viewBox="0 0 {W} {h}" role="img" aria-label="{esc(label)}">',
            f'<rect width="{W}" height="{h}" fill="{BG}"/>']


def wrap(text, limit):
    """SVG no ajusta texto solo: se parte a mano por numero de caracteres."""
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
    H, BAND = 250, 64
    top, right = H - BAND, W - MARGIN
    p = head(H, f"{NAME} — {ROLE}")
    p.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" fill="none" stroke="{RULE}"/>')
    p.append(txt(MARGIN, 52, ROLE, 11.5, MUTED, MONO, spacing=3.4))
    p.append(txt(right, 52, CITY, 11.5, MUTED, MONO, spacing=1.6, anchor="end"))
    p.append(f'<line x1="{MARGIN}" y1="68" x2="{right}" y2="68" stroke="{RULE}" stroke-width="1"/>')
    p.append(txt(MARGIN, 128, NAME, 52, INK, SANS, weight=700, spacing=-1.2))
    p.append(txt(MARGIN, 160, c["claim"], 14.5, MUTED))

    # Banda invertida: blanca con texto negro. El unico bloque solido y el ancla de la portada.
    p.append(f'<rect x="0" y="{top}" width="{W}" height="{BAND}" fill="{INK}"/>')
    col = (W - MARGIN * 2) / 3.0
    for i, (num, label, tech) in enumerate(c["disciplines"]):
        x = MARGIN + i * col
        if i:
            p.append(f'<line x1="{x-24:.0f}" y1="{top+18}" x2="{x-24:.0f}" y2="{H-18}" '
                     f'stroke="{BG}" stroke-width="1" opacity="0.25"/>')
        p.append(txt(x, top + 26, f"{num} · {label}", 10.5, BG, MONO, spacing=2.6, opacity=0.6))
        p.append(txt(x, top + 48, tech, 14, BG, SANS, weight=600))
    p.append('</svg>')
    return "\n".join(p)


def stack(c):
    CHIP_H, PAD, GAP, ROW_GAP, LABEL_COL = 30, 15, 9, 13, 140
    char_w = 7.1  # ancho aproximado por caracter a 12.5px en monoespaciada
    rows = []
    for label, items in c["stack"]:
        chips, cx = [], MARGIN + LABEL_COL
        for it in items:
            w = round(len(it) * char_w + PAD * 2)
            chips.append((cx, w, it))
            cx += w + GAP
        rows.append((label, chips))

    H = 20 + len(rows) * (CHIP_H + ROW_GAP)
    p = head(H, "Stack")
    y = 10
    for label, chips in rows:
        mid = y + CHIP_H / 2 + 4
        p.append(txt(MARGIN, mid, label, 10.5, MUTED, MONO, spacing=2.4))
        for cx, w, it in chips:
            p.append(f'<rect x="{cx}.5" y="{y}.5" width="{w}" height="{CHIP_H}" rx="3" '
                     f'fill="{CHIP}" stroke="{RULE}"/>')
            p.append(txt(cx + w / 2, mid, it, 12.5, INK, MONO, anchor="middle"))
        y += CHIP_H + ROW_GAP
    p.append('</svg>')
    return "\n".join(p)


def card(c, project):
    """Ficha de proyecto. Se publica envuelta en un enlace, asi que toda ella es pulsable."""
    _slug, num, title, desc, tech = project
    BOX, GAP = 110, 10          # el hueco va DENTRO del svg: asi las fichas nunca se pegan
    right = W - 28
    p = head(BOX + GAP, f"{title} — {desc}")
    p.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{BOX-1}" fill="none" stroke="{RULE}" rx="3"/>')
    p.append(f'<rect x="0" y="0" width="4" height="{BOX}" fill="{INK}"/>')
    p.append(txt(32, 34, num, 10.5, MUTED, MONO, spacing=2.4))
    p.append(txt(32, 60, title, 21, INK, SANS, weight=700, spacing=-0.3))
    for i, ln in enumerate(wrap(desc, 88)[:2]):
        p.append(txt(32, 82 + i * 17, ln, 13, MUTED))
    p.append(txt(right, 34, tech, 11, MUTED, MONO, spacing=0.6, anchor="end"))
    p.append(txt(right, 60, c["open_label"], 11, INK, MONO, spacing=1.6, anchor="end"))
    p.append('</svg>')
    return "\n".join(p)


def stats(c, data, stamp):
    """Cifras de entrega, no de vanidad: lo que se ha publicado y lo que se ha descargado."""
    H = 132
    p = head(H, "Numbers")
    p.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" fill="none" stroke="{RULE}" rx="3"/>')
    col = (W - MARGIN * 2) / len(c["stats"])
    for i, (key, label) in enumerate(c["stats"]):
        x = MARGIN + i * col
        if i:
            p.append(f'<line x1="{x-22:.0f}" y1="30" x2="{x-22:.0f}" y2="90" stroke="{RULE}" stroke-width="1"/>')
        p.append(txt(x, 66, f"{data[key]:,}".replace(",", " ") if key != "since" else str(data[key]),
                     34, INK, SANS, weight=700, spacing=-1))
        for j, ln in enumerate(wrap(label, 26)[:2]):
            p.append(txt(x, 88 + j * 14, ln, 9.5, MUTED, MONO, spacing=1.8))
    p.append(f'<line x1="{MARGIN}" y1="104" x2="{W-MARGIN}" y2="104" stroke="{RULE}" stroke-width="1"/>')
    p.append(txt(MARGIN, 120, c["asof"].format(d=stamp), 9.5, MUTED, MONO, spacing=1.2))
    p.append('</svg>')
    return "\n".join(p)


def rule():
    return (XMLDECL + f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="1" '
            f'viewBox="0 0 {W} 1"><rect width="{W}" height="1" fill="{RULE}"/></svg>')


def fetch():
    """Pide las cifras reales a GitHub. Si `gh` no esta, se usan las de FALLBACK."""
    try:
        releases = downloads = 0
        for repo in RELEASE_REPOS:
            raw = subprocess.run(["gh", "api", "--paginate", f"repos/{USER}/{repo}/releases?per_page=100"],
                                 capture_output=True, text=True, check=True, timeout=90).stdout
            for chunk in raw.replace("][", "],[").split("\n"):
                if not chunk.strip():
                    continue
                for rel in json.loads(chunk):
                    releases += 1
                    downloads += sum(a.get("download_count", 0) for a in rel.get("assets", []))
        user = json.loads(subprocess.run(["gh", "api", f"users/{USER}"],
                                         capture_output=True, text=True, check=True, timeout=30).stdout)
        return dict(releases=releases, downloads=downloads, since=int(user["created_at"][:4]))
    except Exception as exc:                      # noqa: BLE001 — sin red o sin gh, seguimos igual
        print("  (gh no respondió, uso las cifras guardadas:", exc, ")")
        return dict(FALLBACK)


def write(name, body):
    with open(os.path.join(HERE, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(body + "\n")
    print("wrote", name)


data = fetch()
stamp = datetime.date.today().strftime("%d/%m/%Y")
print("cifras:", data)
write("rule.svg", rule())
for lang, c in COPY.items():
    write(f"hero-{lang}.svg", hero(c))
    write(f"stack-{lang}.svg", stack(c))
    write(f"stats-{lang}.svg", stats(c, data, stamp))
    for project in c["projects"]:
        write(f"card-{project[0]}-{lang}.svg", card(c, project))
