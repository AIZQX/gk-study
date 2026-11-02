#!/usr/bin/env python3
"""
领域通识报告 Markdown → PDF

用法:
    python3 build_pdf.py 报告.md 报告.pdf [--title "报告标题"] [--author "作者"]

- 优先用本机 Chrome/Chromium 无头打印 PDF；找不到时退回 WeasyPrint。
- 缺少 markdown 库时，自动在技能目录下建 .venv 并安装，然后用它重新运行。
- 术语注释：`**名词**（白话解释）` 中的括号部分会排成浅灰色小一号字。
"""

import argparse
import os
import re
import shutil
import subprocess
import sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV_DIR = os.path.join(SKILL_DIR, ".venv")


def ensure_markdown():
    try:
        import markdown  # noqa: F401
        import pypdfium2  # noqa: F401
        return
    except ImportError:
        pass
    venv_py = os.path.join(VENV_DIR, "bin", "python3")
    if os.name == "nt":
        venv_py = os.path.join(VENV_DIR, "Scripts", "python.exe")
    if os.path.abspath(sys.executable) == os.path.abspath(venv_py):
        try:
            import markdown  # noqa: F401
        except ImportError:
            sys.exit("[ERROR] 虚拟环境里仍然缺少 markdown 库，请手动运行：pip install markdown")
        print("[WARN] 缺少 pypdfium2，目录将不显示页码（可运行 pip install pypdfium2 补上）")
        return
    if not os.path.exists(venv_py):
        print("[INFO] 首次运行：在技能目录创建虚拟环境并安装 markdown …")
        subprocess.check_call([sys.executable, "-m", "venv", VENV_DIR])
    subprocess.check_call([venv_py, "-m", "pip", "install", "-q", "markdown", "pypdfium2", "pillow"])
    os.execv(venv_py, [venv_py, os.path.abspath(__file__)] + sys.argv[1:])


CSS = """
@page {
    size: A4;
    margin: 25mm 20mm 20mm 20mm;
    @top-center {
        content: "HEADER_TEXT";
        font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
        font-size: 8pt; color: #9a9c9e;
    }
    @bottom-center {
        content: counter(page);
        font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
        font-size: 8pt; color: #9a9c9e;
    }
}
@page toc {
    @top-center { content: none; }
}
@page :first {
    @top-center { content: none; }
    @bottom-center { content: none; }
}
body {
    font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans CJK SC", "Droid Sans Fallback", Helvetica, Arial, sans-serif;
    font-size: 10.5pt; line-height: 1.75; color: #2b2f33; text-align: justify;
}
.cover { page-break-after: always; position: relative; height: 245mm; text-align: center; }
.cover .head { position: absolute; top: 52mm; left: 0; right: 0; }
/* 标题和横线放在同一个块里：横线宽度 = 标题实际宽度，最短 70mm */
.cover .title-block { display: inline-block; min-width: 70mm; }
.cover .title { font-size: 36pt; color: #1f2328; font-weight: bold; letter-spacing: 3pt; padding-left: 3pt; line-height: 1.3; }
.cover .title-rule { width: 100%; margin: 6mm 0 5mm; border: none; border-top: 1.8pt solid #9c4a2f; }
.cover .subtitle { font-size: 13pt; color: #7d8185; letter-spacing: 1pt; }
.cover .meta-group { position: absolute; top: 148mm; left: 0; right: 0; text-align: center; }
.cover .meta-grid { display: inline-grid; grid-template-columns: auto auto; row-gap: 2mm; font-size: 9pt; color: #9a9c9e; text-align: left; }
.cover .meta-grid .v { text-align: justify; text-align-last: justify; }
.cover .meta-grid .punct-end { margin-right: -0.04em; }
.cover .meta-grid .full { grid-column: 1 / 3; text-align: center; }
.cover .sign { position: absolute; bottom: 6mm; left: 15%; right: 15%; display: flex; align-items: center; }
.cover .sign::before, .cover .sign::after { content: ""; flex: 1; border-top: 0.6pt solid #dcdcdc; }
.cover .sign span { padding: 0 5mm; font-size: 8.5pt; color: #cdcfd1; letter-spacing: 1pt; }
h2 {
    page-break-before: always; font-size: 18pt; color: #9c4a2f;
    border-bottom: 1.5pt solid #9c4a2f; padding-bottom: 2mm; margin-top: 4mm; margin-bottom: 5mm;
}
h3 { font-size: 13.5pt; color: #3d4247; margin-top: 8mm; margin-bottom: 3mm; }
h4 { font-size: 11.5pt; color: #5c6166; margin-top: 5mm; margin-bottom: 2mm; }
h2, h3, h4 { break-after: avoid; page-break-after: avoid; }
p { margin: 0 0 1em 0; orphans: 3; widows: 3; text-indent: 2em; }
li > p { margin-bottom: 0.4em; }
blockquote p { margin: 0 0 0.5em 0; }
li p, blockquote p, td p, th p, .cover p, p.no-indent { text-indent: 0; }
strong, b { font-weight: bold; color: #1f2328; }
h3 .hnum { color: #9c4a2f; }
ol.sources > li { text-align: left; margin-bottom: 1.8mm; }
.src-link { display: block; color: #1a5fb4; font-weight: normal; font-size: 0.9em; line-height: 1.6;
    text-decoration: underline; text-decoration-thickness: 0.5pt; text-underline-offset: 1.5pt;
    word-break: break-all; margin-top: 0.6mm; }
.mindmap { text-align: center; margin: 2mm 0 0 0; break-inside: avoid; page-break-inside: avoid; }
.mindmap svg { max-width: 100%; }
p.label { margin: 5.5mm 0 2mm 0; }
p.note { color: #8c9093; font-size: 0.9em; }
.gloss { color: #8c9093; font-size: 0.9em; font-weight: normal; }
/* 目录页：标题居中、下方灰色细线；条目 = 标题 + 点状引导线 + 起始页码；整页不用蓝色 */
.toc-page { page: toc; page-break-after: always; }
.toc-title { text-align: center; font-size: 18pt; font-weight: bold; color: #2b2f33; letter-spacing: 0.6em; padding-left: 0.6em; margin: 4mm 0 4mm; }
.toc-rule { border: none; border-top: 1.5pt solid #c9c9c9; margin: 0 0 9mm 0; }
.toc-item { margin-bottom: 6mm; }
.toc-line { display: flex; align-items: baseline; font-size: 11pt; color: #2b2f33; line-height: 1.5; }
.toc-dots { flex: 1; min-width: 8mm; margin: 0 2.5mm; height: 0.8pt; position: relative; top: -0.3em;
    background-image: radial-gradient(circle, #bdbdbd 0.4pt, transparent 0.55pt); background-size: 4.5pt 0.8pt; background-repeat: repeat-x;
    -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.toc-num { min-width: 5mm; text-align: right; }
.toc-desc { display: block; color: #8c9093; font-size: 9pt; line-height: 1.6; margin-top: 1mm; padding-right: 12mm; }
blockquote {
    margin: 4mm 0; padding: 4mm 4mm 4mm 10mm; background: #f7f6f4;
    border-left: 3pt solid #9c4a2f; color: #5c6166; font-size: 10pt;
}
code {
    font-family: Menlo, "Courier New", monospace; background: #f4f0ec; color: #9c4a2f;
    padding: 0.5mm 1.5mm; border-radius: 2pt; font-size: 9.5pt;
}
pre code { display: block; padding: 3mm; white-space: pre-wrap; }
table { width: 100%; border-collapse: collapse; border: 0.6pt solid #c9c9c9; margin: 4mm 0; font-size: 9.5pt; page-break-inside: avoid; }
thead th { background: #efedea; color: #1f2328; border-bottom: 1pt solid #1f2328; padding: 3mm; text-align: left; font-weight: bold; }
tbody td { text-align: left; padding: 2.5mm 3mm; border-bottom: 0.5pt solid #c9c9c9; vertical-align: top; }
tbody tr:nth-child(even) { background: #faf9f7; }
hr { border: none; border-top: 0.5pt solid #c9c9c9; margin: 4mm 0; }
ul, ol { margin: 2mm 0; padding-left: 8mm; }
li { margin-bottom: 1mm; word-break: break-word; }
a { color: #5c6166; text-decoration: none; word-break: break-all; }
"""

GLOSS_RE = re.compile(r"(<strong>[^<]{1,60}</strong>)\s*（([^（）]{1,200})）")


TOC_HEAD_RE = re.compile(r"<(p|h[2-6])>\s*(?:<strong>)?\s*目录\s*(?:</strong>)?\s*</\1>\s*", re.S)
NUM_RE = re.compile(r"^[一二三四五六七八九十]+、")


def format_toc(body, toc_pages=None):
    """目录里的附属说明（子列表项，或带「·」的非编号项）并入上一项，显示为无圆点的浅灰小字。"""
    m = TOC_HEAD_RE.search(body)
    if not m or not body[m.end():].startswith("<ul>"):
        return body
    start = m.end()
    depth, i, end = 0, start, None
    tag_re = re.compile(r"</?ul>")
    for t in tag_re.finditer(body, start):
        depth += 1 if t.group(0) == "<ul>" else -1
        if depth == 0:
            end = t.end()
            break
    if end is None:
        return body
    block = body[start:end]

    items, depth = [], 0
    for t in re.finditer(r"<ul>|</ul>|<li>(.*?)(?=<ul>|</li>)", block, re.S):
        tok = t.group(0)
        if tok == "<ul>":
            depth += 1
        elif tok == "</ul>":
            depth -= 1
        else:
            text = re.sub(r"</?p>", "", t.group(1)).strip()
            if text:
                items.append((depth, text))

    entries = []
    for d, text in items:
        is_desc = entries and (d > 1 or ("·" in text and not NUM_RE.match(text)))
        if is_desc:
            entries[-1][1].append(text)
        else:
            entries.append([text, []])

    pages = toc_pages or {}
    out = ['<div class="toc-page"><div class="toc-title">目录</div><hr class="toc-rule">']
    for main, descs in entries:
        num = pages.get(toc_key(main), "")
        dots = '<span class="toc-dots"></span>' if num else '<span style="flex:1"></span>'
        desc_html = "".join(f'<span class="toc-desc">{x}</span>' for x in descs)
        out.append(f'<div class="toc-item"><div class="toc-line"><span class="toc-text">{main}</span>'
                   f'{dots}<span class="toc-num">{num}</span></div>{desc_html}</div>')
    out.append("</div>")
    return body[:m.start()] + "\n".join(out) + body[end:]


MINDMAP_RE = re.compile(r"^```mindmap[ \t]*\n(.*?)\n```[ \t]*$", re.M | re.S)
MM_SIZE = [15, 11.5, 9.5, 8.5]           # 各层字号（pt）：中心、章节、阶段/分块、要点
MM_COLOR = ["#1f2328", "#1f2328", "#2b2f33", "#5c6166"]
MM_WEIGHT = ["bold", "bold", "normal", "normal"]
MM_MAX_W, MM_MAX_H = 482, 610           # 版心宽 170mm、导图最大高度（pt）
MM_AREA_H = 640                         # 「总览」标题横线以下的可用高度（pt）


def _tw(text, size):
    """估算文字宽度：中文和全角符号按 1 个字宽，其余按 0.56 个字宽。"""
    return sum(size if (ord(c) > 0x2E80 or c in "—…→←↔") else size * 0.56 for c in text)


def render_mindmap(src):
    """把缩进列表画成从左到右展开的思维导图（SVG）。第一行是中心，往下每缩进一层是一级分支。"""
    from html import escape
    rows = []
    for line in src.splitlines():
        if not line.strip():
            continue
        body = line.lstrip(" \t")
        ind = len(line.expandtabs(2)) - len(body.expandtabs(2))
        rows.append((ind, re.sub(r"^[-*+]\s+", "", body).strip()))
    if not rows:
        return ""
    levels = sorted({i for i, _ in rows})
    root, stack = None, []
    for ind, text in rows:
        node = {"text": text, "depth": levels.index(ind), "children": []}
        while stack and stack[-1]["depth"] >= node["depth"]:
            stack.pop()
        if stack:
            stack[-1]["children"].append(node)
        elif root is None:
            root = node
        else:
            root["children"].append(node)
        stack.append(node)

    def walk(n):
        yield n
        for c in n["children"]:
            yield from walk(c)

    def size(d):
        return MM_SIZE[min(d, len(MM_SIZE) - 1)]

    # 纵向位置：叶子逐行排，父节点在子节点中间；章节之间、阶段之间额外留空
    row_h, cur = 21.0, [0.0]

    def place(n):
        if not n["children"]:
            n["y"] = cur[0] + row_h / 2
            cur[0] += row_h
            return
        for c in n["children"]:
            place(c)
            if n["depth"] == 0:
                cur[0] += 12
            elif n["depth"] == 1:
                cur[0] += 3
        ys = [c["y"] for c in n["children"]]
        n["y"] = (ys[0] + ys[-1]) / 2

    place(root)
    height = cur[0]
    # 横向位置：每一层一列，列宽取这一层最宽的文字
    depth_max = max(n["depth"] for n in walk(root))
    widths = [0.0] * (depth_max + 1)
    for n in walk(root):
        n["w"] = _tw(n["text"], size(n["depth"]))
        widths[n["depth"]] = max(widths[n["depth"]], n["w"])
    gap, xs = 22.0, [4.0]
    for d in range(1, depth_max + 1):
        xs.append(xs[d - 1] + widths[d - 1] + gap)
    width = xs[-1] + widths[-1] + 4

    parts = []
    for n in walk(root):
        for c in n["children"]:
            x1, y1 = xs[n["depth"]] + n["w"] + 4, n["y"]
            x2, y2 = xs[c["depth"]] - 4, c["y"]
            mx = (x1 + x2) / 2
            color, sw = ("#8c9093", 1.0) if n["depth"] == 0 else ("#c9c9c9", 0.8)
            parts.append(f'<path d="M{x1:.1f},{y1:.1f} C{mx:.1f},{y1:.1f} {mx:.1f},{y2:.1f} {x2:.1f},{y2:.1f}" '
                         f'fill="none" stroke="{color}" stroke-width="{sw}"/>')
    for n in walk(root):
        d = min(n["depth"], len(MM_SIZE) - 1)
        parts.append(f'<text x="{xs[n["depth"]]:.1f}" y="{n["y"]:.1f}" dominant-baseline="central" '
                     f'font-size="{MM_SIZE[d]}" fill="{MM_COLOR[d]}" font-weight="{MM_WEIGHT[d]}">{escape(n["text"])}</text>')
    scale = min(1.0, MM_MAX_W / width, MM_MAX_H / height)
    if scale < 0.8:
        print(f"[WARN] 思维导图内容偏多，已缩小到 {scale:.0%}，建议精简要点")
    font = '"PingFang SC","Hiragino Sans GB","Microsoft YaHei","Noto Sans CJK SC",sans-serif'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.1f} {height:.1f}" '
            f'width="{width * scale:.1f}pt" height="{height * scale:.1f}pt" font-family=\'{font}\'>'
            + "".join(parts) + "</svg>")


URL_RE = re.compile(r"https?://[^\s<>\"，。；、）]+")


def format_sources(body):
    """信息来源：每条先写来源说明，末尾加冒号，链接另起一行，显示为蓝色带下划线的链接。"""
    m = re.search(r"<h2>[^<]*信息来源</h2>", body)
    if not m:
        return body
    nxt = body.find("<h2", m.end())
    end = nxt if nxt != -1 else len(body)
    sec = body[m.end():end]

    def fix_li(li):
        inner = li.group(1)
        parts, pos = [], 0
        for u in URL_RE.finditer(inner):
            url = u.group(0).rstrip(".:")
            text = inner[pos:u.start()]
            text = re.sub(r"^[\s；;，,]+", "", text) if parts else text
            text = re.sub(r"[\s.:：]+$", "", text)
            parts.append(f"{text}：" if text else "")
            parts.append(f'<a class="src-link" href="{url}">{url}</a>')
            pos = u.start() + len(url)
        if not parts:
            return li.group(0)
        tail = re.sub(r"^[\s。.；;，,]+$", "", inner[pos:])
        return "<li>" + "".join(parts) + tail + "</li>"

    sec = re.sub(r"<li>(.*?)</li>", fix_li, sec, flags=re.S)
    sec = sec.replace("<ol>", '<ol class="sources">').replace('<ol start=', '<ol class="sources" start=')
    return body[:m.end()] + sec + body[end:]


COVER_TITLE_MAX = 7  # 封面大标题每行最多 7 个字（英文和数字按半个字算）


def _units(text):
    return sum(1 if ord(c) > 0x2E80 else 0.5 for c in text)


def split_cover_title(title, manual=None):
    """封面标题不超过 7 个字时一行；8 个字及以上分成两行，两行尽量等长，不拆开英文单词和数字。
    manual：用「/」手动指定的断行位置，如「认知神经科学/研究方法」。"""
    if manual:
        return manual
    if _units(title) <= COVER_TITLE_MAX:
        return [title]
    total, best, best_diff = _units(title), None, None
    for i in range(1, len(title)):
        a, b = title[:i], title[i:]
        if re.match(r"[A-Za-z0-9]", title[i - 1]) and re.match(r"[A-Za-z0-9]", title[i]):
            continue  # 不在英文单词或数字中间断开
        a, b = a.rstrip(), b.lstrip()
        diff = abs(_units(a) - _units(b))
        fits = _units(a) <= COVER_TITLE_MAX and _units(b) <= COVER_TITLE_MAX
        # 优先在「与、和、及、的、·、空格」这类连接处断行（两行都不超过 7 个字时），避免拆开词语；
        # 其次两行尽量等长，再其次第一行不短于第二行
        natural = title[i - 1] in "与和及的·、 " or title[i] in "· "
        key = (0 if fits else 1, 0 if natural else 1, diff, 0 if _units(a) >= _units(b) else 1)
        if best is None or key < best_diff:
            best, best_diff = [a, b], key
    if _units(best[0]) > COVER_TITLE_MAX or _units(best[1]) > COVER_TITLE_MAX:
        print(f"[WARN] 封面标题「{title}」超过两行 14 个字，建议改用更短的领域名")
    return best


CLOSE_PUNCT = "）」』】》〉〕］｝。，、；：！？"


def meta_value_html(value):
    """封面信息的内容：以全角收尾符号（如「）」）结尾时，抵掉它右半格的空白，
    让两行按笔画的实际右边缘对齐，而不是按字格对齐。"""
    from html import escape
    value = value.strip()
    if value and value[-1] in CLOSE_PUNCT:
        return f'{escape(value[:-1])}<span class="punct-end">{escape(value[-1])}</span>'
    return escape(value)


def toc_key(text):
    """目录条目和章节标题的匹配键：去掉标签和空白，取冒号前的部分（如「一、开篇导读」「术语表」）。"""
    t = re.sub(r"<[^>]+>|\s", "", text)
    return re.split(r"[：:]", t, 1)[0]


def toc_entries(md_text):
    """返回目录里所有主条目的匹配键，用于第二遍排版时查页码。"""
    import markdown
    body = markdown.markdown(md_text, extensions=["tables", "fenced_code", "sane_lists"], output_format="html5")
    marker = format_toc(body, {"__collect__": True})
    return [toc_key(x) for x in re.findall(r'<span class="toc-text">(.*?)</span>', marker, re.S)]


def find_toc_pages(pdf_path, keys, header):
    """读回第一遍生成的 PDF，找到每个章节标题所在页（章节都另起一页，标题在页首）。"""
    try:
        import pypdfium2 as pdfium
    except ImportError:
        return {}
    doc = pdfium.PdfDocument(pdf_path)
    texts = []
    for i in range(len(doc)):
        t = doc[i].get_textpage().get_text_range()
        t = re.sub(r"\s", "", t).replace(re.sub(r"\s", "", header), "", 1)
        t = re.sub(r"^(第)?\d+(页)?", "", t)  # 去掉页脚页码
        texts.append(t)
    doc.close()
    result, start = {}, 2  # 第 1 页封面、第 2 页目录
    for k in keys:
        for i in range(start, len(texts)):
            if texts[i].startswith(k):
                result[k] = str(i + 1)
                start = i + 1
                break
    return result


def build_html(md_text, title, author, toc_pages=None):
    import markdown
    from html import escape

    meta_line = ""
    for line in md_text.splitlines():
        s = line.strip().lstrip(">").strip()
        if "研究时间" in s or "所属领域" in s or "研究对象类型" in s:
            meta_line = s
            break

    mindmaps = []

    def _mm(mm):
        mindmaps.append(render_mindmap(mm.group(1)))
        return f"\n\nMINDMAPPLACEHOLDER{len(mindmaps) - 1}\n\n"

    md_text = MINDMAP_RE.sub(_mm, md_text)
    body = markdown.markdown(md_text, extensions=["tables", "fenced_code", "sane_lists"], output_format="html5")
    for i, svg in enumerate(mindmaps):
        # 导图在标题横线以下的剩余空间里略高于正中（视觉中心），不贴着横线
        h = float(re.search(r'height="([\d.]+)pt"', svg).group(1)) if svg else 0
        top = max(8.0, (MM_AREA_H - h) * 0.45)
        body = body.replace(f"<p>MINDMAPPLACEHOLDER{i}</p>",
                            f'<div class="mindmap" style="margin-top:{top:.0f}pt">{svg}</div>')

    m = re.search(r"<h1>(.*?)</h1>", body)
    if m:
        if not title:
            title = re.sub(r"<[^>]+>", "", m.group(1))
        body = body.replace(m.group(0), "", 1)
    title = title or "领域通识报告"
    # 封面和页眉只显示领域名：去掉标题末尾的「横纵通识报告」「领域通识报告」之类后缀
    title = re.sub(r"[\s：:·|\-—_]*(横纵)?(领域)?(通识|分析)?(深度)?(研究)?报告$", "", title).strip() or title
    # 「/」只用来指定封面断行，页眉、目录等其他地方显示时去掉
    manual_lines = [x.strip() for x in title.split("/") if x.strip()] if "/" in title else None
    title = title.replace("/", "").strip()

    # 去掉正文里与封面重复的元信息行
    if meta_line:
        body = re.sub(r"<blockquote>\s*<p>[^<]*研究时间[^<]*</p>\s*</blockquote>", "", body, count=1)

    body = format_toc(body, toc_pages)
    # 「目录」这类独占一行的加粗标签不缩进
    body = re.sub(r"<p>(<strong>[^<]{1,60}</strong>)</p>", r'<p class="no-indent label">\1</p>', body)
    # 文末方法论说明（全文最后一条 --- 之后的斜体段）：浅灰、顶格，不显示「方法论说明：」字样
    body = re.sub(r"<p><em>\s*方法论说明[：:]\s*", '<p class="no-indent note"><em>', body)
    body = re.sub(r"(<hr\s*/?>\s*)<p>(<em>[^<]*</em>)</p>\s*$", r'\1<p class="no-indent note">\2</p>', body)
    # 术语表、信息来源标题下的说明行（如「以下来源访问日期均为……」）顶格，不缩进
    body = re.sub(r"(<h2>(?:[^<]*)(?:术语表|信息来源)</h2>\s*)<p>", r'\1<p class="no-indent note">', body)
    # 二级标题：只有编号（如 2.1）染成赭红，标题文字不染
    body = re.sub(r"<h3>(\d+(?:\.\d+)+)\s*", r'<h3><span class="hnum">\1</span> ', body)
    body = format_sources(body)
    body = GLOSS_RE.sub(r'\1<span class="gloss">（\2）</span>', body)

    header = f"{title}  |  领域通识报告".replace('"', "'")
    css = CSS.replace("HEADER_TEXT", header)
    # 元信息按竖线拆开，每项一行；封面只留研究时间和所属领域。
    # 标签列左对齐，内容列两端对齐，较短的内容（如日期）拉开字距，与最长一行右边对齐
    meta_items = [x.strip() for x in re.split(r"[|｜]", meta_line) if x.strip()]
    meta_items = [x for x in meta_items if not x.startswith("研究对象类型")]
    meta_html = ""
    if meta_items:
        cells = []
        for x in meta_items:
            kv = re.match(r"^([^：:]{1,8})[：:]\s*(.+)$", x)
            if kv:
                cells.append(f'<div class="k">{escape(kv.group(1))}：</div><div class="v">{meta_value_html(kv.group(2))}</div>')
            else:
                cells.append(f'<div class="full">{escape(x)}</div>')
        meta_html = f'<div class="meta-group"><div class="meta-grid">{"".join(cells)}</div></div>'
    title_html = "<br>".join(escape(x) for x in split_cover_title(title, manual_lines))
    cover = f"""
<div class="cover">
  <div class="head">
    <div class="title-block">
      <div class="title">{title_html}</div>
      <hr class="title-rule">
    </div>
    <div class="subtitle">领域通识报告</div>
  </div>
  {meta_html}
  <div class="sign"><span>{escape(author)}</span></div>
</div>"""
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><title>{escape(title)}</title>
<style>{css}</style></head>
<body>{cover}
{body}
</body></html>"""


def find_chrome():
    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    ]
    for name in ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "msedge"]:
        p = shutil.which(name)
        if p:
            candidates.append(p)
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


def to_pdf(html_path, pdf_path):
    chrome = find_chrome()
    if chrome:
        url = "file://" + os.path.abspath(html_path)
        subprocess.run(
            [chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
             f"--print-to-pdf={os.path.abspath(pdf_path)}", url],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300,
        )
        if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
            return "Chrome"
    try:
        from weasyprint import HTML
        HTML(filename=html_path).write_pdf(pdf_path)
        return "WeasyPrint"
    except Exception as e:  # noqa: BLE001
        sys.exit(f"[ERROR] 没有可用的 PDF 引擎（未找到 Chrome，WeasyPrint 也不可用：{e}）。"
                 f"HTML 已生成，可在浏览器中打开后手动打印为 PDF：{html_path}")


def main():
    ensure_markdown()
    ap = argparse.ArgumentParser(description="领域通识报告 Markdown → PDF")
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--title", default=None)
    ap.add_argument("--author", default="AIZ小朱")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        md_text = f.read()
    html = build_html(md_text, args.title, args.author)

    html_path = os.path.splitext(args.output)[0] + ".html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[OK] HTML 已生成: {html_path}")

    if os.path.exists(args.output):
        os.remove(args.output)
    engine = to_pdf(html_path, args.output)

    # 第二遍：读回 PDF 得到各章起始页，填进目录再生成一次（目录独占一页，填页码不会改变分页）
    keys = toc_entries(md_text)
    if keys:
        title_for_header = re.search(r'<title>(.*?)</title>', html).group(1)
        pages = find_toc_pages(args.output, keys, f"{title_for_header}|领域通识报告")
        if pages:
            html = build_html(md_text, args.title, args.author, pages)
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html)
            os.remove(args.output)
            engine = to_pdf(html_path, args.output)
            missing = [k for k in keys if k not in pages]
            print(f"[OK] 目录页码已填入（{len(pages)} 项）" + (f"，未找到：{missing}" if missing else ""))
    print(f"[OK] PDF 已生成（{engine}）: {args.output} ({os.path.getsize(args.output) / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
