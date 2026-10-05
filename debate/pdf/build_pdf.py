"""Genera debate_granada_ES.pdf (solo español) a partir de los .md de ./debate."""
import re, subprocess, pathlib, markdown

D = pathlib.Path(__file__).resolve().parent.parent
ORDER = [
    ("chuleta.md", "Chuleta"),
    ("a_favor.md", "A favor"),
    ("en_contra.md", "En contra"),
    ("apendice_refutaciones.md", "Apéndice de refutaciones"),
    ("fuentes.md", "Fuentes"),
    ("log.md", "Registro del bucle"),
]
LABELS = [" / Claim", " / Reason", " / Fact", " / Why it matters", " / Expected rebuttal",
          " / My answer", " / Second rebuttal", " / Third rebuttal", " / They'll say"]

def spanish_only(md):
    out, skip = [], False
    for line in md.split("\n"):
        s = line.strip()
        if skip:
            if s == "":
                skip = False
                out.append(line)
            continue
        if s == "**EN:**":
            skip = True
            continue
        if s == "**ES:**":
            continue
        if re.match(r"^-\s*(\*\*)?EN:(\*\*)?\s", s) or s.startswith("**EN:** "):
            continue
        line = re.sub(r'^\*\*ES:\*\* ', "", line)
        line = re.sub(r'\s*/\s*EN:\s*"[^"]*"', "", line)
        line = re.sub(r'(^\s*- )\*\*ES:\*\* ', r"\1", line)
        line = re.sub(r'(^\s*- )ES: ', r"\1", line)
        line = re.sub(r'→ ES: ', "→ ", line)
        line = re.sub(r':\*\* ES: ', ":** ", line)
        line = line.replace(": ES: ", ": ")
        for lab in LABELS:
            line = line.replace(lab, "")
        out.append(line)
    return "\n".join(out)

CSS = """
@page { size: A4; margin: 16mm 15mm 16mm 15mm; }
body { font-family: 'DejaVu Sans', Arial, sans-serif; font-size: 10.5pt; line-height: 1.4; color: #111; }
h1 { font-size: 17pt; border-bottom: 2px solid #333; padding-bottom: 4px; margin-top: 0; }
h2 { font-size: 13pt; margin-top: 16px; color: #1a3d6d; }
h3 { font-size: 11pt; margin-top: 12px; color: #333; }
blockquote { border-left: 3px solid #999; margin: 6px 0; padding: 2px 10px; color: #444; }
table { border-collapse: collapse; width: 100%; font-size: 8pt; margin: 6px 0; }
th, td { border: 1px solid #bbb; padding: 3px 4px; vertical-align: top; word-break: break-word; }
th { background: #eee; }
a { color: #1a3d6d; word-break: break-all; }
ul, ol { margin: 4px 0 4px 18px; padding: 0; }
li { margin: 2px 0; }
.doc { page-break-before: always; }
.chuleta { font-size: 9pt; line-height: 1.3; }
.chuleta h2 { font-size: 12pt; margin-top: 6px; }
.chuleta p { margin: 4px 0; }
.pb { page-break-before: always; }
.cover { text-align: center; padding-top: 70mm; }
.cover h1 { border: none; font-size: 24pt; }
.cover p { font-size: 12pt; }
.toc { text-align: left; display: inline-block; margin-top: 20mm; font-size: 12pt; }
"""

parts = ["""<div class="cover"><h1>Debate: ¿Una Smart City sin IA seguirá siendo competitiva en los próximos años?</h1>
<p>Caso Granada · Líderes Digitales Universitarios 2026 · Fase local</p>
<p>6 de octubre de 2026 · 16:20 · Salón de Plenos del Ayuntamiento de Granada</p>
<p><b>A FAVOR</b> = sí sigue siendo competitiva sin IA · <b>EN CONTRA</b> = no</p>
<div class="toc"><b>Contenido</b><ol>""" + "".join(f"<li>{t}</li>" for _, t in ORDER) + "</ol></div></div>"]

for fname, _ in ORDER:
    md = spanish_only((D / fname).read_text(encoding="utf-8"))
    if fname == "chuleta.md":
        md = md.replace("\n---\n\n## EN CONTRA", '\n<div class="pb"></div>\n\n## EN CONTRA')
        md = "\n".join(l + "  " if l.strip() and not l.startswith(("#", "<", "---")) else l for l in md.split("\n"))
    html = markdown.markdown(md, extensions=["tables", "sane_lists"])
    cls = "doc chuleta" if fname == "chuleta.md" else "doc"
    parts.append(f'<div class="{cls}">{html}</div>')

page = f'<!doctype html><html lang="es"><head><meta charset="utf-8"><style>{CSS}</style></head><body>{"".join(parts)}</body></html>'
html_path = D / "pdf" / "debate_granada_ES.html"
html_path.write_text(page, encoding="utf-8")
pdf_path = D / "debate_granada_ES.pdf"
subprocess.run(["/opt/pw-browsers/chromium", "--headless", "--no-sandbox", "--disable-gpu",
                "--no-pdf-header-footer", f"--print-to-pdf={pdf_path}", html_path.as_uri()],
               check=True, capture_output=True)
print(pdf_path)
