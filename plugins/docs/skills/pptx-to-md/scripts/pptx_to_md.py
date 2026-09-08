#!/usr/bin/env python3
"""pptx2md — PPTX를 충실한(faithful) Markdown으로 변환한다.

Usage:
    python pptx2md.py <input.pptx> [-o output.md] [--no-images] [--force]

- 기본 출력: 입력 파일과 동일 경로에 <stem>.md
- 표 → GFM table (셀 내 줄바꿈은 <br>, '|'는 이스케이프)
- 제목 placeholder → '## Slide N — 제목'
- 발표자 노트 → blockquote
- 삽입 이미지 → <output_stem>_assets/ 로 추출 후 상대 링크
- SmartArt(diagram) → 노드 텍스트 목록 (best-effort)
- Wingdings 등 PUA 문자 → 유니코드 정규화
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from datetime import date
from pathlib import Path

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.oxml.ns import qn

try:
    from lxml import etree
except ImportError:  # pragma: no cover
    sys.exit("lxml required: uv run --with python-pptx python pptx2md.py ...")

DGM_NS = "http://schemas.openxmlformats.org/drawingml/2006/diagram"

# Wingdings 주요 PUA(F0xx) 매핑 — 확실한 것만
PUA_MAP = {
    "": "•",
    "": "→",
    "": "←",
    "": "↑",
    "": "→",
    "": "✓",
    "": "✗",
    "": "☑",
    "": "▪",
    "": "□",
}

CTRL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def clean(text: str) -> str:
    text = CTRL_RE.sub("", text.replace("\r", ""))
    return "".join(PUA_MAP.get(ch, ch) for ch in text)


def cell_text(cell) -> str:
    return clean(cell.text).replace("\n", "<br>").replace("|", "\\|").strip()


def para_lines(tf) -> list[str]:
    """buChar/buAutoNum 단락에 불릿, lvl에 들여쓰기 적용."""
    lines: list[str] = []
    for p in tf.paragraphs:
        t = clean(p.text).strip()
        if not t:
            continue
        pPr = p._p.find(qn("a:pPr"))
        bullet = False
        lvl = 0
        if pPr is not None:
            lvl = int(pPr.get("lvl") or 0)
            bullet = pPr.find(qn("a:buChar")) is not None or pPr.find(
                qn("a:buAutoNum")
            ) is not None
        lines.append(f"{'  ' * lvl}- {t}" if bullet else t)
    return lines


def walk_shapes(shapes):
    """그룹 재귀 평탄화. (shape_kind, payload) 생성기."""
    for sh in shapes:
        if sh.shape_type == MSO_SHAPE_TYPE.GROUP:
            yield from walk_shapes(sh.shapes)
        elif sh.shape_type == MSO_SHAPE_TYPE.PICTURE:
            yield ("pic", sh)
        elif getattr(sh, "has_table", False) and sh.has_table:
            yield ("tbl", sh.table)
        elif getattr(sh, "has_text_frame", False) and sh.has_text_frame:
            yield ("txt", sh)


def shape_sort_key(sh):
    top = sh.top if sh.top is not None else 0
    left = sh.left if sh.left is not None else 0
    return (top, left)


def diagram_texts(slide) -> list[str]:
    """SmartArt(diagramData part)의 노드 텍스트 추출 (best-effort)."""
    out: list[str] = []
    for rel in slide.part.rels.values():
        if "diagramData" not in rel.reltype:
            continue
        try:
            root = etree.fromstring(rel.target_part.blob)
        except Exception:
            continue
        for pt in root.findall(f".//{{{DGM_NS}}}pt"):
            if pt.get("type") not in (None, "node", "pres"):
                continue
            t = "".join(e.text or "" for e in pt.findall(f".//{{{DGM_NS}}}t")).strip()
            if t:
                out.append(clean(t))
    # 연속 중복 제거 (동일 파트가 여러 rel로 참조되는 경우 방어)
    return [t for i, t in enumerate(out) if i == 0 or t != out[i - 1]]


def render_table(tbl) -> list[str]:
    rows = [[cell_text(c) for c in r.cells] for r in tbl.rows]
    if not rows:
        return []
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    lines = ["| " + " | ".join(rows[0]) + " |", "| " + " | ".join([":---"] * width) + " |"]
    lines += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return lines


def extract_image(pic, out_dir: Path, slide_no: int) -> str | None:
    try:
        img = pic.image
        blob = img.blob
    except Exception:
        return None
    digest = hashlib.sha1(blob).hexdigest()[:8]
    ext = {"jpeg": "jpg", "jpg": "jpg"}.get(img.ext, img.ext or "png")
    name = f"slide{slide_no:02d}-{digest}.{ext}"
    path = out_dir / name
    if not path.exists():
        path.write_bytes(blob)
    return name


def convert(src: Path, dst: Path, with_images: bool) -> dict:
    prs = Presentation(str(src))
    slides = list(prs.slides)
    assets_dir = dst.parent / f"{dst.stem}_assets"
    if with_images:
        assets_dir.mkdir(parents=True, exist_ok=True)

    stats = {"slides": len(slides), "tables": 0, "images": 0, "notes": 0}
    out: list[str] = [
        f"# {src.stem}",
        "",
        f"> **Source**: `{src.name}` | **Slides**: {len(slides)} | **Generated**: {date.today().isoformat()}",
        "",
    ]

    for no, slide in enumerate(slides, 1):
        title = ""
        try:
            if slide.shapes.title is not None:
                title = clean(slide.shapes.title.text).strip()
        except Exception:
            pass
        out.append("---")
        out.append("")
        out.append(f"## Slide {no} — {title}" if title else f"## Slide {no}")
        out.append("")

        # 최상위 shape를 (top, left) 정렬로 순회 → 근사 읽기 순서
        for sh in sorted(slide.shapes, key=shape_sort_key):
            for kind, payload in walk_shapes([sh]):
                if kind == "tbl":
                    lines = render_table(payload)
                    if lines:
                        stats["tables"] += 1
                        out += lines + [""]
                elif kind == "txt":
                    lines = para_lines(payload.text_frame)
                    if lines:
                        out += lines + [""]
                elif kind == "pic":
                    if not with_images:
                        continue
                    name = extract_image(payload, assets_dir, no)
                    if name:
                        stats["images"] += 1
                        out.append(f"![slide-{no}](<{assets_dir.name}/{name}>)")
                        out.append("")
                    else:
                        out.append(f"> [이미지: slide {no} — 추출 불가]")
                        out.append("")

        dgm = diagram_texts(slide)
        if dgm:
            out.append("**[Diagram]**")
            out += [f"- {t}" for t in dgm] + [""]

        if slide.has_notes_slide:
            note = clean(slide.notes_slide.notes_text_frame.text).strip()
            if note:
                stats["notes"] += 1
                out += [f"> {ln}" for ln in note.splitlines() if ln.strip()] + [""]

    dst.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")
    return stats


def main() -> int:
    ap = argparse.ArgumentParser(description="PPTX → faithful Markdown")
    ap.add_argument("input", type=Path)
    ap.add_argument("-o", "--output", type=Path, default=None,
                    help="기본: <inputdir>/<stem>.md")
    ap.add_argument("--no-images", action="store_true", help="이미지 추출 생략")
    ap.add_argument("--force", action="store_true", help="출력 파일 존재 시 덮어쓰기")
    args = ap.parse_args()

    src = args.input.expanduser()
    if not src.is_file() or src.suffix.lower() != ".pptx":
        print(f"ERROR: PPTX 파일이 아님: {src}", file=sys.stderr)
        return 1
    dst = (args.output or src.with_suffix(".md")).expanduser()
    if dst.exists() and not args.force:
        print(f"ERROR: 출력 파일이 이미 존재함 (--force로 덮어쓰기): {dst}", file=sys.stderr)
        return 1
    dst.parent.mkdir(parents=True, exist_ok=True)

    stats = convert(src, dst, with_images=not args.no_images)
    print(f"OK: {dst}")
    print(
        f"  slides={stats['slides']} tables={stats['tables']} "
        f"images={stats['images']} notes={stats['notes']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
