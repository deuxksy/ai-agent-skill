---
name: revise-readme-md
description: "Use when new documentation or features are added and README.md index or summary needs a light incremental update."
---

# Revise README Markdown

Incremental and lightweight updater for `README.md` after adding new documentation files or modifying features.

---

## 1. Fast Preflight

1. Identify newly added or modified markdown files in current task/commit.
2. Filter out internal files (`docs/superpowers/`, `.git/`, `.claude/`, `.gemini/`).
3. If no human markdown docs were added/modified, check if project summary requires adjustment.

---

## 2. Diátaxis Classification & Index Hunk Update

1. Classify new/modified files into Diátaxis quadrants (Tutorials, How-To, Reference, Explanation).
2. Generate targeted hunk diff for `README.md` (or `docs/okf/README.md` if the file is an OKF doc).
3. Re-verify project summary character count (must remain between 100 and 500 characters).

---

## 3. Approval & Apply

1. Present minimal diff for `README.md`.
2. Wait for explicit user approval.
3. Apply surgical change without modifying unrelated sections.

---

## Safety

- Do not rewrite the entire `README.md`.
- Preserve existing badges, quick start, license, and custom sections.
- Exclude `docs/superpowers/` from indexing.
