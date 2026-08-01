# OKF (Open Knowledge Framework) Reference

This specification defines how `docs/okf/` documentation hub is audited.

## 1. Hub Responsibility
- `docs/okf/README.md` is the Single Source of Truth for OKF documents under `docs/okf/`.
- Root `README.md` links to `docs/okf/README.md` under the Reference quadrant of the Diátaxis index.
- Individual OKF specification files under `docs/okf/*.md` are indexed within `docs/okf/README.md`, NOT listed directly in root `README.md`.

## 2. Orphan Audit Integration
- An OKF document inside `docs/okf/` is considered healthy if it is indexed in `docs/okf/README.md`.
- If an OKF document is unlinked in `docs/okf/README.md`, it is flagged as an Orphan Document during the `readme-md-management` audit.
