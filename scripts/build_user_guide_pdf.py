"""Typeset the public GradLife guide as a compact, print-ready PDF."""
from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, KeepTogether, PageBreak, PageTemplate, Paragraph, Spacer, Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "GradLife 使用指南.md"
OUTPUT = ROOT / "output" / "pdf" / "GradLife_个人工作台使用指南.pdf"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

FONT = "ArialUnicode"
pdfmetrics.registerFont(TTFont(FONT, "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"))
NAVY = colors.HexColor("#202C3E")
BLUE = colors.HexColor("#315B9E")
MUTED = colors.HexColor("#617189")
LINE = colors.HexColor("#DFE6EF")
PALE = colors.HexColor("#F3F6FB")
WHITE = colors.white

style = {
    "eyebrow": ParagraphStyle("eyebrow", fontName=FONT, fontSize=9, leading=14, textColor=BLUE, spaceAfter=7),
    "title": ParagraphStyle("title", fontName=FONT, fontSize=25, leading=36, textColor=NAVY, spaceAfter=11),
    "intro": ParagraphStyle("intro", fontName=FONT, fontSize=10.3, leading=18, textColor=MUTED, spaceAfter=15),
    "section": ParagraphStyle("section", fontName=FONT, fontSize=13.5, leading=21, textColor=NAVY, spaceBefore=17, spaceAfter=9, keepWithNext=True),
    "body": ParagraphStyle("body", fontName=FONT, fontSize=9.5, leading=17, textColor=NAVY, spaceAfter=8, alignment=TA_LEFT),
    "small": ParagraphStyle("small", fontName=FONT, fontSize=8.5, leading=14, textColor=NAVY, spaceAfter=0),
    "tablehead": ParagraphStyle("tablehead", fontName=FONT, fontSize=9, leading=15, textColor=WHITE),
    "label": ParagraphStyle("label", fontName=FONT, fontSize=9, leading=15, textColor=BLUE),
    "url": ParagraphStyle("url", fontName=FONT, fontSize=8.5, leading=15, textColor=BLUE),
}

def rich(text):
    text = escape(text)
    # The source is controlled Markdown. Convert only its simple inline syntax.
    import re
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\`(.+?)\`", r"<font color='#315B9E'>\1</font>", text)
    return text

def P(text, kind="body"):
    return Paragraph(rich(text), style[kind])

lines = SOURCE.read_text(encoding="utf-8").splitlines()
story = [P("GRADLIFE  /  QUICK START GUIDE", "eyebrow"), P("个人工作台使用指南", "title")]
story.append(P("安排日常，整理学习与生活。第一次使用，从这里开始。", "intro"))

import re
url = re.search(r"https://[^)\s]+", SOURCE.read_text()).group(0)
url_box = Table([[P("在线试用", "label"), Paragraph(f'<link href="{escape(url)}" color="#315B9E">{escape(url)}</link>', style["url"])]], colWidths=[62, 425])
url_box.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), PALE), ("BOX", (0, 0), (-1, -1), 0.6, LINE), ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 10), ("LEFTPADDING", (0, 0), (-1, -1), 12)]))
story += [url_box, Spacer(1, 8)]

in_table = False
table_rows = []

def flush_table():
    global table_rows
    if not table_rows:
        return
    data = [[P("栏目", "tablehead"), P("主要用途与入口", "tablehead")]]
    for name, detail in table_rows:
        data.append([P(name, "small"), P(detail, "small")])
    t = Table(data, colWidths=[88, 399], repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PALE]),
        ("LINEBELOW", (0, -1), (-1, -1), 0.65, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(t)
    table_rows = []

for line in lines:
    if not line or line.startswith("# ") or line.startswith("**测试网址：**") or line.startswith("更新：") or line.startswith("> ") or line.startswith("GradLife 用来"):
        continue
    if line.startswith("## "):
        flush_table()
        if in_table:
            in_table = False
            story.append(PageBreak())
        story.append(P(line[3:], "section"))
    elif line.startswith("| ---"):
        continue
    elif line.startswith("| 栏目"):
        in_table = True
    elif in_table and line.startswith("|"):
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) == 2:
            table_rows.append(tuple(cells))
    else:
        if in_table:
            flush_table()
            in_table = False
            story += [PageBreak()]
        if line.startswith("- "):
            story.append(P("•  " + line[2:]))
        else:
            story.append(P(line))
flush_table()

class GuideDoc(BaseDocTemplate):
    def __init__(self, path):
        super().__init__(str(path), pagesize=A4, leftMargin=54, rightMargin=54, topMargin=55, bottomMargin=58, title="GradLife 个人工作台使用指南", author="GradLife")
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, leftPadding=0, bottomPadding=0, rightPadding=0, topPadding=0)
        self.addPageTemplates(PageTemplate(id="guide", frames=[frame], onPage=self.decorate))

    def decorate(self, canv, doc):
        w, h = A4
        canv.setStrokeColor(LINE)
        canv.setLineWidth(.6)
        canv.line(54, h - 37, w - 54, h - 37)
        canv.setFillColor(MUTED)
        canv.setFont(FONT, 8)
        canv.drawString(54, h - 29, "GRADLIFE  ·  PERSONAL WORKSPACE")
        canv.line(54, 43, w - 54, 43)
        canv.drawString(54, 28, "使用指南  /  2026.09.16")
        canv.drawRightString(w - 54, 28, f"{doc.page:02d}")

GuideDoc(OUTPUT).build(story)
print(OUTPUT)
