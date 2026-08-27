# Architecture Documentation (arc42 + C4 + ADR) Reference

This specification defines how architecture documentation layered on the Diátaxis Explanation quadrant is audited. The five frameworks are complementary, not competing — each governs a different object level.

## 1. Framework Role Mapping (Layering)

| Layer | Framework | Answers | Governs |
| :--- | :--- | :--- | :--- |
| Classification | Diátaxis | What kind of document is this? | Entire `docs/` set (`diataxis-spec.md`) |
| Knowledge file format | OKF (Open Knowledge Format) | How is knowledge serialized with metadata? | Per-file YAML frontmatter: `type`, provenance, trust, lifecycle (`okf-spec.md`) |
| Document structure | arc42 | What sections does an architecture doc have? | Architecture docs in `explanation/` |
| Diagrams | C4 | How is architecture drawn at each zoom level? | arc42 §3/§5 diagrams |
| Decision rationale | ADR | Why was this decided? | Individual records in `decisions/` |

Composition rule: arc42 §3/§5 contain C4-level diagrams; arc42 §9 links ADR records; the whole arc42 document belongs to the Diátaxis Explanation quadrant. None of these replaces Diátaxis classification. The upstream OKF spec defines only the knowledge file format and does NOT prescribe an organizational taxonomy — the `docs/okf/` Diátaxis-quadrant hub layout is this repository's convention layered on top of OKF (see `okf-spec.md`).

## 2. Detection (Conditional Activation)

The architecture audit activates **per artifact**, not all-or-nothing:

- **ADR audit**: activates when a `decisions/` directory exists (`docs/okf/reference/decisions/` or `docs/decisions/`)
- **arc42 + C4 audit**: activates when an architecture document is detected — filename pattern (`architecture*.md`, `arc42*.md`) under `docs/`, or arc42 section headers present (e.g. "Context and Scope", "Building Block View", "Architectural Decisions")

Both artifacts present → full audit. Neither → skipped entirely — non-architecture repositories keep the baseline Diátaxis/hub audit behavior and the 100-point scoring matrix unchanged. An ADR-only repository (decisions without an arc42 document) gets the ADR checks only, and is NOT flagged for missing arc42 sections.

## 3. arc42 — 12-Section Structure Checklist

Location: `docs/okf/explanation/` (one document per system, e.g. `architecture.md`).

| # | Section | Audit check |
| :--- | :--- | :--- |
| 1 | Introduction and Goals | Quality goals and key stakeholders stated |
| 2 | Constraints | Technical and organizational constraints listed |
| 3 | Context and Scope | C4 L1 (Context) diagram present; external actors/systems shown |
| 4 | Solution Strategy | Top-level approach; technology choices summarized |
| 5 | Building Block View | C4 L2/L3 breakdown of the system's building blocks |
| 6 | Runtime View | Key scenarios as sequence or flow diagrams |
| 7 | Deployment View | Nodes and deployment mapping of containers |
| 8 | Crosscutting Concepts | Conventions, patterns, standards (logging, security, ...) |
| 9 | Architectural Decisions | Summary table linking to ADR records |
| 10 | Quality Requirements | Quality tree or concrete scenarios |
| 11 | Risks and Technical Debt | Known risks identified |
| 12 | Glossary | Domain and technical terms defined |

Empty sections are acceptable only with an explicit "not applicable" note — silent omission is flagged.

Section-name variants between the arc42 overview page and the downloadable template (e.g. "Constraints" vs "Architecture Constraints", "Architectural Decisions" vs "Architecture Decisions") are treated as equivalent.

## 4. C4 — Zoom-Level Discipline

C4 is adopted as an abstraction discipline, NOT a diagram syntax. Render with Mermaid `graph` keyword only (GitLab renderer compatibility — `flowchart`, `C4Context`, `C4Container` keywords are NOT allowed).

| Level | Shows | Rendering rule |
| :--- | :--- | :--- |
| L1 System Context | System + actors + external systems, no internals | `graph LR`; central node = system of interest, plus one node per actor/external system |
| L2 Container | System boundary + containers (apps, services, DBs) | `graph TD`; `subgraph` = system boundary; node = container with tech in label |
| L3 Component | Inside exactly ONE container | `graph TD`; only components of a single container |

Rules:

- One zoom level per diagram — never mix levels (no DBs in a context diagram, no components in a container diagram)
- Node labels follow repo Mermaid constraints: no quotes, no `()`, no `<br/>`, no circled numerals — use dash separators
- L4 (Code) is out of scope: source code is the single source of truth at that level

## 5. ADR — Decision Record Format

Location: `docs/okf/reference/decisions/` when the OKF hub exists, otherwise `docs/decisions/`. File naming: `NNNN-kebab-case-title.md` with zero-padded sequence.

ADR-lite (Nygard-style) template per record:

```markdown
# NNNN. Decision title

## Status
(Proposed / Accepted / Deprecated / Superseded by NNNN)

## Context
Forces and constraints. Alternatives considered.

## Decision
The decision, stated in a single sentence followed by detail.

## Consequences
Positive, negative, and neutral fallout.
```

Rules:

- One decision per record — atomic and small
- Superseded records are never deleted: update Status and link to the successor
- All records must be indexed in the hub README under the Reference quadrant — orphan audit applies
- The template above (ADR-lite, Nygard-style — NOT a MADR subset) is the minimum audit format; records following the full MADR 4.0.0 template also pass (see Canonical Sources)

## 6. Relationship to Scoring

Architecture audit findings are reported as a separate report section and do NOT alter the 100-point quality matrix (`readme-quality-criteria.md`).

## 7. Canonical Sources

Each link is the normative anchor for a specific claim in this spec — consult the linked page before auditing or extending that claim.

| Framework | Source | Grounds |
| :--- | :--- | :--- |
| Diátaxis | https://diataxis.fr | The four documentation types (tutorials / how-to guides / reference / explanation) |
| OKF | https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md | Knowledge file format: `type` frontmatter, provenance, trust, lifecycle. Note: the `okf/` copy in GoogleCloudPlatform/knowledge-catalog is a frozen snapshot, no longer maintained |
| C4 model | https://c4model.com/introduction | Zoom-level definitions (System Context / Container / Component / Code) as abstraction discipline, not fixed notation |
| ADR / MADR 4.0.0 | https://adr.github.io (concept hub) · https://adr.github.io/madr/ (template spec) | ADR concept; the decision record format this spec audits (ADR-lite/Nygard is the audit minimum) |
| arc42 | https://arc42.org/overview/ | The 12-section structure checklist in section 3 above |
