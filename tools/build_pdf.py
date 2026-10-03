"""Build one PDF-ready HTML file from the plan's Markdown parts.

Usage:
    python3 tools/build_pdf.py OUTPUT_HTML TITLE PART1.md [PART2.md ...]

Then render it with:
    node tools/render_pdf.mjs OUTPUT_HTML OUTPUT_PDF
"""

import html
import pathlib
import re
import sys

import markdown

TOOLS = pathlib.Path(__file__).resolve().parent
FONTS = TOOLS / "node_modules" / "@fontsource" / "sarabun" / "files"

CSS = """
@font-face { font-family: 'Sarabun'; font-weight: 400; src: url('__FONTS__/sarabun-thai-400-normal.woff2') format('woff2'); unicode-range: U+0E01-0E5B, U+200C-200D, U+25CC; }
@font-face { font-family: 'Sarabun'; font-weight: 400; src: url('__FONTS__/sarabun-latin-400-normal.woff2') format('woff2'); }
@font-face { font-family: 'Sarabun'; font-weight: 700; src: url('__FONTS__/sarabun-thai-700-normal.woff2') format('woff2'); unicode-range: U+0E01-0E5B, U+200C-200D, U+25CC; }
@font-face { font-family: 'Sarabun'; font-weight: 700; src: url('__FONTS__/sarabun-latin-700-normal.woff2') format('woff2'); }
@page { size: A4; margin: 16mm 14mm 18mm 14mm; }
:root { --ink: #1f2937; --muted: #4b5563; --line: #d1d5db; --head: #f3f4f6; --accent: #1d4ed8; }
html, body { background: #ffffff; color: var(--ink); }
body { font-family: 'Sarabun', 'Loma', sans-serif; font-size: 10.5pt; line-height: 1.55; }
h1 { font-size: 18pt; color: #111827; border-bottom: 2px solid var(--accent); padding-bottom: 4px; margin-top: 18px; page-break-after: avoid; }
h1.doc-break { page-break-before: always; }
h2 { font-size: 14pt; color: #111827; margin-top: 16px; page-break-after: avoid; }
h3 { font-size: 12pt; margin-top: 12px; page-break-after: avoid; }
h4 { font-size: 11pt; margin-top: 10px; page-break-after: avoid; }
p, li { overflow-wrap: anywhere; }
a { color: var(--accent); text-decoration: none; overflow-wrap: anywhere; word-break: break-all; }
table { border-collapse: collapse; width: 100%; margin: 8px 0 12px; font-size: 9pt; line-height: 1.4; }
th, td { border: 1px solid var(--line); padding: 4px 5px; vertical-align: top; text-align: left; overflow-wrap: anywhere; }
th { background: var(--head); font-weight: 700; }
tr { page-break-inside: avoid; }
blockquote { border-left: 4px solid var(--accent); margin: 8px 0; padding: 6px 10px; background: #eff6ff; }
code { font-family: 'DejaVu Sans Mono', monospace; font-size: 8.5pt; background: #f3f4f6; padding: 0 2px; }
pre { background: #f9fafb; border: 1px solid var(--line); padding: 8px; font-size: 8.5pt; white-space: pre-wrap; page-break-inside: avoid; }
pre code { background: none; padding: 0; }
pre.mermaid { background: #ffffff; border: none; text-align: center; white-space: pre; margin: 0; }
@page wide { size: A4 landscape; margin: 8mm; }
.diagram-page { page: wide; break-before: page; break-after: page; }
.diagram-page svg { width: 100% !important; max-width: none !important; height: auto; max-height: 185mm; }
td:first-child, th:first-child { min-width: 3.2em; }
hr { border: none; border-top: 1px solid var(--line); margin: 14px 0; }
.cover { text-align: center; margin-top: 80px; }
.cover h1 { border: none; font-size: 22pt; }
.cover p { color: var(--muted); }
"""

MERMAID_BLOCK = re.compile(
    r'<pre><code class="language-mermaid">(.*?)</code></pre>', re.DOTALL
)


def convert(md_text: str) -> str:
    body = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "sane_lists"],
        output_format="html5",
    )
    return MERMAID_BLOCK.sub(
        lambda m: '<div class="diagram-page"><pre class="mermaid">' + html.unescape(m.group(1)) + "</pre></div>", body
    )


def main() -> None:
    out, title, *parts = sys.argv[1:]
    sections = []
    for i, part in enumerate(parts):
        body = convert(pathlib.Path(part).read_text(encoding="utf-8"))
        if i > 0:
            body = body.replace("<h1>", '<h1 class="doc-break">', 1)
        sections.append(body)
    mermaid_js = (TOOLS / "node_modules" / "mermaid" / "dist" / "mermaid.min.js").as_uri()
    page = f"""<!doctype html>
<html lang="th"><head><meta charset="utf-8">
<title>{html.escape(title)}</title>
<style>{CSS.replace('__FONTS__', FONTS.as_uri())}</style>
<script src="{mermaid_js}"></script>
</head><body>
<div class="cover"><h1>{html.escape(title)}</h1>
<p>แผน 5 ปี 2 ตุลาคม 2569 ถึง 30 กันยายน 2574</p></div>
{''.join(sections)}
<script>
  mermaid.initialize({{ startOnLoad: false, theme: 'neutral', fontFamily: 'Sarabun', themeVariables: {{ fontSize: '18px' }}, flowchart: {{ useMaxWidth: true, nodeSpacing: 18, rankSpacing: 45 }} }});
  document.fonts.load("16px Sarabun", "กขค abc")
    .then(() => document.fonts.ready)
    .then(() => mermaid.run({{ querySelector: 'pre.mermaid' }}))
    .then(() => {{ document.body.dataset.ready = '1'; }})
    .catch(() => {{ document.body.dataset.ready = 'error'; }});
</script>
</body></html>"""
    pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(out).write_text(page, encoding="utf-8")


if __name__ == "__main__":
    main()
