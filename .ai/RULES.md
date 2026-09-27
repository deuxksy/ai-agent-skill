# Repository Common Rules (.ai/RULES.md)

This document serves as the Single Source of Truth (SSoT) for all runtime AI agents working in this repository.

## Project Overview

- **Project**: `zzizily` — Personal automation AI Agent Skill marketplace providing 12 domain plugins.
- **Repository**: `deuxksy/ai-agent-skill`
- **Plugin Versions**: independent per-plugin SemVer (v2.0.0 epoch; `kisa` starts at `1.0.0`). Source of Truth: `.claude-plugin/marketplace.json` (marketplace-registered plugins only)
- **Author**: Crong (kyolim)

## Versioning & Commit Convention

- **SemVer**: Follow Semantic Versioning per plugin. All plugin manifests (`.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`, `plugins/*/.claude-plugin/`, `plugins/*/.codex-plugin/`, `plugins/*/plugin.json`) and catalog tables must stay in sync. `plugins/*/plugin.json` is a symlink to `.claude-plugin/plugin.json` — edit the real file only.
- **Local-only plugins**: Not registered in `marketplace.json`. Never add them to public catalog tables.
- **Conventional Commits**: Commit tag in English (e.g. `feat`, `fix`, `docs`, `chore`), commit message in Korean.

## Core Guidelines

1. **Runtime Neutrality**: Skills must remain runtime-neutral and cross-compatible across Claude, Gemini/Antigravity, and Codex.
2. **SKILL.md Specification** (Agent Skills standard, [agentskills/agentskills](https://github.com/agentskills/agentskills)): Every skill folder under `plugins/<domain>/skills/` must contain a `SKILL.md` with YAML frontmatter:
   ```yaml
   ---
   name: <skill-name>               # 1-64 chars, lowercase/numbers/hyphens only, must match parent directory name
   description: <one-line summary>  # 1-1024 chars: purpose, when to use, keywords
   ---
   ```
   Keep the body under 500 lines; move details to `references/`, executable code to `scripts/`, templates/data to `assets/`. Validate with `skills-ref validate <skill-dir>` (Python tool — `uv sync` from the repo's `skills-ref/`, not on npm).
3. **No Hardcoded Secrets/Paths**: Never commit credentials, personal absolute paths, or unverified environment configurations.
