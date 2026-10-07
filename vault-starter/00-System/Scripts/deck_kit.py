"""
deck_kit.py — reusable PowerPoint building blocks for vault deliverables.

A thin, content-agnostic toolkit. A project's own build script (or the
`presentation-builder` skill) imports this to get: Times New Roman enforcement,
consistent slide helpers, an audience-preset layer, and a data-pipeline diagram
helper. It holds NO project-specific content.

Standards (see memory: output-language-and-formatting, presentation-formats-by-audience,
keeping-outputs-engaging):
  - English only, Times New Roman on every run
  - action-title headings, one idea per slide
  - a methodology / pipeline diagram in any methodological deck
  - limitations slide + references slide near the end

Usage
-----
    from deck_kit import Deck, pipeline_diagram
    d = Deck("My Analysis", "subtitle line 1\\nsubtitle line 2", audience="executive")
    d.bullets("Bottom line", ["...", "...", "..."])
    d.chart("Revenue fell 8% as the premium segment contracted", "chart1.png", "caption / source")
    d.bullets("Limitations", [...]);  d.bullets("References", [...])
    d.save("my-analysis_20260905.pptx")

Audience presets (see the skill and the memory note for the full rationale):
  executive  — answer-first, SCR flow, ~12-15 slides, methodology light, action titles
  technical  — methodology visible, all charts, limitations prominent  (default)
  academic   — IMRAD order, concept titles allowed, mandatory references slide
  student    — IMRAD + references, 10/20/30 discipline (>=30pt body, image-only chart slides)
  general    — plain language, big type, few numbers per slide
  sales      — problem -> solution arc, benefit-forward, one CTA

Requires: python-pptx, matplotlib.
"""
from __future__ import annotations
import zipfile, re, shutil, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

FONT = "Times New Roman"
NAVY = RGBColor(0x0b, 0x53, 0x94)
GREY = RGBColor(0x44, 0x44, 0x44)

plt.rcParams.update({
    "figure.dpi": 150, "font.size": 11, "axes.grid": True, "grid.alpha": 0.25,
    "axes.spines.top": False, "axes.spines.right": False,
    "font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"],
    "mathtext.fontset": "dejavuserif",
})

_BODY_PT = {"student": 30, "general": 22}          # audience -> min body font
_CAPTIONS = {"student"}                             # audiences whose chart slides carry no caption


def _patch_theme_font(path):
    """Defense-in-depth for the Times New Roman rule: `_tnr()` only overrides
    runs it's actually called on. python-pptx's default Presentation() theme
    has Calibri baked into <a:majorFont>/<a:minorFont>, so ANY text that skips
    _tnr() (an unstyled placeholder, an empty-run paragraph, a shape added by
    other code) silently renders in Calibri regardless of the per-run
    convention. Confirmed 2026-09-22 this had gone unnoticed across 48 decks
    vault-wide. Patch the theme XML directly as the real fix; _tnr() remains
    useful for explicit per-run control but is not sufficient alone."""
    tmp = path + ".tmp_fontfix"
    with zipfile.ZipFile(path, "r") as zin:
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.namelist():
                data = zin.read(item)
                if item.endswith(".xml") and (item.startswith("ppt/theme/") or item.startswith("ppt/slideMasters/")):
                    text = data.decode("utf-8", errors="ignore")
                    for bad in ("Calibri Light", "Calibri", "Arial"):
                        text = re.sub(rf'typeface="{bad}"', f'typeface="{FONT}"', text)
                    data = text.encode("utf-8")
                zout.writestr(item, data)
    shutil.move(tmp, path)


def _patch_notes_master_decl(path):
    """Fix a python-pptx bug: adding a notes slide lazily creates
    ppt/notesMasters/notesMaster1.xml plus a relationship to it, but
    python-pptx never adds the required <p:notesMasterIdLst> element to
    ppt/presentation.xml. The file is then schema-inconsistent: a part is
    related and content-typed but never declared as used. PowerPoint and
    Google Slides silently tolerate/repair this; Apple Keynote's importer
    rejects the whole file outright with "The file format is invalid."
    Root cause confirmed 2026-09-22 via isolated from-scratch repro (a bare
    python-pptx file with one note failed to import in Keynote; the same
    file with this element inserted opened correctly) and fixed vault-wide
    across 50 affected decks."""
    with zipfile.ZipFile(path, "r") as zin:
        names = zin.namelist()
        if "ppt/presentation.xml" not in names or "ppt/_rels/presentation.xml.rels" not in names:
            return
        has_notes_master_part = any(
            n.startswith("ppt/notesMasters/") and n.endswith(".xml") for n in names
        )
        if not has_notes_master_part:
            return
        data = {n: zin.read(n) for n in names}

    pres_xml = data["ppt/presentation.xml"].decode("utf-8")
    if "notesMasterIdLst" in pres_xml:
        return

    pres_rels = data["ppt/_rels/presentation.xml.rels"].decode("utf-8")
    m = re.search(r'Id="(rId\d+)"[^>]*Type="[^"]*relationships/notesMaster"', pres_rels)
    if not m:
        m = re.search(r'Type="[^"]*relationships/notesMaster"[^>]*Id="(rId\d+)"', pres_rels)
    if not m:
        return
    rid = m.group(1)

    insert = f'<p:notesMasterIdLst><p:notesMasterId r:id="{rid}"/></p:notesMasterIdLst>'
    new_pres_xml, n = re.subn(r'(</p:sldMasterIdLst>)', r'\1' + insert, pres_xml, count=1)
    if n != 1:
        return
    data["ppt/presentation.xml"] = new_pres_xml.encode("utf-8")

    tmp = path + ".tmp_notesfix"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for name in names:
            zout.writestr(name, data[name])
    shutil.move(tmp, path)


def _tnr(text_frame):
    for para in text_frame.paragraphs:
        for run in para.runs:
            run.font.name = FONT
        if not para.runs and para.text:
            para.font.name = FONT


class Deck:
    def __init__(self, title: str, subtitle: str = "", audience: str = "technical"):
        self.audience = audience.lower()
        self.body_pt = _BODY_PT.get(self.audience, 16)
        self.prs = Presentation()
        self.prs.slide_width = Inches(13.333)
        self.prs.slide_height = Inches(7.5)
        self._blank = self.prs.slide_layouts[6]
        self._title_slide(title, subtitle)

    # -- internal slide builders --------------------------------------------
    def _slide(self):
        return self.prs.slides.add_slide(self._blank)

    def _heading(self, s, text, size=24):
        tb = s.shapes.add_textbox(Inches(0.5), Inches(0.25), Inches(12.3), Inches(0.95))
        tb.text_frame.word_wrap = True
        p = tb.text_frame.paragraphs[0]
        p.text = text
        p.font.size = Pt(size)
        p.font.bold = True
        p.font.color.rgb = NAVY
        _tnr(tb.text_frame)

    def _title_slide(self, title, subtitle):
        s = self._slide()
        tb = s.shapes.add_textbox(Inches(0.8), Inches(2.3), Inches(11.7), Inches(1.9))
        tb.text_frame.word_wrap = True
        p = tb.text_frame.paragraphs[0]
        p.text = title
        p.font.size = Pt(40)
        p.font.bold = True
        p.font.color.rgb = NAVY
        if subtitle:
            sb = s.shapes.add_textbox(Inches(0.8), Inches(4.2), Inches(11.7), Inches(2.4))
            sb.text_frame.word_wrap = True
            sb.text_frame.paragraphs[0].text = subtitle
            sb.text_frame.paragraphs[0].font.size = Pt(16)
            sb.text_frame.paragraphs[0].font.color.rgb = RGBColor(0x55, 0x55, 0x55)
            _tnr(sb.text_frame)
        _tnr(tb.text_frame)

    # -- public API --------------------------------------------------------
    def bullets(self, title: str, items: list[str]):
        s = self._slide()
        self._heading(s, title, size=26)
        bb = s.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.7), Inches(5.6))
        tf = bb.text_frame
        tf.word_wrap = True
        for i, b in enumerate(items):
            par = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            par.text = "•  " + b
            par.font.size = Pt(min(self.body_pt, 18))
            par.space_after = Pt(10)
        _tnr(tf)
        return s

    def chart(self, title: str, image_path: str, caption: str = ""):
        s = self._slide()
        self._heading(s, title, size=23)
        s.shapes.add_picture(image_path, Inches(1.2), Inches(1.2), height=Inches(4.95))
        if caption and self.audience not in _CAPTIONS:
            cb = s.shapes.add_textbox(Inches(0.5), Inches(6.35), Inches(12.3), Inches(1.0))
            cb.text_frame.word_wrap = True
            cp = cb.text_frame.paragraphs[0]
            cp.text = caption
            cp.font.size = Pt(11.5)
            cp.font.color.rgb = GREY
            _tnr(cb.text_frame)
        return s

    def save(self, path: str):
        self.prs.save(path)
        _patch_theme_font(path)
        _patch_notes_master_decl(path)
        return path


# ----------------------------------------------------------------------------
def pipeline_diagram(stages: list[list[str]], out_path: str, title: str = "Analysis pipeline"):
    """Draw a left-to-right data/process flow diagram.

    stages: a list of columns; each column is a list of box labels (use \\n for line breaks).
    Arrows are drawn from every box in column i to every box in column i+1.
    Colours cycle blue -> purple -> green -> gold across columns.
    """
    cols = len(stages)
    fig, ax = plt.subplots(figsize=(2.4 * cols + 1.5, 5.0))
    ax.axis("off")
    ax.set_xlim(0, cols * 3.0)
    ax.set_ylim(0, 6.2)
    palette = ["#dbe9f6", "#e9e3f2", "#e7f2e3", "#f6ecd9", "#f6dede"]
    centres = {}
    for ci, col in enumerate(stages):
        n = len(col)
        gap = 5.4 / max(n, 1)
        x = ci * 3.0 + 0.2
        for ri, label in enumerate(col):
            y = 5.6 - (ri + 0.5) * gap
            h = min(gap * 0.8, 1.7)
            ax.add_patch(FancyBboxPatch((x, y - h / 2), 2.5, h, boxstyle="round,pad=0.05",
                                        fc=palette[ci % len(palette)], ec="#333", lw=1))
            ax.text(x + 1.25, y, label, ha="center", va="center", fontsize=8.5)
            centres.setdefault(ci, []).append((x + 2.5, y, x))
    for ci in range(cols - 1):
        for (x2, y2, _) in centres[ci]:
            for (_, y1, x1n) in centres[ci + 1]:
                ax.add_patch(FancyArrowPatch((x2, y2), (x1n, y1), arrowstyle="-|>",
                                             mutation_scale=13, color="#666", lw=1.1))
    ax.text(cols * 1.5, 6.0, title, ha="center", fontsize=12, weight="bold")
    fig.savefig(out_path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out_path
