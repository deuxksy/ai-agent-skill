# docs

Runtime-neutral AI Agent skills for auditing, restructuring, and updating repository `README.md` files and documentation hierarchy based on the Diátaxis framework, OKF standards, orphan document detection, document migration (split/merge/move), layered architecture documentation (arc42 structure + C4 diagrams + ADR records), and converting PPTX decks (기획자료) to faithful Markdown.

## Skills

- `docs-md-management`: Audits `README.md` and overall project documentation under `docs/`, verifies 100~500 char summary, builds Diátaxis document indexes, verifies sub-hubs, detects orphan docs, and conditionally audits architecture documentation (arc42/C4/ADR) per `references/arch-docs-spec.md`.
- `docs-restructure`: Surgically migrates scattered, unstructured project documentation into the standard Diátaxis/OKF hierarchy — moves files (`git mv`), splits multi-role documents, merges duplicates into a single Source of Truth, and updates links repository-wide. Verbatim content only; approval gate on the mapping table. Execution counterpart to `docs-md-management`.
- `revise-readme-md`: Lightly updates `README.md` index and summary when new documentation or features are added.
- `pptx-to-md`: One-shot PPTX → Markdown conversion (`/docs:pptx-to-md deck.pptx` → `deck.md`). Extracts slide titles, bulleted paragraphs, GFM tables, speaker notes, SmartArt node text, and embedded images (`<stem>_assets/`) with Wingdings/PUA normalization via `scripts/pptx_to_md.py` (python-pptx, run with `uv run --with python-pptx`). Legacy `.ppt` requires prior conversion (see SKILL.md Preflight).

## Claude Code

```bash
claude plugin install docs@zzizily
```

호출:

```text
/docs:docs-md-management
/docs:docs-restructure
/docs:revise-readme-md
/docs:pptx-to-md <file.pptx>
```
