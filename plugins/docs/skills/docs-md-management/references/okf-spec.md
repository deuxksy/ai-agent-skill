# OKF (Open Knowledge Format) Reference

Upstream spec: https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md

The upstream OKF defines a knowledge **file format** (UTF-8 markdown + YAML frontmatter, `type` required, optional provenance/trust/lifecycle metadata) and deliberately does NOT prescribe an organizational taxonomy. The Diátaxis 4-quadrant hub layout for `docs/okf/` defined below is this repository's convention layered on top of OKF.

This specification defines how `docs/okf/` documentation hub is audited.

## 1. Hub Responsibility & Diátaxis Folder Structure
- `docs/okf/README.md` is the Single Source of Truth for OKF documents under `docs/okf/`.
- Root `README.md` links to `docs/okf/README.md` under the Reference quadrant of the Diátaxis index.
- All OKF documentation files under `docs/okf/` MUST be organized into Diátaxis 4-quadrant subfolders:
  - `docs/okf/tutorials/`: Hands-on tutorial documents.
  - `docs/okf/how-to/`: Task-oriented how-to guides.
  - `docs/okf/reference/`: Technical specifications and reference docs.
  - `docs/okf/explanation/`: Conceptual and architectural explanations.
- Individual OKF specification files (`docs/okf/*/*.md`) are indexed under their respective Diátaxis category in `docs/okf/README.md`, NOT listed directly in root `README.md`.

## 2. Orphan Audit Integration
- An OKF document inside `docs/okf/` (e.g. `docs/okf/how-to/example.md`) is considered healthy if it is placed in the correct Diátaxis subfolder AND indexed in `docs/okf/README.md`.
- If an OKF document is unlinked in `docs/okf/README.md` or placed outside the Diátaxis subfolders (directly under `docs/okf/*.md` without being `README.md`), it is flagged as an Orphan/Misplaced Document during the `docs-md-management` audit.
