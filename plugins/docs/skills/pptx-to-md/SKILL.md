---
name: pptx-to-md
description: "Use when converting a PPTX presentation (기획서, design spec, proposal deck) into a faithful Markdown file — extracts slide titles, bulleted paragraphs, GFM tables, speaker notes, SmartArt node text, and embedded images. /docs:pptx-to-md <file.pptx> writes <file.md> next to the input. Also use when the user says 'pptx 마크다운 변환', 'pptx to md', '기획서 md로'."
---

# PPTX to Markdown

One-shot converter: `<file>.pptx` → `<file>.md` (same directory, same basename). Produces a **faithful structural dump** — titles, tables, bullets, notes, images — not a summary. Use it as the grounding source for downstream curation (spec docs, summaries, diffing deck versions).

---

## 1. Preflight

1. Resolve the input path argument (expand `~`, accept absolute or CWD-relative).
2. Verify the file exists and has a `.pptx` extension.
3. For a legacy `.ppt` (OLE2 binary): python-pptx cannot read it. Convert first with LibreOffice if available (`soffice --headless --convert-to pptx --outdir <dir> <file.ppt>`), then convert the `.pptx` and report that fidelity depends on that conversion step. If LibreOffice is not installed, ask the user to re-save as `.pptx` in PowerPoint/Keynote.
4. If `<stem>.md` already exists in the same directory, show both timestamps and ask whether to overwrite (`--force`) or pick another output path.

---

## 2. Convert

```bash
uv run --with python-pptx --no-project python "<this-skill-dir>/scripts/pptx_to_md.py" <input.pptx> [--force]
```

Options:

- `-o <path>` — explicit output path (default: `<inputdir>/<stem>.md`)
- `--no-images` — skip image extraction (text/tables only)
- `--force` — overwrite existing output

The script prints `OK: <path>` plus `slides= tables= images= notes=` counts on success.

---

## 3. Verify

1. Exit code 0 and `OK:` line present.
2. The output file exists and the `**Slides**` header count matches the script's `slides=` count.
3. Spot-check one known table slide: pipe-table rows aligned, `:---` separator row present.
4. On failure, report the exact stderr line — do not retry the same command more than twice (3-Strike).

---

## 4. Report

Reply concisely with:

- Output path and stats line (slides / tables / images / notes)
- Assets directory (`<stem>_assets/`) if images were extracted
- Known limitations that apply to this deck (see below)

---

## Conversion Contract

| PPTX element | Markdown output |
| :--- | :--- |
| Title placeholder | `## Slide N — <title>` |
| Text shape (buChar/buAutoNum paragraphs) | `- item` with indent by `lvl` |
| Table shape | GFM table, `:---` separator, cell `\|` escaped, cell newlines → `<br>` |
| Picture (incl. inside groups) | `![slide-N](<stem>_assets/slideNN-<sha1>.png>)` |
| SmartArt / diagram | `**[Diagram]**` bulleted node text (best-effort) |
| Speaker notes | `> blockquote` under the slide |
| Wingdings/PUA chars (→ ← • ✓ …) | normalized to Unicode |

Slides are separated by `---`; shapes are ordered by (top, left) to approximate reading order.

---

## Limitations

- **Faithful dump, not a summary** — deck annotation callouts and mockup labels interleave. Offer a curated summary (like a spec doc) as a follow-up when the user needs one.
- **`.ppt` legacy format** is not read directly — see Preflight step 3.
- **Merged table cells** flatten to empty cells — Markdown tables cannot merge.
- **SmartArt structure** (arrows, layout) is lost; only node texts survive. Decks whose flowcharts are plain shapes are unaffected.
- **Visual mockups** are extracted as images — a text-only read cannot verify them. When the spec depends on layout, open the extracted images.
- Chart (embedded xlsx) data labels come through as text only if authored as shapes.
